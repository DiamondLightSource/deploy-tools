# The deployment process

A deployment is made up of several conceptual **steps**, deliberately **not** one-to-one
with the CLI commands: one command may run several steps, and some are never exposed as
a command of their own. For the commands themselves see the [CLI reference](../cli.md).

| Step | Description | Run by |
|------|-------------|--------|
| Compare | Compare the current deployment snapshot against the modulefiles and built modules that actually exist, confirming the [deployment area](deployment-area.md) is healthy. | `compare` |
| Validate | Diff the new configuration against the current snapshot to determine the set of actions to take, and check those actions are permitted by the [release lifecycle](deprecation-lifecycle.md). | `validate`, `sync` |
| Build | Generate entrypoint scripts, configuration files and environment variables for each changed Module, writing them to the build area. | `sync` (`validate --test-build`) |
| Deploy | Move the built Modules from the build area into the Modules Area, link each modulefile into the live or deprecated tree according to its status, and update default versions. | `sync` |

## Why build and deploy are not separate commands

There is no standalone `build` or `deploy` command. `sync` always runs them together, so
a half-built Module is never exposed to users: either a version is built *and* linked into
place, or nothing changes.

## How the steps fit together

`sync` is the only step that writes to the deployment area; `compare` and `validate` are
read-only checks run before it. See
[snapshots and the compare safety net](snapshots-and-compare.md) for how the snapshot
ties them together, and [drive deploy-tools from CI](../how-to/ci-pipeline.md) for the
order a pipeline runs them in.
