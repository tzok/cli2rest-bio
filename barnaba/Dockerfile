ARG CLI2REST_BASE=ghcr.io/tzok/cli2rest:latest

FROM ${CLI2REST_BASE} AS builder

ARG BARNABA_TAG=master

ADD https://github.com/srnas/barnaba.git#${BARNABA_TAG} /barnaba

COPY requirements.lock .

RUN python -m pip wheel --no-cache-dir --no-deps -w /wheels /barnaba \
 && python -m pip wheel --no-cache-dir -w /wheels -r requirements.lock \
 && cp requirements.lock /wheels/

#######################################

FROM ${CLI2REST_BASE}

COPY --from=builder /wheels /wheels

RUN python -m pip install --no-cache-dir --no-index --find-links=/wheels -r /wheels/requirements.lock \
 && python -m pip install --no-cache-dir --no-index --find-links=/wheels --no-deps barnaba \
 && rm -rf /wheels
