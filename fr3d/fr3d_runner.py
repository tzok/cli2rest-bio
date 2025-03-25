#!/usr/bin/env python3

import json
import sys
import tempfile
import shutil
import os
from fr3d.classifiers.NA_pairwise_interactions import generatePairwiseAnnotation

def process_cif(cif_content):
    # Create a temporary directory
    tmpdir = tempfile.mkdtemp()
    
    try:
        # Write the CIF content to a file
        cif_path = os.path.join(tmpdir, "fr3d.cif")
        with open(cif_path, "wb") as f:
            f.write(cif_content)
        
        # Run FR3D analysis
        generatePairwiseAnnotation("fr3d", None, tmpdir, tmpdir, "basepair_detail,stacking,backbone", "txt")
        
        # Read the results
        results = {}
        
        with open(os.path.join(tmpdir, "fr3d_basepair_detail.txt"), "rt") as f:
            results["basepair"] = f.read()
        
        with open(os.path.join(tmpdir, "fr3d_stacking.txt"), "rt") as f:
            results["stacking"] = f.read()
        
        with open(os.path.join(tmpdir, "fr3d_backbone.txt"), "rt") as f:
            results["backbone"] = f.read()
        
        return results
    
    finally:
        # Clean up
        shutil.rmtree(tmpdir)

if __name__ == "__main__":
    # Read CIF content from stdin
    cif_content = sys.stdin.buffer.read()
    
    # Process the CIF file
    results = process_cif(cif_content)
    
    # Output the results as JSON
    print(json.dumps(results, indent=2))
