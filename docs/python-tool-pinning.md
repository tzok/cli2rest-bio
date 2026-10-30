# Python Tool Pinning

The repository root, plus `rnapolis`, `barnaba`, and `fr3d`, use `uv` projects and lockfiles.

## Root CLI project

- Manifest: `pyproject.toml`
- Lockfile: `uv.lock`
- Source: PyPI
- Update mode: automatic via Dependabot `uv` updates

Refresh the root lockfile after dependency changes with:

```bash
uv lock
```

Sync the local development environment with:

```bash
uv sync --locked
```

Run the CLI from the locked project environment with:

```bash
uv run --locked cli2rest-bio --help
```

## Update model

### RNAPOLIS

- Manifest: `rnapolis/pyproject.toml`
- Lockfile: `rnapolis/uv.lock`
- Source: PyPI
- Update mode: automatic via Dependabot `uv` updates

`rnapolis` is intentionally pinned to a released PyPI version instead of a Git SHA.

### Barnaba

- Manifest: `barnaba/pyproject.toml`
- Lockfile: `barnaba/uv.lock`
- Source: `https://github.com/srnas/barnaba`
- Update mode: manual Git SHA pinning

### FR3D

- Manifest: `fr3d/pyproject.toml`
- Lockfile: `fr3d/uv.lock`
- Source: `https://github.com/BGSU-RNA/fr3d-python`
- Update mode: manual Git SHA pinning

Upstream collapsed its `latest` and `master` branches into a single `main`
branch (the old branches survive only as archive tags). The image is therefore
built from one pinned commit, published as `:latest`.

## Manual SHA pinning

Dependabot is configured to monitor the `uv` projects, but it is not relied on to bump Git SHAs.
Git-based dependency pins for `barnaba` and `fr3d` must be updated manually.

Image rebuild identity includes the tool lockfile checksum, so dependency-only `uv.lock` changes also produce new image tags in CI.

### Barnaba update procedure

1. Choose the target upstream commit in `srnas/barnaba`.
2. Update `tool.uv.sources.barnaba.rev` in `barnaba/pyproject.toml`.
3. Refresh the lockfile:

```bash
uv lock --directory barnaba
```

4. Rebuild and test the image.

### FR3D update procedure

1. Choose the target upstream commit on `BGSU-RNA/fr3d-python`'s `main` branch.
2. Update `tool.uv.sources.fr3d.rev` in `fr3d/pyproject.toml`.
3. Refresh the lockfile:

```bash
uv lock --directory fr3d
```

4. Rebuild and test the image.

## Local validation

Useful commands after changing a pin:

```bash
docker build -t cli2rest-rnapolis ./rnapolis
docker build -t cli2rest-barnaba ./barnaba
docker build -t cli2rest-fr3d ./fr3d
```

Then run the existing integration workflows or local CLI checks against the built image.
