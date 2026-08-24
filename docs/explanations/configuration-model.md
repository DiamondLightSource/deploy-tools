# The configuration model

This page is for anyone writing or editing deployment configuration. It explains how the
files you author are structured — the objects they map to and how they nest. For every
field in exhaustive detail see the [schema reference](../schemas.md); for the meaning of
individual terms, the [glossary](../glossary.md).

## What you author

You author two kinds of file: a single `settings.yaml`, and one `<name>/<version>.yaml`
per Module version. The [schema reference](../schemas.md) covers which schema validates
which and how to point your editor at them.

They are structured as follows:

```text
settings.yaml
  └── default_versions

<name>/<version>.yaml               one file per Module version
  ├── deprecated: false             lifecycle flag
  └── module
      ├── name                      Module name
      ├── version                   Module version
      ├── description               shown by `module whatis`
      ├── env_vars                  variables set on load
      ├── dependencies              other Modules to load first
      └── applications              one or more, each with an app_type of:
          ├── apptainer             container image + entrypoints
          ├── shell                 a bash script
          └── binary                a downloaded, hash-checked executable
```

Those last three are the values `app_type` can take rather than fields of their own —
see [the three application types](#the-three-application-types) below.

## A Module

A Module is the unit an end user loads. Alongside its `name` and `version` it carries:

| Field | Purpose |
|-------|---------|
| `description` | Shown by `module whatis <name>`. |
| `env_vars` | Environment variables set when the Module is loaded. |
| `dependencies` | Other Modules loaded first, optionally version-pinned. |
| `applications` | One or more applications providing the executables (below). |
| `allow_updates` | Permit in-place changes to this version — see [the guard rails](deprecation-lifecycle.md#the-guard-rails). |
| `exclude_from_defaults` | Keep this version out of automatic default selection — see [default versions](default-versions.md#excluding-a-version-from-the-automatic-default). |

`load_script` and `unload_script` run extra commands when the Module is loaded and
unloaded respectively, injected raw into the generated Modulefile. They are an advanced
escape hatch — check with a `deploy-tools` admin before using them.

Each per-version file also carries a `deprecated` flag; see
[the release lifecycle](deprecation-lifecycle.md).

## The three application types

Every entry under `applications` sets `app_type` to select one of three kinds; a single
Module can mix them.

| `app_type` | Provides | Key fields |
|------------|----------|------------|
| `apptainer` | Commands that run inside a container image | `container`, `entrypoints`, `global_options` |
| `shell` | A single executable running a bash script | `name`, `script` |
| `binary` | A downloaded executable added to the path | `name`, `url`, `hash`, `hash_type` |

The demo `example-module-apps` Module combines an Apptainer app with a Shell app:

```{literalinclude} ../../src/deploy_tools/demo_configuration/example-module-apps/0.1.yaml
:language: yaml
:lines: 3-
```

**Apptainer** uses one container image with one or more `entrypoints`, each mapping an
executable name to a command run inside the container. Options — container `mounts`,
`command_args`, `apptainer_args`, `host_binaries` — can be set per entrypoint or shared
across all of them via `global_options`.

**Shell** exposes a single executable (`name`) that runs the `script` list as bash.

**Binary** downloads `url`, checks it against `hash` using `hash_type` (`sha256`,
`sha512`, `md5`, or `none` to skip the check), and adds the executable to the path as
`name`. The demo `argocd` Module uses one:

```{literalinclude} ../../src/deploy_tools/demo_configuration/argocd/v2.14.10.yaml
:language: yaml
:lines: 3-
```

## Settings

`settings.yaml` holds deployment-wide settings. It currently has a single field,
`default_versions`, mapping a Module name to the version handed to `module load <name>`
when no version is given:

```{literalinclude} ../../src/deploy_tools/demo_configuration/settings.yaml
:language: yaml
:lines: 3-
```

How that choice is resolved — and how to keep a version out of automatic selection — is
covered in [default version resolution](default-versions.md).
