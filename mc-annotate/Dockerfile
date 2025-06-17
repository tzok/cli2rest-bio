# Start from the specified base image
FROM ghcr.io/tzok/cli2rest:latest

# Set default MC-Annotate version that can be overridden at build time
ARG MC_ANNOTATE_VERSION=1.6.2

# Install necessary dependencies
RUN apt-get update -y \
 && apt-get install -y \
      wget \
      unzip \
 && rm -rf /var/lib/apt/lists/*

# Download and extract MC-Annotate
RUN wget https://major.iric.ca/MajorLabEn/MC-Tools_files/MC-Annotate.zip \
 && unzip MC-Annotate.zip \
 && chmod +x MC-Annotate \
 && mv MC-Annotate /usr/local/bin/ \
 && rm MC-Annotate.zip

# Add version label
LABEL mc-annotate.version=${MC_ANNOTATE_VERSION}

# Make sure the installed binary is in the PATH
ENV PATH="/usr/local/bin:${PATH}"
