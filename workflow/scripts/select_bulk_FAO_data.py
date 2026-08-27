import pandas as pd
import heapq as hq
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(snakemake.input.helper_functions_path).parent))
from helper_functions import get_alpha_3, change_FAO_column_names



def select_bulk_FAO_data(bulk : str, landlocked : str, params_relevant: list, selected_path : str,):
    """
    Processes the downloaded bulk FAO AQUASTAT data to select columns relevant
    for this module.

    Parameters:
    - bulk: str - Path to the downloaded bulk FAO AQUASTAT data CSV file.
    - landlocked: str - Path to the predefined landlocked countries CSV file.
    - selected: str - Path to the output of selected csv for further processing.

    Unit: 1e9 m3/year
    """

    bulk = pd.read_csv(bulk, encoding='latin')
    years = bulk['timePointYears'].unique()
    # only select the data for the most recent 3 years
    largest_nums = hq.nlargest(3, years)
    bulk_recent = bulk[bulk['timePointYears'].isin(largest_nums)]

    # split the initial dataframe into two different columns to match our param names
    # hard-coded column names
    bulk_recent['aquastatElement.1'] = bulk_recent['aquastatElement.1'].astype(str)
    bulk_recent['unit'] = bulk_recent['aquastatElement.1'].str.extract(r'\[(.*?)\]')       # everything inside [...]
    bulk_recent['param'] = bulk_recent['aquastatElement.1'].str.replace(r'\s*\[.*?\]', '', regex=True)  # remove [..] from original
    # read the relevant data in the param list
    bulk_recent = bulk_recent[bulk_recent['param'].isin(params_relevant)]
    # assign country code, and only keep country data (no continental data)
    bulk_recent['ISO3'] = bulk_recent['AREA'].apply(get_alpha_3)
    bulk_recent = bulk_recent[(bulk_recent['ISO3']!='not found') & (~bulk_recent['ISO3'].apply(lambda x: isinstance(x, list)))]
    bulk_recent = bulk_recent.drop(columns=['aquastatElement','timePointYears'])

    # select only the most recent data for a certain param
    keys = ['ISO3', 'param']
    latest_idx = bulk_recent.groupby(keys, dropna=False)['timePointYears.1'].idxmax()
    df_latest = bulk_recent.loc[latest_idx].sort_values(keys).reset_index(drop=True)
    # pivot the resulting df
    df_latest = df_latest.pivot(index='ISO3', columns='param', values='Value').fillna(0)
    df_latest = change_FAO_column_names(df_latest)

    # add a column that tells if the country is land locked
    landlocked_countries = pd.read_csv(landlocked)
    landlocked_countries['ISO3'] = landlocked_countries['Country'].apply(get_alpha_3)
    landlocked_countries['landlocked'] = True
    landlocked_countries = landlocked_countries.drop(columns=['Country']).set_index('ISO3')
    df_latest = pd.merge(df_latest, landlocked_countries, on='ISO3', how='left').fillna(False)

    # create the directory if not exists
    directory = selected_path.replace(selected_path.split('/')[-1], "")
    os.makedirs(os.path.dirname(directory), exist_ok=True)
    df_latest.to_csv(selected_path)



if __name__ == "__main__":
    select_bulk_FAO_data(
        bulk = snakemake.input.bulk,
        landlocked=snakemake.input.landlocked,
        params_relevant=snakemake.params.params_relevant,
        selected_path=snakemake.output.selected_path,
    )