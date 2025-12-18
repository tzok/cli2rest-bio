FROM debian:stable AS builder

RUN apt-get update -y \
 && apt-get install -y --no-install-recommends \
      build-essential \
      cmake \
 && rm -rf /var/lib/apt/lists/*

ARG REDUCE_VERSION=master

ENV CC="gcc" CXX="g++" FC="gfortran" \
    CFLAGS="-O3 -pipe -fomit-frame-pointer -fno-plt -march=x86-64 -mtune=generic -DNDEBUG" \
    CXXFLAGS="-O3 -pipe -fomit-frame-pointer -fno-plt -march=x86-64 -mtune=generic -DNDEBUG" \
    FFLAGS="-O3 -pipe -fomit-frame-pointer -fno-plt -march=x86-64 -mtune=generic" \
    FCFLAGS="-O3 -pipe -fomit-frame-pointer -fno-plt -march=x86-64 -mtune=generic" \
    LDFLAGS="-Wl,-O1 -Wl,--as-needed -s"

ADD https://github.com/rlabduke/reduce.git#${REDUCE_VERSION} /reduce-src

RUN mkdir /reduce-src/build \
 && cd /reduce-src/build \
 && cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/opt/reduce -DCMAKE_C_FLAGS_RELEASE="$CFLAGS" -DCMAKE_CXX_FLAGS_RELEASE="$CXXFLAGS" -DCMAKE_Fortran_FLAGS_RELEASE="$FFLAGS" -DCMAKE_EXE_LINKER_FLAGS_RELEASE="$LDFLAGS" -DCMAKE_SHARED_LINKER_FLAGS_RELEASE="$LDFLAGS" .. \
 && make \
 && make install

#######################################

FROM ghcr.io/tzok/cli2rest:latest

COPY --from=builder /opt/reduce/bin /usr/local/bin

COPY wrapper.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/wrapper.sh
