[![CI](https://github.com/DiamondLightSource/deploy-tools/actions/workflows/ci.yml/badge.svg)](https://github.com/DiamondLightSource/deploy-tools/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/DiamondLightSource/deploy-tools/branch/main/graph/badge.svg)](https://codecov.io/gh/DiamondLightSource/deploy-tools)
[![PyPI](https://img.shields.io/pypi/v/dls-deploy-tools.svg)](https://pypi.org/project/dls-deploy-tools)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0)

# deploy_tools

A set of tools used for deploying applications to a shared filesystem.

This is used for deploying containerised desktop applications to many users who have
access to a shared filesystem. We use the
[Environment Modules](https://modules.readthedocs.io/en/latest/) package to make these
applications available to the end user.

What            | Where
:---:           | :---:
Source          | <https://github.com/DiamondLightSource/deploy-tools>
PyPI            | `pip install dls-deploy-tools`
Docker          | `docker run ghcr.io/diamondlightsource/deploy-tools:latest`
Documentation   | <https://diamondlightsource.github.io/deploy-tools>
Releases        | <https://github.com/DiamondLightSource/deploy-tools/releases>

The demo_configuration folder in this repository can be passed as the config_folder to
the deploy-tools commands. The deployment_root needs to be a writeable location for all
files to get deployed under.

The examples below use the `deploy-tools` console script; `python -m deploy_tools` is
equivalent if you prefer to invoke the module directly.

```
deployment_root = /path/to/deployment/root
config_folder = /path/to/config/folder

# Validate the deployment configuration files, also ensuring that the required updates
# are compatible with the previous deployments.
deploy-tools validate $deployment_root $config_folder

# Synchronise the deployment area with the configuration files. This will first run
# validation as part of determining the required changes
deploy-tools sync $deployment_root $config_folder

# Compare the current deployment snapshot against what is actually deployed in the
# deployment area. CI/CD should run this before a deploy to confirm a healthy state.
deploy-tools compare $deployment_root

```

Generating the JSON schema files with `deploy-tools schema <folder>` is a separate,
occasional task: it produces the schemas that editors use to validate configuration files,
and is not part of a deployment. See the schema reference in the documentation.

<!-- README only content. Anything below this line won't be included in index.md -->

See https://diamondlightsource.github.io/deploy-tools for more detailed documentation.
