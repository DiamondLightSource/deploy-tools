# Your first deployment

This tutorial takes you from a set of configuration files to a Module you can load and run,
using the demo configuration that ships in the repository.

It is a hands-on learning exercise: you run each command yourself, in a throwaway directory.
A real deployment targets a shared area, where we recommend driving these commands from
a CI pipeline instead (see
[drive deploy-tools from CI](../how-to/ci-pipeline.md)) — but running them by hand once
is the quickest way to see what each does.

## Before you start

You will need:

- `deploy-tools` installed and on your path — see [installation](installation.md).
- **Environment Modules** (the `module` command). Check with `module --version`.
- **Apptainer** and network access. The demo Modules include containerised apps, so `sync`
  runs `apptainer pull` against public images. (The shell entrypoints below work without
  either, if you only want to see the mechanics.)

## 1. Get the demo configuration

The demo configuration lives in the repository, so clone it:

```
$ git clone https://github.com/DiamondLightSource/deploy-tools.git
$ export CONFIG=$PWD/deploy-tools/src/deploy_tools/demo_configuration
```

That folder contains a `settings.yaml` and one folder per Module, each holding a Release
file named `<version>.yaml`. Have a look — `example-module-apps/0.1.yaml`, for example,
defines a Module with a containerised app and a couple of small shell entrypoints.

```{note}
The `# yaml-language-server: $schema=…` line at the top of each file only drives editor
validation; the CLI ignores it. See [the JSON Schema reference](../schemas.md) for how to
point your editor at the schemas.
```

## 2. Create an empty deployment area

The deployment area is the directory `deploy-tools` writes into. Make a fresh, empty one:

```
$ export DEPLOY=/tmp/deploy-tools-demo
$ mkdir -p $DEPLOY
```

## 3. Check the area is ready

There is no snapshot yet, so use the `--from-scratch` form, which just asserts the
area is empty and exits without error:

```
$ deploy-tools compare --from-scratch $DEPLOY
```

## 4. Preview the changes

`validate` reports the Modules that *would* be deployed, without touching anything. Again
use `--from-scratch`, since there is no prior snapshot:

```
$ deploy-tools validate --from-scratch $DEPLOY $CONFIG
```

You should see every demo Module listed as an addition, along with the default version
chosen for each name.

## 5. Deploy

Now synchronise the area with the configuration. `sync` runs validation, builds every
Module (pulling the container images), and moves the results into place, all in one command:

```
$ deploy-tools sync --from-scratch $DEPLOY $CONFIG
```

`--from-scratch` deploys into the empty area and implies `--allow-all`, since there is no
prior state to protect. `sync` also initialises a git repository in the area and writes
the first snapshot, the reference for later `compare` and `sync` runs.

## 6. See what was created

The area now has the standard layout (explained in
[the deployment area](../explanations/deployment-area.md)):

```
$ ls $DEPLOY
build  deployment.yaml  modules  modulefiles
$ ls $DEPLOY/modulefiles
dls-pmac-control  example-module-apps  example-module-deps  phoebus  ...
```

`modules/` holds the built files for every version; `modulefiles/` holds the symlinks that
make them visible to Environment Modules; `deployment.yaml` is the snapshot.

## 7. Make the Modules available

Add the area's `modulefiles` folder to your `MODULEPATH`, then list what is available:

```
$ module use $DEPLOY/modulefiles
$ module avail
```

The demo Modules now appear alongside any others on your system.

## 8. Load a Module and run it

Load the demo Module `example-module-apps`:

```
$ module load example-module-apps
```

Loading the Module sets its environment variables and adds its entrypoints to your path.
Run the shell entrypoint, which echoes one of those variables — no container involved:

```
$ test-echo-module-folder
Test message OTHER_VALUE from example-module-folder
```

If Apptainer is available, run one of the Module's containerised entrypoints:

```
$ cowsay-hello
```

When you are done, unload it:

```
$ module unload example-module-apps
```

```{note}
Some names ship more than one version. The demo deploys `dls-pmac-control` as both `0.1`
and `0.2`, and its `settings.yaml` pins `0.1` as the default, so `module load
dls-pmac-control` loads `0.1` unless you ask for `dls-pmac-control/0.2` explicitly. See
[default version resolution](../explanations/default-versions.md).
```

## What you have learned

You took a configuration folder, checked the area was clean, previewed the changes, and
deployed Modules you could load and run. Those are the same `compare`, `validate` and
`sync` commands a real deployment runs; a CI pipeline spreads them across separate stages
(see [drive deploy-tools from CI](../how-to/ci-pipeline.md)).

From here:

- [The release lifecycle](../explanations/deprecation-lifecycle.md) — how to update,
  deprecate, restore and remove versions in later syncs.
- [Snapshots and the compare safety net](../explanations/snapshots-and-compare.md)
  — what to run before each `sync` and how to recover from a failure.
- [The JSON schema reference](../schemas.md) — every field you can set in a configuration
  file.
