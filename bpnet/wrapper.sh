#!/bin/bash

# Wrapper script to run both bpnet.linux and metbp.linux on the input file
# Usage: wrapper.sh input.cif

set -e

INPUT_FILE="$1"

if [ -z "$INPUT_FILE" ]; then
	echo "Usage: $0 <input.cif>" >&2
	exit 1
fi

if [ ! -f "$INPUT_FILE" ]; then
	echo "Error: Input file '$INPUT_FILE' not found" >&2
	exit 1
fi

# Extract base name without extension for output files
BASE_NAME=$(basename "$INPUT_FILE" .cif)

echo "Running BPNet on $INPUT_FILE..." >&2
bpnet.linux "$INPUT_FILE"

echo "Running MetBP on $INPUT_FILE..." >&2
metbp.linux "$INPUT_FILE" -mode=dev

# Check if .rob file was created by BPNet (it should be created automatically)
if [ ! -f "${BASE_NAME}.rob" ]; then
	echo "Warning: Expected .rob file not found" >&2
fi

echo "Analysis complete. Output files:" >&2
echo "  ${BASE_NAME}_basepair.json (from MetBP)" >&2
echo "  ${BASE_NAME}.rob (from BPNet)" >&2
