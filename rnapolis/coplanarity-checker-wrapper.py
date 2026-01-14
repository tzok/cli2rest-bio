#!/usr/bin/env python3
import argparse
import os
import sys

# Attempt to import required RNAPOLIS pieces
try:
    from rnapolis.geometry import are_bases_coplanar
    from rnapolis.parser_v2 import parse_cif_atoms
    from rnapolis.tertiary_v2 import Structure
except ImportError as exc:
    print("False", file=sys.stdout)
    print(f"Error: Could not import required RNAPOLIS modules: {exc}", file=sys.stderr)
    sys.exit(1)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check coplanarity of nucleobases in an mmCIF file."
    )
    parser.add_argument("mmcif_path", help="Path to the input mmCIF (*.cif) file")
    args = parser.parse_args()

    if not os.path.isfile(args.mmcif_path):
        print("False")
        print(f"Error: Input file '{args.mmcif_path}' not found.", file=sys.stderr)
        return 1

    try:
        with open(args.mmcif_path, "r", encoding="utf-8") as handle:
            atoms_df = parse_cif_atoms(handle)

        structure = Structure(atoms_df)
        nucleotide_residues = [r for r in structure.residues if r.is_nucleotide]

        result = are_bases_coplanar(nucleotide_residues)
        print(result)
        return 0
    except Exception as exc:
        print("False")
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

