#!/bin/bash

# Wrapper script to run both bpnet.linux and metbp.linux on the input file
# Usage: wrapper.sh input.cif|input.pdb

set -e

INPUT_FILE="$1"

if [ -z "$INPUT_FILE" ]; then
	echo "Usage: $0 <input.cif|input.pdb>" >&2
	exit 1
fi

if [ ! -f "$INPUT_FILE" ]; then
	echo "Error: Input file '$INPUT_FILE' not found" >&2
	exit 1
fi

# Extract base name without extension for output files
# Handle both .cif and .pdb extensions
if [[ "$INPUT_FILE" == *.cif ]]; then
	BASE_NAME=$(basename "$INPUT_FILE" .cif)
elif [[ "$INPUT_FILE" == *.pdb ]]; then
	BASE_NAME=$(basename "$INPUT_FILE" .pdb)
else
	# Fallback: remove any extension
	BASE_NAME=$(basename "$INPUT_FILE" | sed 's/\.[^.]*$//')
fi

echo "Running BPNet on $INPUT_FILE..." >&2
bpnet.linux "$INPUT_FILE"

echo "Running MetBP on $INPUT_FILE..." >&2
metbp.linux "$INPUT_FILE" -mode=dev

# Rename the MetBP basepair JSON file to match expected output name
if [ -f "${BASE_NAME}_basepair.json" ]; then
	mv "${BASE_NAME}_basepair.json" "input_basepair.json"
fi

# Check if .rob file was created by BPNet (it should be created automatically)
if [ ! -f "${BASE_NAME}.rob" ]; then
	echo "Warning: Expected .rob file not found" >&2
else
	# Rename .rob file to match expected output name
	mv "${BASE_NAME}.rob" "input.rob"
fi

echo "Analysis complete. Output files:" >&2
echo "  input_basepair.json (from MetBP)" >&2
echo "  input.rob (from BPNet)" >&2
