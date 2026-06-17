ARG CLI2REST_BASE=ghcr.io/tzok/cli2rest:latest

FROM ${CLI2REST_BASE} AS r-builder

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
      r-cran-rpostgresql \
 && rm -rf /var/lib/apt/lists/*

ARG BIOC_VERSION
ARG R4RNA_VERSION

RUN if [ -z "$BIOC_VERSION" ] || [ -z "$R4RNA_VERSION" ]; then \
      echo "Error: BIOC_VERSION and R4RNA_VERSION build args are required."; \
      exit 1; \
    fi \
 && curl -sfL -o /tmp/R4RNA.tar.gz "https://bioconductor.org/packages/${BIOC_VERSION}/bioc/src/contrib/R4RNA_${R4RNA_VERSION}.tar.gz" \
 && R CMD INSTALL /tmp/R4RNA.tar.gz \
 && rm -f /tmp/R4RNA.tar.gz \
 && Rscript -e "actual_r4rna <- as.character(packageVersion(\"R4RNA\")); if (actual_r4rna != Sys.getenv(\"R4RNA_VERSION\")) { stop(sprintf(\"R4RNA version mismatch: expected %s, got %s\", Sys.getenv(\"R4RNA_VERSION\"), actual_r4rna)) }"

ARG SVGCLEANER_VERSION=0.9.5

ADD https://github.com/RazrFalcon/svgcleaner/releases/download/v${SVGCLEANER_VERSION}/svgcleaner_linux_x86_64_${SVGCLEANER_VERSION}.tar.gz /tmp/
RUN tar xfz "/tmp/svgcleaner_linux_x86_64_${SVGCLEANER_VERSION}.tar.gz" -C /usr/local/bin

#######################################

FROM ${CLI2REST_BASE}

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
