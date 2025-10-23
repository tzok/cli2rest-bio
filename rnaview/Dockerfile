FROM debian:stable AS builder

RUN apt-get update -y \
 && apt-get install -y --no-install-recommends \
      build-essential \
      ca-certificates \
      git \
      make \
 && rm -rf /var/lib/apt/lists/*

ARG RNAVIEW_VERSION

RUN git clone https://github.com/rcsb/RNAView.git /RNAView

RUN cd /RNAView \
 && git fetch --tags \
 && git checkout tags/${RNAVIEW_VERSION} \
 && make

#######################################

FROM ghcr.io/tzok/cli2rest:latest

COPY --from=builder /RNAView /opt/RNAView

ENV RNAVIEW=/opt/RNAView \
    PATH="/opt/RNAView/bin:${PATH}"
