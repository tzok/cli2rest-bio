ARG CLI2REST_BASE=ghcr.io/tzok/cli2rest:latest

# Start from the specified base image
FROM ${CLI2REST_BASE}

# Install inkscape
RUN apt-get update -y \
 && apt-get install -y --no-install-recommends \
      ghostscript \
      inkscape \
 && rm -rf /var/lib/apt/lists/*

COPY add-text-to-svg.py /add-text-to-svg.py
