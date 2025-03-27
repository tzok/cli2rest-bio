#!/usr/bin/env python3

import json
import sys
import tempfile
import shutil
import os
import argparse
from fr3d.classifiers.NA_pairwise_interactions import generatePairwiseAnnotation


def parse_fr3d_output(file_path):
    """
    Parse FR3D output file with tab-separated values into a structured format.

    Each line contains: first unit id, classification, second unit id, number of overlapping pairs
    """
    data = []
    with open(file_path, "rt") as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and comments
            if not line or line.startswith("#"):
                continue

            # Split by tabs
            parts = line.split("\t")
            if len(parts) >= 4:  # Ensure we have at least 4 columns
                entry = {
                    "unit_id_1": parts[0],
                    "classification": parts[1],
                    "unit_id_2": parts[2],
                    "overlapping_pairs": int(parts[3])
                    if parts[3].isdigit()
                    else parts[3],
                }
                # Add any additional columns if present
                for i, value in enumerate(parts[4:], 4):
                    entry[f"column_{i}"] = value

                data.append(entry)

    return data


def process_cif(cif_path):
    # Get the directory containing the input file
    input_dir = os.path.dirname(cif_path)
    base_name = os.path.basename(cif_path).split(".")[0]

    # Create a temporary directory for output
    tmpdir = tempfile.mkdtemp()

    try:
        # Redirect stdout/stderr to devnull to silence output
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        sys.stdout = open(os.devnull, "w")
        sys.stderr = open(os.devnull, "w")

        try:
            # Run FR3D analysis silently
            generatePairwiseAnnotation(
                base_name,
                None,
                input_dir,
                tmpdir,
                "basepair_detail,stacking,backbone",
                "txt",
            )
        finally:
            # Restore stdout/stderr
            sys.stdout.close()
            sys.stderr.close()
            sys.stdout = original_stdout
            sys.stderr = original_stderr

        # Parse the results
        results = {}

        # Parse basepair details
        basepair_file = os.path.join(tmpdir, f"{base_name}_basepair_detail.txt")
        results["basepair"] = parse_fr3d_output(basepair_file)

        # Parse stacking interactions
        stacking_file = os.path.join(tmpdir, f"{base_name}_stacking.txt")
        results["stacking"] = parse_fr3d_output(stacking_file)

        # Parse backbone conformations
        backbone_file = os.path.join(tmpdir, f"{base_name}_backbone.txt")
        results["backbone"] = parse_fr3d_output(backbone_file)

        return results

    finally:
        # Clean up
        shutil.rmtree(tmpdir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process CIF file with FR3D")
    parser.add_argument("cif_file", help="Path to the CIF file to process")
    args = parser.parse_args()

    # Process the CIF file
    results = process_cif(args.cif_file)

    # Output the results as JSON (compact format)
    print(json.dumps(results))
