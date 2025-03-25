#!/bin/bash

# Exit on error
set -e

# Check if a PDB file was provided
if [ $# -lt 1 ]; then
	echo "Usage: $0 <pdb_file>"
	echo "Example: $0 protein.pdb"
	exit 1
fi

# Get the absolute path of the input file
INPUT_FILE=$(realpath "$1")

if [ ! -f "$INPUT_FILE" ]; then
	echo "Error: File '$1' not found"
	exit 1
fi

# Generate a unique container name
CONTAINER_NAME="reduce-$(date +%s)"

echo "Starting Reduce container..."
# Start the container in the background with a random port
docker run -d --name "$CONTAINER_NAME" -P ghcr.io/tzok/cli2rest-reduce:latest

# Get the port that Docker assigned
PORT=$(docker port "$CONTAINER_NAME" 8000/tcp | cut -d ':' -f 2)
echo "Container running on port: $PORT"

# Wait for the container to be ready
echo "Waiting for service to be ready..."
until $(curl --output /dev/null --silent --head --fail http://localhost:$PORT/health); do
  printf '.'
  sleep 1
done
echo " Ready!"

echo "Processing PDB file: $INPUT_FILE"
# Create a temporary file for the JSON payload
TEMP_JSON=$(mktemp)

# Create the JSON payload using a different approach to handle large files
cat > "$TEMP_JSON" << EOF
{
  "cli_tool": "reduce",
  "arguments": ["input.pdb"],
  "files": [
    {
      "relative_path": "input.pdb",
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

# Extract and display only stdout from the response
echo "Results:"
echo "$RESPONSE" | jq -r '.stdout'

# Clean up - stop and remove the container
echo "Cleaning up..."
docker stop "$CONTAINER_NAME" >/dev/null
docker rm "$CONTAINER_NAME" >/dev/null

echo "Done!"
