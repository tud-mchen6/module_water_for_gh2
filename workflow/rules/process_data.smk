"""Rules to process the downloaded FAO data."""


rule select_bulk_FAO_data:
    message:
        """Select the relevant parts from the FAO bulk data."""
    input:
        bulk="resources/automatic/bulk_FAO.csv",
        # TODO: not sure yet where this file should be placed, this is a temporary location
        landlocked="workflow/internal/landlocked_countries.csv",
    params:
        params_relevant=internal["resources"]["automatic"]["params_relevant"],
    output:
        selected_path="resources/processed/selected_FAO.csv",
    script:
        "../scripts/select_bulk_FAO_data.py"


rule process_FAO_data:
    message:
        """Process the selected FAO data into final format."""
    input:
        selected_path="resources/processed/selected_FAO.csv",
    params:
        municipal_benchmark=config["municipal_benchmark"],
        internal_use_factor=config["internal_use_factor"],
    output:
        processed_path="resources/processed/processed_FAO.csv",
    script:
        "../scripts/process_FAO_data.py"