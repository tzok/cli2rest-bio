# Start from the specified base image
FROM ghcr.io/tzok/cli2rest:latest

# Install necessary build dependencies
RUN apt-get update -y \
 && apt-get install -y \
      build-essential \
      cmake \
      git \
 && rm -rf /var/lib/apt/lists/*

# Clone the reduce repository
RUN git clone https://github.com/rlabduke/reduce.git

# Build reduce using CMake
RUN mkdir reduce/build \
 && cd reduce/build \
 && cmake .. \
 && make \
 && make install

# Make sure the installed binary is in the PATH
ENV PATH="/usr/local/bin:${PATH}"
