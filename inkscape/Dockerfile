# Start from the specified base image
FROM ghcr.io/tzok/cli2rest:latest

# Install inkscape
RUN apt-get update -y \
 && apt-get install -y \
      inkscape \
 && rm -rf /var/lib/apt/lists/*

# Make sure the installed binary is in the PATH
ENV PATH="/usr/bin:${PATH}"
