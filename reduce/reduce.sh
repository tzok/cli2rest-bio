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
# Start the container in the background
docker run -d --name "$CONTAINER_NAME" -p 8000:8000 ghcr.io/tzok/cli2rest-reduce:latest

# Wait for the container to be ready
echo "Waiting for service to be ready..."
until $(curl --output /dev/null --silent --head --fail http://localhost:8000/health); do
  printf '.'
  sleep 1
done
echo " Ready!"

echo "Processing PDB file: $INPUT_FILE"
# Use jq to create the JSON payload and send it to the API
RESPONSE=$(jq -n --arg pdb "$(cat "$INPUT_FILE")" '{
  cli_tool: "reduce",
  arguments: ["input.pdb"],
  files: [
    {
      relative_path: "input.pdb",
      content: $pdb
    }
  ]
}' | curl -s -X POST http://localhost:8000/run-command \
     -H "Content-Type: application/json" \
     -d @-)

# Extract and display only stdout from the response
echo "Results:"
echo "$RESPONSE" | jq -r '.stdout'

# Clean up - stop and remove the container
echo "Cleaning up..."
docker stop "$CONTAINER_NAME" > /dev/null
docker rm "$CONTAINER_NAME" > /dev/null

echo "Done!"
