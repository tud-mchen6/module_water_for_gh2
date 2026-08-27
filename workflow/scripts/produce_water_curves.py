import pandas as pd
import heapq as hq
import os
import sys
sys.path.insert(0, str(snakemake.input.helper_functions_path.rsplit("/", 1)[0]))
from internal.helper_functions import *


def produce_water_curves(
    processed: str,
    cost_curves_output: str,
    include_desal: bool,
    include_ZLD: bool,
    suffix: str,
    basic_withdrawal_cost: float = 0.01,
    freshwater_for_h2: float = 0.8,
    compensate: bool = True,
    plot_limit: float = 5,
    countries: list = [],
):
    """
    Produce both cost-quantity curves and energy-quantity curves for water for a
    given country with fixed cost and technical parameters for desalination.

    Parameters:
    - processed: str - Path to the processed FAO AQUASTAT data CSV file.
    - cost_curves_output: str - Path to store the final water cost curves files.
    - include_desal: bool - Whether to include desalination in the calculation.
    - include_ZLD: bool - Whether to include zero liquid discharge in the calculation.
    - basic_withdrawal_cost: float - Basic cost for freshwater withdrawal, in EUR/m3.
    - freshwater_for_h2: float - Share of available freshwater that can be used for
        hydrogen production.
    - compensate: bool - Whether to use desalinated water to compensate for
        local water stress.
    - plot_limit: float - The artificial x-axis limit in the final plot.
    - countries: list - List of country codes to produce curves for. If empty, produce for all countries.

    Unit: water, 1e9 m3/year; monetary value, 1e9 EUR; energy, TWh/year.
    """

    # DESALINATION PARAMS
    # TODO: is it wiser to move these out of the script and into the internal params? But they seem too many to be defined in the rule.
    init_salinity = 35  # kg/m3. A rather conservative value. But the Mediterranean might go up to 39. See https://explore.webodv.awi.de/ocean/woa23/1.00-degree/01_all-years/01_annual/woa23_1.00deg_all-years_annual/
    recovery = 0.45  # single-pass recovery rate of the first stage of desalination. Out of 1 m3 feed seawater, 0.45 m3 freshwater passes. Reference: Reddy and Ghaffour, 2007
    E_stage1 = 3.5  # kWh/m3 freshwater. The electricity needed for the first stage. According to Table 2 of Voutchkov 2018, this is a conservative value.
    E_stage2_1 = 15  # kWh/m3 freshwater. The electricity needed for the second stage. Assumed to be brine concentrating (BC), see Panagopoulos et al. 2019.
    saturate_salinity = (
        0.26  # percent of mass in total solution mass. At < 30 degree centigrate.
    )
    density_saturate_solution = 1200  # kg/m3. Rough density of the saturated solution.
    E_stage2_2 = 50  # kWh/m3 freshwater. The heat needed for the final crystallisation process. Assume BCr, see Panagopoulos et al. 2019.
    water_content_crystal = 0.1  # mass content of water in the final contrifuge cake.
    cost_stage1 = 1.2  # EUR/m3 freshwater produced at the first stage. Some further investment into elec-heat energy may be needed. See Eke et al. 2020
    cost_stage2 = 5  # EUR/m3 freshwater produced at the second stage. See Fthenakis et al. 2024 and O'Connell et al. 2024. Assume it is BC + BCr.
    cost_non_energy_share = (
        0.75  # the share of non-energy cost, since we assume using our own renewables.
    )

    # Calculate per m3 freshwater cost and the energy consumption
    # For 1 m3 feed seawater

    # Stage 1, assume RO
    E_total = 0
    E_total += E_stage1 * recovery  # kWh
    cost_total = 0
    cost_total += cost_stage1 * cost_non_energy_share * recovery
    total_freshwater_volume = 0
    total_freshwater_volume += recovery

    # Stage 2, assume BC + BCr (Panagopoulos et al. 2019)
    if include_ZLD:
        # Stage 2.1, preconcentration until saturation
        salt_mass = init_salinity  # 1 m3 * 35 kg/m3
        saturate_water_volume = (
            salt_mass / saturate_salinity / density_saturate_solution
        )  # kg / (kg/m3) = m3. First calculate the total mass of the saturated solution, then use density to calculate the volume of the solution
        freshwater_volume_2_1 = (
            1 - recovery
        ) - saturate_water_volume  # Approximate the volume of produced freshwater in the saturation process; remaining brine volume minus the saturated brine volume
        E_total += E_stage2_1 * freshwater_volume_2_1
        total_freshwater_volume += freshwater_volume_2_1

        # Stage 2.2, crystallisation
        final_cake_mass = salt_mass / (
            1 - water_content_crystal
        )  # Final cake still contains certain mass of water
        distill_water_volume = (
            salt_mass / saturate_salinity - final_cake_mass
        ) / 1e3  # First calculate the mass of distilled water, then convert to volume
        E_total += E_stage2_2 * distill_water_volume
        total_freshwater_volume += distill_water_volume
        cost_total += (
            cost_stage2 * cost_non_energy_share * (total_freshwater_volume - recovery)
        )

    # Electricity and cost per m3 freshwater produced
    E_total_freshwater = E_total / total_freshwater_volume
    cost_total_freshwater = cost_total / total_freshwater_volume

    # create the curve folders
    if not os.path.exists(cost_curves_output):
        os.makedirs(cost_curves_output)
    else:
        if os.listdir(cost_curves_output):
            print(
                f"Warning: The folder '{cost_curves_output}' is NOT empty, might overwrite previous data!"
            )

    # create water curves and energy curves
    df = pd.read_csv(processed, index_col=0)

    # Iterate over each country
    for index, row in df.reset_index().iterrows():
        # If countries list is provided, only produce curves for those countries
        if (len(countries) > 0) and (row["ISO3"] not in countries):
            continue

        # Initialise the df for the country, with columns prod, cost, and ener
        dict_country = {
            "prod": [],
            "cost": [],
            "ener": [],
        }
        if not row["landlocked"]:
            # If there is no sufficient local renewable freshwater
            if row["excess"] < 0:
                if include_desal:
                    if compensate:
                        # First data point: the needed compensation part
                        dict_country["prod"].append(
                            row["excess"]
                        )  # negative value to show the difference with actual available water
                        dict_country["cost"].append(cost_total_freshwater)
                        dict_country["ener"].append(E_total_freshwater)
                    # Only desalinated water is available
                    dict_country["prod"].append(plot_limit)
                    dict_country["cost"].append(cost_total_freshwater)
                    dict_country["ener"].append(E_total_freshwater)
                else:
                    # No water is available
                    dict_country["prod"].append(0)
                    dict_country["cost"].append(0)
                    dict_country["ener"].append(0)
            # If there is sufficient local renewable freshwater, only part of it can be used for hydrogen production.
            # Beyond that limit, desalination is needed.
            else:
                if row["excess"] * freshwater_for_h2 < plot_limit:
                    # The use of freshwater
                    dict_country["prod"].append(row["excess"] * freshwater_for_h2)
                    dict_country["cost"].append(basic_withdrawal_cost)
                    dict_country["ener"].append(0)

                    if include_desal:
                        dict_country["prod"].append(
                            plot_limit - (row["excess"] * freshwater_for_h2)
                        )
                        dict_country["cost"].append(cost_total_freshwater)
                        dict_country["ener"].append(E_total_freshwater)
                else:
                    dict_country["prod"].append(plot_limit)
                    dict_country["cost"].append(basic_withdrawal_cost)
                    dict_country["ener"].append(0)

        else:
            # If there's no excess, landlocked country cannot use seawater desalination
            if row["excess"] < 0:
                dict_country["prod"].append(0)
                dict_country["cost"].append(0)
                dict_country["ener"].append(0)
            else:
                dict_country["prod"].append(
                    min(row["excess"] * freshwater_for_h2, plot_limit)
                )
                dict_country["cost"].append(basic_withdrawal_cost)
                dict_country["ener"].append(0)

        output_df = pd.DataFrame(dict_country)
        output_df["unit_cost"] = "EUR/m3"
        output_df["unit_ener"] = "kWh/m3"

        output_df.to_csv(
            cost_curves_output + "/"
            + row["ISO3"]
            + "_"
            + suffix
            + ".csv",
            index=False,
        )


if __name__ == "__main__":
    produce_water_curves(
        processed=snakemake.input.processed,
        cost_curves_output=snakemake.output.cost_curves_output,
        include_desal=snakemake.params.include_desal,
        include_ZLD=snakemake.params.include_ZLD,
        suffix=snakemake.params.suffix,
        basic_withdrawal_cost=snakemake.params.basic_withdrawal_cost,
        freshwater_for_h2=snakemake.params.freshwater_for_h2,
        compensate=snakemake.params.compensate,
        plot_limit=snakemake.params.plot_limit,
        countries=snakemake.params.countries,
    )
