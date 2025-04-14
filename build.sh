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

	# Build arguments (specific to certain images)
	build_args=""

	# Special handling for 'reduce' to get the latest tag
	if [ "$dir" == "reduce" ]; then
		echo "Fetching latest Reduce tag..."
		# Fetch tags, sort by version, get the last one, extract the tag name, remove ^{} if present
		REDUCE_VERSION=$(git ls-remote --tags --sort="v:refname" https://github.com/rlabduke/reduce.git | tail -n1 | sed 's/.*\///; s/\^{}//')
		if [ -z "$REDUCE_VERSION" ]; then
			echo "Error: Could not fetch Reduce version tag."
			exit 1
		fi
		echo "Using Reduce version: $REDUCE_VERSION"
		build_args="--build-arg REDUCE_VERSION=$REDUCE_VERSION"
	fi

	# Enter directory and build the image
	(
		cd "$dir"
		# Pass build arguments if any were set
		docker build $build_args -t "ghcr.io/tzok/cli2rest-$dir" .
	)
	images=(${images[@]} "ghcr.io/tzok/cli2rest-$dir")

	echo "Successfully built cli2rest-$dir image"
	echo "----------------------------------------"
done

echo "All images built successfully!"
echo "Available images: ${images[@]}"
