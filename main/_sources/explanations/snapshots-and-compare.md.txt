# Snapshots and the compare safety net

`deploy-tools` has no transactional rollback. Instead it relies on a *snapshot* of the
intended configuration plus a `compare` command that detects when reality has drifted from
it. This page explains how the two fit together.

## What the snapshot is

The snapshot is a single file, `deployment.yaml`, at the root of the deployment area.
It is a serialised [`Deployment`](../schemas.md) — the complete set of Releases
(live and deprecated) plus the settings, including each Module's default version. It
records what the deployment area is supposed to contain.

The `sync` command writes it; `sync`, `validate` and `compare` read it back to work out
what has changed since the last `sync`.

## Why it is written *before* the deploy

During a `sync`, the snapshot is written **before** the files are moved into place. This
means the snapshot always describes the *target* state. If the deploy step then fails part
way through, the snapshot and the actual files no longer agree, and the next `compare`
reports that discrepancy. Were the snapshot written last, a deploy that died before making
any changes could result in `compare` identifying a broken area as healthy.

## How compare works

It reconstructs the de-facto `Deployment` by walking the deployment area — reading every
`module.yaml`, checking which versions have a live versus a deprecated modulefile link,
and reading each `.version` file — then diffs that against the snapshot. Any mismatch (a
missing modulefile, a built module with no link, a wrong default version, a corrupt
metadata file) is raised as a clear error showing the differing lines.

`compare` checks the area's *structure* — the modulefiles, links and metadata whose
breakage would disable many Modules at once. It does not inspect the contents of large
built files such as Apptainer `.sif` images, so a corrupted `.sif` in the correct location
will not be detected. The risk of corruption is avoided at build time instead: a Module
is built on the same filesystem as the deployment area and published by a single atomic
rename, so a partial or failed build (including `.sif` files) is never moved into place.

This is why CI should run `compare` *before* every `sync`: it confirms the area is in the
healthy state the last `sync` claimed to leave it in.

## Recovery is manual

With no automatic rollback, recovering from a failed `sync` is an administrator task: use
`compare` to see what differs, repair the area by hand (or restore the previous snapshot),
and re-run `compare` before another `sync`. Automatic self-healing was rejected to keep
the tool simple for a small development team.

Two facilities help here:

- `compare --use-ref <ref>` compares the area against the snapshot stored at a previous
  git commit of the deployment area (e.g. `HEAD~1`); each `sync` commits its snapshot.
  This is helpful when attempting to fix a broken deployment area, as it is
  often easier to rollback the configuration to a previous state rather than fix the
  latest deployment.
- `compare --from-scratch` asserts only that the deployment root exists and is *empty* —
  this is the check to run in CI before the very first `sync`, when no snapshot exists yet.

The git repository in the deployment area exists only to give `compare --use-ref` this
reference point. It deliberately excludes the build area and Apptainer images, and is
**not** intended for reverting the area's state.

Otherwise, it is expected that the deployment area is properly backed up, preferably with
some kind of filesystem-level snapshot system.
