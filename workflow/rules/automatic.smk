"""Rules to used to download automatic resource files."""


rule download_FAO_bulk:
    message:
        "Download the bulk data from FAO."
    params:
        url=internal["resources"]["automatic"]["FAO_bulk_url"],
    output:
        bulk="resources/automatic/bulk_FAO.csv",
    shell:
        'curl -sSLo {output.bulk} "{params.url}"'
