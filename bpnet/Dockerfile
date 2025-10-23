# Builder stage based on Debian stable
FROM debian:stable AS builder

# Install necessary build dependencies
RUN apt-get update -y \
 && apt-get install -y --no-install-recommends \
      build-essential \
      ca-certificates \
      gfortran \
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

# Clone the metbp repository into /metbp-src
RUN git clone https://github.com/computational-biology/metbp.git /metbp-src

# Build metbp
RUN cd /metbp-src \
 && make clean \
 && make

#######################################

FROM ghcr.io/tzok/cli2rest:latest

# Create directory for system files and copy them from builder
RUN mkdir -p /usr/local/bin/bpnet-sysfiles
COPY --from=builder /bpnet-src/sysfiles/* /usr/local/bin/bpnet-sysfiles/
COPY --from=builder /metbp-src/sys/* /usr/local/bin/bpnet-sysfiles/

# Copy the binaries from builder to a standard location
COPY --from=builder /bpnet-src/src/bpnet.linux /usr/local/bin/
COPY --from=builder /metbp-src/bin/metbp.linux /usr/local/bin/

# Copy and make the wrapper script executable
COPY wrapper.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/wrapper.sh

# Set the required environment variable
ENV NUCLEIC_ACID_DIR=/usr/local/bin/bpnet-sysfiles/
