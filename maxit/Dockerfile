# Start from the specified base image
FROM ghcr.io/tzok/cli2rest:latest

# Set MAXIT version from the latest version file
ENV MAXIT_VERSION=11.300

# Install necessary build dependencies
RUN apt-get update -y \
 && apt-get install -y \
      build-essential \
      wget \
      make \
      gcc \
      g++ \
 && rm -rf /var/lib/apt/lists/*

# Download and extract MAXIT
RUN wget https://sw-tools.rcsb.org/apps/MAXIT/maxit-v${MAXIT_VERSION}-prod-src.tar.gz \
 && tar -xzf maxit-v${MAXIT_VERSION}-prod-src.tar.gz -C / \
 && rm maxit-v${MAXIT_VERSION}-prod-src.tar.gz

# Set RCSBROOT environment variable
ENV RCSBROOT=/maxit-v${MAXIT_VERSION}-prod-src

# Build MAXIT
WORKDIR ${RCSBROOT}
RUN make \
 && make binary

# Make sure the installed binary is in the PATH
ENV PATH="${RCSBROOT}/bin:${PATH}"
