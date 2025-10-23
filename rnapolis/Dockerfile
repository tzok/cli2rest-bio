FROM ghcr.io/tzok/cli2rest:latest AS builder

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      build-essentials \
      cmake \
      flex \
      bison \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN . /opt/venv/bin/activate \
 && pip install --upgrade pip \
 && pip install -r requirements.txt

#######################################

FROM ghcr.io/tzok/cli2rest:latest

COPY --from=builder /opt/venv /opt/venv

COPY unifier-wrapper.py /usr/local/bin/unifier-wrapper.py
COPY splitter-wrapper.py /usr/local/bin/splitter-wrapper.py
RUN chmod +x /usr/local/bin/unifier-wrapper.py
RUN chmod +x /usr/local/bin/splitter-wrapper.py
