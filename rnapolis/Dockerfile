FROM ghcr.io/tzok/cli2rest:latest AS builder

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

FROM ghcr.io/tzok/cli2rest:latest

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      highs \
 && rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/venv /opt/venv

COPY unifier-wrapper.py /usr/local/bin/unifier-wrapper.py
COPY splitter-wrapper.py /usr/local/bin/splitter-wrapper.py
RUN chmod +x /usr/local/bin/unifier-wrapper.py
RUN chmod +x /usr/local/bin/splitter-wrapper.py
