ARG CLI2REST_BASE=ghcr.io/tzok/cli2rest:latest

FROM ${CLI2REST_BASE} AS builder

RUN apt-get update \
 && apt-get install -y --no-install-recommends git \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/barnaba

COPY pyproject.toml uv.lock ./

RUN UV_PROJECT_ENVIRONMENT=/opt/barnaba/.venv uv sync --locked --no-dev

FROM ${CLI2REST_BASE}

COPY --from=builder /opt/barnaba/.venv /opt/barnaba/.venv

ENV PATH="/opt/barnaba/.venv/bin:/app/.venv/bin:$PATH"

WORKDIR /app
