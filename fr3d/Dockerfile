ARG CLI2REST_BASE=ghcr.io/tzok/cli2rest:latest

FROM ${CLI2REST_BASE} AS builder

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      build-essential \
      git \
 && rm -rf /var/lib/apt/lists/*

ARG FR3D_REF=latest

RUN python -m pip install --no-cache-dir --prefix=/install "git+https://github.com/BGSU-RNA/fr3d-python.git@${FR3D_REF}"

#######################################

FROM ${CLI2REST_BASE}

COPY --from=builder /install /usr/local

COPY wrapper.py /usr/local/bin/wrapper.py
RUN chmod +x /usr/local/bin/wrapper.py
