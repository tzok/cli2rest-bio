#!/usr/bin/env python3

import os
import argparse
import glob
from fr3d.classifiers.NA_pairwise_interactions import generatePairwiseAnnotation


def process_cif(cif_path):
    # Get the directory containing the input file
    input_dir = os.path.dirname(cif_path) or '.'
    base_name = os.path.basename(cif_path).split(".")[0]

    # Run FR3D analysis - using input_dir for both input and output
    generatePairwiseAnnotation(
        base_name,
        None,
        input_dir,
        input_dir,
        "basepair_detail,stacking,backbone",
        "txt",
    )
    
    # Rename output files to remove the base_name prefix
    for output_file in glob.glob(os.path.join(input_dir, f"{base_name}_*.txt")):
        new_name = output_file.replace(f"{base_name}_", "")
        os.rename(output_file, new_name)
        print(f"Created: {os.path.basename(new_name)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process CIF file with FR3D")
    parser.add_argument("cif_file", help="Path to the CIF file to process")
    args = parser.parse_args()

    # Process the CIF file
    process_cif(args.cif_file)
