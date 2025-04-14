# Start from the specified base image
FROM ghcr.io/tzok/cli2rest:latest

# Install necessary build dependencies
RUN apt-get update -y \
 && apt-get install -y \
      build-essential \
      gcc \
      git \
      make \
      wget \
 && rm -rf /var/lib/apt/lists/*

# Define build argument for RNAView version
ARG RNAVIEW_VERSION

# Clone the RNAView repository
RUN git clone https://github.com/rcsb/RNAView.git /RNAView

# Set working directory
WORKDIR /RNAView

# Checkout the specified tag
RUN git fetch --tags && \
    echo "Checking out RNAView version: ${RNAVIEW_VERSION}" && \
    git checkout tags/${RNAVIEW_VERSION}

# Build RNAView
RUN make

# Set RNAVIEW environment variable
ENV RNAVIEW=/RNAView

# Make sure the installed binary is in the PATH
ENV PATH="${RNAVIEW}/bin:${PATH}"

# Reset working directory (optional, good practice)
WORKDIR /
