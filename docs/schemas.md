# JSON Schema files

These JSON schema files are generated from the Pydantic models in
`src/deploy_tools/models`. The YAML language server and other tooling use them to validate
deployment configuration files. This section links to per-schema reference pages that
render each schema and list its properties.

## Which file uses which schema

You author two kinds of configuration file, each validated against a different schema:

| Configuration file | Schema | Pydantic model |
|--------------------|--------|----------------|
| `settings.yaml` (one per config folder) | `deployment-settings.json` | `DeploymentSettings` |
| `<name>/<version>.yaml` (one per Module version) | `release.json` | `Release` |

Per-version files sit in a folder named after the Module, so the path is
`<config folder>/<name>/<version>.yaml` (folder = Module `name`, filename = `version`).
Add a `yaml-language-server` comment pointing at the matching schema so your editor
validates each file as you type.

The other two generated schemas cover files you don't normally author by hand:
`deployment.json` (the `deployment.yaml` snapshot written by `sync`) and `module.json`
(the `Module` that a `Release` wraps).

## Schema pages

```{toctree}
:maxdepth: 1

schemas/deployment-settings
schemas/release
```

## How the schemas are generated

`deploy_tools.models.schema.generate_schema` writes these files from the corresponding
Pydantic models. To regenerate them manually:

```bash
deploy-tools schema path/to/output/folder
```
