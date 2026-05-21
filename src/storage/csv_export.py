from pathlib import Path

import pandas as pd

from src.simulation.solve import ProjectileResult


def result_to_dataframe(result: ProjectileResult) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "t": result["t"],
            "x": result["x"],
            "y": result["y"],
            "vx": result["vx"],
            "vy": result["vy"],
            "v": result["v"],
            "Ek": result["Ek"],
            "Ep": result["Ep"],
            "E": result["E"],
        }
    )


def save_result_to_csv(path: str | Path, result: ProjectileResult) -> None:
    dataframe = result_to_dataframe(result)
    dataframe.to_csv(path, index=False)


def export_simulation_results_to_csv(
    no_drag: ProjectileResult,
    linear_drag: ProjectileResult,
    quadratic_drag: ProjectileResult,
    output_directory: str | Path = "results",
) -> None:
    output_path = Path(output_directory)
    output_path.mkdir(exist_ok=True)

    save_result_to_csv(output_path / "no_drag.csv", no_drag)
    save_result_to_csv(output_path / "linear_drag.csv", linear_drag)
    save_result_to_csv(output_path / "quadratic_drag_rk4.csv", quadratic_drag)
