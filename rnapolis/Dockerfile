# Start from the specified base image
FROM ghcr.io/tzok/cli2rest:latest

# Install necessary build dependencies
RUN apt-get update -y \
 && apt-get install -y \
      python3 \
      python3-pip \
      python3-dev \
 && rm -rf /var/lib/apt/lists/*

# Install RNAPOLIS
RUN pip3 install rnapolis

# Make sure the installed binary is in the PATH
# (pip install usually handles this, but ensure /usr/local/bin or similar is in PATH)
ENV PATH="/usr/local/bin:${PATH}"
