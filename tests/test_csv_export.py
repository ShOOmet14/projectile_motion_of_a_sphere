from csv import reader
from pathlib import Path
from unittest.mock import Mock

import numpy as np
import pytest

from src.simulation.solve import ProjectileResult
from src.storage import csv_export
from src.storage.csv_export import (
    export_simulation_results_to_csv,
    save_result_to_csv,
)


CSV_HEADER = ["t", "x", "y", "vx", "vy", "v", "Ek", "Ep", "E"]


def make_projectile_result(offset: float = 0.0) -> ProjectileResult:
    return {
        "t": np.array([0.0, 0.5, 1.0], dtype=np.float64),
        "x": np.array([0.0, 2.0, 4.0], dtype=np.float64) + offset,
        "y": np.array([1.0, 2.0, 0.0], dtype=np.float64) + offset,
        "vx": np.array([4.0, 4.0, 4.0], dtype=np.float64) + offset,
        "vy": np.array([3.0, -2.0, -7.0], dtype=np.float64) + offset,
        "v": np.array([5.0, 4.5, 8.0], dtype=np.float64) + offset,
        "Ek": np.array([25.0, 20.25, 64.0], dtype=np.float64) + offset,
        "Ep": np.array([10.0, 20.0, 0.0], dtype=np.float64) + offset,
        "E": np.array([35.0, 40.25, 64.0], dtype=np.float64) + offset,
    }


def read_csv_rows(path: Path) -> list[list[str]]:
    with path.open("r", encoding="utf-8", newline="") as file:
        return list(reader(file))


def test_export_simulation_results_creates_directory_and_delegates_named_files(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    no_drag = make_projectile_result(1.0)
    linear_drag = make_projectile_result(2.0)
    quadratic_drag = make_projectile_result(3.0)
    output_directory = tmp_path / "results"

    saver = Mock()
    monkeypatch.setattr(csv_export, "save_result_to_csv", saver)

    export_simulation_results_to_csv(
        no_drag,
        linear_drag,
        quadratic_drag,
        output_directory,
    )

    assert output_directory.is_dir()
    assert saver.call_args_list == [
        ((output_directory / "no_drag.csv", no_drag),),
        ((output_directory / "linear_drag.csv", linear_drag),),
        ((output_directory / "quadratic_drag_rk4.csv", quadratic_drag),),
    ]


def test_export_simulation_results_writes_all_csv_files(tmp_path: Path) -> None:
    no_drag = make_projectile_result(1.0)
    linear_drag = make_projectile_result(2.0)
    quadratic_drag = make_projectile_result(3.0)
    output_directory = tmp_path / "results"

    export_simulation_results_to_csv(
        no_drag,
        linear_drag,
        quadratic_drag,
        str(output_directory),
    )

    assert {path.name for path in output_directory.iterdir()} == {
        "no_drag.csv",
        "linear_drag.csv",
        "quadratic_drag_rk4.csv",
    }

    for filename in (
        "no_drag.csv",
        "linear_drag.csv",
        "quadratic_drag_rk4.csv",
    ):
        rows = read_csv_rows(output_directory / filename)

        assert rows[0] == CSV_HEADER
        assert len(rows) == 4


def test_export_simulation_results_creates_nested_output_directory(
    tmp_path: Path,
) -> None:
    no_drag = make_projectile_result(1.0)
    linear_drag = make_projectile_result(2.0)
    quadratic_drag = make_projectile_result(3.0)

    output_directory = tmp_path / "exports" / "csv" / "results"

    export_simulation_results_to_csv(
        no_drag,
        linear_drag,
        quadratic_drag,
        output_directory,
    )

    assert output_directory.is_dir()
    assert {path.name for path in output_directory.iterdir()} == {
        "no_drag.csv",
        "linear_drag.csv",
        "quadratic_drag_rk4.csv",
    }


def test_save_result_to_csv_writes_header_and_values(
    tmp_path: Path,
) -> None:
    result = make_projectile_result()
    output_path = tmp_path / "trajectory.csv"

    save_result_to_csv(output_path, result)

    assert output_path.exists()
    assert read_csv_rows(output_path) == [
        CSV_HEADER,
        ["0.0", "0.0", "1.0", "4.0", "3.0", "5.0", "25.0", "10.0", "35.0"],
        ["0.5", "2.0", "2.0", "4.0", "-2.0", "4.5", "20.25", "20.0", "40.25"],
        ["1.0", "4.0", "0.0", "4.0", "-7.0", "8.0", "64.0", "0.0", "64.0"],
    ]


def test_save_result_to_csv_rejects_arrays_with_different_lengths(
    tmp_path: Path,
) -> None:
    result = make_projectile_result()
    result["x"] = np.array([0.0, 2.0], dtype=np.float64)

    output_path = tmp_path / "trajectory.csv"

    with pytest.raises(
        ValueError,
        match="Projectile result arrays must have equal lengths",
    ):
        save_result_to_csv(output_path, result)

    assert not output_path.exists()


def test_save_result_to_csv_creates_parent_directories(
    tmp_path: Path,
) -> None:
    result = make_projectile_result()
    output_path = tmp_path / "exports" / "csv" / "trajectory.csv"

    save_result_to_csv(output_path, result)

    assert output_path.is_file()
