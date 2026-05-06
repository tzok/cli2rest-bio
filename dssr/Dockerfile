ARG CLI2REST_BASE=ghcr.io/tzok/cli2rest:latest

# Start from the specified base image
FROM ${CLI2REST_BASE}

# Copy the DSSR binary to the container
COPY x3dna-dssr /usr/local/bin/x3dna-dssr

# Make the binary executable
RUN chmod +x /usr/local/bin/x3dna-dssr
