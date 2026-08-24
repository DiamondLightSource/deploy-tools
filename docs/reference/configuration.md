# Configuration

This page is for anyone writing or editing deployment configuration. It documents every
field of the files you author and how they nest. The field tables are curated by hand
from the Pydantic models in `src/deploy_tools/models`, so a change to those models needs
a change here too; the [schema reference](../schemas.md) renders the same fields
mechanically from the generated JSON schemas. For the meaning of individual terms, see
the [glossary](../glossary.md).

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

A Module is the unit an end user loads. It carries:

| Field | Purpose |
|-------|---------|
| `name` | The name an end user loads it by. |
| `version` | The version an end user loads it by. |
| `description` | Shown by `module whatis <name>`. |
| `env_vars` | Environment variables set when the Module is loaded. |
| `dependencies` | Other Modules loaded first, optionally version-pinned. |
| `applications` | One or more applications providing the executables (below). |
| `load_script` | Extra commands run when the Module is loaded — see below. |
| `unload_script` | Extra commands run when the Module is unloaded — see below. |
| `allow_updates` | Permit in-place changes to this version — see [the guard rails](../explanations/deprecation-lifecycle.md#the-guard-rails). |
| `exclude_from_defaults` | Keep this version out of automatic default selection — see [default versions](../explanations/default-versions.md#excluding-a-version-from-the-automatic-default). |

**`env_vars`** — each entry is a name/value pair:

| Field | Purpose |
|-------|---------|
| `name` | The variable to set. |
| `value` | The value to set it to. |

**`dependencies`** — each entry names another Module:

| Field | Purpose |
|-------|---------|
| `name` | The Module to load first. |
| `version` | The version to pin to. If omitted, that Module's default version is resolved at load time. |

`load_script` and `unload_script` are injected raw into the generated Modulefile. They
are for advanced cases the other fields cannot cover — check with a `deploy-tools` admin
before using them.

Each per-version file also carries a `deprecated` flag; see
[the release lifecycle](../explanations/deprecation-lifecycle.md).

## The three application types

Every entry under `applications` sets `app_type` to select one of three kinds; a single
Module can mix them.

| `app_type` | Provides |
|------------|----------|
| `apptainer` | Commands that run inside a container image |
| `shell` | A single executable running a bash script |
| `binary` | A downloaded executable added to the path |

The demo `example-module-apps` Module combines an Apptainer app with a Shell app:

```{literalinclude} ../../src/deploy_tools/demo_configuration/example-module-apps/0.1.yaml
:language: yaml
:lines: 3-
```

### Apptainer

One container image with one or more entrypoints, each mapping an executable name to a
command run inside the container.

| Field | Purpose |
|-------|---------|
| `container` | The image to use (below). |
| `entrypoints` | The executables provided (below). |
| `global_options` | Options applied to every entrypoint. |

**`container`** — splits the image reference into `path:version`:

| Field | Purpose |
|-------|---------|
| `path` | The image URL, excluding the version or tag. `docker`, `shub`, `oras` and `https` schemes are accepted. |
| `version` | The image version or tag. |

**`entrypoints`** — each entry is one executable:

| Field | Purpose |
|-------|---------|
| `name` | The executable provided. |
| `command` | The command to run inside the container. Defaults to `name`. |
| `options` | Options applied to this entrypoint only. |

**`options` and `global_options`** — both take the same fields:

| Field | Purpose |
|-------|---------|
| `apptainer_args` | Arguments passed to Apptainer when launching the container. |
| `command_args` | Arguments passed to the command being run. |
| `mounts` | Mount points as `host_path[:container_path[:opts]]`, where `opts` is `ro` or `rw` (default `rw`). |
| `host_binaries` | Host binaries, found on the current `PATH`, to mount into the container at `/usr/bin/<name>`. |

### Shell

A single executable running a bash script.

| Field | Purpose |
|-------|---------|
| `name` | The executable provided. |
| `script` | The lines of bash it runs. |

### Binary

An executable downloaded, hash-checked and added to the path.

| Field | Purpose |
|-------|---------|
| `name` | The executable provided. |
| `url` | Where the binary is downloaded from. |
| `hash` | The expected hash of the download. |
| `hash_type` | `sha256`, `sha512`, `md5`, or `none` to skip the check. |

The demo `argocd` Module uses one:

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
covered in [default version resolution](../explanations/default-versions.md).
