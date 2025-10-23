FROM debian:stable AS builder

RUN apt-get update -y \
 && apt-get install -y --no-install-recommends \
      build-essential \
      ca-certificates \
      cmake \
      git \
 && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/rlabduke/reduce.git /reduce-src

ARG REDUCE_VERSION

RUN cd /reduce-src \
 && git fetch --tags \
 && git checkout tags/${REDUCE_VERSION} \
 && mkdir build \
 && cd build \
 && cmake -DCMAKE_INSTALL_PREFIX=/opt/reduce .. \
 && make \
 && make install

#######################################

FROM ghcr.io/tzok/cli2rest:latest

COPY --from=builder /opt/reduce/bin /usr/local/bin
