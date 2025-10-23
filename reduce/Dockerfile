FROM debian:stable AS builder

RUN apt-get update -y \
 && apt-get install -y --no-install-recommends \
      build-essential \
      cmake \
 && rm -rf /var/lib/apt/lists/*

ARG REDUCE_VERSION=master

ADD https://github.com/rlabduke/reduce.git#${REDUCE_VERSION} /reduce-src

RUN mkdir /reduce-src/build \
 && cd /reduce-src/build \
 && cmake -DCMAKE_INSTALL_PREFIX=/opt/reduce .. \
 && make \
 && make install

#######################################

FROM ghcr.io/tzok/cli2rest:latest

COPY --from=builder /opt/reduce/bin /usr/local/bin
