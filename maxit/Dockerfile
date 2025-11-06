FROM debian:stable AS builder

RUN apt-get update -y \
 && apt-get install -y --no-install-recommends \
      bison \
      build-essential \
      flex \
 && rm -rf /var/lib/apt/lists/*

ARG MAXIT_VERSION=11.300

ENV CFLAGS="-O3 -pipe -fomit-frame-pointer -fno-plt -march=x86-64 -mtune=generic -DNDEBUG" \
    CXXFLAGS="-O3 -pipe -fomit-frame-pointer -fno-plt -march=x86-64 -mtune=generic -DNDEBUG" \
    CPPFLAGS="-DNDEBUG" \
    LDFLAGS="-Wl,-O1 -Wl,--as-needed -s"

ADD https://sw-tools.rcsb.org/apps/MAXIT/maxit-v${MAXIT_VERSION}-prod-src.tar.gz /

RUN tar xf maxit-v${MAXIT_VERSION}-prod-src.tar.gz \
 && cd /maxit-v${MAXIT_VERSION}-prod-src \
 && make \
 && make binary

#######################################

FROM ghcr.io/tzok/cli2rest:latest

ARG MAXIT_VERSION=11.300

COPY --from=builder /maxit-v${MAXIT_VERSION}-prod-src /opt/maxit

ENV RCSBROOT=/opt/maxit \
    PATH="/opt/maxit/bin:${PATH}"
