#!/usr/bin/env python3

import json
import sys
import tempfile
import shutil
import os
import argparse
from fr3d.classifiers.NA_pairwise_interactions import generatePairwiseAnnotation


def process_cif(cif_path):
    # Get the directory containing the input file
    input_dir = os.path.dirname(cif_path)
    base_name = os.path.basename(cif_path).split('.')[0]
    
    # Create a temporary directory for output
    tmpdir = tempfile.mkdtemp()

    try:
        # Run FR3D analysis
        generatePairwiseAnnotation(
            base_name, None, input_dir, tmpdir, "basepair_detail,stacking,backbone", "txt"
        )

        # Read the results
        results = {}

        with open(os.path.join(tmpdir, f"{base_name}_basepair_detail.txt"), "rt") as f:
            results["basepair"] = f.read()

        with open(os.path.join(tmpdir, f"{base_name}_stacking.txt"), "rt") as f:
            results["stacking"] = f.read()

        with open(os.path.join(tmpdir, f"{base_name}_backbone.txt"), "rt") as f:
            results["backbone"] = f.read()

        return results

    finally:
        # Clean up
        shutil.rmtree(tmpdir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process CIF file with FR3D')
    parser.add_argument('cif_file', help='Path to the CIF file to process')
    args = parser.parse_args()
    
    # Process the CIF file
    results = process_cif(args.cif_file)

    # Output the results as JSON
    print(json.dumps(results, indent=2))
