# Start from the specified base image
FROM ghcr.io/tzok/cli2rest:latest

# Install necessary build dependencies
RUN apt-get update && apt-get install -y \
    git \
    cmake \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create a working directory
WORKDIR /app

# Clone the reduce repository
RUN git clone https://github.com/rlabduke/reduce.git

# Build reduce using CMake
WORKDIR /app/reduce
RUN mkdir -p build && \
    cd build && \
    cmake .. && \
    make && \
    make install

# Make sure the installed binary is in the PATH
ENV PATH="/usr/local/bin:${PATH}"

# Verify installation
RUN reduce -h

# Set the working directory back to /app
WORKDIR /app
