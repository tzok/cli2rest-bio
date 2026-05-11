ARG CLI2REST_BASE=ghcr.io/tzok/cli2rest:latest

FROM ${CLI2REST_BASE}

WORKDIR /opt/rnapolis

COPY pyproject.toml uv.lock ./

RUN UV_PROJECT_ENVIRONMENT=/opt/rnapolis/.venv uv sync --locked --no-dev

ENV PATH="/opt/rnapolis/.venv/bin:/app/.venv/bin:$PATH"

WORKDIR /app

COPY unifier-wrapper.py /usr/local/bin/unifier-wrapper.py
COPY splitter-wrapper.py /usr/local/bin/splitter-wrapper.py
COPY coplanarity-checker-wrapper.py /usr/local/bin/coplanarity-checker-wrapper.py
COPY base-triple.cif /usr/local/share/rnapolis/base-triple.cif

RUN chmod +x \
      /usr/local/bin/unifier-wrapper.py \
      /usr/local/bin/splitter-wrapper.py \
      /usr/local/bin/coplanarity-checker-wrapper.py
