#!/usr/bin/env bash

# Exit on error
set -e

echo "Pulling latest base image..."
docker pull ghcr.io/tzok/cli2rest:latest
# barnaba pins the Python 3.13 base (barnaba needs NumPy 1.x) rather than :latest
docker pull ghcr.io/tzok/cli2rest:py3.13

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
	elif [ "$dir" == "rnaview" ]; then
		echo "Fetching latest RNAView tag..."
		# Fetch tags, sort by version, get the last one, extract the tag name, remove ^{} if present
		RNAVIEW_VERSION=$(git ls-remote --tags --sort="v:refname" https://github.com/rcsb/RNAView.git | tail -n1 | sed 's/.*\///; s/\^{}//')
		if [ -z "$RNAVIEW_VERSION" ]; then
			echo "Error: Could not fetch RNAView version tag."
			exit 1
		fi
		echo "Using RNAView version: $RNAVIEW_VERSION"
		build_args="--build-arg RNAVIEW_VERSION=$RNAVIEW_VERSION"
	elif [ "$dir" == "rnapuzzler" ]; then
		echo "Fetching latest ViennaRNA version..."
		VIENNARNA_VERSION=$(curl -fsSL --retry 3 https://www.tbi.univie.ac.at/RNA/install.html \
			| grep -oE '/RNA/download/debian/debian_13/viennarna_[[:alnum:].+~:_-]+_amd64[.]deb' \
			| sed -E 's#.*/viennarna_([[:alnum:].+~:_-]+)_amd64[.]deb#\1#' \
			| sort -V \
			| tail -n1)
		if [ -z "$VIENNARNA_VERSION" ]; then
			echo "Error: Could not determine the latest ViennaRNA version."
			exit 1
		fi
		echo "Using ViennaRNA version: $VIENNARNA_VERSION"
		build_args="--build-arg VIENNARNA_VERSION=$VIENNARNA_VERSION"
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
