ARG CLI2REST_BASE=ghcr.io/tzok/cli2rest:latest

FROM ${CLI2REST_BASE} AS builder

COPY requirements.txt .

RUN python -m pip download --no-cache-dir -d /wheels -r requirements.txt \
 && cp requirements.txt /wheels/

#######################################

FROM ${CLI2REST_BASE}

COPY --from=builder /wheels /wheels

RUN python -m pip install --no-cache-dir --no-index --find-links=/wheels -r /wheels/requirements.txt \
 && rm -rf /wheels

COPY unifier-wrapper.py /usr/local/bin/unifier-wrapper.py
COPY splitter-wrapper.py /usr/local/bin/splitter-wrapper.py
COPY coplanarity-checker-wrapper.py /usr/local/bin/coplanarity-checker-wrapper.py
COPY base-triple.cif /usr/local/share/rnapolis/base-triple.cif

RUN chmod +x \
      /usr/local/bin/unifier-wrapper.py \
      /usr/local/bin/splitter-wrapper.py \
      /usr/local/bin/coplanarity-checker-wrapper.py
