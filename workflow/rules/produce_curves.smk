"""Rules to produce the water cost curve and energy curve."""

suffix_0 = "noDesal" if not config["include_desal"] else ""
suffix_1 = "ZLD" if config["include_ZLD"] else ""
suffix_2 = "comp" if config["compensate"] else ""

suffix = "_".join(s for s in [suffix_0, suffix_1, suffix_2] if s)
if suffix == "":
    suffix = "base"


rule produce_water_curves:
    input:
        processed="<resources>/processed/processed_FAO.csv",
        configfile="config/config.yaml",
        helper_functions_path=workflow.source_path("../internal/helper_functions.py"),
    output:
        cost_curves_output=directory(f"<results>/cost_curves/{suffix}/"),
    conda:
        "../envs/default.yaml"
    params:
        include_desal=config["include_desal"],
        include_ZLD=config["include_ZLD"],
        suffix=suffix,
        basic_withdrawal_cost=config["basic_withdrawal_cost"],
        freshwater_for_h2=config["freshwater_for_h2"],
        compensate=config["compensate"],
        plot_limit=config["plot_limit"],
        countries=lambda wildcards: config.get("countries", ""),
    message:
        """Produce the water curves."""
    script:
        "../scripts/produce_water_curves.py"


rule get_specific_water_curve:
    input:
        cost_curves_dir=directory(f"<results>/cost_curves/{suffix}/"),
    output:
        cost_curve_file="<results>/cost_curves/exposed/{shape}_{suffix}.csv",
    log:
        "<logs>/get_specific_water_curve_{shape}_{suffix}.log",
    message:
        """



        Get the requested country water curve from the directory.



        """
    script:
        "../scripts/get_specific_water_curve.py"


# TODO: rewrite this rule to fit the new water curve format
rule plot_curves:
    input:
        cost_curves_dir=directory("results/cost_curves/"),
        helper_functions_path=workflow.source_path("../internal/helper_functions.py"),
    output:
        directory("<results>/curves_plots"),
    conda:
        "../envs/default.yaml"
    params:
        plot_limit=config["plot_limit"],
        output_dir="results/curves_plots/",
        plot_countries=lambda wildcards: config.get("countries", ""),
    message:
        """Plot the water cost curve and energy curve that are







        found in the results folder."""
    script:
        "../scripts/plot_water_curves.py"
