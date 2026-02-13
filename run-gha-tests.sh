#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

KEEP=0
NO_PULL=0
WORKDIR=""
TAG="latest"

CONTAINERS=()

usage() {
  cat <<'EOF'
Usage: ./run-gha-tests.sh [options]

Runs the same integration-style tests as .github/workflows/build-and-push-*.yml,
but locally (manual runner). By default, pulls GHCR images and runs all tests in
an ephemeral temp directory.

Options:
  --keep             Keep the temporary workdir (do not delete)
  --workdir DIR      Use DIR instead of creating a temp directory
  --no-pull          Do not docker pull images (use local cache)
  --tag TAG          Image tag to use (default: latest)
  -h, --help         Show this help
EOF
}

die() {
  echo "ERROR: $*" >&2
  exit 1
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "Missing required command: $1"
}

cleanup() {
  # Best-effort cleanup; never fail from cleanup.
  set +e

  # Stop+remove any containers we started.
  for c in "${CONTAINERS[@]:-}"; do
    docker rm -f "$c" >/dev/null 2>&1 || true
  done

  if [[ -n "${WORKDIR:-}" && "$KEEP" -eq 0 ]]; then
    rm -rf "$WORKDIR" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

while [[ $# -gt 0 ]]; do
  case "$1" in
    --keep)
      KEEP=1
      shift
      ;;
    --workdir)
      [[ $# -ge 2 ]] || die "--workdir requires a path"
      WORKDIR="$2"
      shift 2
      ;;
    --no-pull)
      NO_PULL=1
      shift
      ;;
    --tag)
      [[ $# -ge 2 ]] || die "--tag requires a value"
      TAG="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      die "Unknown argument: $1 (use --help)"
      ;;
  esac
done

require_cmd docker
require_cmd curl
require_cmd jq
require_cmd python

if [[ -z "$WORKDIR" ]]; then
  WORKDIR="$(mktemp -d -t cli2rest-bio-tests.XXXXXX)"
else
  mkdir -p "$WORKDIR"
  WORKDIR="$(cd "$WORKDIR" && pwd)"
fi

echo "Workdir: $WORKDIR" >&2

echo "Installing cli2rest-bio into current Python environment..." >&2
(
  cd "$ROOT_DIR"
  python -m pip install .
)

pull_image() {
  local image="$1"
  if [[ "$NO_PULL" -eq 0 ]]; then
    echo "Pulling: $image" >&2
    docker pull "$image" >/dev/null
  else
    echo "Skipping pull: $image" >&2
  fi
}

start_service() {
  local name="$1"
  local image="$2"

  docker run --name "$name" -d -p 8000 "$image" >/dev/null
  CONTAINERS+=("$name")

  local host_port
  host_port="$(docker port "$name" 8000 | cut -d: -f2)"
  [[ -n "$host_port" ]] || die "Failed to determine mapped port for $name"
  echo "$host_port"
}

wait_healthy() {
  local host_port="$1"

  local deadline=$((SECONDS + 60))
  while (( SECONDS < deadline )); do
    if curl -fs "http://localhost:${host_port}/health" | grep -q '"status":"healthy"'; then
      return 0
    fi
    sleep 1
  done

  echo "Health check failed for http://localhost:${host_port}/health" >&2
  curl -s "http://localhost:${host_port}/health" >&2 || true
  return 1
}

stop_and_rm() {
  local name="$1"
  docker stop "$name" >/dev/null || true
  docker rm "$name" >/dev/null || true
}

assert_completed() {
  local metadata="$1"
  local status
  status="$(jq -r .status "$metadata")"
  if [[ "$status" != "COMPLETED" ]]; then
    echo "Test failed: Job status is not COMPLETED (status=$status)" >&2
    cat "$metadata" >&2
    exit 1
  fi
}

assert_files_exist() {
  local missing=0
  for f in "$@"; do
    if [[ ! -f "$f" ]]; then
      echo "Test failed: Output file $f is missing." >&2
      missing=1
    fi
  done
  if [[ "$missing" -ne 0 ]]; then
    ls -la >&2 || true
    exit 1
  fi
}

download_rcsb() {
  local pdb_id_upper="$1"  # e.g. 1EHZ
  local out="$2"           # e.g. 1ehz.pdb
  curl -L -o "$out" "https://files.rcsb.org/download/${pdb_id_upper}" >/dev/null
}

run_tool_test() {
  local tool="$1"
  local image_tag="$2"
  local func="$3"

  local dir="$WORKDIR/$tool"
  mkdir -p "$dir"

  echo "==> $tool ($image_tag)" >&2
  (
    cd "$dir"
    "$func" "$image_tag"
  )
}

# --- Individual tests (mirrors workflows) ---

test_reduce() {
  local tag="$1"
  local image="ghcr.io/tzok/cli2rest-reduce:${tag}"
  local cname="cli2rest-reduce-manual-${RANDOM}${RANDOM}"

  pull_image "$image"
  local host_port
  host_port="$(start_service "$cname" "$image")"
  wait_healthy "$host_port"

  curl -L -o 1ehz.pdb https://files.rcsb.org/download/1EHZ.pdb >/dev/null

  cli2rest-bio --api-url "http://localhost:${host_port}" --output-metadata metadata.json \
    "$ROOT_DIR/src/cli2rest_bio/configs/reduce/config.yaml" 1ehz.pdb
  assert_completed metadata.json
  assert_files_exist reduce-1ehz-output.pdb

  echo "Test passed: reduce" >&2
  stop_and_rm "$cname"
}

test_maxit() {
  local tag="$1"
  local image="ghcr.io/tzok/cli2rest-maxit:${tag}"
  local cname="cli2rest-maxit-manual-${RANDOM}${RANDOM}"

  pull_image "$image"
  local host_port
  host_port="$(start_service "$cname" "$image")"
  wait_healthy "$host_port"

  curl -L -o 1ehz.pdb https://files.rcsb.org/download/1EHZ.pdb >/dev/null

  cli2rest-bio --api-url "http://localhost:${host_port}" --output-metadata metadata.json \
    "$ROOT_DIR/src/cli2rest_bio/configs/maxit/config-pdb2cif.yaml" 1ehz.pdb
  assert_completed metadata.json
  assert_files_exist maxit-1ehz-output.cif

  echo "Test passed: maxit" >&2
  stop_and_rm "$cname"
}

test_fr3d() {
  local tag="$1"
  local image="ghcr.io/tzok/cli2rest-fr3d:${tag}"
  local cname="cli2rest-fr3d-manual-${tag}-${RANDOM}${RANDOM}"

  pull_image "$image"
  local host_port
  host_port="$(start_service "$cname" "$image")"
  wait_healthy "$host_port"

  curl -L -o 1ehz.cif https://files.rcsb.org/download/1EHZ.cif >/dev/null

  cli2rest-bio --api-url "http://localhost:${host_port}" --output-metadata metadata.json \
    "$ROOT_DIR/src/cli2rest_bio/configs/fr3d/config.yaml" 1ehz.cif
  assert_completed metadata.json
  assert_files_exist \
    fr3d-1ehz-basepair_detail.txt \
    fr3d-1ehz-stacking.txt \
    fr3d-1ehz-backbone.txt

  echo "Test passed: fr3d ($tag)" >&2
  stop_and_rm "$cname"
}

test_inkscape() {
  local tag="$1"
  local image="ghcr.io/tzok/cli2rest-inkscape:${tag}"
  local cname="cli2rest-inkscape-manual-${RANDOM}${RANDOM}"

  pull_image "$image"
  local host_port
  host_port="$(start_service "$cname" "$image")"
  wait_healthy "$host_port"

  printf '%s\n' '<svg height="233" width="526" xmlns="http://www.w3.org/2000/svg"><rect fill="none" height="200" rx="50" ry="100" stroke="#00f" stroke-width="10" width="500" x="13" y="14"/></svg>' > example.svg

  cli2rest-bio --api-url "http://localhost:${host_port}" --output-metadata metadata.json \
    "$ROOT_DIR/src/cli2rest_bio/configs/inkscape/config-svg2png.yaml" example.svg
  assert_completed metadata.json
  assert_files_exist inkscape-example-output.png

  echo "Test passed: inkscape" >&2
  stop_and_rm "$cname"
}

test_mc_annotate() {
  local tag="$1"
  local image="ghcr.io/tzok/cli2rest-mc-annotate:${tag}"
  local cname="cli2rest-mc-annotate-manual-${RANDOM}${RANDOM}"

  pull_image "$image"
  local host_port
  host_port="$(start_service "$cname" "$image")"
  wait_healthy "$host_port"

  curl -L -o 1ehz.pdb https://files.rcsb.org/download/1EHZ.pdb >/dev/null

  cli2rest-bio --api-url "http://localhost:${host_port}" --output-metadata metadata.json \
    "$ROOT_DIR/src/cli2rest_bio/configs/mc-annotate/config.yaml" 1ehz.pdb
  assert_completed metadata.json
  assert_files_exist mc-annotate-1ehz-stdout.txt

  echo "Test passed: mc-annotate" >&2
  stop_and_rm "$cname"
}

test_rchie() {
  local tag="$1"
  local image="ghcr.io/tzok/cli2rest-rchie:${tag}"
  local cname="cli2rest-rchie-manual-${RANDOM}${RANDOM}"

  pull_image "$image"
  local host_port
  host_port="$(start_service "$cname" "$image")"
  wait_healthy "$host_port"

  cat > example.json <<'EOF'
{
  "sequence": "GCAUUGC",
  "top": [
    {"i": 1, "j": 7},
    {"i": 2, "j": 6}
  ],
  "bottom": []
}
EOF

  cli2rest-bio --api-url "http://localhost:${host_port}" --output-metadata metadata.json \
    "$ROOT_DIR/src/cli2rest_bio/configs/rchie/config.yaml" example.json
  assert_completed metadata.json
  assert_files_exist rchie-example-clean.svg

  echo "Test passed: rchie" >&2
  stop_and_rm "$cname"
}

test_rnaview() {
  local tag="$1"
  local image="ghcr.io/tzok/cli2rest-rnaview:${tag}"
  local cname="cli2rest-rnaview-manual-${RANDOM}${RANDOM}"

  pull_image "$image"
  local host_port
  host_port="$(start_service "$cname" "$image")"
  wait_healthy "$host_port"

  curl -L -o 1ehz.pdb https://files.rcsb.org/download/1EHZ.pdb >/dev/null

  cli2rest-bio --api-url "http://localhost:${host_port}" --output-metadata metadata.json \
    "$ROOT_DIR/src/cli2rest_bio/configs/rnaview/config-pdb.yaml" 1ehz.pdb
  assert_completed metadata.json
  assert_files_exist rnaview-1ehz-input.pdb.out

  echo "Test passed: rnaview" >&2
  stop_and_rm "$cname"
}

test_varna_tz() {
  local tag="$1"
  local image="ghcr.io/tzok/cli2rest-varna-tz:${tag}"
  local cname="cli2rest-varna-tz-manual-${RANDOM}${RANDOM}"

  pull_image "$image"
  local host_port
  host_port="$(start_service "$cname" "$image")"
  wait_healthy "$host_port"

  cat > example.json <<'EOF'
{
  "drawingAlgorithm": "NAVIEW",
  "nucleotides": [
    { "id": 1, "number": 1, "char": "C", "outlineColor": "red" },
    { "id": 2, "number": 2, "char": "A", "innerColor": "red" },
    { "id": 3, "number": 10, "char": "G" },
    { "id": 4, "number": 11, "char": "A", "nameColor": "red" },
    { "id": 5, "number": 12, "char": "A" },
    { "id": 6, "number": 13, "char": "A" },
    { "id": 7, "number": 14, "char": "U" },
    { "id": 8, "number": 15, "char": "G" }
  ],
  "basePairs": [
    { "id1": 1, "id2": 8, "stericity": "CIS", "edge5": "WC", "edge3": "WC", "canonical": true, "color": "red" },
    { "id1": 2, "id2": 7, "stericity": "CIS", "edge5": "WC", "edge3": "WC", "canonical": true, "color": "#FF00FF", "thickness": 40.0 },
    { "id1": 3, "id2": 6, "stericity": "TRANS", "edge5": "WC", "edge3": "SUGAR", "canonical": false, "color": "green", "thickness": 2.0 }
  ],
  "stackings": [
    { "id1": 1, "id2": 7 }
  ]
}
EOF

  cli2rest-bio --api-url "http://localhost:${host_port}" --output-metadata metadata.json \
    "$ROOT_DIR/src/cli2rest_bio/configs/varna-tz/config.yaml" example.json
  assert_completed metadata.json
  assert_files_exist varna-tz-example-clean.svg

  echo "Test passed: varna-tz" >&2
  stop_and_rm "$cname"
}

test_bpnet() {
  local tag="$1"
  local image="ghcr.io/tzok/cli2rest-bpnet:${tag}"
  local cname="cli2rest-bpnet-manual-${RANDOM}${RANDOM}"

  pull_image "$image"
  local host_port
  host_port="$(start_service "$cname" "$image")"
  wait_healthy "$host_port"

  curl -L -o 1ehz.pdb https://files.rcsb.org/download/1EHZ.pdb >/dev/null

  cli2rest-bio --api-url "http://localhost:${host_port}" --output-metadata metadata.json \
    "$ROOT_DIR/src/cli2rest_bio/configs/bpnet/config-pdb.yaml" 1ehz.pdb
  assert_completed metadata.json
  assert_files_exist bpnet-1ehz-input.rob

  echo "Test passed: bpnet" >&2
  stop_and_rm "$cname"
}

test_barnaba() {
  local tag="$1"
  local image="ghcr.io/tzok/cli2rest-barnaba:${tag}"
  local cname="cli2rest-barnaba-manual-${RANDOM}${RANDOM}"

  pull_image "$image"
  local host_port
  host_port="$(start_service "$cname" "$image")"
  wait_healthy "$host_port"

  curl -L -o 1ehz.pdb https://files.rcsb.org/download/1EHZ.pdb >/dev/null

  cli2rest-bio --api-url "http://localhost:${host_port}" --output-metadata metadata.json \
    "$ROOT_DIR/src/cli2rest_bio/configs/barnaba/config.yaml" 1ehz.pdb
  assert_completed metadata.json
  assert_files_exist \
    barnaba-1ehz-outfile.ANNOTATE.pairing.out \
    barnaba-1ehz-outfile.ANNOTATE.stacking.out

  echo "Test passed: barnaba" >&2
  stop_and_rm "$cname"
}

test_rnapolis() {
  local tag="$1"
  local image="ghcr.io/tzok/cli2rest-rnapolis:${tag}"
  local cname="cli2rest-rnapolis-manual-${RANDOM}${RANDOM}"

  pull_image "$image"
  local host_port
  host_port="$(start_service "$cname" "$image")"
  wait_healthy "$host_port"

  # Verify coplanarity-checker-wrapper.py via cli2rest-bio
  docker cp "$cname:/usr/local/share/rnapolis/base-triple.cif" base-triple.cif

  cli2rest-bio --api-url "http://localhost:${host_port}" --output-metadata metadata.json \
    "$ROOT_DIR/src/cli2rest_bio/configs/rnapolis/config-coplanarity-checker.yaml" base-triple.cif
  assert_completed metadata.json
  assert_files_exist rnapolis-output.json

  if ! jq -e '."base-triple.cif" == true' rnapolis-output.json >/dev/null; then
    echo "Test failed: Coplanarity result for base-triple.cif is not true" >&2
    cat rnapolis-output.json >&2
    exit 1
  fi

  curl -L -o 1ehz.pdb https://files.rcsb.org/download/1EHZ.pdb >/dev/null

  cli2rest-bio --api-url "http://localhost:${host_port}" --output-metadata metadata.json \
    "$ROOT_DIR/src/cli2rest_bio/configs/rnapolis/config-splitter.yaml" 1ehz.pdb
  assert_completed metadata.json
  assert_files_exist rnapolis-1ehz-output.tar.gz

  cli2rest-bio --api-url "http://localhost:${host_port}" --output-metadata metadata.json \
    "$ROOT_DIR/src/cli2rest_bio/configs/rnapolis/config-annotator.yaml" 1ehz.pdb
  assert_completed metadata.json
  assert_files_exist rnapolis-1ehz-output.json

  echo "Test passed: rnapolis" >&2
  stop_and_rm "$cname"
}

# --- Run suite ---

run_tool_test "reduce" "$TAG" test_reduce
run_tool_test "maxit" "$TAG" test_maxit

# fr3d workflow tests both branches; mirror that unless user pinned a tag.
if [[ "$TAG" == "latest" ]]; then
  run_tool_test "fr3d-latest" "latest" test_fr3d
  run_tool_test "fr3d-master" "master" test_fr3d
else
  run_tool_test "fr3d" "$TAG" test_fr3d
fi

run_tool_test "inkscape" "$TAG" test_inkscape
run_tool_test "mc-annotate" "$TAG" test_mc_annotate
run_tool_test "rchie" "$TAG" test_rchie
run_tool_test "rnaview" "$TAG" test_rnaview
run_tool_test "varna-tz" "$TAG" test_varna_tz
run_tool_test "bpnet" "$TAG" test_bpnet
run_tool_test "barnaba" "$TAG" test_barnaba
run_tool_test "rnapolis" "$TAG" test_rnapolis

echo "All tests passed." >&2
if [[ "$KEEP" -eq 1 ]]; then
  echo "Kept workdir: $WORKDIR" >&2
fi
