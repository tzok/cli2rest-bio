# Start from the specified base image
FROM ghcr.io/tzok/cli2rest:latest

# Install necessary build dependencies
RUN apt-get update -y \
 && apt-get install -y \
      build-essential \
      git \
 && rm -rf /var/lib/apt/lists/*

# Clone the bpnet repository into /bpnet-src
RUN git clone https://github.com/computational-biology/bpnet.git /bpnet-src

# Copy and apply the patch
COPY 001-change-chain-separatator.patch /tmp/
RUN cd /bpnet-src && patch -p0 < /tmp/001-change-chain-separatator.patch

# Build bpnet
RUN cd /bpnet-src/src \
 && make clean \
 && make

# Create directory for system files and copy them
RUN mkdir -p /usr/local/bin/bpnet-sysfiles \
 && cp -r /bpnet-src/sysfiles/* /usr/local/bin/bpnet-sysfiles/

# Copy the binary to a standard location
RUN cp /bpnet-src/bin/bpnet.linux /usr/local/bin/

# Set the required environment variable
ENV NUCLEIC_ACID_DIR=/usr/local/bin/bpnet-sysfiles/

# Make sure the installed binary is in the PATH
ENV PATH="/usr/local/bin:${PATH}"

