ARG CLI2REST_BASE=ghcr.io/tzok/cli2rest:latest

FROM ${CLI2REST_BASE} AS builder

ARG FR3D_REF=latest

ADD https://github.com/BGSU-RNA/fr3d-python.git#${FR3D_REF} /fr3d-src

COPY requirements.lock .

RUN python -m pip wheel --no-cache-dir --no-deps -w /wheels /fr3d-src \
 && python -m pip wheel --no-cache-dir -w /wheels -r requirements.lock \
 && cp requirements.lock /wheels/

#######################################

FROM ${CLI2REST_BASE}

COPY --from=builder /wheels /wheels

RUN python -m pip install --no-cache-dir --no-index --find-links=/wheels -r /wheels/requirements.lock \
 && python -m pip install --no-cache-dir --no-index --find-links=/wheels --no-deps fr3d \
 && rm -rf /wheels

COPY wrapper.py /usr/local/bin/wrapper.py
RUN chmod +x /usr/local/bin/wrapper.py
