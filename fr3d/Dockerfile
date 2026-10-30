ARG CLI2REST_BASE=ghcr.io/tzok/cli2rest:latest

FROM ${CLI2REST_BASE} AS builder

RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/fr3d

COPY pyproject.toml uv.lock ./

# --no-managed-python forces uv to use the base image interpreter instead of
# downloading one. A downloaded interpreter lives outside the paths copied to
# the final stage, which would leave the venv's shebangs dangling.
RUN UV_PROJECT_ENVIRONMENT=/opt/fr3d/.venv uv sync --locked --no-dev --no-managed-python

FROM ${CLI2REST_BASE}

COPY --from=builder /opt/fr3d/.venv /opt/fr3d/.venv

ENV PATH="/opt/fr3d/.venv/bin:/app/.venv/bin:$PATH"

WORKDIR /app

COPY wrapper.py /usr/local/bin/wrapper.py
RUN chmod +x /usr/local/bin/wrapper.py
