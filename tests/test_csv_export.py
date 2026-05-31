from pathlib import Path
from unittest.mock import Mock

from pytest import MonkeyPatch

import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal

from src.storage import csv_export
from src.storage.csv_export import (
    export_simulation_results_to_csv,
    result_to_dataframe,
    save_result_to_csv,
)


COLUMNS = ["t", "x", "y", "vx", "vy", "v", "Ek", "Ep", "E"]


def make_projectile_result(offset: float = 0.0) -> dict[str, np.ndarray]:
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


def test_result_to_dataframe_preserves_expected_columns_and_values() -> None:
    result = make_projectile_result()

    dataframe = result_to_dataframe(result)

    expected = pd.DataFrame({column: result[column] for column in COLUMNS})
    assert_frame_equal(dataframe, expected)
    assert list(dataframe.columns) == COLUMNS


def test_save_result_to_csv_writes_values_without_dataframe_index(
    tmp_path: Path,
) -> None:
    result = make_projectile_result()
    output_path = tmp_path / "trajectory.csv"

    save_result_to_csv(output_path, result)

    assert output_path.exists()
    dataframe = pd.read_csv(output_path)
    expected = result_to_dataframe(result)
    assert_frame_equal(dataframe, expected)
    assert "Unnamed: 0" not in dataframe.columns


def test_export_simulation_results_creates_directory_and_delegates_named_files(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
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

    expected_results = {
        "no_drag.csv": no_drag,
        "linear_drag.csv": linear_drag,
        "quadratic_drag_rk4.csv": quadratic_drag,
    }
    assert {path.name for path in output_directory.iterdir()} == set(expected_results)

    for filename, result in expected_results.items():
        dataframe = pd.read_csv(output_directory / filename)
        assert_frame_equal(dataframe, result_to_dataframe(result))
