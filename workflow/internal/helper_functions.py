import pandas as pd
import numpy as np
import pycountry
import country_converter as coco


def get_alpha_3(name):
    """Convert country name to ISO3 code."""
    try:
        return pycountry.countries.lookup(name).alpha_3
    except Exception as e:
        return coco.convert(names=name, to='ISO3')


def get_country_name(iso3):
    """Convert country name to ISO3 code."""
    try:
        return pycountry.countries.get(alpha_3=iso3).name
    except Exception as e:
        return coco.convert(names=iso3, to='name_short')



def change_FAO_column_names(df):
    """
    Change the column names of the FAO data to more readable names.
    """
    df = df.rename(columns={
        'Agricultural water withdrawal per capita': 'agri_withdrawal_per_capita',
        'Industrial water withdrawal per capita': 'ind_withdrawal_per_capita',
        'Municipal water withdrawal per capita (total population)': 'muni_withdrawal_per_capita',
        'Total water withdrawal per capita': 'withdrawal_per_capita',
        'SDG 6.4.2. Water Stress': 'water_stress',
        'Rural population with access to safe drinking-water (JMP)': 'rural_drink_access',
        'Urban population with access to safe drinking-water (JMP)': 'urban_drink_access',
        'Total population with access to safe drinking-water (JMP)': 'total_drink_access',
        'Total renewable water resources per capita': 'renewable_per_capita',
        'Total internal renewable water resources per capita': 'internal_renewable_per_capita',
        'Total population': 'population',
        'Environmental Flow Requirements': 'env_flow_requirements',
        'Exploitable: irregular renewable surface water': 'exploitable_irr_renew_surface',
        'Exploitable: regular renewable groundwater': 'exploitable_reg_renew_ground',
        'Exploitable: regular renewable surface water': 'exploitable_reg_renew_surface',
        'Total exploitable water resources': 'total_exploitable',
        'Total internal renewable water resources (IRWR)': 'internal_renewable',
        'Desalinated water produced':'desalinated',
        'Agricultural water withdrawal': 'agri_withdrawal',
        'Industrial water withdrawal': 'ind_withdrawal',
        'Municipal water withdrawal': 'muni_withdrawal',
        'Total water withdrawal': 'total_withdrawal',
        'Direct use of treated municipal wastewater for irrigation purposes': 'treated_wastewater_irrigation',
        
    })

    return df



def read_FAO_data(file_path, country_only=True, year=None):
    """
    Read csv FAO data and select the relevant columns and rows.
    year should be in integer, not string format.
    """
    cols_to_use = ['Variable', 'Area', 'Year', 'Value', 'Unit']
    df = pd.read_csv(file_path, usecols=cols_to_use)
    df['country_id'] = get_alpha_3(df['Area'])
    
    if year is not None:
        df = df[df['Year'] == year]
    else:
        # select the newest data
        if len(np.unique(df['Year'])) > 1:
            latest_year = np.max(np.unique(df['Year']))
            df = df[df['Year'] == latest_year]
        # TODO: for some countries in some indices, the 2022 data is significantly lower than 2020 and 2021. This is not yet fixed here; should try to fix on the FAO side

    # if there is continent names included
    null_mask = df['country_id'].isnull()
    if null_mask.any():
        print("Warning: Something is not converted to ISO3 codes.")
        print(df.loc[null_mask, 'Area'].unique())
        df = df[~null_mask]
    
    if country_only:
        df = df[(df['country_id']!='not found') & (~df['country_id'].apply(lambda x: isinstance(x, list)))]
    

    df = df.pivot(index='country_id', columns='Variable', values='Value')
    df = change_FAO_column_names(df)

    # print("The variables are: ")
    # print(df['Variable'].unique())

    return df


