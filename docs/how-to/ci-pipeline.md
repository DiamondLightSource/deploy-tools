# Drive deploy-tools from CI

In normal use, nobody should run `sync`, `validate` or `compare` by hand. Those commands
touch a shared deployment area, so they belong to a CI pipeline in the configuration
repository, gated by change review. End users only edit configuration and open a change;
merging it deploys.

This guide describes what that pipeline must do. It is deliberately independent of any
particular CI system — translate the responsibilities below into your own.

## On a proposed change

When someone opens a change (before it is merged), run, without altering the area:

- `deploy-tools compare <area>` — confirm the area still matches its last snapshot, so
  the change is being checked against a known-healthy baseline.
- `deploy-tools validate <area> <config>` — confirm the new configuration is valid and its
  [lifecycle transitions](../explanations/deprecation-lifecycle.md) are permitted. Add
  `--test-build` to build every changed Module in a temporary directory, catching build
  failures before merge.

This gives reviewers a green light that the change is deployable without changing anything
on the filesystem.

## On acceptance

When the change is merged to the main branch, deploy it:

- `deploy-tools compare <area>` — re-check the area is healthy immediately before the sync.
- `deploy-tools sync <area> <config>` — validate again, build, and move the results into
  place.

## Run one at a time

`deploy-tools` has no locking of its own. The pipeline must ensure only one run
touches the area at a time — two concurrent `sync`s, or a `sync` racing a `compare`,
can corrupt the area or report false drift. Serialise the relevant jobs (and, if
possible, restrict them to a single runner).

## Manual operations

Some tasks fall outside the automatic flows and are best run from a manually-triggered
pipeline, exposing the relevant options as parameters:

- **The first deployment.** A brand-new area has no snapshot to compare against, so it is
  run manually rather than triggered by a merge. Use `--from-scratch`, which assumes the
  area is empty: `compare --from-scratch` to confirm it, then `sync --from-scratch` to
  deploy. This
  path is walked through in [your first deployment](../tutorials/your-first-deployment.md).
- **Comparing against an earlier snapshot.** `compare --use-ref <ref>` compares the area
  against the snapshot from an earlier commit (e.g. `HEAD~1`), to check how it matches the
  configuration from before the last `sync`.
- **Forcing blocked transitions.** `--allow-all` (on `validate`/`sync`) permits lifecycle
  transitions that are otherwise rejected, such as removing a live version. The area must
  still be healthy.

See [snapshots and the compare safety net](../explanations/snapshots-and-compare.md) for
how these fit into recovery.
