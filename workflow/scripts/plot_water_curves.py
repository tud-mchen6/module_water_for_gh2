import pandas as pd
import heapq as hq
import os
from internal.helper_functions import *
from matplotlib import pyplot as plt



def plot_water_curves(cost_curves_dir: str, 
                    energy_curves_dir: str,
                    output_dir: str,
                    plot_limit: float = 5,
                    plot_countries: list = []
                    ):
    """
    Plots water cost and energy curves that are in the results folder.

    Parameters:
    - cost_curves_dir: str - Directory to save cost curves.
    - energy_curves_dir: str - Directory to save energy curves.
    - plot_limit: float - Maximum limit for plotting water withdrawal (in billion cubic meters).

    """
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(cost_curves_dir):
        if filename.endswith(".csv"):
            filename_trancate = filename.replace('.csv', '') # to avoid trouble in following string slicing
            country = filename_trancate.split('_')[2] # hard-coded based on naming convention
            if (len(plot_countries) > 0) and (country not in plot_countries):
                continue
            filepath = os.path.join(cost_curves_dir, filename)
            water_curve = pd.read_csv(filepath)

            # Add suffix
            verbal_suffix = ''
            flag_zld = False
            if 'noDesal' in filename_trancate:
                verbal_suffix += ', no desalination'
            else:
                if 'ZLD' in filename_trancate:
                    verbal_suffix += ' with ZLD'
                    flag_zld = True
                if ('comp' in filename_trancate) and flag_zld:
                    verbal_suffix += ', with compensation'
                elif ('comp' in filename_trancate) and flag_zld==False:
                    verbal_suffix += ' with compensation'
                if verbal_suffix != '':
                    verbal_suffix = ' (' + verbal_suffix.strip() + ')'
            suffix = filename_trancate.split(country, 1)[1]

            # Start plotting
            plt.figure(figsize=(8,6))
            plt.plot(water_curve['water_quantity'], water_curve['cost'], linewidth=6,)
            plt.xlabel('Cumulative Water Supply (billion m³/year)')
            plt.ylabel('Cumulative cost (billion EUR/year)')
            xlim = plot_limit
            plt.xlim(0, xlim)
            plt.ylim(ymin=0)
            plt.title(f'Water Supply Cost Curve for {get_country_name([country])}' + verbal_suffix)
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.savefig(output_dir + 'water_curve_' + country + suffix + '.png', bbox_inches="tight", )

    # Energy curves
    for filename in os.listdir(energy_curves_dir):
        if filename.endswith(".csv"):
            filename_trancate = filename.replace('.csv', '') # to avoid trouble in following string slicing
            country = filename_trancate.split('_')[2] # hard-coded based on naming convention
            if (len(plot_countries) > 0) and (country not in plot_countries):
                continue
            filepath = os.path.join(energy_curves_dir, filename)
            water_curve = pd.read_csv(filepath)

            # Add suffix
            verbal_suffix = ''
            flag_zld = False
            if 'noDesal' in filename_trancate:
                verbal_suffix += ', no desalination'
            else:
                if 'ZLD' in filename_trancate:
                    verbal_suffix += ' with ZLD'
                    flag_zld = True
                if ('comp' in filename_trancate) and flag_zld:
                    verbal_suffix += ', with compensation'
                elif ('comp' in filename_trancate) and flag_zld==False:
                    verbal_suffix += ' with compensation'
                if verbal_suffix != '':
                    verbal_suffix = ' (' + verbal_suffix.strip() + ')'
            suffix = filename_trancate.split(country, 1)[1]

            # Start plotting
            plt.figure(figsize=(8,6))
            plt.plot(water_curve['water_quantity'], water_curve['energy'], linewidth=6,)
            plt.xlabel('Cumulative Water Supply (billion m³/year)')
            plt.ylabel('Cumulative energy (TWh/year)')
            xlim = plot_limit
            plt.xlim(0, xlim)
            plt.ylim(ymin=0)
            plt.title(f'Water Supply Energy Demand for {get_country_name([country])}' + verbal_suffix)
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.savefig(output_dir + 'energy_curve_' + country + suffix + '.png', bbox_inches="tight", )






if __name__ == "__main__":
    plot_water_curves(
        cost_curves_dir=snakemake.params.cost_curves_dir,
        energy_curves_dir=snakemake.params.energy_curves_dir,
        output_dir=snakemake.params.output_dir,
        plot_limit=snakemake.params.plot_limit,
        plot_countries=snakemake.params.plot_countries,
    )