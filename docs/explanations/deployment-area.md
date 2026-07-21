# The deployment area

The *deployment area* is the directory tree that `deploy-tools` writes into. It is normally
a shared filesystem location that end users put on their `MODULEPATH`, so its layout is
important to the end user. This page explains what lives where, and why.

## Layout

Everything below is created and maintained by `deploy-tools`; nothing in the area is meant
to be edited by hand.

```text
<deployment root>/
├── deployment.yaml          # snapshot of the deployed configuration
├── modules/                 # Modules Area — the built files for every Module
│   └── <name>/<version>/
│       ├── modulefile        # the Environment Modules (Tcl) file
│       ├── entrypoints/      # the executables added to PATH on module load
│       ├── module.yaml       # this Module's configuration snapshot
│       └── sif_files/        # Apptainer images, when the Module uses any
├── modulefiles/             # Modulefiles Folder — placed on MODULEPATH
│   └── <name>/
│       ├── <version>         # symlink → ../../modules/<name>/<version>/modulefile
│       └── .version          # records the default version (see below)
├── deprecated/
│   └── modulefiles/         # Deprecated Folder — optionally on MODULEPATH
│       └── <name>/<version>  # symlink for a deprecated Module version
└── build/                   # transient build area (default location)
```

The split between the **Modules Area** (`modules/`) and the **Modulefiles Folder**
(`modulefiles/`) is the central design choice. The Modules Area holds the real files for
*every* version that has been deployed and not removed, both live and deprecated. The
Modulefiles Folder holds only a thin tree of symlinks, one per version, pointing at the
corresponding `modulefile`. Users put only the *modulefiles* directories on their
`MODULEPATH`, making each Module visible to `module avail` and `module load`.

Deprecation is therefore cheap and reversible: the built files never move, only the symlink
moves between `modulefiles/` and `deprecated/modulefiles/`. See
[the release lifecycle](deprecation-lifecycle.md) for the full set of transitions.

## The build area

Modules are first assembled under the **build area** (`build/` by default), then moved into
the Modules Area. The move is a filesystem `rename`, which is atomic *only when source and
destination are on the same filesystem* — hence the default build area sits inside the
deployment root. Building and deploying separately means a half-built Module is never
visible: either the rename succeeds and the whole version appears, or nothing changes.

The transient `build/` directory and the large Apptainer `sif_files/` images are
deliberately kept out of the deployment area's git history (see
[snapshots and the compare safety net](snapshots-and-compare.md)). They are reference-only
data used by the `compare` command, not something to revert to.

## Why modulefiles embed absolute paths

A generated `modulefile` adds its Module's executables to the user's path with one line:

```tcl
prepend-path PATH "<deployment root>/modules/<name>/<version>/entrypoints"
```

That path is **absolute**, so a deployment area cannot be relocated after the fact.
This is a deliberate trade-off.

A path relative to the modulefile does not work. Environment Modules sources the file
*through the symlink* under `modulefiles/` without resolving it first (`[info script]`
/ `ModulesCurrentModulefile` report the link path). A relative path would be interpreted
relative to the *link's* location — which changes when a Module is deprecated and the link
moves to a different location in the tree, silently breaking it.

This allows us to use two separate `modulefiles/` folders, corresponding to live and
deprecated modules, without needing to edit modulefiles after initial creation.
