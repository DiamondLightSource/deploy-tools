[![CI](https://github.com/DiamondLightSource/deploy-tools/actions/workflows/ci.yml/badge.svg)](https://github.com/DiamondLightSource/deploy-tools/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/DiamondLightSource/deploy-tools/branch/main/graph/badge.svg)](https://codecov.io/gh/DiamondLightSource/deploy-tools)
[![PyPI](https://img.shields.io/pypi/v/dls-deploy-tools.svg)](https://pypi.org/project/dls-deploy-tools)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0)

# deploy_tools

A set of tools used for deploying applications to a shared filesystem.

This is used for deploying containerised desktop applications to many users who have
access to a shared filesystem.

Source          | <https://github.com/DiamondLightSource/deploy-tools>
:---:           | :---:
PyPI            | `pip install dls-deploy-tools`
Docker          | `docker run ghcr.io/diamondlightsource/deploy-tools:latest`
Releases        | <https://github.com/DiamondLightSource/deploy-tools/releases>

The demo_configuration folder can be passed as the config_folder to the deploy-tools
commands. The deployment_root just needs to be a writeable location for all files to get
deployed under.

```
deployment_root = /path/to/deployment/root
config_folder = /path/to/config/folder
schema_folder = /path/to/schema/folder

# Generate the schema for configuration yaml files
python -m deploy_tools schema $schema_folder

# Validate the deployment configuration files, also ensuring that the required updates
# are compatible with the previous deployments.
python -m deploy_tools validate $deployment_root $config_folder

# Synchronise the deployment area with the configuration files. This will first run
# validation
python -m deploy_tools sync $deployment_root $config_folder

```

## VSCode Tasks and Debug Configuration

The following tasks are configured for VSCode, to allow for local testing of deploy-tools. These tasks (plus their default input) should create a separate `demo-output` folder at the top-level of the project folder. In addition, separate Debug configurations are also provided, corresponding to these same commands.

The equivalent CLI commands are included for reference, but it is recommended that you use `--help` to explore the commands, arguments and options in greater detail.

| **Name**                       | **CLI command**            | **Description**                                                                                                                                           |
|--------------------------------|----------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------|
| Generate Schema                | `deploy-tools schema`      | Generate the yaml schema (in .json format) for the top-level configuration files                                                                          |
| Clean deployment               | `rm -rf <Deployment Root>` | Wipe the deployment area local to your own checkout of deploy-tools, enabling you to test a deployment from scratch                                       |
| Sync Modules                   | `deploy-tools sync`        | Synchronise the Deployment configuration with the Deployment Area                                                                                         |
| Validate deployment            | `deploy-tools validate`    | Compare the new configuration with that previously used when deploying modules, and check that all expected Deploy operations are unlikely to fail        |
| Compare deployment to snapshot | `deploy-tools compare`     | Compare the configuration stored from the last Sync run, with the state of any deployed Modules. This may be useful in the event of a failed Sync process |

## Glossary

| **Term**            | **Definition**                                                                                                                                                                                                                                                                                               |
|---------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Environment Modules | A [standard package for Linux](https://modules.readthedocs.io/en/latest/) that provides definitions for loading and unloading 'Environment Modules'. Note that while we are using this system, our definition of Module is separate. If we are referring to an Environment Module, we will use the full name |
| Modulefile          | Used by the Environment Modules package to specify all details of an Environment Module. This can include executables to add to the path, environment variables to set, etc.                                                                                                                                 |
| Module              | A set of files that can be used to provide applications on your path, provide configuration, and set environment variables. We do this using the Environment Modules system by providing a Modulefile with the relevant configuration                                                                        |
| Application         | Each Module can be configured with multiple Applications, each one providing one or more executables. As of writing, there are 2 types of Application: `Apptainer` and `Shell` (Bash script)
| Deployment Area     | The filesystem location where all Modules are to be deployed. This is typically a shared filesystem location for general use by multiple people                                                                                                                                                              |
| Deployment Root     | Refers to the filesystem path at the root of the Deployment Area. The term 'Root' is used similarly for other directories                                                                                                                                                                                    |
| Build (verb)        | Generate entrypoint scripts, configuration files and environment variables for a given Module. These are output to the Build Area                                                                                                                                                                            |
| Build Area          | The filesystem location used for building modules. This should ideally be on the same filesystem as the Deployment area to ensure that later move operations are atomic, so by default it is the `build` subdirectory of the Deployment Root. We use a different location when testing builds                |
| Deploy              | Act of moving built Modules from the Build Area into the Modules Area. A copy of the modulefile is moved to either the Modulefiles Folder or Deprecated Folder, depending on its deprecation status. The Module can then be used by the End User                                                             |
| Modules Area        | Refers to the `modules` folder under the Deployment Root. The final location for files built for a particular Module configuration                                                                                                                                                                           |
| Modulefiles Folder  | Refers to the `modulefiles` folder under the Deployment Root. When this path is added to the MODULEPATH environment variable, all modulefiles can then be accessed by the End User using the standard Environment Modules interface (`module avail`, etc.)                                                   |
| Deprecate           | Moving a modulefile to the separate Deprecated Folder, to indicate that its use should be discouraged                                                                                                                                                                                                        |
| Deprecated Folder   | The folder used to contain Modulefiles for Modules that have been deprecated. By adding the modulefiles subdirectory to your MODULEPATH environment variable, you then have the ability to use any deprecated Module as normal. Where possible, the use of deprecated modules by the End User should be avoided               |
| Release (noun)      | A Module, including version, alongside its lifecycle (i.e. deprecation) status                                                                                                                                                                                                                               |
| Deployment          | The sum total of all releases (deprecated or not) that are to be maintained in the deployment area                                                                                                                                                                                                           |
| End User            | Refers to anybody who is intended to make use of a deployed Module. This can include the people modifying configuration themselves                                                                                                                                                                           |
