#!/bin/bash

# Exit on error
set -e

echo "Pulling latest base image..."
docker pull ghcr.io/tzok/cli2rest:latest

echo "Building CLI2REST container images..."

# Find all directories with a Dockerfile
images=()
for dir in */; do
	# Remove trailing slash
	dir=${dir%/}

	# Skip if not a directory or doesn't contain a Dockerfile
	if [ ! -d "$dir" ] || [ ! -f "$dir/Dockerfile" ]; then
		continue
	fi

	echo "Building cli2rest-$dir image..."

	# Enter directory and build the image
	(
		cd "$dir"
		docker build -t "ghcr.io/tzok/cli2rest-$dir" .
	)
	images=(${images[@]} "ghcr.io/tzok/cli2rest-$dir")

	echo "Successfully built cli2rest-$dir image"
	echo "----------------------------------------"
done

echo "All images built successfully!"
echo "Available images: ${images[@]}"
