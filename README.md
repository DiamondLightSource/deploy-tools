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
schema_folder = /path/to/schema/folder

# Generate the schema for configuration yaml files
deploy-tools schema $schema_folder

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

## Glossary

See the Deployment Steps above for an overview of the primary stages of a deployment.

|**Term**           |**Definition**                                                                                                                                                                                                                                                                                              |
|-------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|Environment Modules|A [standard package for Linux](https://modules.readthedocs.io/en/latest/) that provides definitions for loading and unloading 'Environment Modules'. Note that while we are using this system, our definition of Module is separate. If we are referring to an Environment Module, we will use the full name|
|Modulefile         |Used by the Environment Modules package to specify all details of an Environment Module. This can include executables to add to the path, environment variables to set, etc.                                                                                                                                |
|Deployment         |The sum total of all Releases (deprecated or not) that are to be maintained in the Deployment Area                                                                                                                                                                                                          |
|Module             |A set of files that can be used to provide applications on your path, provide configuration, and set environment variables. We do this using the Environment Modules system by providing a Modulefile with the relevant configuration                                                                       |
|Release (noun)     |A Module, including version, alongside its lifecycle (i.e. deprecation) status                                                                                                                                                                                                                              |
|Application        |Each Module can be configured with multiple Applications, each one providing one or more executables. There are 3 types of Application: `Apptainer` (an executable container image), `Shell` (a Bash script) and `Binary` (an executable downloaded from a URL and verified against a hash)                                                                                                                |
|Deployment Area    |The top-level location where all Modules are to be deployed. This is typically a shared filesystem location for general use by multiple people. Note that there are several subdirectories which are used by `deploy-tools` for different purposes                                                          |
|(Area) Root        |Refers to the filesystem path at the root of the given Area.                                                                                                                                                                                                                                                |
|Deployment Step    |Refers to one of the primary steps that make up the Deployment process. See the section 'Deployment Steps' above for a breakdown                                                                                                                                                                            |
|Build Area         |The filesystem location used for building modules. This should ideally be on the same filesystem as the Deployment area to ensure that later move operations are atomic, so by default it is the `build` subdirectory of the Deployment Root. We use a different location when testing builds               |
|Modules Area       |Refers to the `modules` folder under the Deployment Root. The final location for files built for a particular Module configuration                                                                                                                                                                          |
|Modulefiles Folder |Refers to the `modulefiles` folder under the Deployment Root. When this path is added to the MODULEPATH environment variable, all modulefiles can then be accessed by the End User using the standard Environment Modules interface (`module avail`, etc.)                                                  |
|Deprecate          |Moving a modulefile to the separate Deprecated Folder, to indicate that its use should be discouraged                                                                                                                                                                                                       |
|Deprecated Folder  |The folder used to contain Modulefiles for Modules that have been deprecated. By adding the modulefiles subdirectory to your MODULEPATH environment variable, you then have the ability to use any deprecated Module as normal.                                                                             |
|End User           |Refers to anybody who is intending to make use of a deployed Module. This can include the people modifying configuration themselves                                                                                                                                                                         |

<!-- README only content. Anything below this line won't be included in index.md -->

See https://diamondlightsource.github.io/deploy-tools for more detailed documentation.
