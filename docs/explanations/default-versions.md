# Default version resolution

When a user runs `module load <name>` without a version, Environment Modules must pick
one. By default it picks the lexically last version, which is often wrong: `1.10` sorts
before `1.9`, and an unfinished alpha might also win. `deploy-tools` allows you to make
an explicit choice, and otherwise uses the `natsort` library for a more reasonable default.

## Every Module has a specific default configured

For every live module name, `deploy-tools` writes a `.version` file next to its modulefile
links (`modulefiles/<name>/.version`) with a single `set ModulesVersion <version>` line.
It is written whether or not the configuration names a default, so Environment Modules never
guesses.

The version it records is resolved as follows:

1. **An explicit default has priority.** If `settings.default_versions` names a version,
   it is used. It must be a live (non-deprecated) version that exists, or validation fails.
2. **Otherwise the highest eligible version is chosen automatically**, by natural version
   sorting (see below), considering only versions *not* marked `exclude_from_defaults`.

Deprecated versions are never candidates and never get a `.version` file.

## Natural version sorting

Automatic selection uses [`natsort`](https://natsort.readthedocs.io) rather than plain
string comparison, so `1.10` sorts after `1.9`. It also uses natsort's key for
pre-release schemes, so pre-release tags sort *before* the release they lead up to:

```text
1.2alpha1  <  1.2rc1  <  1.2  <  1.2.1
```

So publishing `1.2rc1` does not make it the default while `1.2` exists, and publishing
`1.2` makes it the default over its own release candidates. Be aware that `1.3alpha1` still
sorts after `1.2.1`, however; to keep alphas or similar out of the automatic default, mark
them `exclude_from_defaults: true`.

## Excluding a version from the automatic default

Marking a version `exclude_from_defaults: true` keeps it out of *automatic* selection
while still allowing it to be set explicitly. Use this to publish an alpha or beta that
users can opt into with `module load <name>/<version>` without it ever being handed to
someone who just typed `module load <name>`.

One safety check applies: if *every* version of a name is excluded and no explicit default
is given, validation fails rather than leave the Module with no default. Either give an
explicit default or keep at least one non-excluded version.
