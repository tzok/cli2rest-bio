ARG CLI2REST_BASE=ghcr.io/tzok/cli2rest:latest
ARG FR3D_CHANNEL=latest

FROM ${CLI2REST_BASE}

WORKDIR /opt/fr3d

COPY uv ./uv

WORKDIR /opt/fr3d/uv/${FR3D_CHANNEL}

RUN UV_PROJECT_ENVIRONMENT=/opt/fr3d/.venv uv sync --locked --no-dev

ENV PATH="/opt/fr3d/.venv/bin:/app/.venv/bin:$PATH"

WORKDIR /app

COPY wrapper.py /usr/local/bin/wrapper.py
RUN chmod +x /usr/local/bin/wrapper.py
