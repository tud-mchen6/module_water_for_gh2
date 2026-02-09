# Home

Welcome to the documentation of the `module_water_for_gh2` data module!
Please consult the [specification guidelines](./specification.md) and the [`clio` documentation](https://clio.readthedocs.io/) for more information.


This module produces water supply curves for green hydrogen production given certain parametric assumptions. The assumptions are configured in `config/config.yaml`. For explanations of these parameters, see `workflow/internal/config.schema.yaml`.

### Running the module
To produce the data of water curves: `snakemake -c 4 produce_water_curves`
To plot the curves: `snakemake -c 4 plot_curves`

### TODO list
- The total withdrawal in `selected_FAO.csv` is sometimes wrong to be 0. It is just AQUASTAT has some data caveats that doesn't provide the data for total withdrawal, but the data on municipal, industry and agricultural are complete. We can just compute the total value.
- For countries whose all sectoral withdrawal data are 0, they should be excluded from the dataset.