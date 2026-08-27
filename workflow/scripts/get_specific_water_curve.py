from pathlib import Path
import pandas as pd


def get_specific_water_curve(
    cost_curves_dir: str,
    cost_curve_file: str,
):

    input_path = Path(cost_curves_dir)
    files = [str(file) for file in input_path.iterdir() if file.is_file()]
    shape = snakemake.wildcards.shape
    suffix = snakemake.wildcards.suffix
    found = False
    for file in files:
        if shape in file:
            try:
                curve = pd.read_csv(
                    cost_curves_dir + "/" + shape + "_" + suffix + ".csv", index_col=0
                )
                curve.to_csv(cost_curve_file)
                found = True
                return
            except:
                raise FileNotFoundError("Cost curve directory doesn't exist.")
    if not found:
        raise FileNotFoundError("File not in target directory.")


if __name__ == "__main__":
    get_specific_water_curve(
        cost_curves_dir=snakemake.input.cost_curves_dir,
        cost_curve_file=snakemake.output.cost_curve_file,
    )
