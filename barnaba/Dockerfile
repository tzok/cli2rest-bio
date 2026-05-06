ARG CLI2REST_BASE=ghcr.io/tzok/cli2rest:latest

FROM ${CLI2REST_BASE} AS builder

ARG BARNABA_TAG=master

ADD https://github.com/srnas/barnaba.git#${BARNABA_TAG} /barnaba

RUN cd /barnaba \
 && python -m pip install --no-cache-dir --prefix=/install .

#######################################

FROM ${CLI2REST_BASE}

COPY --from=builder /install /usr/local
