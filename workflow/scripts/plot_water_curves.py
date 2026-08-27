import pandas as pd
import heapq as hq
import os
import sys
sys.path.insert(0, str(snakemake.input.helper_functions_path.rsplit("/", 1)[0]))
from internal.helper_functions import *
from matplotlib import pyplot as plt
import itertools
import numpy as np



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

    # iterate over cost or energy
    params_dict = {
        'cost': {
            'dir': cost_curves_dir,
            'column_name': 'cost',
            'ylabel': 'Cumulative cost (billion EUR/year)',
            'plot_title': 'Water Supply Cost Curve',
            'savefig_name': '/cost_curve_',

        },
        'energy': {
            'dir': energy_curves_dir,
            'column_name': 'energy',
            'ylabel': 'Cumulative energy (TWh/year)',
            'plot_title': 'Water Supply Energy Demand Curve',
            'savefig_name': '/energy_curve_',
        },
    }

    countries = plot_countries
    for country in countries:
        os.makedirs(output_dir + country, exist_ok=True)

        for key in params_dict.keys():
            data_dir = params_dict[key]['dir']
            column_name = params_dict[key]['column_name']
            ylabel = params_dict[key]['ylabel']
            plot_title = params_dict[key]['plot_title']
            savefig_name = params_dict[key]['savefig_name']

            curves_dict = {}
            for filename in os.listdir(os.path.join(data_dir, country)):
                if filename.endswith(".csv"):
                    filename_trancate = filename.replace('.csv', '') # to avoid trouble in following string slicing
                    if (len(plot_countries) > 0) and (country not in plot_countries):
                        continue
                    filepath = os.path.join(data_dir, country, filename)
                    water_curve = pd.read_csv(filepath)
                    ylabel = params_dict[key]['ylabel']

                    # Add suffix for single plots
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
                    if 'noDesal' not in filename_trancate:
                        curves_dict[column_name.capitalize() + ' curve'+verbal_suffix] = water_curve

            # For combined plots
            line_styles = [
                            "-",                 # solid
                            "--",                # dashed
                            ":",                 # dotted
                            "-.",                # dash-dot
                        ]
            styles = itertools.cycle(line_styles)
            plt.figure(figsize=(8,6))
            for (label, water_curve), ls in zip(curves_dict.items(), styles):
                plt.plot(water_curve['water_quantity'], water_curve[column_name], linewidth=3, linestyle=ls, label=label, alpha=0.7)
            plt.xlabel('Cumulative Water Supply (billion m³/year)')
            plt.ylabel(ylabel)
            xlim = plot_limit
            plt.xlim(0, xlim)
            ylim = np.interp(xlim, water_curve['water_quantity'], water_curve[column_name]) * 1.1
            plt.ylim(ymin=0, ymax=ylim)
            plt.title(plot_title + f' {get_country_name([country])}')
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.savefig(output_dir + country + savefig_name + country + '_combined.png', bbox_inches="tight", )






if __name__ == "__main__":
    plot_water_curves(
        cost_curves_dir=snakemake.params.cost_curves_dir,
        energy_curves_dir=snakemake.params.energy_curves_dir,
        output_dir=snakemake.params.output_dir,
        plot_limit=snakemake.params.plot_limit,
        plot_countries=snakemake.params.plot_countries,
    )