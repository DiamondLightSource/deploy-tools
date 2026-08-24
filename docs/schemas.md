# JSON Schema files

These JSON schema files are generated from the Pydantic models in
`src/deploy_tools/models`. The YAML language server and other tooling use them to validate
deployment configuration files. This page covers which file each schema validates and how
to point your editor at it.

To look a field up, use [the configuration model](reference/configuration-model.md) — it
documents the same fields in a form meant for reading. The
[schema pages](#schema-pages) below render each schema mechanically, so they are the
exhaustive detail rather than the place to start.

## Which file uses which schema

You author two kinds of configuration file, each validated against a different schema:

| Configuration file | Schema | Pydantic model |
|--------------------|--------|----------------|
| `settings.yaml` (one per config folder) | `deployment-settings.json` | `DeploymentSettings` |
| `<name>/<version>.yaml` (one per Module version) | `release.json` | `Release` |

Per-version files sit in a folder named after the Module, so the path is
`<config folder>/<name>/<version>.yaml` (folder = Module `name`, filename = `version`).
Add a `yaml-language-server` comment as the first line of each file, pointing at the
matching schema, so your editor validates it as you type:

```yaml
# yaml-language-server: $schema=https://raw.githubusercontent.com/DiamondLightSource/deploy-tools/main/src/deploy_tools/models/schemas/release.json
```

This requires an editor with a YAML language server — e.g. VS Code with the
[Red Hat YAML extension](https://marketplace.visualstudio.com/items?itemName=redhat.vscode-yaml),
or any [LSP](https://microsoft.github.io/language-server-protocol/)-capable editor
running [`yaml-language-server`](https://github.com/redhat-developer/yaml-language-server).

Alternatively, VS Code's [`yaml.schemas`](https://github.com/redhat-developer/vscode-yaml#associating-schemas)
setting (committed to `.vscode/settings.json`) maps schemas to file paths once for the
whole repository, avoiding the per-file comment. This documentation uses the comment
because it is self-contained and editor-agnostic, but a real configuration repository may
reasonably prefer the repository-level setting.

```{note}
The bundled `demo_configuration` instead points at the locally generated schemas via an
absolute workspace path (e.g.
`/workspaces/deploy-tools/src/deploy_tools/models/schemas/release.json`), so it validates
against uncommitted schema changes during development. This dev-container-only path is not
suitable for production configuration.
```

The other two generated schemas cover files you don't normally author by hand:
`deployment.json` (the `deployment.yaml` snapshot written by `sync`) and `module.json`
(the `Module` that a `Release` wraps).

## Schema pages

```{toctree}
:maxdepth: 1

schemas/deployment-settings
schemas/release
```

## Regenerating the schemas

These files are checked in and do not update automatically when the models change.
Contributors who change the models must regenerate them — see
[regenerate the JSON schemas](how-to/regenerate-schemas.md).
