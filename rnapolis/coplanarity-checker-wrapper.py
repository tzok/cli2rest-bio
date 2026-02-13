#!/usr/bin/env python3
import glob
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed

from rnapolis.geometry import are_bases_coplanar
from rnapolis.parser_v2 import parse_cif_atoms
from rnapolis.tertiary_v2 import Structure


def check_coplanarity(mmcif_path: str) -> tuple[str, bool]:
    """Check coplanarity of nucleobases in a single mmCIF file."""
    filename = os.path.basename(mmcif_path)
    try:
        with open(mmcif_path, "r", encoding="utf-8") as handle:
            atoms_df = parse_cif_atoms(handle)
        structure = Structure(atoms_df)
        nucleotide_residues = [r for r in structure.residues if r.is_nucleotide]
        result = are_bases_coplanar(nucleotide_residues)
        return filename, bool(result)
    except Exception as exc:
        print(f"Error processing {filename}: {exc}", file=sys.stderr)
        return filename, False


def main() -> int:
    """Discover all .cif files in the working directory, check coplanarity in parallel."""
    cif_files = sorted(glob.glob("*.cif"))

    if not cif_files:
        print("Error: No .cif files found in working directory.", file=sys.stderr)
        with open("output.json", "w", encoding="utf-8") as f:
            json.dump({}, f)
        return 1

    results: dict[str, bool] = {}

    with ProcessPoolExecutor() as executor:
        futures = {
            executor.submit(check_coplanarity, path): path for path in cif_files
        }
        for future in as_completed(futures):
            filename, is_coplanar = future.result()
            results[filename] = is_coplanar

    # Sort by filename for deterministic output
    sorted_results = dict(sorted(results.items()))

    with open("output.json", "w", encoding="utf-8") as f:
        json.dump(sorted_results, f, indent=2)

    print(
        f"Processed {len(sorted_results)} file(s). Results in output.json",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
