"""Display formatted summaries of projectile-motion simulation results."""

from PySide6.QtWidgets import QLabel, QPlainTextEdit, QVBoxLayout, QWidget

from src.simulation.solve import ProjectileResult


class ResultsPanel(QWidget):
    """Display summary metrics for each projectile-motion model."""

    def __init__(self) -> None:
        """Create the read-only results panel."""

        super().__init__()

        layout = QVBoxLayout()

        self.title_label = QLabel("Results")
        self.title_label.setProperty("class", "h1")

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
        """Display summaries for all three projectile-motion models."""

        model_results = (
            ("No drag", no_drag),
            ("Linear drag", linear_drag),
            ("Quadratic drag RK4", quadratic_drag),
        )

        summaries = (
            self.format_result(model_name, result)
            for model_name, result in model_results
        )

        self.results_text.setPlainText("\n\n".join(summaries))

    @staticmethod
    def format_result(
        model_name: str,
        result: ProjectileResult,
    ) -> str:
        """Return a readable summary of one simulation result."""

        flight_time = float(result["t"][-1])

        projectile_range = abs(float(result["x"][-1] - result["x"][0]))

        max_height = float(result["y"].max())

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
