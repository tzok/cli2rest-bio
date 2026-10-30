ARG CLI2REST_BASE=ghcr.io/tzok/cli2rest:py3.13

FROM ${CLI2REST_BASE} AS builder

RUN apt-get update \
 && apt-get install -y --no-install-recommends git \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/barnaba

COPY pyproject.toml uv.lock ./

# --no-managed-python forces uv to use the base image interpreter instead of
# downloading one. A downloaded interpreter lives outside the paths copied to
# the final stage, which would leave the venv's shebangs dangling.
RUN UV_PROJECT_ENVIRONMENT=/opt/barnaba/.venv uv sync --locked --no-dev --no-managed-python

FROM ${CLI2REST_BASE}

COPY --from=builder /opt/barnaba/.venv /opt/barnaba/.venv

ENV PATH="/opt/barnaba/.venv/bin:/app/.venv/bin:$PATH"

WORKDIR /app
