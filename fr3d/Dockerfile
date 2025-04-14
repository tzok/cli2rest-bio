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

# Define build argument for FR3D branch (default to latest)
ARG FR3D_BRANCH=latest

# Clone the specified branch of the FR3D repository
RUN echo "Cloning FR3D branch: ${FR3D_BRANCH}" && \
    git clone --branch ${FR3D_BRANCH} https://github.com/BGSU-RNA/fr3d-python.git

# Install FR3D and its dependencies
RUN cd fr3d-python && pip3 install -e .

# Create a script to run FR3D
COPY wrapper.py /usr/local/bin/wrapper.py
RUN chmod +x /usr/local/bin/wrapper.py

# Make sure the installed binary is in the PATH
ENV PATH="/usr/local/bin:${PATH}"
