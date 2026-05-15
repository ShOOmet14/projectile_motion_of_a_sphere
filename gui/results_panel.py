import numpy as np

from PySide6.QtWidgets import QLabel, QPlainTextEdit, QVBoxLayout, QWidget

from simulation.solve import ProjectileResult


class ResultsPanel(QWidget):
    def __init__(self) -> None:
        super().__init__()

        layout = QVBoxLayout()

        self.title_label = QLabel("Results")

        self.results_text = QPlainTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setPlaceholderText("Run simulation to display results here.")

        layout.addWidget(self.title_label)
        layout.addWidget(self.results_text)

        self.setLayout(layout)

    def set_results(
        self,
        no_drag: ProjectileResult,
        linear_drag: ProjectileResult,
        quadratic_drag: ProjectileResult,
    ) -> None:
        text = "\n\n".join(
            (
                self.format_result("No drag", no_drag),
                self.format_result("Linear drag", linear_drag),
                self.format_result("Quadratic drag RK4", quadratic_drag),
            )
        )

        self.results_text.setPlainText(text)

    def format_result(self, model_name: str, result: ProjectileResult) -> str:
        flight_time = float(result["t"][-1])
        projectile_range = float(result["x"][-1])
        max_height = float(np.max(result["y"]))

        initial_speed = float(result["v"][0])
        min_speed = float(result["v"].min())
        final_speed = float(result["v"][-1])

        initial_energy = float(result["E"][0])
        final_energy = float(result["E"][-1])

        return (
            f"{model_name}:\n"
            f"Flight time: {flight_time:.2f} s\n"
            f"Range: {projectile_range:.2f} m\n"
            f"Max height: {max_height:.2f} m\n"
            f"Initial speed: {initial_speed:.2f} m/s\n"
            f"Min speed: {min_speed:.2f} m/s\n"
            f"Final speed: {final_speed:.2f} m/s\n"
            f"Initial energy: {initial_energy:.2f} J\n"
            f"Final energy: {final_energy:.2f} J"
        )
