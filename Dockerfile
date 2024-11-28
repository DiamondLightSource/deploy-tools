# The devcontainer should use the developer target and run as root with podman
# or docker with user namespaces.
ARG PYTHON_VERSION=3.12
FROM python:${PYTHON_VERSION} AS developer

# Add any system dependencies for the developer/build environment here
RUN apt-get update && apt-get install -y --no-install-recommends \
    graphviz environment-modules wget \
    && cd /tmp \
    && wget https://github.com/apptainer/apptainer/releases/download/v1.3.3/apptainer_1.3.3_amd64.deb \
    && apt install -y ./apptainer_1.3.3_amd64.deb \
    && rm -rf /var/lib/apt/lists/*

# Set up a virtual environment and put it in PATH
RUN python -m venv /venv
ENV PATH=/venv/bin:$PATH

# The build stage installs the context into the venv
FROM developer AS build
COPY . /context
WORKDIR /context
RUN touch dev-requirements.txt && pip install -c dev-requirements.txt .

FROM build AS runtime
# Add apt-get system dependecies for runtime here if needed

ENTRYPOINT ["deploy-tools"]
CMD ["--version"]
