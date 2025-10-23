FROM ghcr.io/tzok/cli2rest:latest AS builder

ARG FR3D_BRANCH=latest

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      git \
 && rm -rf /var/lib/apt/lists/*

RUN echo "Cloning FR3D branch: ${FR3D_BRANCH}" && \
    git clone --branch ${FR3D_BRANCH} https://github.com/BGSU-RNA/fr3d-python.git

RUN cd fr3d-python \
 && . /opt/venv/bin/activate \
 && pip install --upgrade pip \
 && pip install .

#######################################

FROM ghcr.io/tzok/cli2rest:latest

ARG FR3D_BRANCH=latest

COPY --from=builder /opt/venv /opt/venv

# Create a script to run FR3D
COPY wrapper.py /usr/local/bin/wrapper.py
RUN chmod +x /usr/local/bin/wrapper.py

# Make sure the installed binary is in the PATH
ENV PATH="/usr/local/bin:${PATH}"

LABEL fr3d.version=${FR3D_BRANCH}
