ARG CLI2REST_BASE=ghcr.io/tzok/cli2rest:latest

FROM ${CLI2REST_BASE}

RUN . /etc/os-release \
 && echo "deb http://deb.debian.org/debian trixie main" > /etc/apt/sources.list.d/trixie.list \
 && printf 'Package: *\nPin: release n=%s\nPin-Priority: 900\n\nPackage: vienna-rna\nPin: release n=trixie\nPin-Priority: 950\n' "$VERSION_CODENAME" > /etc/apt/preferences.d/vienna-rna \
 && apt-get update -y \
 && apt-get install -y --no-install-recommends \
      python3-lxml \
      vienna-rna \
 && rm -rf /var/lib/apt/lists/*

ARG SVGCLEANER_VERSION=0.9.5

ADD https://github.com/RazrFalcon/svgcleaner/releases/download/v${SVGCLEANER_VERSION}/svgcleaner_linux_x86_64_${SVGCLEANER_VERSION}.tar.gz /tmp/
RUN tar xfz "/tmp/svgcleaner_linux_x86_64_${SVGCLEANER_VERSION}.tar.gz" -C /usr/local/bin

COPY wrapper.py /usr/local/bin/wrapper.py
RUN chmod +x /usr/local/bin/wrapper.py
