# Regenerate the JSON schemas

The JSON schema files under `src/deploy_tools/models/schemas` are generated from the
Pydantic models in `src/deploy_tools/models` by
`deploy_tools.models.schema.generate_schema`. They are checked in and do not update
automatically, so they must be regenerated and committed after changing any model.

A `generate-schema` pre-commit hook does this for you: when you commit a change to
any file under `src/deploy_tools/models`, it regenerates the schemas. If they changed,
pre-commit reports the modified files and aborts the commit, so you just `git add` the
schemas and commit again.

If you bypass the hooks (for example with `git commit --no-verify`), regenerate the
schemas manually. The simplest way is the **Generate Schema** VSCode task (see
[the VSCode tasks guide](vscode-tasks.md#running-a-task)), which writes to the correct location.
Equivalently, run the CLI, pointing it at that folder:

```bash
deploy-tools schema src/deploy_tools/models/schemas
```

Either way, commit the regenerated files alongside your model change. CI fails if they
are out of date.
