ARG CLI2REST_BASE=ghcr.io/tzok/cli2rest:latest

FROM ${CLI2REST_BASE} AS builder

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      bison \
      build-essential \
      cmake \
      flex \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN python -m pip install --no-cache-dir --prefix=/install -r requirements.txt

#######################################

FROM ${CLI2REST_BASE}

COPY --from=builder /install /usr/local

COPY unifier-wrapper.py /usr/local/bin/unifier-wrapper.py
COPY splitter-wrapper.py /usr/local/bin/splitter-wrapper.py
COPY coplanarity-checker-wrapper.py /usr/local/bin/coplanarity-checker-wrapper.py
COPY base-triple.cif /usr/local/share/rnapolis/base-triple.cif

RUN chmod +x \
      /usr/local/bin/unifier-wrapper.py \
      /usr/local/bin/splitter-wrapper.py \
      /usr/local/bin/coplanarity-checker-wrapper.py
