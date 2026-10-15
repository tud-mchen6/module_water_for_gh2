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
- For usual usages, ZLD is not considered. Try to make the unit cost and energy demand for desalination configurable, also differentiatable for each country.
- Change the default setting of "use natural water first". Change it into "use natural water or not". If it is included, then natural water first. Otherwise, only use desalination. If possible, make this also differentiatable for each country.
- Rewrite the plotting code based on the new type of output.
- The water withdrawal cost might want to be differentiated between countries and source of water (ground water more than surface water?).