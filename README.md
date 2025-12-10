# Module to estimate water provision for green hydrogen production

This module uses external data, mostly from FAO AQUASTAT, to estimate the water available for additional green hydrogen production on a national geographical resolution. If there is water stress, then assume a certain level of desalination can be used for that, with configurable assumptions of to what quantity desalination can be used and how desalination is deployed. The module outputs the quantity-cost curve for the water for green hydrogen.

A modular `snakemake` workflow built for [`clio`](https://clio.readthedocs.io/) data modules.

## Using this module

This module can be imported directly into any `snakemake` workflow.
Please consult the integration example in `tests/integration/Snakefile` for more information.

## Development

We use [`pixi`](https://pixi.sh/) as our package manager for development.
Once installed, run the following to clone this repo and install all dependencies.

```shell
git clone git@github.com:calliope-project/module_water_for_gh2.git
cd module_water_for_gh2
pixi install --all
```

For testing, simply run:

```shell
pixi run test-integration
```

To view the documentation locally, use:

```shell
pixi run serve-docs
```

To test a minimal example of a workflow using this module:

```shell
pixi shell    # activate this project's environment
cd tests/integration/  # navigate to the integration example
snakemake --use-conda --cores 2  # run the workflow!
```
