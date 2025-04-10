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

# Copy the wrapper scripts
COPY unifier-wrapper.py /usr/local/bin/unifier-wrapper.py
COPY splitter-wrapper.py /usr/local/bin/splitter-wrapper.py
RUN chmod +x /usr/local/bin/unifier-wrapper.py
RUN chmod +x /usr/local/bin/splitter-wrapper.py

# Make sure the installed binary and script are in the PATH
# (pip install usually handles this, but ensure /usr/local/bin or similar is in PATH)
ENV PATH="/usr/local/bin:${PATH}"
