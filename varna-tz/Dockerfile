FROM maven:3.9-eclipse-temurin-17 AS builder

WORKDIR /build

ARG VARNA_TZ_VERSION=1.3.0

RUN git clone https://github.com/tzok/varna-tz.git . \
 && git checkout tags/${VARNA_TZ_VERSION} \
 && mvn package -DskipTests

#######################################

FROM ghcr.io/tzok/cli2rest:latest

RUN apt-get update -y \
 && apt-get install -y --no-install-recommends \
      librsvg2-bin \
      openjdk-21-jre-headless \
 && rm -rf /var/lib/apt/lists/*

ARG SVGCLEANER_VERSION=0.9.5

ADD https://github.com/RazrFalcon/svgcleaner/releases/download/v${SVGCLEANER_VERSION}/svgcleaner_linux_x86_64_${SVGCLEANER_VERSION}.tar.gz /usr/local/bin

COPY --from=builder /build/target/varna-tz-*.jar /varna-tz.jar

COPY wrapper.sh /usr/local/bin/wrapper.sh
RUN chmod +x /usr/local/bin/wrapper.sh
