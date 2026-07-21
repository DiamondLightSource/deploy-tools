# Run the VSCode tasks and debug configurations

The repository ships with [VSCode tasks](https://code.visualstudio.com/docs/editor/tasks)
and [debug launch configurations](https://code.visualstudio.com/docs/editor/debugging)
so that contributors can exercise the `deploy-tools` CLI without typing out full
commands. They run the same subcommands documented in the [CLI reference](../cli.md),
pre-filled to operate on the bundled `demo_configuration`.

## The demo configuration

`src/deploy_tools/demo_configuration/` holds a small, self-contained set of module
definitions used as sample input. The tasks default to reading this configuration and
writing the generated deployment to `demo-output/`, giving you a realistic deployment to
inspect without needing a real configuration repository.

## Running a task

Open the command palette and choose **Tasks: Run Task**, then pick one of:

- **Tests, lint and docs** — run `tox -p` (type checking, tests, and the docs build).
- **Generate schema** — regenerate the JSON schemas under `models/schemas/`.
- **Sync modules** — build and deploy the demo configuration into `demo-output/`.
- **Clean deployment** — empty and recreate `demo-output/`.
- **Validate deployment** — preview the changes a sync would make (read-only).
- **Compare deployment to snapshot** — diff the deployment against a previous snapshot.
- **Recreate tests sample output from demo_configuration** — regenerate the golden-master
  test samples via `tests/generate_samples.sh`.

Tasks that take flags (such as `--allow-all`, `--from-scratch`, or the compare mode)
prompt for those options when run, defaulting to the most common choice.

## Debugging a command

The **Run and Debug** panel offers equivalent launch configurations (Debug Schema
Generation, Debug Validation, Debug Compare, Debug Sync, and Debug Unit Test). These
invoke the same commands under `debugpy` so you can set breakpoints and step through the
CLI while it processes the demo configuration.
