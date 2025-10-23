FROM ghcr.io/tzok/cli2rest:latest AS builder

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      build-essential \
      git \
 && rm -rf /var/lib/apt/lists/*

ARG FR3D_BRANCH=latest

RUN . /opt/venv/bin/activate \
 && pip install --upgrade pip \
 && pip install "git+https://github.com/BGSU-RNA/fr3d-python.git@${FR3D_BRANCH}"

#######################################

FROM ghcr.io/tzok/cli2rest:latest

COPY --from=builder /opt/venv /opt/venv

COPY wrapper.py /usr/local/bin/wrapper.py
RUN chmod +x /usr/local/bin/wrapper.py
