# Start from the specified base image
FROM ghcr.io/tzok/cli2rest:latest

# Define build argument for Reduce version
ARG REDUCE_VERSION

# Install necessary build dependencies
RUN apt-get update -y \
 && apt-get install -y \
      build-essential \
      cmake \
      git \
 && rm -rf /var/lib/apt/lists/*

# Clone the reduce repository into /reduce-src
RUN git clone https://github.com/rlabduke/reduce.git /reduce-src

# Set working directory
WORKDIR /reduce-src

# Checkout the specified tag
RUN git fetch --tags && \
    echo "Checking out Reduce version: ${REDUCE_VERSION}" && \
    git checkout tags/${REDUCE_VERSION}

# Build reduce using CMake
RUN mkdir build \
 && cd build \
 && cmake .. \
 && make \
 && make install

# Make sure the installed binary is in the PATH
ENV PATH="/usr/local/bin:${PATH}"

# Reset working directory (optional, good practice)
WORKDIR /
