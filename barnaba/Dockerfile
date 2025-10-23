FROM ghcr.io/tzok/cli2rest:latest AS builder

ARG BARNABA_TAG=master

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      git \
 && rm -rf /var/lib/apt/lists/*

RUN git clone --branch ${BARNABA_TAG} https://github.com/srnas/barnaba.git

RUN cd barnaba \
 && . /opt/venv/bin/activate \
 && pip install --upgrade pip \
 && pip install .

#######################################

FROM ghcr.io/tzok/cli2rest:latest

ARG BARNABA_TAG=master

COPY --from=builder /opt/venv /opt/venv

LABEL barnaba.version=${BARNABA_TAG}
