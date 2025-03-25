#!/bin/bash

# Exit on error
set -e

# Check if a directory or file was provided
if [ $# -lt 1 ]; then
	echo "Usage: $0 <directory_or_cif_file>" >&2
	echo "Examples:" >&2
	echo "  $0 your_rna.cif" >&2
	echo "  $0 /path/to/cif/files/" >&2
	exit 1
fi

# Get the absolute path of the input
INPUT_PATH=$(realpath "$1")

# Check if input is a file or directory
if [ -f "$INPUT_PATH" ]; then
	# Single file mode
	if [[ "$INPUT_PATH" != *.cif ]]; then
		echo "Error: Input file must have .cif extension" >&2
		exit 1
	fi
	INPUT_FILES=("$INPUT_PATH")
elif [ -d "$INPUT_PATH" ]; then
	# Directory mode - find all .cif files (including symbolic links)
	INPUT_FILES=($(find "$INPUT_PATH" -name "*.cif"))
	if [ ${#INPUT_FILES[@]} -eq 0 ]; then
		echo "Error: No .cif files found in directory '$1'" >&2
		exit 1
	fi
	echo "Found ${#INPUT_FILES[@]} .cif files to process" >&2
else
	echo "Error: '$1' is not a valid file or directory" >&2
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

# Define a function to process a single file
process_file() {
	local INPUT_FILE="$1"
	local PORT="$2"
	
	echo "Processing CIF file: $INPUT_FILE" >&2
	echo "Converting CIF to PDB format" >&2
	
	# Get the base filename without extension
	FILENAME=$(basename "$INPUT_FILE" .cif)
	OUTPUT_FILE="${INPUT_FILE%.*}.pdb"
	
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
	
	# Extract the output and save to file
	echo "$RESPONSE" | jq -r '.stdout' > "$OUTPUT_FILE"
	echo "Saved output to: $OUTPUT_FILE" >&2
}

# Export the function so GNU parallel can use it
export -f process_file

# Process files in parallel
echo "Processing ${#INPUT_FILES[@]} files in parallel..." >&2
parallel -j $(nproc) process_file {} $PORT ::: "${INPUT_FILES[@]}"

# Clean up - stop and remove the container
echo "Cleaning up..." >&2
docker stop "$CONTAINER_NAME" >/dev/null
docker rm "$CONTAINER_NAME" >/dev/null

echo "Done!" >&2
