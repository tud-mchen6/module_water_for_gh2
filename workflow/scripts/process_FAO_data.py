import pandas as pd
import heapq as hq
import os
from internal.helper_functions import *



def process_FAO_data(selected_path : str, processed_path : str,
                     municipal_benchmark: float = 36.5, internal_use_factor: float = 0.7):
    """
    Processes the cleaned FAO AQUASTAT data to perform calculations for each country.

    Parameters:
    - selected_path: str - Path to the output of selected csv for further processing.
    - processed_path: str - Path to save the processed csv file.
    - municipal_benchmark: float - Benchmark for municipal water withdrawal per as decent living capita (in cubic meters per year).
    - internal_use_factor: float - Factor representing the proportion of water that can be used in internal renewable water.

    """

    df = pd.read_csv(selected_path, index_col=0)

    # only use renewable exploitable water (excluding non-renewable groundwater etc.)
    df['total_renew_exploitable'] = round(df['exploitable_irr_renew_surface'] + df['exploitable_reg_renew_ground'] + df['exploitable_reg_renew_surface'], 3)
    # make sure the data is valid and coherent
    df['exploitable_usable'] = (df['total_renew_exploitable'] > 1e-3) & (df['total_renew_exploitable'] <= df['total_exploitable'] * 1.1)

    # For countries without exploitable data, use internal renewable water
    df['internal_renewable_discounted'] = round(df['internal_renewable'] * internal_use_factor, 3)

    # combine both sources; exploitable has the priority
    df['usable'] = np.where(df['exploitable_usable'], df['total_renew_exploitable'], df['internal_renewable_discounted'])
    # add desalinated water
    df['usable'] += df['desalinated']
    # add treated agriculture water
    df['agri_withdrawal_adjusted'] = round(df['agri_withdrawal'] - df['treated_wastewater_irrigation'], 6)


    # For municipal, calculate municipal withdrawal per capita. If too low, raise to a certain level. This does not represent the amount of water used by actual people.

    # In emergency cases, one person needs 20 litres a day, which is 7.3 m3 per year. Source: https://www.who.int/teams/environment-climate-change-and-health/water-sanitation-and-health/environmental-health-in-emergencies/humanitarian-emergencies
    # In other cases, a decent living standard is 50 litres a day, not including hot water (10.1016/j.gloenvcha.2020.102168)
    # A comfortable amount would be 100 L/person per day (https://www.who.int/publications/i/item/9789240015241), which is 36.5 m3 per year
    df['muni_withdrawal_pp'] = np.maximum(round(df['muni_withdrawal'] / df['population'] * 1e6, 6), municipal_benchmark)
    df['muni_withdrawal_adjusted'] = round(df['muni_withdrawal_pp'] * df['population'] / 1e6, 6)
    df['total_withdrawal_adjusted'] = round(df['agri_withdrawal_adjusted'] + df['ind_withdrawal'] + df['muni_withdrawal_adjusted'], 6)

    # in cases where some country data is missing, print warnings
    country_names = get_country_name(df.index)
    df.insert(0, 'country_name', country_names)
    for (row_idx, col_name), is_nan in pd.isna(df).stack().items():
        if is_nan:
            country_name = df.loc[row_idx, 'country_name']
            print(f"Country {country_name} does not have {col_name}")
    
    # calculate the 'excess' water that could possible be used
    df['excess'] = round(df['usable'] - df['total_withdrawal_adjusted'], 6)
    # for now, just remove the countries with not sufficient data from FAO
    df = df.dropna(subset=['excess']) # unit: 1e9 m3/year

    output_dir = selected_path.replace(processed_path.split('/')[-1], "")
    os.makedirs(os.path.dirname(output_dir), exist_ok=True)
    df.to_csv(processed_path)


if __name__ == "__main__":
    process_FAO_data(
        selected_path = snakemake.input.selected_path,
        processed_path = snakemake.output.processed_path,
        municipal_benchmark=snakemake.params.municipal_benchmark,
        internal_use_factor=snakemake.params.internal_use_factor,
    )

