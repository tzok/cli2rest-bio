# Start from the specified base image
FROM ghcr.io/tzok/cli2rest:latest

ARG VARNA_TZ_VERSION=1.3.0
ARG SVGCLEANER_VERSION=0.9.5

# Install necessary build dependencies
RUN apt-get update -y \
 && apt-get install -y \
      curl \
      librsvg2-bin \
      openjdk-17-jre \
 && rm -rf /var/lib/apt/lists/*

# Download varna-tz JAR as /varna-tz.jar
RUN curl -L -o /varna-tz.jar https://github.com/tzok/varna-tz/releases/download/${VARNA_TZ_VERSION}/varna-tz-${VARNA_TZ_VERSION}.jar

# Download and install svgcleaner
RUN curl -L https://github.com/RazrFalcon/svgcleaner/releases/download/v${SVGCLEANER_VERSION}/svgcleaner_linux_x86_64_${SVGCLEANER_VERSION}.tar.gz | tar xz -C /usr/local/bin

# Copy the wrapper scripts
COPY wrapper.sh /usr/local/bin/wrapper.sh
RUN chmod +x /usr/local/bin/wrapper.sh

# Make sure the installed binary and script are in the PATH
# (pip install usually handles this, but ensure /usr/local/bin or similar is in PATH)
ENV PATH="/usr/local/bin:${PATH}"
