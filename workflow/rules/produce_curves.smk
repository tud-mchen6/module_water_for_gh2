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
        touch("results/cost_curves/compute_complete.flag")
    # conda:
    script:
        "../scripts/produce_water_curves.py"


