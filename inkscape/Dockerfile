# Start from the specified base image
FROM ghcr.io/tzok/cli2rest:latest

# Install inkscape
RUN apt-get update -y \
 && apt-get install -y --no-install-recommends \
      ghostscript \
      inkscape \
 && rm -rf /var/lib/apt/lists/*
