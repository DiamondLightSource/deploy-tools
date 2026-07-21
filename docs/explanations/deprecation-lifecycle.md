# The release lifecycle

A *Release* is a Module version plus one boolean: whether it is `deprecated`. The whole
lifecycle of a deployed Module — appearing, being updated, retired, restored, and finally
deleted — is expressed by adding or removing a Release in configuration and toggling its
`deprecated` flag. This page explains these transitions and the guard rails around them.

## Configuration is declarative

You never tell `deploy-tools` to "deprecate" or "remove" something directly. You describe
the set of Releases you want, and the tool compares that against the
[snapshot](snapshots-and-compare.md) of the last `sync` to derive the actions needed. Each
Release falls into one of these cases:

| Transition | Detected when… | Effect on the deployment area |
|------------|----------------|-------------------------------|
| **Add** | the name or version is not in the last snapshot | build the Module, create a live modulefile link |
| **Update** | the version exists but its Module config changed | rebuild in place (only if `allow_updates` is set) |
| **Deprecate** | the version was live in the last snapshot, now `deprecated: true` | move the modulefile link into `deprecated/modulefiles/` |
| **Restore** | was deprecated in the last snapshot, now `deprecated: false` | move the link back into `modulefiles/` |
| **Remove** | present in the last snapshot, absent from configuration | delete the modulefile link and the built files |

Deprecate and restore only move a symlink; the built files stay in the Modules Area (see
[the deployment area](deployment-area.md)). If your `MODULEPATH` includes
`deprecated/modulefiles`, a deprecated Module still loads as before — deprecation indicates
"you should stop using this", not "this is gone".

## The guard rails

Some transitions are blocked by default so mistakes aren't applied silently:

- **A new version may not be born deprecated.** Adding a Release with `deprecated: true`
  is rejected.
- **An existing version may not change without a new version.** If its configuration differs
  from the last snapshot, validation fails unless the Module sets `allow_updates: true`.
- **A live version may not be deleted directly.** Deprecate it in one `sync`, then
  remove it in a later one.

`--allow-all` lifts the first and third guards, so you can force those transitions. It does
*not* affect updates: changing a version always requires `allow_updates: true`.
`--from-scratch` implies `--allow-all`. Neither relaxes the integrity checks — the area
must still be healthy.
