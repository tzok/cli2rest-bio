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

# Clone the RNAView repository
RUN git clone https://github.com/rcsb/RNAView.git /RNAView

# Build RNAView
RUN cd /RNAView \
 && make

# Set RNAVIEW environment variable
ENV RNAVIEW=/RNAView

# Make sure the installed binary is in the PATH
ENV PATH="${RNAVIEW}/bin:${PATH}"
