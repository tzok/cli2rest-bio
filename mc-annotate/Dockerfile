FROM debian:stable AS builder

RUN apt-get update -y \
 && apt-get install -y --no-install-recommends \
      ca-certificates \
      curl \
      unzip \
 && rm -rf /var/lib/apt/lists/*

RUN curl -LsSf https://major.iric.ca/MajorLabEn/MC-Tools_files/MC-Annotate.zip | funzip > /MC-Annotate

#######################################

FROM ghcr.io/tzok/cli2rest:latest

COPY --from=builder /MC-Annotate /usr/local/bin/MC-Annotate
