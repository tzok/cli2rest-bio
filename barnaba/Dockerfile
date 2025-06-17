# Start from the specified base image
FROM ghcr.io/tzok/cli2rest:latest

# Install necessary build dependencies
RUN apt-get update -y \
 && apt-get install -y \
      python3 \
      python3-pip \
      python3-dev \
      git \
 && rm -rf /var/lib/apt/lists/*

# Define build argument for barnaba branch/tag (default to master)
ARG BARNABA_TAG=master

# Clone the specified tag/branch of the barnaba repository
RUN echo "Cloning barnaba tag/branch: ${BARNABA_TAG}" && \
    git clone --branch ${BARNABA_TAG} https://github.com/srnas/barnaba.git

# Install barnaba and its dependencies
RUN cd barnaba && pip3 install -e .

# Make sure the installed binary is in the PATH
ENV PATH="/usr/local/bin:${PATH}"

# Add version label
LABEL barnaba.version=${BARNABA_TAG}
