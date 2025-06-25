# Start from the specified base image
FROM ghcr.io/tzok/cli2rest:latest

# Copy the DSSR binary to the container
COPY x3dna-dssr /usr/local/bin/x3dna-dssr

# Make the binary executable
RUN chmod +x /usr/local/bin/x3dna-dssr

# Make sure the installed binary is in the PATH
ENV PATH="/usr/local/bin:${PATH}"
