#!/bin/bash

# Exit on error
set -e

# Check if a PDB file was provided
if [ $# -lt 1 ]; then
  echo "Usage: $0 <pdb_file> [output_format]"
  echo "Example: $0 protein.pdb cif"
  echo "Supported output formats: cif (default), pdb"
  exit 1
fi

# Get the absolute path of the input file
INPUT_FILE=$(realpath "$1")

if [ ! -f "$INPUT_FILE" ]; then
  echo "Error: File '$1' not found"
  exit 1
fi

# Determine output format (default to cif)
OUTPUT_FORMAT="cif"
if [ $# -ge 2 ]; then
  OUTPUT_FORMAT="$2"
fi

# Set up arguments based on output format
if [ "$OUTPUT_FORMAT" == "cif" ]; then
  MAXIT_ARGS="-input input.pdb -output output.cif -o"
  OUTPUT_FILE="output.cif"
elif [ "$OUTPUT_FORMAT" == "pdb" ]; then
  MAXIT_ARGS="-input input.pdb -output output.pdb -i"
  OUTPUT_FILE="output.pdb"
else
  echo "Error: Unsupported output format '$OUTPUT_FORMAT'"
  echo "Supported formats: cif, pdb"
  exit 1
fi

# Generate a unique container name
CONTAINER_NAME="maxit-$(date +%s)"

echo "Starting MAXIT container..."
# Start the container in the background
docker run -d --name "$CONTAINER_NAME" -p 8000:8000 ghcr.io/tzok/cli2rest-maxit:latest

# Wait for the container to be ready
echo "Waiting for service to be ready..."
until $(curl --output /dev/null --silent --head --fail http://localhost:8000/health); do
  printf '.'
  sleep 1
done
echo " Ready!"

echo "Processing file: $INPUT_FILE"
echo "Converting to $OUTPUT_FORMAT format"

# Create a temporary file for the JSON payload
TEMP_JSON=$(mktemp)

# Create the JSON payload using a different approach to handle large files
cat > "$TEMP_JSON" << EOF
{
  "cli_tool": "maxit",
  "arguments": ${MAXIT_ARGS//,/ },
  "files": [
    {
      "relative_path": "input.pdb",
      "content": "$(cat "$INPUT_FILE" | sed 's/"/\\"/g' | sed ':a;N;$!ba;s/\n/\\n/g')"
    }
  ]
}
EOF

# Send the request using the temporary file
RESPONSE=$(curl -s -X POST http://localhost:8000/run-command \
  -H "Content-Type: application/json" \
  -d @"$TEMP_JSON")

# Remove the temporary file
rm "$TEMP_JSON"

# Extract and display the output file content
echo "Results:"
echo "$RESPONSE" | jq -r ".files[] | select(.relative_path == \"$OUTPUT_FILE\") | .content"

# Clean up - stop and remove the container
echo "Cleaning up..."
docker stop "$CONTAINER_NAME" >/dev/null
docker rm "$CONTAINER_NAME" >/dev/null

echo "Done!"
