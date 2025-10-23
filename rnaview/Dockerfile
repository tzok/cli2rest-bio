FROM debian:stable AS builder

RUN apt-get update -y \
 && apt-get install -y --no-install-recommends \
      build-essential \
 && rm -rf /var/lib/apt/lists/*

ARG RNAVIEW_VERSION=master

ADD https://github.com/rcsb/RNAView.git#${RNAVIEW_VERSION} /RNAView

RUN cd /RNAView \
 && make

#######################################

FROM ghcr.io/tzok/cli2rest:latest

COPY --from=builder /RNAView /opt/RNAView

ENV RNAVIEW=/opt/RNAView \
    PATH="/opt/RNAView/bin:${PATH}"
