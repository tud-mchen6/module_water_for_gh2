"""Rules to process the downloaded FAO data."""


rule select_bulk_FAO_data:
    message:
        """Select the relevant parts from the FAO bulk data."""
    input:
        bulk="<resources>/automatic/bulk_FAO.csv",
        landlocked=workflow.source_path("../internal/landlocked_countries.csv"),
        helper_functions_path=workflow.source_path("../internal/helper_functions.py")
    params:
        params_relevant=internal["resources"]["automatic"]["params_relevant"],
    output:
        selected_path="<resources>/processed/selected_FAO.csv",
    conda:
        "../envs/default.yaml",
    script:
        "../scripts/select_bulk_FAO_data.py"


rule process_FAO_data:
    message:
        """Process the selected FAO data into final format."""
    input:
        selected_path="<resources>/processed/selected_FAO.csv",
        helper_functions_path=workflow.source_path("../internal/helper_functions.py")
    params:
        municipal_benchmark=config["municipal_benchmark"],
        internal_use_factor=config["internal_use_factor"],
    output:
        processed_path="<resources>/processed/processed_FAO.csv",
    conda:
        "../envs/default.yaml",
    script:
        "../scripts/process_FAO_data.py"