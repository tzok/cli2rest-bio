#!/bin/bash

# Exit on error
set -e

# Check if a CIF file was provided
if [ $# -lt 1 ]; then
	echo "Usage: $0 <cif_file>" >&2
	echo "Example: $0 your_rna.cif" >&2
	exit 1
fi

# Get the absolute path of the input file
INPUT_FILE=$(realpath "$1")

if [ ! -f "$INPUT_FILE" ]; then
	echo "Error: File '$1' not found" >&2
	exit 1
fi

# Generate a unique container name
CONTAINER_NAME="maxit-$(date +%s)"

echo "Starting MAXIT container..." >&2
# Start the container in the background with a random port
docker run -d --name "$CONTAINER_NAME" -P ghcr.io/tzok/cli2rest-maxit:latest >&2

# Get the port that Docker assigned
PORT=$(docker port "$CONTAINER_NAME" 8000/tcp | cut -d ':' -f 2)
echo "Container running on port: $PORT" >&2

# Wait for the container to be ready
echo "Waiting for service to be ready..." >&2
until $(curl --output /dev/null --silent --fail http://localhost:$PORT/health); do
	printf '.' >&2
	sleep 1
done
echo " Ready!" >&2

echo "Processing CIF file: $INPUT_FILE" >&2
echo "Converting CIF to PDB format" >&2

# Create a temporary file for the JSON payload
TEMP_JSON=$(mktemp)

# Create the JSON payload using a different approach to handle large files
cat >"$TEMP_JSON" <<EOF
{
  "cli_tool": "maxit",
  "arguments": ["-input", "input.cif", "-output", "/dev/stdout", "-o", "2"],
  "files": [
    {
      "relative_path": "input.cif",
      "content": "$(cat "$INPUT_FILE" | sed 's/"/\\"/g' | sed ':a;N;$!ba;s/\n/\\n/g')"
    }
  ]
}
EOF

# Send the request using the temporary file
RESPONSE=$(curl -s -X POST http://localhost:$PORT/run-command \
	-H "Content-Type: application/json" \
	-d @"$TEMP_JSON")

# Remove the temporary file
rm "$TEMP_JSON"

# Extract and display the output file content
echo "$RESPONSE" | jq -r '.stdout'

# Clean up - stop and remove the container
echo "Cleaning up..." >&2
docker stop "$CONTAINER_NAME" >/dev/null
docker rm "$CONTAINER_NAME" >/dev/null

echo "Done!" >&2
