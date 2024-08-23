[![CI](https://github.com/MJGaughran/deploytools/actions/workflows/ci.yml/badge.svg)](https://github.com/MJGaughran/deploytools/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/MJGaughran/deploytools/branch/main/graph/badge.svg)](https://codecov.io/gh/MJGaughran/deploytools)
[![PyPI](https://img.shields.io/pypi/v/deploytools.svg)](https://pypi.org/project/deploytools)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

# deploytools

A set of tools used for deploying applications to a shared filesystem.

This is used for deploying containerised desktop applications to many users who have
access to a shared filesystem.

Source          | <https://github.com/MJGaughran/deploytools>
:---:           | :---:
PyPI            | `pip install deploytools`
Releases        | <https://github.com/MJGaughran/deploytools/releases>

The demo_configuration folder can be passed as the config_folder to the deploytools
commands. The deployment_root just needs to be a writeable location for all files to get
deployed under.

VSCode configuration has been added to perform the primary functions using defaults that
reference locations in the VSCode dev container.

An additional 'Clean deployment' task has been provided to set up the deployment_root
correctly. For the moment, this will output everything to a 'demo-output' folder.

```
deployment_root = /path/to/deployment/root
config_folder = /path/to/config/folder
schema_folder = /path/to/schema/folder

# Generate the schema for configuration yaml files
python -m deploytools schema $schema_folder

# Validate the deployment configuration files, also ensuring that the required updates
# are compatible with the previous deployments.
python -m deploytools validate $deployment_root $config_folder

# Synchronise the deployment area with the configuration files. This will first run
# validation
python -m deploytools sync $deployment_root $config_folder

```
