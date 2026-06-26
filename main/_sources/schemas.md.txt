# JSON Schema files

These JSON schema files are generated from the Pydantic models in `src/deploy_tools/models`.

They are used by the YAML language server and other tooling to validate deployment configuration files.

This section links to per-schema reference pages which render the schema and list the individual
properties as tables.

## Schema pages

```{toctree}
:maxdepth: 1

schemas/deployment-settings
schemas/release
```

## How the schemas are generated

The `deploy_tools.models.schema.generate_schema` function writes these files from the corresponding Pydantic models.

To regenerate them manually:

```bash
deploy-tools schema path/to/output/folder
```
