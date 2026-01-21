FROM debian:trixie-slim AS r-builder

RUN apt-get update -y \
 && apt-get install -y --no-install-recommends \
      build-essential \
      ca-certificates \
      curl \
      gzip \
      tar \
      r-base \
      r-base-dev \
      r-bioc-biostrings \
      r-cran-biocmanager \
      r-cran-ggplot2 \
      r-cran-plotly \
      r-cran-remotes \
      r-cran-rpostgresql \
 && rm -rf /var/lib/apt/lists/*

ARG R4RNA_VERSION

RUN Rscript -e 'if (nzchar(Sys.getenv("R4RNA_VERSION"))) { remotes::install_version("R4RNA", version = Sys.getenv("R4RNA_VERSION"), repos = BiocManager::repositories(), upgrade = "never") } else { BiocManager::install(c("R4RNA"), update=FALSE, ask=FALSE) }'

ARG SVGCLEANER_VERSION=0.9.5

ADD https://github.com/RazrFalcon/svgcleaner/releases/download/v${SVGCLEANER_VERSION}/svgcleaner_linux_x86_64_${SVGCLEANER_VERSION}.tar.gz /tmp/
RUN tar xfz "/tmp/svgcleaner_linux_x86_64_${SVGCLEANER_VERSION}.tar.gz" -C /usr/local/bin

#######################################

FROM ghcr.io/tzok/cli2rest:latest

RUN apt-get update -y \
 && apt-get install -y --no-install-recommends \
      poppler-utils \
      r-base \
 && rm -rf /var/lib/apt/lists/*

COPY --from=r-builder /usr/local/lib/R/site-library /usr/local/lib/R/site-library
COPY --from=r-builder /usr/lib/R/site-library /usr/lib/R/site-library
COPY --from=r-builder /usr/local/bin/svgcleaner /usr/local/bin/svgcleaner

COPY wrapper.py /usr/local/bin/wrapper.py
RUN chmod +x /usr/local/bin/wrapper.py
