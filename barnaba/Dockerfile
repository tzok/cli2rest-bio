FROM ghcr.io/tzok/cli2rest:latest AS builder

ARG BARNABA_TAG=master

ADD https://github.com/srnas/barnaba.git#${BARNABA_TAG} /barnaba

RUN cd /barnaba \
 && . /opt/venv/bin/activate \
 && pip install --upgrade pip \
 && pip install .

#######################################

FROM ghcr.io/tzok/cli2rest:latest

COPY --from=builder /opt/venv /opt/venv
