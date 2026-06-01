"""Export projectile-motion simulation results as CSV files."""

from collections.abc import Iterator
from csv import writer
from pathlib import Path
from typing import Literal

from src.simulation.solve import ProjectileResult


CsvColumn = Literal[
    "t",
    "x",
    "y",
    "vx",
    "vy",
    "v",
    "Ek",
    "Ep",
    "E",
]

CsvRow = tuple[float, ...]

_CSV_COLUMNS: tuple[CsvColumn, ...] = (
    "t",
    "x",
    "y",
    "vx",
    "vy",
    "v",
    "Ek",
    "Ep",
    "E",
)


def _iter_result_rows(result: ProjectileResult) -> Iterator[CsvRow]:
    """Return trajectory rows in CSV column order.

    All result arrays must contain the same number of samples. Rejecting
    inconsistent lengths prevents partially truncated exports.
    """

    columns = tuple(result[column] for column in _CSV_COLUMNS)
    row_count = len(columns[0])

    if any(len(column) != row_count for column in columns[1:]):
        raise ValueError("Projectile result arrays must have equal lengths.")

    return (
        tuple(float(column[row_index]) for column in columns)
        for row_index in range(row_count)
    )


def save_result_to_csv(path: str | Path, result: ProjectileResult) -> None:
    """Write one projectile trajectory to a CSV file."""

    output_path = Path(path)
    rows = _iter_result_rows(result)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8", newline="") as file:
        csv_writer = writer(file, lineterminator="\n")
        csv_writer.writerow(_CSV_COLUMNS)
        csv_writer.writerows(rows)


def export_simulation_results_to_csv(
    no_drag: ProjectileResult,
    linear_drag: ProjectileResult,
    quadratic_drag: ProjectileResult,
    output_directory: str | Path = "results",
) -> None:
    """Export all simulation models as separate CSV files."""

    output_path = Path(output_directory)
    output_path.mkdir(parents=True, exist_ok=True)

    save_result_to_csv(output_path / "no_drag.csv", no_drag)
    save_result_to_csv(output_path / "linear_drag.csv", linear_drag)
    save_result_to_csv(output_path / "quadratic_drag_rk4.csv", quadratic_drag)
