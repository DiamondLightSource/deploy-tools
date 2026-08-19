# Glossary

See [the deployment process](explanations/deployment-steps.md) for an overview of the
primary stages of a deployment, and [the deployment area](explanations/deployment-area.md)
for the on-disk layout these terms refer to.

| Term | Definition |
|------|------------|
| Environment Modules | A [standard package for Linux](https://modules.readthedocs.io/en/latest/) that provides the commands for loading and unloading 'Environment Modules' (each defined by a Modulefile). Note that while we are using this system, our definition of Module is separate. If we are referring to an Environment Module, we will use the full name. |
| Modulefile | Used by the Environment Modules package to specify all details of an Environment Module. This can include executables to add to the path, environment variables to set, etc. |
| Module | A set of files that can be used to provide applications on your path, provide configuration, and set environment variables. We do this using the Environment Modules system by providing a Modulefile with the relevant configuration. |
| Application | Each Module can be configured with multiple Applications, each one providing one or more executables. There are 3 types of Application: `Apptainer` (an executable container image), `Shell` (a Bash script) and `Binary` (an executable downloaded from a URL and verified against a hash). See [the configuration model](explanations/configuration-model.md). |
| Release (noun) | A Module, including version, alongside its [lifecycle](explanations/deprecation-lifecycle.md) (i.e. deprecation) status. |
| Deployment | The declared configuration for a Deployment Area: all Releases (deprecated or not) to be maintained there, plus global settings. Written to the `deployment.yaml` snapshot by `sync`. The act of deploying is written lowercase. |
| Deployment Step | Refers to one of the primary steps that make up the deployment process. See [the deployment process](explanations/deployment-steps.md) for a breakdown. |
| End User | Refers to anybody who is intending to make use of a deployed Module. This can include the people modifying configuration themselves. |
| Area | One of the filesystem locations that `deploy-tools` manages for a distinct purpose: the Deployment, Build, Modules, Modulefiles and Deprecated Areas. Lowercase "folder" is used in its plain sense for any other directory, such as the config folder or a Module's entrypoints folder. |
| (Area) Root | Refers to the filesystem path at the root of the given Area; e.g. the Deployment Root is the root of the Deployment Area. |
| Deployment Area | The top-level location where all Modules are to be deployed. This is typically a shared filesystem location for general use by multiple people. Note that there are several subdirectories which are used by `deploy-tools` for different purposes. |
| Build Area | The filesystem location used for building modules. This should ideally be on the same filesystem as the Deployment Area to ensure that later move operations are atomic, so by default it is the `build` subdirectory of the Deployment Root. We use a different location when testing builds. |
| Modules Area | Refers to the `modules` folder under the Deployment Root. The final location for files built for a particular Module configuration. |
| Modulefiles Area | Refers to the `modulefiles` folder under the Deployment Root. When this path is added to the MODULEPATH environment variable, all live (non-deprecated) Modules can then be accessed by the End User using the standard Environment Modules interface (`module avail`, etc.). Deprecated Modules live in the separate Deprecated Area. |
| Deprecate | Moving a modulefile into the Deprecated Area, to indicate that its use should be discouraged. See [the release lifecycle](explanations/deprecation-lifecycle.md). |
| Deprecated Area | Refers to the `deprecated` folder under the Deployment Root, which holds its own `modulefiles` folder mirroring the Modulefiles Area. By adding that `deprecated/modulefiles` path to your MODULEPATH environment variable, you then have the ability to use any deprecated Module as normal. |
