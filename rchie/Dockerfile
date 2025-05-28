# Start from the cli2rest base image
FROM ghcr.io/tzok/cli2rest:latest

ARG SVGCLEANER_VERSION=0.9.5

# Install R and its dependencies, then clean up
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
        r-base \
        r-base-dev \
        libcurl4-openssl-dev \
        libssl-dev \
        libxml2-dev \
        libfontconfig1-dev \
        libcairo2-dev \
        curl \
        poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Download and install svgcleaner
RUN curl -L https://github.com/RazrFalcon/svgcleaner/releases/download/v${SVGCLEANER_VERSION}/svgcleaner_linux_x86_64_${SVGCLEANER_VERSION}.tar.gz | tar xz -C /usr/local/bin \
 && chmod +x /usr/local/bin/svgcleaner

# Make sure the installed binary and script are in the PATH (though /usr/local/bin usually is)
ENV PATH="/usr/local/bin:${PATH}"

# Install BiocManager, then R4RNA package using BiocManager
# Using a CRAN mirror for BiocManager installation
# ask=FALSE and update=FALSE for non-interactive installation
RUN R -e "install.packages('BiocManager', repos='https://cloud.r-project.org')" && \
    R -e "BiocManager::install('R4RNA', update=FALSE, ask=FALSE)"

# Copy the wrapper script
COPY wrapper.py /usr/local/bin/wrapper.py
RUN chmod +x /usr/local/bin/wrapper.py
