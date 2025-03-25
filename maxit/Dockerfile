# Start from the specified base image
FROM ghcr.io/tzok/cli2rest:latest

# Set default MAXIT version that can be overridden at build time
ARG MAXIT_VERSION=11.300

# Install necessary build dependencies
RUN apt-get update -y \
 && apt-get install -y \
      bison \
      build-essential \
      flex \
      g++ \
      gcc \
      make \
      wget \
 && rm -rf /var/lib/apt/lists/*

# Download and extract MAXIT
RUN wget https://sw-tools.rcsb.org/apps/MAXIT/maxit-v${MAXIT_VERSION}-prod-src.tar.gz \
 && tar -xzf maxit-v${MAXIT_VERSION}-prod-src.tar.gz -C / \
 && rm maxit-v${MAXIT_VERSION}-prod-src.tar.gz

# Set RCSBROOT environment variable
ENV RCSBROOT=/maxit-v${MAXIT_VERSION}-prod-src

# Build MAXIT
RUN cd ${RCSBROOT} \
 && make \
 && make binary

# Make sure the installed binary is in the PATH
ENV PATH="${RCSBROOT}/bin:${PATH}"
