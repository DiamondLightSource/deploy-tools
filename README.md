[![CI](https://github.com/MJGaughran/deploytools/actions/workflows/ci.yml/badge.svg)](https://github.com/MJGaughran/deploytools/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/MJGaughran/deploytools/branch/main/graph/badge.svg)](https://codecov.io/gh/MJGaughran/deploytools)

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

# deploytools

A collection of tools used for deploying applications to the shared filesystem at
Diamond Light Source.

Source          | <https://github.com/MJGaughran/deploytools>
:---:           | :---:
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
