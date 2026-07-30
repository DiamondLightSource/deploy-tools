# Regenerate the JSON schemas

The JSON schema files under `src/deploy_tools/models/schemas` are generated from the
Pydantic models in `src/deploy_tools/models` by
`deploy_tools.models.schema.generate_schema`. They are checked in and do not update
automatically, so after changing any model you must regenerate and commit them.

The simplest way is the **Generate Schema** VSCode task (see
[the VSCode tasks guide](vscode-tasks.md)), which writes to the correct location.
Equivalently, run the CLI, pointing it at that folder:

```bash
deploy-tools schema src/deploy_tools/models/schemas
```

Commit the regenerated files alongside your model change.
