# To do

1. fix plots and gif exports so that elements don't overlap
2. update readme assets after fixing png and gif exporting
3. update readme after adding wind
4. fix code around wind logic

# Projectile Motion Simulator

A desktop application for simulating and comparing projectile motion models with an interactive PySide6 interface.

This project was created as a learning exercise in Python GUI development, numerical methods, automated testing, and the physics of projectile motion. The application lets the user configure launch conditions and physical parameters, compare three motion models, inspect calculated results, and export simulation data and visualizations.

## Features

- Simulation of projectile motion with three models: no air resistance, linear drag, and quadratic drag using **Runge-Kutta numerical integration**.
- Interactive parameter panel with input validation for physically incorrect values.
- Many configuration options such as: launch conditions, projectile and environment properties, numerial settings.
- Light and dark themes.
- Styled GUI using **Qt CSS**.
- Multiple result tabs: trajectory comparison, mechanical-energy comparison, speed comparison, interactive playback, text summary.
- Show or hide wind and velocity vectors.
- Export options for: **CSV files**, plots, and GIF animation.
- Buttons for opening exported plots and animations directories.
- User settings and app settings are saved to **JSON files**.

## Preview

### Light theme with trajectory comparison

![Main window](docs/readme-assets/app_1.png)

### Dark theme with playback panel

![Animation panel](docs/readme-assets//app_2.png)

### Exported GIF animation

![Exported animation](docs/readme-assets/projectile_motion.gif)

## Physics stuff

If you are interested in the physics part, take a look at the PDF file inside the `docs/` folder. It contains the equations and explanations of how the simulation works, based on my current understanding of the topic.

[Read the physics explanation PDF](docs/physics_projectile_motion.pdf)

## Project structure

```bash
├── docs/
│   ├── physics_projectile_motion.pdf
│   └── readme-assets/
├── src/
│   ├── config/
│   │   ├── parameters.py
│   │   └── settings.py
│   ├── gui/
│   │   ├── animation_canvas.py
│   │   ├── main_window.py
│   │   ├── parameter_panel.py
│   │   ├── plot_canvas.py
│   │   └── results_panel.py
│   ├── simulation/
│   │   └── solve.py
│   ├── storage/
│   │   └── csv_export.py
│   └── visualization/
│       └── export.py
├── style/
├── tests/
├── main.py
├── requirements.txt
└── requirements-dev.txt
```

## Installation

### 1. Clone the repository

```bash
git clone "https://github.com/ShOOmet14/projectile_motion_of_a_sphere"
cd projectile_motion_of_a_sphere/
```

### 2. Create a virtual environment

#### Windows

```bash
python -m venv venv
```

#### macOS / Linux

```bash
python3 -m venv venv
```

### 3. Activate the virtual environment

#### Windows PowerShell

```powershell
venv\Scripts\Activate.ps1
```

#### Windows Command Prompt

```cmd
venv\Scripts\activate.bat
```

#### macOS / Linux

```bash
source venv/bin/activate
```

### 4. Install dependencies

#### Windows

```bash
pip install -r requirements.txt
```

#### macOS / Linux

```bash
pip3 install -r requirements.txt
```

### 5. Run the application

#### Windows

```bash
python main.py
```

#### macOS / Linux

```bash
python3 main.py
```

### 6. Deactivate the virtual environment

After closing the app, you can deactivate the virtual environment with:

```bash
deactivate
```
