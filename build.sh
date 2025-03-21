#!/bin/bash

# Exit on error
set -e

echo "Building CLI2REST container images..."

# Find all directories with a Dockerfile
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
    docker build -t "cli2rest-$dir" .
  )
  
  echo "Successfully built cli2rest-$dir image"
  echo "----------------------------------------"
done

echo "All images built successfully!"
echo ""
echo "You can run the containers with:"
echo "docker run -p 8000:8000 cli2rest-reduce"
echo "docker run -p 8001:8000 cli2rest-maxit"
