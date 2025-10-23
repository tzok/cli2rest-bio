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

ARG R4RNA_VERSION
ARG SVGCLEANER_VERSION=0.9.5

# Install BiocManager, remotes, and R4RNA package
# Using a CRAN mirror for BiocManager and remotes installation
# ask=FALSE and update=FALSE for non-interactive installation
RUN R -e "install.packages(c('BiocManager', 'remotes'), repos='https://cloud.r-project.org')" \
 && R -e "if (Sys.getenv('R4RNA_VERSION') != '') { remotes::install_version('R4RNA', version = Sys.getenv('R4RNA_VERSION'), repos = BiocManager::repositories()) } else { BiocManager::install('R4RNA', update=FALSE, ask=FALSE) }"

ADD https://github.com/RazrFalcon/svgcleaner/releases/download/v${SVGCLEANER_VERSION}/svgcleaner_linux_x86_64_${SVGCLEANER_VERSION}.tar.gz /
RUN tar xfz /svgcleaner_linux_x86_64_${SVGCLEANER_VERSION}.tar.gz -C /usr/local/bin

#######################################

FROM ghcr.io/tzok/cli2rest:latest

RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
        poppler-utils \
        r-base \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/lib/R/site-library /usr/local/lib/R/site-library
COPY --from=builder /usr/local/bin/svgcleaner /usr/local/bin/svgcleaner

COPY wrapper.py /usr/local/bin/wrapper.py
RUN chmod +x /usr/local/bin/wrapper.py
