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

# Clone the FR3D repository
RUN git clone https://github.com/BGSU-RNA/fr3d-python.git

# Install FR3D and its dependencies
RUN cd fr3d-python && pip3 install -e .

# Create a script to run FR3D
COPY fr3d_runner.py /usr/local/bin/fr3d_runner.py
RUN chmod +x /usr/local/bin/fr3d_runner.py

# Make sure the installed binary is in the PATH
ENV PATH="/usr/local/bin:${PATH}"
