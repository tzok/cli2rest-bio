ARG CLI2REST_BASE=ghcr.io/tzok/cli2rest:latest

FROM ${CLI2REST_BASE} AS builder

ARG BARNABA_TAG=master

ADD https://github.com/srnas/barnaba.git#${BARNABA_TAG} /barnaba

COPY requirements.txt .

RUN python -m pip download --no-cache-dir -d /wheels -r requirements.txt \
 && python -m pip wheel --no-cache-dir --no-deps -w /wheels /barnaba \
 && cp requirements.txt /wheels/

#######################################

FROM ${CLI2REST_BASE}

COPY --from=builder /wheels /wheels

RUN python -m pip install --no-cache-dir --no-index --find-links=/wheels -r /wheels/requirements.txt \
 && python -m pip install --no-cache-dir --no-index --find-links=/wheels --no-deps barnaba \
 && rm -rf /wheels
