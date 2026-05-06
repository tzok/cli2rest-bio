ARG CLI2REST_BASE=ghcr.io/tzok/cli2rest:latest

FROM ${CLI2REST_BASE} AS builder

COPY requirements.lock .

RUN python -m pip wheel --no-cache-dir -w /wheels -r requirements.lock \
 && cp requirements.lock /wheels/

#######################################

FROM ${CLI2REST_BASE}

COPY --from=builder /wheels /wheels

RUN python -m pip install --no-cache-dir --no-index --find-links=/wheels -r /wheels/requirements.lock \
 && rm -rf /wheels

COPY unifier-wrapper.py /usr/local/bin/unifier-wrapper.py
COPY splitter-wrapper.py /usr/local/bin/splitter-wrapper.py
COPY coplanarity-checker-wrapper.py /usr/local/bin/coplanarity-checker-wrapper.py
COPY base-triple.cif /usr/local/share/rnapolis/base-triple.cif

RUN chmod +x \
      /usr/local/bin/unifier-wrapper.py \
      /usr/local/bin/splitter-wrapper.py \
      /usr/local/bin/coplanarity-checker-wrapper.py
