# Write a Module configuration

To add or change a Module, you edit YAML in the configuration folder. This guide covers
the mechanics. For the shape of the files and every field they take, see
[the configuration reference](../reference/configuration.md); to point your editor at
the matching schema, the [schema reference](../schemas.md).

## Add a new Module version

1. Create the file at `<config folder>/<name>/<version>.yaml`. The folder name is the
   Module `name` and the filename is the `version`, so `phoebus/0.1.yaml` defines version
   `0.1` of `phoebus`. The `name` and `version` inside the file must match the path.

2. Add the schema line as the first line so your editor validates as you type:

   ```yaml
   # yaml-language-server: $schema=https://raw.githubusercontent.com/DiamondLightSource/deploy-tools/main/src/deploy_tools/models/schemas/release.json
   ```

   The line is read by [`yaml-language-server`](https://github.com/redhat-developer/yaml-language-server),
   so it takes effect in VS Code with the Red Hat YAML extension or any other editor
   running that language server; elsewhere it is an inert comment. See the
   [schema reference](../schemas.md) for details.

3. Define the Module. Most Modules provide one or more applications; the smallest useful
   one is a single shell script:

   ```yaml
   module:
     name: my-module
     version: "1.0"
     description: What this Module provides
     applications:
       - app_type: shell
         name: hello
         script:
           - echo "hello from my-module"
   ```

   Swap the application for an `apptainer` or `binary` one as needed — see
   [the three application types](../reference/configuration.md#the-three-application-types).

   A Module doesn't have to provide an application: it can instead just set environment
   variables or pull in other Modules as
   [dependencies](../reference/configuration.md#a-module). Give such a Module an
   empty `applications: []`.

## Set the default version

`module load <name>` with no version loads the default. If you don't choose one the
highest version is picked automatically; to pin a specific version, add it to
`settings.yaml`:

```yaml
default_versions:
  my-module: "1.0"
```

To keep a version out of automatic selection — an alpha or release candidate, say — while
still allowing an explicit `module load <name>/<version>`, set
`exclude_from_defaults: true` on that Module.

See [default version resolution](../explanations/default-versions.md) for how the
automatic choice is made.

## Get your change deployed

You don't run `deploy-tools` yourself. Open a merge request in the configuration
repository; CI validates the change and, once it is merged, deploys it (see
[drive deploy-tools from CI](ci-pipeline.md)). The `yaml-language-server` schema line
catches structural mistakes in your editor as you type, before you open the request.

## Change or retire a version

- **Update an existing version in place.** Rejected by default so published versions stay
  stable; prefer publishing a new version. If you must, set `allow_updates: true` on the
  Module — see [the guard rails](../explanations/deprecation-lifecycle.md#the-guard-rails).
- **Retire a version.** Set `deprecated: true` to steer users away from it. Deleting it
  outright has to wait until after it is deprecated (unless the Module has
  `allow_updates: true`). See
  [the guard rails](../explanations/deprecation-lifecycle.md#the-guard-rails).
