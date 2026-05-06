FROM debian:stable AS builder

ARG MC_ANNOTATE_URL=https://major.iric.ca/MajorLabEn/MC-Tools_files/MC-Annotate.zip
ARG MC_ANNOTATE_SHA256

RUN apt-get update -y \
 && apt-get install -y --no-install-recommends \
      ca-certificates \
      curl \
      unzip \
 && rm -rf /var/lib/apt/lists/*

RUN test -n "$MC_ANNOTATE_SHA256" \
 && curl -fsSL "$MC_ANNOTATE_URL" -o /tmp/MC-Annotate.zip \
 && echo "$MC_ANNOTATE_SHA256  /tmp/MC-Annotate.zip" | sha256sum -c - \
 && unzip /tmp/MC-Annotate.zip

#######################################

ARG CLI2REST_BASE=ghcr.io/tzok/cli2rest:latest

FROM ${CLI2REST_BASE}

COPY --from=builder /MC-Annotate /usr/local/bin/MC-Annotate

COPY wrapper.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/wrapper.sh
