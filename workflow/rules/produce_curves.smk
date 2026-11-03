"""Rules to produce the water cost curve and energy curve."""

import json

rule produce_water_curves:
    input:
        processed="<resources>/processed/processed_FAO.csv",
        configfile="config/config.yaml",
        helper_functions_path=workflow.source_path("../internal/helper_functions.py"),
    conda:
        "../envs/default.yaml"
    params:
        config=lambda wildcards: config["scenarios"][wildcards.scenario],
        countries=lambda wildcards: config.get("countries", ""),
    output:
        cost_curves_output=directory("<results>/cost_curves/{scenario}/"),
    message:
        """Produce the water curves."""
    script:
        "../scripts/produce_water_curves.py"


rule get_specific_water_curve:
    input:
        cost_curves_dir="<results>/cost_curves/{scenario}/",
    output:
        cost_curve_file="<results>/cost_curves/exposed/water_curve_{shape}_{scenario}.csv",
    log:
        "<logs>/get_specific_water_curve_{shape}_{scenario}.log",
    message:
        """
        Get the requested country water curve from the directory.
        """
    script:
        "../scripts/get_specific_water_curve.py"


# TODO: rewrite this rule to fit the new water curve format
# rule plot_curves:
#     input:
#         cost_curves_dir="<results>/cost_curves/",
#         helper_functions_path=workflow.source_path("../internal/helper_functions.py"),
#     output:
#         directory("<results>/curves_plots"),
#     conda:
#         "../envs/default.yaml"
#     params:
#         plot_limit=config["plot_limit"],
#         output_dir="<results>/curves_plots/",
#         plot_countries=lambda wildcards: config.get("countries", ""),
#     message:
#         """Plot the water cost curve and energy curve that are
#         found in the results folder."""
#     script:
#         "../scripts/plot_water_curves.py"
