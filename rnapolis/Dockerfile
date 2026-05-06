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

RUN . /opt/venv/bin/activate \
 && pip install --upgrade pip \
 && pip install -r requirements.txt

#######################################

FROM ${CLI2REST_BASE}

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      highs \
 && rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/venv /opt/venv

COPY unifier-wrapper.py /usr/local/bin/unifier-wrapper.py
COPY splitter-wrapper.py /usr/local/bin/splitter-wrapper.py
COPY coplanarity-checker-wrapper.py /usr/local/bin/coplanarity-checker-wrapper.py
COPY base-triple.cif /usr/local/share/rnapolis/base-triple.cif

RUN chmod +x \
      /usr/local/bin/unifier-wrapper.py \
      /usr/local/bin/splitter-wrapper.py \
      /usr/local/bin/coplanarity-checker-wrapper.py
