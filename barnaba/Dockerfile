ARG CLI2REST_BASE=ghcr.io/tzok/cli2rest:latest

FROM ${CLI2REST_BASE}

WORKDIR /opt/barnaba

COPY pyproject.toml uv.lock ./

RUN UV_PROJECT_ENVIRONMENT=/opt/barnaba/.venv uv sync --locked --no-dev

ENV PATH="/opt/barnaba/.venv/bin:/app/.venv/bin:$PATH"

WORKDIR /app
