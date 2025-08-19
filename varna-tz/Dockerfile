# Build stage
FROM maven:3.9-eclipse-temurin-17 AS builder

ARG VARNA_TZ_VERSION=1.3.0
WORKDIR /build

# Clone the repository and checkout the specific version
RUN git clone https://github.com/tzok/varna-tz.git . \
 && git checkout tags/${VARNA_TZ_VERSION}

# Build the JAR file
# Skip tests as they might require extra setup or resources not needed for just the JAR
RUN mvn package -DskipTests

# ---

# Final stage
FROM ghcr.io/tzok/cli2rest:latest

ARG SVGCLEANER_VERSION=0.9.5

# Install necessary runtime dependencies
RUN apt-get update -y \
 && apt-get install -y --no-install-recommends \
      curl \
      librsvg2-bin \
      openjdk-21-jre-headless \
 && rm -rf /var/lib/apt/lists/*

# Copy the built JAR from the builder stage
COPY --from=builder /build/target/varna-tz-*.jar /varna-tz.jar

# Download and install svgcleaner
RUN curl -L https://github.com/RazrFalcon/svgcleaner/releases/download/v${SVGCLEANER_VERSION}/svgcleaner_linux_x86_64_${SVGCLEANER_VERSION}.tar.gz | tar xz -C /usr/local/bin \
 && chmod +x /usr/local/bin/svgcleaner

# Copy the wrapper script
COPY wrapper.sh /usr/local/bin/wrapper.sh
RUN chmod +x /usr/local/bin/wrapper.sh

# Make sure the installed binary and script are in the PATH
ENV PATH="/usr/local/bin:${PATH}"
