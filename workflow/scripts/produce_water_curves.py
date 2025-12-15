import pandas as pd
import heapq as hq
import os
from internal.helper_functions import *



def produce_water_curves(processed : str, 
                        cost_curves_dir : list, energy_curves_dir : str,
                        include_desal : bool, include_ZLD : bool,
                        basic_withdrawal_cost : float = 0.01,
                        freshwater_for_h2 : float = 0.8,
                        compensate : bool = True, plot_limit : float = 5):
    """
    Produce both cost-quantity curves and energy-quantity curves for water for a
    given country with fixed cost and technical parameters for desalination.

    Parameters:
    - processed: str - Path to the processed FAO AQUASTAT data CSV file.
    - cost_curves_dir: str - Path to store the final water cost curves files.
    - energy_curves_dir: str - Path to store the final water energy curves files.
    - include_desal: bool - Whether to include desalination in the calculation.
    - include_ZLD: bool - Whether to include zero liquid discharge in the calculation.
    - basic_withdrawal_cost: float - Basic cost for freshwater withdrawal, in EUR/m3.
    - freshwater_for_h2: float - Share of available freshwater that can be used for 
        hydrogen production.
    - compensate: bool - Whether to use desalinated water to compensate for 
        local water stress.
    - plot_limit: float - The artificial x-axis limit in the final plot.

    Unit: water, 1e9 m3/year; monetary value, 1e9 EUR; energy, TWh/year.
    """

    # DESALINATION PARAMS
    # TODO: is it wiser to move these out of the script and into the internal params? But they seem too many to be defined in the rule.
    init_salinity = 35 # kg/m3. A rather conservative value. But the Mediterranean might go up to 39. See https://explore.webodv.awi.de/ocean/woa23/1.00-degree/01_all-years/01_annual/woa23_1.00deg_all-years_annual/
    recovery = 0.45 # single-pass recovery rate of the first stage of desalination. Out of 1 m3 feed seawater, 0.45 m3 freshwater passes. Reference: Reddy and Ghaffour, 2007
    E_stage1 = 3.5 # kWh/m3 freshwater. The electricity needed for the first stage. According to Table 2 of Voutchkov 2018, this is a conservative value. 
    E_stage2_1 = 15 # kWh/m3 freshwater. The electricity needed for the second stage. Assumed to be brine concentrating (BC), see Panagopoulos et al. 2019.
    saturate_salinity = 0.26 # percent of mass in total solution mass. At < 30 degree centigrate.
    density_saturate_solution = 1200 # kg/m3. Rough density of the saturated solution.
    E_stage2_2 = 50 # kWh/m3 freshwater. The heat needed for the final crystallisation process. Assume BCr, see Panagopoulos et al. 2019.
    water_content_crystal = 0.1 # mass content of water in the final contrifuge cake.
    cost_stage1 = 1.2 # EUR/m3 freshwater produced at the first stage. Some further investment into elec-heat energy may be needed. See Eke et al. 2020
    cost_stage2 = 5 # EUR/m3 freshwater produced at the second stage. See Fthenakis et al. 2024 and O'Connell et al. 2024. Assume it is BC + BCr.
    cost_non_energy_share = 0.75 # the share of non-energy cost, since we assume using our own renewables.




    # Calculate per m3 freshwater cost and the energy consumption
    # For 1 m3 feed seawater

    # Stage 1, assume RO
    E_total = 0
    E_total += E_stage1 * recovery # kWh
    cost_total = 0
    cost_total += cost_stage1 * cost_non_energy_share * recovery
    total_freshwater_volume = 0
    total_freshwater_volume += recovery

    # Stage 2, assume BC + BCr (Panagopoulos et al. 2019)
    if include_ZLD:
        # Stage 2.1, preconcentration until saturation
        salt_mass = init_salinity # 1 m3 * 35 kg/m3
        saturate_water_volume = salt_mass / saturate_salinity / density_saturate_solution # kg / (kg/m3) = m3. First calculate the total mass of the saturated solution, then use density to calculate the volume of the solution
        freshwater_volume_2_1 = (1 - recovery) - saturate_water_volume # Approximate the volume of produced freshwater in the saturation process; remaining brine volume minus the saturated brine volume
        E_total += E_stage2_1 * freshwater_volume_2_1
        total_freshwater_volume += freshwater_volume_2_1

        # Stage 2.2, crystallisation
        final_cake_mass = salt_mass / (1 - water_content_crystal) # Final cake still contains certain mass of water
        distill_water_volume = (salt_mass / saturate_salinity - final_cake_mass) / 1e3 # First calculate the mass of distilled water, then convert to volume
        E_total += E_stage2_2 * distill_water_volume
        total_freshwater_volume += distill_water_volume
        cost_total += cost_stage2 * cost_non_energy_share * (total_freshwater_volume - recovery)


    # Electricity and cost per m3 freshwater produced
    E_total_freshwater = E_total / total_freshwater_volume
    cost_total_freshwater = cost_total / total_freshwater_volume



    # create the curve folders
    if not os.path.exists(cost_curves_dir):
        os.makedirs(cost_curves_dir)
    else:
        if os.listdir(cost_curves_dir):
            print(f"Warning: The folder '{cost_curves_dir}' is NOT empty, might overwrite previous data!")

    if not os.path.exists(energy_curves_dir):
        os.makedirs(energy_curves_dir)
    else:
        if os.listdir(energy_curves_dir):
            print(f"Warning: The folder '{energy_curves_dir}' is NOT empty, might overwrite previous data!")



    # create water curves and energy curves
    df = pd.read_csv(processed, index_col=0)
    suffix_0 = '_noDesal' if not include_desal else ''
    suffix_1 = '_ZLD' if include_ZLD else ''
    # Compensation means if local renewable freshwater is insufficient, desalinated water needs to
    # first be used for local withdrawal, before being used for hydrogen production.
    suffix_2 = '_comp' if compensate else ''

    for index, row in df.reset_index().iterrows():
        file_name = f"_{row['ISO3']}"
        
        if not row['landlocked']:
            # If there is no sufficient local renewable freshwater
            if row['excess'] < 0:
                if include_desal:
                    if compensate:
                        x = np.linspace(0, plot_limit, 100)
                        y = cost_total_freshwater * (x - row['excess'])
                        y_E = E_total_freshwater * (x - row['excess'])
                    else:
                        x = np.linspace(0, plot_limit, 100)
                        y = cost_total_freshwater * x # unit: 1e9 EUR
                        y_E = E_total_freshwater * x
                else:
                    x = np.zeros(100)
                    y = np.zeros(100)
                    y_E = np.zeros(100)
            # If there is sufficient local renewable freshwater, only part of it can be used for hydrogen production.
            # Beyond that limit, desalination is needed.
            else:
                if row['excess'] * freshwater_for_h2 < plot_limit:
                    x_1 = np.linspace(0, row['excess'] * freshwater_for_h2, 100)
                    y_1 = np.full_like(x_1, basic_withdrawal_cost)
                    y_1_E = np.full_like(x_1, 0)
                
                    if include_desal:
                        x_2 = np.linspace(row['excess'] * freshwater_for_h2, plot_limit, 100)
                        y_2 = cost_total_freshwater * (x_2 - row['excess'] * freshwater_for_h2) + basic_withdrawal_cost
                        y_2_E = E_total_freshwater * (x_2 - row['excess'] * freshwater_for_h2)

                        x = np.concatenate([x_1, x_2])
                        y = np.concatenate([y_1, y_2])
                        y_E = np.concatenate([y_1_E, y_2_E])
                    else:
                        x = np.linspace(0, row['excess'] * freshwater_for_h2, 100)
                        y = np.full_like(x, basic_withdrawal_cost)
                        y_E 
                else:
                    x = np.linspace(0, row['excess'] * freshwater_for_h2, 100)
                    y = np.full_like(x, basic_withdrawal_cost)
                    y_E = np.full_like(x, 0)

        
        else:
            # If there's no excess, landlocked country cannot use seawater desalination
            if row['excess'] < 0:
                x = np.zeros(100)
                y = np.zeros(100)
                y_E = np.zeros(100)
            else:
                x = np.linspace(0, row['excess'] * freshwater_for_h2, 100)
                y = np.full_like(x, basic_withdrawal_cost)
                y_E = np.full_like(x, 0)


        output_df = pd.DataFrame({'water_quantity': x, 'unit_water':'1e9 m3', 'cost': y, 'unit_cost':'1e9 EUR'})
        output_E_df = pd.DataFrame({'water_quantity': x, 'unit_water':'1e9 m3', 'energy': y_E, 'unit_cost':'TWh'})
        os.makedirs(os.path.dirname(cost_curves_dir), exist_ok=True)
        os.makedirs(os.path.dirname(energy_curves_dir), exist_ok=True)
        if include_desal:
            output_df.to_csv(cost_curves_dir+'/water_curve'+file_name+suffix_0+suffix_1+suffix_2+'.csv', index=False)
            output_E_df.to_csv(energy_curves_dir+'/energy_curve'+file_name+suffix_0+suffix_1+suffix_2+'.csv', index=False)
        else:
            output_df.to_csv(cost_curves_dir+'/water_curve'+file_name+suffix_0+'.csv', index=False)
            output_E_df.to_csv(energy_curves_dir+'/energy_curve'+file_name+suffix_0+'.csv', index=False)





if __name__ == "__main__":
    produce_water_curves(
        processed=snakemake.input.processed,
        cost_curves_dir=snakemake.params.cost_curves_dir,
        energy_curves_dir=snakemake.params.energy_curves_dir,
        include_desal=snakemake.params.include_desal,
        include_ZLD=snakemake.params.include_ZLD,
        basic_withdrawal_cost=snakemake.params.basic_withdrawal_cost,
        freshwater_for_h2=snakemake.params.freshwater_for_h2,
        compensate=snakemake.params.compensate,
        plot_limit=snakemake.params.plot_limit,
    )


