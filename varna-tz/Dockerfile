FROM maven:3.9-eclipse-temurin-17 AS builder

ARG VARNA_TZ_VERSION=master

ADD https://github.com/tzok/varna-tz.git#${VARNA_TZ_VERSION} /varna-tz

RUN cd /varna-tz \
 && mvn clean package -DskipTests

ARG SVGCLEANER_VERSION=0.9.5

ADD https://github.com/RazrFalcon/svgcleaner/releases/download/v${SVGCLEANER_VERSION}/svgcleaner_linux_x86_64_${SVGCLEANER_VERSION}.tar.gz /
RUN tar xfz /svgcleaner_linux_x86_64_${SVGCLEANER_VERSION}.tar.gz -C /usr/local/bin

#######################################

FROM ghcr.io/tzok/cli2rest:latest

RUN apt-get update -y \
 && apt-get install -y --no-install-recommends \
      inkscape \
      openjdk-21-jre-headless \
 && rm -rf /var/lib/apt/lists/*

COPY --from=builder /varna-tz/target/varna-tz-*.jar /varna-tz.jar
COPY --from=builder /usr/local/bin/svgcleaner /usr/local/bin/svgcleaner

COPY wrapper.sh /usr/local/bin/wrapper.sh
RUN chmod +x /usr/local/bin/wrapper.sh
