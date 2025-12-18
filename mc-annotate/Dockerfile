FROM debian:stable AS builder

RUN apt-get update -y \
 && apt-get install -y --no-install-recommends \
      unzip \
 && rm -rf /var/lib/apt/lists/*

ADD https://major.iric.ca/MajorLabEn/MC-Tools_files/MC-Annotate.zip /
RUN unzip /MC-Annotate.zip

#######################################

FROM ghcr.io/tzok/cli2rest:latest

COPY --from=builder /MC-Annotate /usr/local/bin/MC-Annotate

COPY wrapper.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/wrapper.sh
