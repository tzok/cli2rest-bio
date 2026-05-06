ARG CLI2REST_BASE=ghcr.io/tzok/cli2rest:latest

FROM ${CLI2REST_BASE} AS builder

ARG BARNABA_TAG=master

ADD https://github.com/srnas/barnaba.git#${BARNABA_TAG} /barnaba

RUN cd /barnaba \
 && . /opt/venv/bin/activate \
 && pip install --upgrade pip \
 && pip install .

#######################################

FROM ${CLI2REST_BASE}

COPY --from=builder /opt/venv /opt/venv
