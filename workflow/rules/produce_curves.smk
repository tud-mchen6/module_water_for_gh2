"""Rules to produce the water cost curve and energy curve."""


rule produce_water_curves:
    message:
        """Produce the water cost curve and energy curve."""
    input:
        processed="resources/processed/processed_FAO.csv",
    params:
        cost_curves_dir=config["cost_curves_dir"],
        energy_curves_dir=config["energy_curves_dir"],
        include_desal=config["include_desal"],
        include_ZLD=config["include_ZLD"],
        basic_withdrawal_cost=config["basic_withdrawal_cost"],
        freshwater_for_h2=config["freshwater_for_h2"],
        compensate=config["compensate"],
        plot_limit=config["plot_limit"],
    output:
        touch("results/cost_curves/compute_complete.flag"),
    conda:
        "../envs/default.yaml",
    script:
        "../scripts/produce_water_curves.py"


rule plot_curves:
    message:
        """Plot the water cost curve and energy curve that are
        found in the results folder."""
    params:
        cost_curves_dir=config["cost_curves_dir"],
        energy_curves_dir=config["energy_curves_dir"],
        plot_limit=config["plot_limit"],
        output_dir="results/curves_plots/",
        plot_countries=lambda wildcards: config.get("plot_countries", "")
    output:
        touch("results/curves_plotted/plot_complete.flag"),
    conda:
        "../envs/default.yaml",
    script:
        "../scripts/plot_water_curves.py"