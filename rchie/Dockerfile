FROM ghcr.io/tzok/cli2rest:latest AS builder

RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
        r-base \
        r-base-dev \
        libcurl4-openssl-dev \
        libssl-dev \
        libxml2-dev \
        libfontconfig1-dev \
        libcairo2-dev \
    && rm -rf /var/lib/apt/lists/*

# Install BiocManager, then R4RNA package using BiocManager
# Using a CRAN mirror for BiocManager installation
# ask=FALSE and update=FALSE for non-interactive installation
RUN R -e "install.packages('BiocManager', repos='https://cloud.r-project.org')" \
 && R -e "BiocManager::install('R4RNA', update=FALSE, ask=FALSE)"

#######################################

FROM ghcr.io/tzok/cli2rest:latest

RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
        r-base \
    && rm -rf /var/lib/apt/lists/*

ARG SVGCLEANER_VERSION=0.9.5

ADD https://github.com/RazrFalcon/svgcleaner/releases/download/v${SVGCLEANER_VERSION}/svgcleaner_linux_x86_64_${SVGCLEANER_VERSION}.tar.gz /usr/local/bin

COPY --from=builder /usr/local/lib/R/site-library /usr/local/lib/R/site-library

COPY wrapper.py /usr/local/bin/wrapper.py
RUN chmod +x /usr/local/bin/wrapper.py
