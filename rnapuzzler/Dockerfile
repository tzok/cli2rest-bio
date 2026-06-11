ARG CLI2REST_BASE=ghcr.io/tzok/cli2rest:latest

FROM ${CLI2REST_BASE}

ARG VIENNARNA_VERSION=2.7.2-1
ARG VIENNARNA_DEBIAN_RELEASE=debian_13

ADD https://www.tbi.univie.ac.at/RNA/download/debian/${VIENNARNA_DEBIAN_RELEASE}/viennarna_${VIENNARNA_VERSION}_amd64.deb /tmp/viennarna.deb

RUN apt-get update -y \
    && apt-get install -y --no-install-recommends \
        inkscape \
        python3-lxml \
    && apt-get install -y --no-install-recommends /tmp/viennarna.deb \
    && rm -rf /var/lib/apt/lists/* /tmp/viennarna.deb

ARG SVGCLEANER_VERSION=0.9.5

ADD https://github.com/RazrFalcon/svgcleaner/releases/download/v${SVGCLEANER_VERSION}/svgcleaner_linux_x86_64_${SVGCLEANER_VERSION}.tar.gz /tmp/
RUN tar xfz "/tmp/svgcleaner_linux_x86_64_${SVGCLEANER_VERSION}.tar.gz" -C /usr/local/bin

COPY wrapper.py /usr/local/bin/wrapper.py
RUN chmod +x /usr/local/bin/wrapper.py