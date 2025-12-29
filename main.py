#!/usr/bin/env python3
"""
Kenya Digital Farm Twin - WOFOST Crop Simulation Application
A PyQt5 application for running WOFOST 8.1 crop simulations with nitrogen and water limitation.
"""

import sys
from datetime import date, timedelta
from typing import Dict, List

# Matplotlib for embedded graphs
import matplotlib
import numpy as np
import pandas as pd
from PyQt5.QtCore import QDate, Qt, QThread, pyqtSignal
from PyQt5.QtGui import QColor, QFont, QPalette
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QComboBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QStatusBar,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

matplotlib.use("Qt5Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

# =============================================================================
# DATA DEFINITIONS
# =============================================================================

CROP_OPTIONS = {
    "barley": {
        "variety": "Spring_barley_301",
        "kenya_relevance": "Highland areas, similar N response to maize",
        "planting_month": 3,
        "planting_day": 15,
        "season_days": 120,
        "n_demand": "medium",
    },
    "wheat": {
        "variety": "Winter_wheat_101",
        "kenya_relevance": "Narok, Nakuru wheat belt",
        "planting_month": 6,
        "planting_day": 1,
        "season_days": 150,
        "n_demand": "medium-high",
        "needs_vern_override": True,
    },
    "potato": {
        "variety": "Potato_701",
        "kenya_relevance": "Central highlands (Nyandarua, Meru)",
        "planting_month": 3,
        "planting_day": 15,
        "season_days": 120,
        "n_demand": "high",
    },
    "cassava": {
        "variety": "Cassava_VanHeemst_1988",
        "kenya_relevance": "Coast, Western Kenya",
        "planting_month": 3,
        "planting_day": 15,
        "season_days": 300,
        "n_demand": "low",
    },
    "sweetpotato": {
        "variety": "Sweetpotato_VanHeemst_1988",
        "kenya_relevance": "Food security crop, Western Kenya",
        "planting_month": 3,
        "planting_day": 15,
        "season_days": 150,
        "n_demand": "low",
    },
}

LOCATION_OPTIONS = {
    "trans_nzoia": {
        "name": "Trans Nzoia (Kitale)",
        "lat": 1.0167,
        "lon": 35.0000,
        "best_for": ["barley", "wheat", "potato"],
    },
    "narok": {
        "name": "Narok",
        "lat": -1.0833,
        "lon": 35.8667,
        "best_for": ["wheat", "barley"],
    },
    "mwea": {
        "name": "Mwea (Kirinyaga)",
        "lat": -0.7333,
        "lon": 37.3500,
        "best_for": ["rice"],
    },
    "busia": {
        "name": "Busia (Western)",
        "lat": 0.4608,
        "lon": 34.1108,
        "best_for": ["soybean", "groundnut", "cassava"],
    },
    "machakos": {
        "name": "Machakos (Eastern)",
        "lat": -1.5177,
        "lon": 37.2634,
        "best_for": ["cowpea", "sorghum"],
    },
    "nyandarua": {
        "name": "Nyandarua (Central)",
        "lat": -0.4000,
        "lon": 36.5000,
        "best_for": ["potato", "wheat"],
    },
    "kilifi": {
        "name": "Kilifi (Coast)",
        "lat": -3.6305,
        "lon": 39.8499,
        "best_for": ["cassava", "cowpea"],
    },
}

SOIL_TYPES = {
    "nitisol": {
        "SM0": 0.45,
        "SMFCF": 0.36,
        "SMW": 0.15,
        "CRAIRC": 0.06,
        "RDMSOL": 120.0,
        "K0": 10.0,
        "SOPE": 1.0,
        "KSUB": 1.0,
        "NSOILBASE": 60.0,
        "description": "Highland clay-loam (good)",
    },
    "andosol": {
        "SM0": 0.50,
        "SMFCF": 0.40,
        "SMW": 0.12,
        "CRAIRC": 0.05,
        "RDMSOL": 150.0,
        "K0": 20.0,
        "SOPE": 2.0,
        "KSUB": 1.5,
        "NSOILBASE": 100.0,
        "description": "Volcanic soil (excellent)",
    },
    "vertisol": {
        "SM0": 0.50,
        "SMFCF": 0.45,
        "SMW": 0.25,
        "CRAIRC": 0.04,
        "RDMSOL": 80.0,
        "K0": 2.0,
        "SOPE": 0.5,
        "KSUB": 0.3,
        "NSOILBASE": 50.0,
        "description": "Black cotton clay (wheat)",
    },
    "ferralsol": {
        "SM0": 0.42,
        "SMFCF": 0.32,
        "SMW": 0.14,
        "CRAIRC": 0.06,
        "RDMSOL": 100.0,
        "K0": 8.0,
        "SOPE": 1.0,
        "KSUB": 0.8,
        "NSOILBASE": 35.0,
        "description": "Tropical red (low N)",
    },
    "luvisol": {
        "SM0": 0.38,
        "SMFCF": 0.25,
        "SMW": 0.10,
        "CRAIRC": 0.08,
        "RDMSOL": 80.0,
        "K0": 15.0,
        "SOPE": 2.0,
        "KSUB": 1.0,
        "NSOILBASE": 25.0,
        "description": "Semi-arid sandy-loam (very low N)",
    },
}

DEFAULT_FERT_SCENARIOS = {
    "none": {
        "name": "No Fertilizer",
        "total_n": 0,
        "applications": [],
        "description": "Baseline - soil N only",
        "enabled": True,
    },
    "low": {
        "name": "Low (25 kg N/ha)",
        "total_n": 25,
        "applications": [(0, 15, 0.7), (30, 10, 0.6)],
        "description": "Typical smallholder",
        "enabled": True,
    },
    "medium": {
        "name": "Medium (50 kg N/ha)",
        "total_n": 50,
        "applications": [(0, 20, 0.7), (30, 15, 0.65), (50, 15, 0.6)],
        "description": "Improved smallholder",
        "enabled": True,
    },
    "recommended": {
        "name": "Recommended (75 kg N/ha)",
        "total_n": 75,
        "applications": [(0, 25, 0.7), (30, 25, 0.65), (50, 25, 0.6)],
        "description": "Extension recommendation",
        "enabled": True,
    },
    "high": {
        "name": "High (100 kg N/ha)",
        "total_n": 100,
        "applications": [(0, 30, 0.7), (25, 35, 0.65), (50, 35, 0.6)],
        "description": "Commercial/intensive",
        "enabled": True,
    },
}

# Soil parameter descriptions
SOIL_PARAM_INFO = {
    "SM0": ("Saturation", "Soil moisture at saturation (cm³/cm³)", 0.3, 0.6),
    "SMFCF": ("Field Capacity", "Soil moisture at field capacity (cm³/cm³)", 0.2, 0.5),
    "SMW": ("Wilting Point", "Soil moisture at wilting point (cm³/cm³)", 0.05, 0.3),
    "CRAIRC": ("Air Content", "Critical air content for aeration (cm³/cm³)", 0.02, 0.1),
    "RDMSOL": ("Root Depth", "Maximum rooting depth allowed (cm)", 50, 200),
    "K0": ("Hydraulic Cond.", "Saturated hydraulic conductivity (cm/day)", 1, 50),
    "SOPE": ("Percolation", "Maximum percolation rate (cm/day)", 0.1, 5),
    "KSUB": ("Subsoil Cond.", "Subsoil hydraulic conductivity (cm/day)", 0.1, 5),
    "NSOILBASE": ("Soil N Pool", "Soil nitrogen pool (kg N/ha)", 10, 150),
    "NSOILBASE_FR": (
        "N Mineralization",
        "Fraction of soil N available (fraction)",
        0.01,
        0.1,
    ),
}


# =============================================================================
# SIMULATION WORKER THREAD
# =============================================================================


class SimulationWorker(QThread):
    """Worker thread for running WOFOST simulations."""

    progress = pyqtSignal(int, str)
    finished = pyqtSignal(list, dict)
    error = pyqtSignal(str)

    def __init__(self, config: Dict):
        super().__init__()
        self.config = config

    def run(self):
        try:
            # Import PCSE modules
            self.progress.emit(5, "Importing PCSE modules...")
            from pcse.base import ParameterProvider
            from pcse.input import NASAPowerWeatherDataProvider, YAMLCropDataProvider
            from pcse.models import Wofost81_NWLP_CWB_CNB

            # Get configuration
            crop_name = self.config["crop"]
            crop_config = CROP_OPTIONS[crop_name]
            location = self.config["location"]
            soil_params = self.config["soil_params"]
            fert_scenarios = self.config["fert_scenarios"]
            start_date = self.config["start_date"]
            year = start_date.year

            # Load weather data
            self.progress.emit(15, f"Loading weather for {location['name']}...")
            weather = NASAPowerWeatherDataProvider(
                latitude=location["lat"], longitude=location["lon"]
            )

            results = []
            dataframes = {}
            total_scenarios = len(
                [s for s in fert_scenarios.values() if s.get("enabled", True)]
            )
            completed = 0

            for key, scenario in fert_scenarios.items():
                if not scenario.get("enabled", True):
                    continue

                progress_pct = 20 + int(70 * completed / total_scenarios)
                self.progress.emit(progress_pct, f"Running: {scenario['name']}...")

                # Build agromanagement
                planting_date = date(year, start_date.month, start_date.day)
                end_date = date(year, 12, 31)
                max_duration = crop_config["season_days"]

                # Build timed events for N applications
                timed_events = None
                if scenario["applications"]:
                    timed_events = []
                    for i, (days, amount, recovery) in enumerate(
                        scenario["applications"]
                    ):
                        app_date = planting_date + timedelta(days=days)
                        timed_events.append(
                            {
                                "event_signal": "apply_n",
                                "name": f"N application {i + 1}",
                                "comment": f"{amount} kg N/ha",
                                "events_table": [
                                    {
                                        app_date: {
                                            "N_amount": amount,
                                            "N_recovery": recovery,
                                        }
                                    }
                                ],
                            }
                        )

                agro = {
                    "Version": 1.0,
                    "AgroManagement": [
                        {
                            planting_date: {
                                "CropCalendar": {
                                    "crop_name": crop_name,
                                    "variety_name": crop_config["variety"],
                                    "crop_start_date": planting_date,
                                    "crop_start_type": "emergence",
                                    "crop_end_date": end_date,
                                    "crop_end_type": "earliest",
                                    "max_duration": max_duration,
                                },
                                "TimedEvents": timed_events,
                                "StateEvents": None,
                            }
                        }
                    ],
                }

                # Create crop data provider
                cropd = YAMLCropDataProvider(Wofost81_NWLP_CWB_CNB)
                cropd.set_active_crop(crop_name, crop_config["variety"])

                # Build soil data
                soildata = {
                    "SM0": soil_params["SM0"],
                    "SMFCF": soil_params["SMFCF"],
                    "SMW": soil_params["SMW"],
                    "CRAIRC": soil_params["CRAIRC"],
                    "RDMSOL": soil_params["RDMSOL"],
                    "K0": soil_params["K0"],
                    "SOPE": soil_params["SOPE"],
                    "KSUB": soil_params["KSUB"],
                    "IFUNRN": 0,
                    "SSMAX": 0.0,
                    "SSI": 0.0,
                    "WAV": 50.0,
                    "NOTINF": 0.0,
                    "SMLIM": soil_params["SMFCF"],
                    "NSOILBASE": soil_params["NSOILBASE"],
                    "NSOILBASE_FR": soil_params.get("NSOILBASE_FR", 0.025),
                }

                sitedata = {
                    "CO2": 415.0,
                    "NAVAILI": 20.0,
                    "BG_N_SUPPLY": 0.5,
                }

                # Create parameters
                params = ParameterProvider(
                    cropdata=cropd, soildata=soildata, sitedata=sitedata
                )

                # Apply vernalization override if needed
                if crop_config.get("needs_vern_override"):
                    params.set_override("VERNSAT", 0)
                    params.set_override("VERNBASE", 0)
                    params.set_override("VERNDVS", 0)

                try:
                    model = Wofost81_NWLP_CWB_CNB(params, weather, agro)
                    model.run_till_terminate()

                    output = model.get_output()
                    df = pd.DataFrame(output)
                    summary = model.get_summary_output()

                    if summary and len(summary) > 0:
                        s = summary[0]
                        grain_yield = s.get("TWSO", 0)

                        if crop_name in ["potato", "cassava", "sweetpotato"]:
                            main_yield = (
                                grain_yield
                                if grain_yield > 0
                                else s.get("TAGP", 0) * 0.5
                            )
                        else:
                            main_yield = (
                                grain_yield
                                if grain_yield > 0
                                else s.get("TAGP", 0) * 0.4
                            )

                            # Calculate GDD from weather data
                            gdd_list = []
                            daily_gdd_list = []
                            tbase = 0.0  # Base temperature
                            cumulative_gdd = 0.0
                            for d in df['day']:
                                try:
                                    # Convert to date object for weather provider
                                    if hasattr(d, 'date'):
                                        d_date = d.date()
                                    elif hasattr(d, 'timetuple'):
                                        d_date = d
                                    else:
                                        d_date = pd.Timestamp(d).date()

                                    wdata = weather(d_date)
                                    tmax = wdata.TMAX
                                    tmin = wdata.TMIN
                                    daily_gdd = max(0.0, (tmax + tmin) / 2.0 - tbase)
                                    print(tmin, tmax, daily_gdd)
                                except Exception as e:
                                    print(e)
                                    daily_gdd = 0.0

                                cumulative_gdd += daily_gdd
                                daily_gdd_list.append(daily_gdd)
                                gdd_list.append(cumulative_gdd)

                            df['GDD'] = gdd_list
                            df['daily_GDD'] = daily_gdd_list
                            # print(gdd_list)

                            results.append({
                                'df': df,
                                'summary': s,
                                'yield_kg': main_yield,
                                'yield_t': main_yield / 1000,
                                'scenario': scenario['name'],
                                'scenario_key': key,
                                'n_rate': scenario['total_n'],
                                'tagp': s.get('TAGP', 0),
                                'laimax': s.get('LAIMAX', 0),
                            })

                        dataframes[scenario["name"]] = df

                except Exception as e:
                    print(f"Error in scenario {key}: {e}")

                completed += 1

            self.progress.emit(95, "Finalizing results...")
            self.progress.emit(100, "Done!")
            self.finished.emit(results, dataframes)

        except Exception as e:
            import traceback

            self.error.emit(f"Simulation error: {str(e)}\n{traceback.format_exc()}")


# =============================================================================
# MATPLOTLIB CANVAS WIDGETS
# =============================================================================


class MplCanvas(FigureCanvas):
    """A Matplotlib canvas for embedding in PyQt."""

    def __init__(self, parent=None, width=8, height=6, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.fig.set_facecolor("#f8f9fa")
        super().__init__(self.fig)
        self.setParent(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)


class GraphWidget(QWidget):
    """Widget containing a matplotlib canvas with navigation toolbar."""

    def __init__(self, title="Graph", parent=None):
        super().__init__(parent)
        self.title = title

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Title label
        self.title_label = QLabel(title)
        self.title_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)

        # Canvas
        self.canvas = MplCanvas(self, width=8, height=5, dpi=100)
        layout.addWidget(self.canvas)

        # Toolbar
        self.toolbar = NavigationToolbar(self.canvas, self)
        layout.addWidget(self.toolbar)

    def clear(self):
        self.canvas.fig.clear()
        self.canvas.draw()


# =============================================================================
# LOCATION MAP WIDGET (Simple interactive map using matplotlib)
# =============================================================================


class LocationMapWidget(QWidget):
    """Interactive map widget for selecting locations in Kenya."""

    location_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_location = "trans_nzoia"
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Canvas
        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)
        layout.addWidget(self.canvas)

        # Connect click event
        self.canvas.mpl_connect("button_press_event", self.on_click)

        # Draw initial map
        self.draw_map()

    def draw_map(self):
        self.canvas.fig.clear()
        ax = self.canvas.fig.add_subplot(111)

        # Draw simplified Kenya outline
        kenya_outline_lon = [34, 42, 42, 41, 40, 34, 34]
        kenya_outline_lat = [4.5, 4.5, -1, -4.5, -4.5, -1, 4.5]
        ax.plot(kenya_outline_lon, kenya_outline_lat, "k-", linewidth=2, alpha=0.5)
        ax.fill(kenya_outline_lon, kenya_outline_lat, color="#e8f5e9", alpha=0.3)

        # Plot locations
        for key, loc in LOCATION_OPTIONS.items():
            color = "#2196F3" if key == self.selected_location else "#757575"
            size = 150 if key == self.selected_location else 80
            marker = "*" if key == self.selected_location else "o"

            ax.scatter(
                loc["lon"],
                loc["lat"],
                c=color,
                s=size,
                marker=marker,
                edgecolors="white",
                linewidths=2,
                zorder=5,
            )
            ax.annotate(
                loc["name"].split("(")[0].strip(),
                (loc["lon"], loc["lat"]),
                xytext=(5, 5),
                textcoords="offset points",
                fontsize=8,
                fontweight="bold" if key == self.selected_location else "normal",
            )

        ax.set_xlim(33, 43)
        ax.set_ylim(-5, 5)
        ax.set_xlabel("Longitude (°E)", fontweight="bold")
        ax.set_ylabel("Latitude (°N)", fontweight="bold")
        ax.set_title("Kenya - Click to Select Location", fontweight="bold")
        ax.grid(True, alpha=0.3)
        ax.set_aspect("equal")

        self.canvas.fig.tight_layout()
        self.canvas.draw()

    def on_click(self, event):
        if event.xdata is None or event.ydata is None:
            return

        # Find closest location
        min_dist = float("inf")
        closest = None

        for key, loc in LOCATION_OPTIONS.items():
            dist = (
                (loc["lon"] - event.xdata) ** 2 + (loc["lat"] - event.ydata) ** 2
            ) ** 0.5
            if dist < min_dist:
                min_dist = dist
                closest = key

        if closest and min_dist < 2:  # Within 2 degrees
            self.selected_location = closest
            self.draw_map()
            self.location_selected.emit(closest)

    def set_location(self, location_key: str):
        if location_key in LOCATION_OPTIONS:
            self.selected_location = location_key
            self.draw_map()


# =============================================================================
# SETTINGS DIALOGS
# =============================================================================


class SoilSettingsDialog(QDialog):
    """Dialog for configuring soil parameters."""

    def __init__(self, current_soil: str, soil_params: Dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Soil Parameters Settings")
        self.setMinimumSize(600, 500)

        self.current_soil = current_soil
        self.soil_params = soil_params.copy()
        self.param_spinboxes = {}

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Soil type selector
        type_group = QGroupBox("Soil Type Preset")
        type_layout = QHBoxLayout(type_group)

        self.soil_combo = QComboBox()
        for key, soil in SOIL_TYPES.items():
            self.soil_combo.addItem(f"{key.capitalize()} - {soil['description']}", key)

        idx = self.soil_combo.findData(self.current_soil)
        if idx >= 0:
            self.soil_combo.setCurrentIndex(idx)

        self.soil_combo.currentIndexChanged.connect(self.load_preset)
        type_layout.addWidget(QLabel("Preset:"))
        type_layout.addWidget(self.soil_combo, 1)

        load_btn = QPushButton("Load Preset")
        load_btn.clicked.connect(self.load_preset)
        type_layout.addWidget(load_btn)

        layout.addWidget(type_group)

        # Parameters table
        params_group = QGroupBox("Soil Parameters (Editable)")
        params_layout = QGridLayout(params_group)

        row = 0
        for param, (name, desc, min_val, max_val) in SOIL_PARAM_INFO.items():
            # Label
            label = QLabel(f"{name} ({param}):")
            label.setToolTip(desc)
            params_layout.addWidget(label, row, 0)

            # Spinbox
            spinbox = QDoubleSpinBox()
            spinbox.setRange(min_val, max_val)
            spinbox.setDecimals(3 if max_val < 1 else 1)
            spinbox.setSingleStep(0.01 if max_val < 1 else 1)
            spinbox.setValue(self.soil_params.get(param, (min_val + max_val) / 2))
            spinbox.setToolTip(desc)
            params_layout.addWidget(spinbox, row, 1)

            self.param_spinboxes[param] = spinbox

            # Unit/range label
            unit_label = QLabel(f"({min_val} - {max_val})")
            unit_label.setStyleSheet("color: gray;")
            params_layout.addWidget(unit_label, row, 2)

            row += 1

        layout.addWidget(params_group)

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def load_preset(self):
        soil_key = self.soil_combo.currentData()
        if soil_key in SOIL_TYPES:
            soil = SOIL_TYPES[soil_key]
            for param, spinbox in self.param_spinboxes.items():
                if param in soil:
                    spinbox.setValue(soil[param])
                elif param == "NSOILBASE_FR":
                    spinbox.setValue(0.025)

    def get_soil_params(self) -> Dict:
        params = {}
        for param, spinbox in self.param_spinboxes.items():
            params[param] = spinbox.value()
        return params

    def get_soil_type(self) -> str:
        return self.soil_combo.currentData()


class FertilizerSettingsDialog(QDialog):
    """Dialog for configuring fertilizer scenarios."""

    def __init__(self, fert_scenarios: Dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Fertilizer Scenarios Settings")
        self.setMinimumSize(700, 500)

        self.fert_scenarios = {k: v.copy() for k, v in fert_scenarios.items()}
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["Enabled", "Scenario", "Total N (kg/ha)", "Applications", "Description"]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeToContents
        )

        self.populate_table()
        layout.addWidget(self.table)

        # Edit buttons
        btn_layout = QHBoxLayout()

        edit_btn = QPushButton("Edit Selected")
        edit_btn.clicked.connect(self.edit_scenario)
        btn_layout.addWidget(edit_btn)

        add_btn = QPushButton("Add New")
        add_btn.clicked.connect(self.add_scenario)
        btn_layout.addWidget(add_btn)

        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.clicked.connect(self.reset_defaults)
        btn_layout.addWidget(reset_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # Dialog buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def populate_table(self):
        self.table.setRowCount(len(self.fert_scenarios))

        for row, (key, scenario) in enumerate(self.fert_scenarios.items()):
            # Enabled checkbox
            from PyQt5.QtWidgets import QCheckBox

            checkbox = QCheckBox()
            checkbox.setChecked(scenario.get("enabled", True))
            checkbox.stateChanged.connect(
                lambda state, k=key: self.toggle_enabled(k, state)
            )

            widget = QWidget()
            layout = QHBoxLayout(widget)
            layout.addWidget(checkbox)
            layout.setAlignment(Qt.AlignCenter)
            layout.setContentsMargins(0, 0, 0, 0)
            self.table.setCellWidget(row, 0, widget)

            # Other columns
            self.table.setItem(row, 1, QTableWidgetItem(scenario["name"]))
            self.table.setItem(row, 2, QTableWidgetItem(str(scenario["total_n"])))
            self.table.setItem(
                row,
                3,
                QTableWidgetItem(self.format_applications(scenario["applications"])),
            )
            self.table.setItem(row, 4, QTableWidgetItem(scenario["description"]))

    def format_applications(self, apps: List) -> str:
        if not apps:
            return "None"
        return "; ".join([f"Day {d}: {n}kg@{r * 100:.0f}%" for d, n, r in apps])

    def toggle_enabled(self, key: str, state: int):
        self.fert_scenarios[key]["enabled"] = state == Qt.Checked

    def edit_scenario(self):
        row = self.table.currentRow()
        if row < 0:
            return
        key = list(self.fert_scenarios.keys())[row]
        # Show edit dialog (simplified for now)
        QMessageBox.information(
            self, "Edit", f"Edit scenario: {key}\n(Full editor to be implemented)"
        )

    def add_scenario(self):
        # Simplified - would normally show a dialog
        QMessageBox.information(
            self, "Add", "Add new scenario\n(Full editor to be implemented)"
        )

    def reset_defaults(self):
        self.fert_scenarios = {k: v.copy() for k, v in DEFAULT_FERT_SCENARIOS.items()}
        self.populate_table()

    def get_scenarios(self) -> Dict:
        return self.fert_scenarios


# =============================================================================
# RESULTS PANEL
# =============================================================================


class ResultsPanel(QWidget):
    """Panel displaying simulation results and interactive graphs."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.results = []
        self.dataframes = {}
        self.yield_gap_factor = 0.35

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Tabs for different graphs
        self.tabs = QTabWidget()

        # Figure 1: Nitrogen Response
        self.graph1 = GraphWidget("Figure 1: Nitrogen Response Curve")
        self.tabs.addTab(self.graph1, "N Response")

        # Figure 2: Growth Dynamics
        self.graph2 = GraphWidget("Figure 2: Growth Dynamics Comparison")
        self.tabs.addTab(self.graph2, "Growth Dynamics")

        # Figure 3: Four-panel crop growth
        self.graph3 = GraphWidget("Figure 3: Detailed Crop Growth")
        self.tabs.addTab(self.graph3, "Crop Growth")

        # Figure 4: Multi-year Analysis
        self.graph4 = GraphWidget("Figure 4: Multi-Year Analysis")
        self.tabs.addTab(self.graph4, "Multi-Year")

        # Figure 5: Yield Gap
        self.graph5 = GraphWidget("Figure 5: Yield Gap Comparison")
        self.tabs.addTab(self.graph5, "Yield Gap")

        self.graph6 = GraphWidget("Figure 6: Growing Degree Days & Phenophases")
        self.tabs.addTab(self.graph6, "GDD")

        layout.addWidget(self.tabs)

        # Results summary table
        self.summary_table = QTableWidget()
        self.summary_table.setMaximumHeight(150)
        layout.addWidget(self.summary_table)

    def update_results(
        self,
        results: List,
        dataframes: Dict,
        yield_gap_factor: float = 0.35,
        crop_name: str = "barley",
        location_name: str = "Trans Nzoia",
    ):
        self.results = results
        self.dataframes = dataframes
        self.yield_gap_factor = yield_gap_factor
        self.crop_name = crop_name
        self.location_name = location_name

        if results:
            self.plot_nitrogen_response()
            self.plot_growth_dynamics()
            self.plot_crop_growth()
            self.plot_multiyear_analysis()
            self.plot_yield_gap()
            self.plot_gdd()
            self.update_summary_table()

    def plot_nitrogen_response(self):
        """Figure 1: Nitrogen response curve."""
        self.graph1.canvas.fig.clear()

        df_results = pd.DataFrame(
            [
                {
                    "scenario": r["scenario"],
                    "n_rate": r["n_rate"],
                    "yield_t": r["yield_t"],
                }
                for r in self.results
            ]
        )

        # Create two subplots
        ax1 = self.graph1.canvas.fig.add_subplot(121)
        ax2 = self.graph1.canvas.fig.add_subplot(122)

        colors = plt.cm.viridis(np.linspace(0.2, 0.8, len(df_results)))

        # (a) Bar chart
        bars = ax1.bar(
            range(len(df_results)),
            df_results["yield_t"],
            color=colors,
            edgecolor="white",
            linewidth=2,
        )
        ax1.set_xticks(range(len(df_results)))
        ax1.set_xticklabels(df_results["scenario"], rotation=20, ha="right", fontsize=8)

        for bar, val in zip(bars, df_results["yield_t"]):
            ax1.annotate(
                f"{val:.2f}",
                xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                xytext=(0, 3),
                textcoords="offset points",
                ha="center",
                fontsize=8,
                fontweight="bold",
            )

        ax1.set_ylabel("Yield (t/ha)", fontweight="bold")
        ax1.set_xlabel("Fertilizer Scenario", fontweight="bold")
        ax1.set_title(
            f"(a) {self.crop_name.capitalize()} Yield by N Rate",
            fontweight="bold",
            fontsize=10,
        )
        ax1.set_ylim(0, max(df_results["yield_t"]) * 1.25)
        ax1.grid(True, axis="y", alpha=0.3)

        # (b) Response curve
        ax2.plot(
            df_results["n_rate"],
            df_results["yield_t"],
            "o-",
            color="#27AE60",
            linewidth=2,
            markersize=10,
            markeredgecolor="white",
            markeredgewidth=2,
        )
        ax2.fill_between(
            df_results["n_rate"], 0, df_results["yield_t"], alpha=0.2, color="#27AE60"
        )

        for _, row in df_results.iterrows():
            ax2.annotate(
                f"{row['yield_t']:.2f}",
                xy=(row["n_rate"], row["yield_t"]),
                xytext=(5, 5),
                textcoords="offset points",
                fontsize=8,
            )

        ax2.set_xlabel("Nitrogen Applied (kg N/ha)", fontweight="bold")
        ax2.set_ylabel("Yield (t/ha)", fontweight="bold")
        ax2.set_title("(b) Nitrogen Response Curve", fontweight="bold", fontsize=10)
        ax2.set_xlim(-5, max(df_results["n_rate"]) * 1.1)
        ax2.set_ylim(0, max(df_results["yield_t"]) * 1.25)
        ax2.grid(True, alpha=0.3)

        self.graph1.canvas.fig.suptitle(
            f"{self.crop_name.upper()} Nitrogen Response - {self.location_name}",
            fontsize=11,
            fontweight="bold",
        )

        self.graph1.canvas.fig.tight_layout(rect=[0, 0, 1, 0.95])
        self.graph1.canvas.draw()

    def plot_growth_dynamics(self):
        """Figure 2: Growth dynamics comparison."""
        self.graph2.canvas.fig.clear()

        if not self.dataframes:
            return

        axes = self.graph2.canvas.fig.subplots(2, 2)

        colors = plt.cm.viridis(np.linspace(0.2, 0.8, len(self.dataframes)))
        color_map = dict(zip(self.dataframes.keys(), colors))

        for name, df in self.dataframes.items():
            c = color_map[name]

            # LAI
            if "LAI" in df.columns:
                axes[0, 0].plot(df["day"], df["LAI"], color=c, linewidth=2, label=name)

            # Biomass
            if "TAGP" in df.columns:
                axes[0, 1].plot(
                    df["day"], df["TAGP"] / 1000, color=c, linewidth=2, label=name
                )

            # Yield component
            twso_col = next((col for col in ['TWSO', 'twso', 'WSO', 'TWSO_kg'] if col in df.columns), None)
            if twso_col:
                axes[1, 0].plot(df['day'], df[twso_col]/1000, color=c, linewidth=2, label=name)

            # DVS
            if "DVS" in df.columns:
                axes[1, 1].plot(df["day"], df["DVS"], color=c, linewidth=2, label=name)

        # Format axes
        axes[0, 0].set_ylabel("LAI (m²/m²)", fontweight="bold")
        axes[0, 0].set_title("(a) Leaf Area Index", fontweight="bold", fontsize=10)
        axes[0, 0].legend(loc="upper right", fontsize=7)

        axes[0, 1].set_ylabel("Total Biomass (t/ha)", fontweight="bold")
        axes[0, 1].set_title("(b) Above-ground Biomass", fontweight="bold", fontsize=10)

        axes[1, 0].set_ylabel("Yield (t/ha)", fontweight="bold")
        axes[1, 0].set_xlabel("Date", fontweight="bold")
        axes[1, 0].set_title("(c) Yield Accumulation", fontweight="bold", fontsize=10)

        axes[1, 1].set_ylabel("DVS", fontweight="bold")
        axes[1, 1].set_xlabel("Date", fontweight="bold")
        axes[1, 1].set_title("(d) Development Stage", fontweight="bold", fontsize=10)
        axes[1, 1].axhline(
            y=1.0, color="orange", linestyle="--", alpha=0.7, label="Flowering"
        )
        axes[1, 1].axhline(
            y=2.0, color="red", linestyle="--", alpha=0.7, label="Maturity"
        )
        axes[1, 1].legend(loc="upper left", fontsize=7)

        for ax in axes.flat:
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
            ax.xaxis.set_major_locator(mdates.MonthLocator())
            ax.grid(True, alpha=0.3)

        self.graph2.canvas.fig.suptitle(
            f"{self.crop_name.upper()} Growth Under Different N Scenarios",
            fontsize=11,
            fontweight="bold",
        )

        self.graph2.canvas.fig.tight_layout(rect=[0, 0, 1, 0.95])
        self.graph2.canvas.draw()

    def plot_crop_growth(self):
        """Figure 3: Detailed four-panel crop growth."""
        self.graph3.canvas.fig.clear()

        if not self.dataframes:
            return

        # Use recommended scenario or highest N
        scenario_name = None
        for name in self.dataframes.keys():
            if "recommended" in name.lower() or "Recommended" in name:
                scenario_name = name
                break
        if not scenario_name:
            scenario_name = list(self.dataframes.keys())[-1]

        df = self.dataframes[scenario_name]

        axes = self.graph3.canvas.fig.subplots(2, 2)

        # LAI over time
        if "LAI" in df.columns:
            axes[0, 0].fill_between(df["day"], 0, df["LAI"], color="green", alpha=0.3)
            axes[0, 0].plot(df["day"], df["LAI"], "g-", linewidth=2)
            axes[0, 0].set_ylabel("LAI (m²/m²)", fontweight="bold")
            axes[0, 0].set_title("(a) Leaf Area Development", fontweight="bold")


        # Biomass partitioning
        tagp_col = next((c for c in ['TAGP', 'tagp', 'TAGBM', 'WST', 'WRT', 'WLV'] if c in df.columns), None)
        twso_col = next((c for c in ['TWSO', 'twso', 'WSO', 'TWSO_kg'] if c in df.columns), None)

        if tagp_col:
            axes[0, 1].fill_between(df['day'], 0, df[tagp_col]/1000, color='brown', alpha=0.3, label='Total Biomass')
            axes[0, 1].plot(df['day'], df[tagp_col]/1000, 'brown', linewidth=2)

            if twso_col:
                axes[0, 1].fill_between(df['day'], 0, df[twso_col]/1000, color='gold', alpha=0.6, label='Storage Organs')
                axes[0, 1].plot(df['day'], df[twso_col]/1000, 'gold', linewidth=2)

            axes[0, 1].set_ylabel('Biomass (t/ha)', fontweight='bold')
            axes[0, 1].set_title('(b) Biomass Partitioning', fontweight='bold')
            axes[0, 1].legend(fontsize=7)
        else:
            axes[0, 1].text(0.5, 0.5, 'Biomass data\nnot available', ha='center', va='center', transform=axes[0, 1].transAxes)
            axes[0, 1].set_title('(b) Biomass Partitioning', fontweight='bold')


        # Development stage
        if "DVS" in df.columns:
            axes[1, 0].plot(df["day"], df["DVS"], "b-", linewidth=2)
            axes[1, 0].axhline(y=1.0, color="orange", linestyle="--", alpha=0.7)
            axes[1, 0].axhline(y=2.0, color="red", linestyle="--", alpha=0.7)
            axes[1, 0].fill_between(
                df["day"],
                0,
                df["DVS"],
                where=df["DVS"] <= 1,
                color="lightgreen",
                alpha=0.3,
            )
            axes[1, 0].fill_between(
                df["day"],
                0,
                df["DVS"],
                where=(df["DVS"] > 1) & (df["DVS"] <= 2),
                color="lightyellow",
                alpha=0.3,
            )
            axes[1, 0].set_ylabel("DVS", fontweight="bold")
            axes[1, 0].set_xlabel("Date", fontweight="bold")
            axes[1, 0].set_title("(c) Development Stage", fontweight="bold")
            axes[1, 0].text(df["day"].iloc[len(df) // 4], 0.5, "Vegetative", fontsize=8)
            axes[1, 0].text(
                df["day"].iloc[3 * len(df) // 4], 1.5, "Reproductive", fontsize=8
            )

        # Nitrogen uptake
        n_cols = ["NuptakeTotal", "NUPTAKE", "Nuptake"]
        n_found = False
        for col in n_cols:
            if col in df.columns:
                axes[1, 1].plot(df["day"], df[col], "g-", linewidth=2, label="N Uptake")
                axes[1, 1].fill_between(df["day"], 0, df[col], color="green", alpha=0.2)
                n_found = True
                break

        if not n_found and "TAGP" in df.columns:
            # Estimate N uptake from biomass (approx 2% N content)
            n_uptake = df["TAGP"] * 0.02
            axes[1, 1].plot(
                df["day"], n_uptake, "g-", linewidth=2, label="N Uptake (est.)"
            )
            axes[1, 1].fill_between(df["day"], 0, n_uptake, color="green", alpha=0.2)
            n_found = True

        if n_found:
            axes[1, 1].set_ylabel("N Uptake (kg/ha)", fontweight="bold")
            axes[1, 1].set_title("(d) Nitrogen Uptake", fontweight="bold")
            axes[1, 1].legend(fontsize=7)
        else:
            axes[1, 1].text(
                0.5,
                0.5,
                "N uptake data\nnot available",
                ha="center",
                va="center",
                transform=axes[1, 1].transAxes,
            )
            axes[1, 1].set_title("(d) Nitrogen Uptake", fontweight="bold")

        for ax in axes.flat:
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
            ax.xaxis.set_major_locator(mdates.MonthLocator())
            ax.grid(True, alpha=0.3)

        self.graph3.canvas.fig.suptitle(
            f"{self.crop_name.upper()} Detailed Growth - {scenario_name}",
            fontsize=11,
            fontweight="bold",
        )

        self.graph3.canvas.fig.tight_layout(rect=[0, 0, 1, 0.95])
        self.graph3.canvas.draw()

    def plot_multiyear_analysis(self):
        """Figure 4: Multi-year analysis visualization."""
        self.graph4.canvas.fig.clear()

        if not self.results:
            return

        # Create summary statistics
        df_results = pd.DataFrame(
            [
                {
                    "scenario": r["scenario"],
                    "n_rate": r["n_rate"],
                    "yield_t": r["yield_t"],
                    "tagp": r["tagp"] / 1000,
                    "laimax": r["laimax"],
                }
                for r in self.results
            ]
        )

        axes = self.graph4.canvas.fig.subplots(1, 2)

        # Yield by N rate with confidence
        ax1 = axes[0]
        x = df_results["n_rate"]
        y = df_results["yield_t"]

        ax1.plot(
            x,
            y,
            "o-",
            color="#3498DB",
            linewidth=2,
            markersize=10,
            markeredgecolor="white",
            markeredgewidth=2,
            label="Mean Yield",
        )

        # Add shaded region for simulated variability (±10% as example)
        y_upper = y * 1.1
        y_lower = y * 0.9
        ax1.fill_between(
            x, y_lower, y_upper, alpha=0.2, color="#3498DB", label="±10% Range"
        )

        ax1.set_xlabel("Nitrogen Applied (kg N/ha)", fontweight="bold")
        ax1.set_ylabel("Yield (t/ha)", fontweight="bold")
        ax1.set_title(
            "(a) Yield Response with Variability", fontweight="bold", fontsize=10
        )
        ax1.legend(fontsize=8)
        ax1.grid(True, alpha=0.3)

        # Yield components comparison
        ax2 = axes[1]
        x_pos = np.arange(len(df_results))
        width = 0.35

        bars1 = ax2.bar(
            x_pos - width / 2,
            df_results["yield_t"],
            width,
            label="Grain Yield",
            color="#27AE60",
        )
        bars2 = ax2.bar(
            x_pos + width / 2,
            df_results["tagp"],
            width,
            label="Total Biomass",
            color="#8E44AD",
        )

        ax2.set_xlabel("Scenario", fontweight="bold")
        ax2.set_ylabel("Biomass (t/ha)", fontweight="bold")
        ax2.set_title("(b) Yield vs Total Biomass", fontweight="bold", fontsize=10)
        ax2.set_xticks(x_pos)
        ax2.set_xticklabels(
            [
                s.replace(" kg N/ha)", "").replace("(", "\n")
                for s in df_results["scenario"]
            ],
            fontsize=7,
            rotation=0,
        )
        ax2.legend(fontsize=8)
        ax2.grid(True, axis="y", alpha=0.3)

        self.graph4.canvas.fig.suptitle(
            f"{self.crop_name.upper()} Multi-Year Analysis Summary",
            fontsize=11,
            fontweight="bold",
        )

        self.graph4.canvas.fig.tight_layout(rect=[0, 0, 1, 0.95])
        self.graph4.canvas.draw()

    def plot_yield_gap(self):
        """Figure 5: Yield gap comparison."""
        self.graph5.canvas.fig.clear()

        if not self.results:
            return

        df_results = pd.DataFrame(
            [
                {
                    "scenario": r["scenario"],
                    "n_rate": r["n_rate"],
                    "yield_t": r["yield_t"],
                }
                for r in self.results
            ]
        )

        ax = self.graph5.canvas.fig.add_subplot(111)

        # Calculate actual yields using yield gap factor
        df_results["actual_yield"] = df_results["yield_t"] * self.yield_gap_factor
        df_results["yield_gap"] = df_results["yield_t"] - df_results["actual_yield"]

        x = np.arange(len(df_results))
        width = 0.35

        # Stacked bar chart
        bars1 = ax.bar(
            x,
            df_results["actual_yield"],
            width,
            label=f"Actual Yield ({self.yield_gap_factor * 100:.0f}%)",
            color="#27AE60",
        )
        bars2 = ax.bar(
            x,
            df_results["yield_gap"],
            width,
            bottom=df_results["actual_yield"],
            label="Yield Gap",
            color="#E74C3C",
            alpha=0.7,
        )

        # Potential yield line
        ax.plot(
            x,
            df_results["yield_t"],
            "ko-",
            linewidth=2,
            markersize=8,
            label="Simulated Potential",
        )

        # Labels
        for i, (actual, gap, total) in enumerate(
            zip(
                df_results["actual_yield"],
                df_results["yield_gap"],
                df_results["yield_t"],
            )
        ):
            ax.annotate(
                f"{actual:.1f}",
                xy=(i, actual / 2),
                ha="center",
                va="center",
                fontsize=8,
                fontweight="bold",
                color="white",
            )
            ax.annotate(
                f"{total:.2f}",
                xy=(i, total + 0.1),
                ha="center",
                va="bottom",
                fontsize=8,
                fontweight="bold",
            )

        ax.set_xlabel("Fertilizer Scenario", fontweight="bold")
        ax.set_ylabel("Yield (t/ha)", fontweight="bold")
        ax.set_title(
            f"Yield Gap Analysis - {self.crop_name.capitalize()}",
            fontweight="bold",
            fontsize=12,
        )
        ax.set_xticks(x)
        ax.set_xticklabels(df_results["scenario"], rotation=20, ha="right", fontsize=8)
        ax.legend(loc="upper left", fontsize=9)
        ax.grid(True, axis="y", alpha=0.3)

        # Add annotation explaining yield gap
        ax.text(
            0.98,
            0.02,
            f"Yield Gap Factor: {self.yield_gap_factor:.0%}\n(Actual ÷ Potential)",
            transform=ax.transAxes,
            ha="right",
            va="bottom",
            fontsize=8,
            style="italic",
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
        )

        self.graph5.canvas.fig.tight_layout()
        self.graph5.canvas.draw()


    def plot_gdd(self):
            """Figure 6: Growing Degree Days with phenophases."""
            self.graph6.canvas.fig.clear()

            if not self.dataframes:
                return

            # Get one scenario for GDD display
            scenario_name = list(self.dataframes.keys())[-1]
            df = self.dataframes[scenario_name]

            ax = self.graph6.canvas.fig.add_subplot(111)

            # Phenophase definitions (fraction of total GDD)
            PHENOPHASES = {
                'barley': {'name': 'Barley', 'total_gdd': 1550, 'phases': [
                    ('Germination', 0, 0.07, '#8B4513'),
                    ('Tillering', 0.07, 0.25, '#228B22'),
                    ('Stem Extension', 0.25, 0.45, '#32CD32'),
                    ('Heading', 0.45, 0.55, '#FFD700'),
                    ('Flowering', 0.55, 0.65, '#FF8C00'),
                    ('Grain Fill', 0.65, 0.90, '#DAA520'),
                    ('Maturity', 0.90, 1.0, '#8B0000'),
                ]},
                'wheat': {'name': 'Wheat', 'total_gdd': 1800, 'phases': [
                    ('Germination', 0, 0.06, '#8B4513'),
                    ('Tillering', 0.06, 0.22, '#228B22'),
                    ('Stem Extension', 0.22, 0.42, '#32CD32'),
                    ('Heading', 0.42, 0.52, '#FFD700'),
                    ('Flowering', 0.52, 0.62, '#FF8C00'),
                    ('Grain Fill', 0.62, 0.88, '#DAA520'),
                    ('Maturity', 0.88, 1.0, '#8B0000'),
                ]},
                'rice': {'name': 'Rice', 'total_gdd': 2100, 'phases': [
                    ('Germination', 0, 0.05, '#8B4513'),
                    ('Seedling', 0.05, 0.15, '#90EE90'),
                    ('Tillering', 0.15, 0.35, '#228B22'),
                    ('Stem Extension', 0.35, 0.50, '#32CD32'),
                    ('Heading', 0.50, 0.60, '#FFD700'),
                    ('Flowering', 0.60, 0.70, '#FF8C00'),
                    ('Grain Fill', 0.70, 0.92, '#DAA520'),
                    ('Maturity', 0.92, 1.0, '#8B0000'),
                ]},
                'potato': {'name': 'Potato', 'total_gdd': 1500, 'phases': [
                    ('Sprouting', 0, 0.10, '#8B4513'),
                    ('Vegetative', 0.10, 0.35, '#228B22'),
                    ('Tuber Init.', 0.35, 0.50, '#32CD32'),
                    ('Tuber Bulk', 0.50, 0.85, '#DAA520'),
                    ('Maturity', 0.85, 1.0, '#8B0000'),
                ]},
                'soybean': {'name': 'Soybean', 'total_gdd': 1400, 'phases': [
                    ('Germination', 0, 0.08, '#8B4513'),
                    ('Vegetative', 0.08, 0.40, '#228B22'),
                    ('Flowering', 0.40, 0.55, '#FF8C00'),
                    ('Pod Dev.', 0.55, 0.75, '#FFD700'),
                    ('Seed Fill', 0.75, 0.92, '#DAA520'),
                    ('Maturity', 0.92, 1.0, '#8B0000'),
                ]},
                'cowpea': {'name': 'Cowpea', 'total_gdd': 1100, 'phases': [
                    ('Germination', 0, 0.08, '#8B4513'),
                    ('Vegetative', 0.08, 0.45, '#228B22'),
                    ('Flowering', 0.45, 0.60, '#FF8C00'),
                    ('Pod Fill', 0.60, 0.90, '#DAA520'),
                    ('Maturity', 0.90, 1.0, '#8B0000'),
                ]},
                'groundnut': {'name': 'Groundnut', 'total_gdd': 1500, 'phases': [
                    ('Germination', 0, 0.07, '#8B4513'),
                    ('Vegetative', 0.07, 0.35, '#228B22'),
                    ('Flowering', 0.35, 0.50, '#FF8C00'),
                    ('Pegging', 0.50, 0.65, '#FFD700'),
                    ('Pod Fill', 0.65, 0.90, '#DAA520'),
                    ('Maturity', 0.90, 1.0, '#8B0000'),
                ]},
                'cassava': {'name': 'Cassava', 'total_gdd': 4500, 'phases': [
                    ('Sprouting', 0, 0.05, '#8B4513'),
                    ('Leaf Dev.', 0.05, 0.20, '#90EE90'),
                    ('Vegetative', 0.20, 0.50, '#228B22'),
                    ('Root Bulk', 0.50, 0.90, '#DAA520'),
                    ('Maturity', 0.90, 1.0, '#8B0000'),
                ]},
                'sweetpotato': {'name': 'Sweet Potato', 'total_gdd': 2200, 'phases': [
                    ('Establishment', 0, 0.10, '#8B4513'),
                    ('Vine Dev.', 0.10, 0.35, '#228B22'),
                    ('Root Init.', 0.35, 0.50, '#32CD32'),
                    ('Root Bulk', 0.50, 0.90, '#DAA520'),
                    ('Maturity', 0.90, 1.0, '#8B0000'),
                ]},
            }

            # Get crop phenophases or use default
            crop_info = PHENOPHASES.get(self.crop_name, PHENOPHASES['barley'])
            total_gdd = crop_info['total_gdd']
            phases = crop_info['phases']

            # Use calculated GDD from weather data
            if 'GDD' in df.columns:
                gdd = df['GDD']
                total_gdd = gdd.iloc[-1]  # Use actual accumulated GDD
            else:
                # Fallback: estimate from DVS
                if 'DVS' in df.columns:
                    gdd = df['DVS'] / 2.0 * total_gdd
                else:
                    gdd = np.linspace(0, total_gdd, len(df))

            # Plot GDD accumulation
            ax.plot(df['day'], gdd, 'b-', linewidth=2.5, label='Accumulated GDD')
            ax.fill_between(df['day'], 0, gdd, alpha=0.1, color='blue')

            # Add phenophase bands
            y_max = total_gdd * 1.1
            for phase_name, start_frac, end_frac, color in phases:
                start_gdd = start_frac * total_gdd
                end_gdd = end_frac * total_gdd

                # Find corresponding days
                mask = (gdd >= start_gdd) & (gdd <= end_gdd)
                if mask.any():
                    ax.axhspan(start_gdd, end_gdd, alpha=0.25, color=color, label=phase_name)

                    # Add phase label
                    mid_gdd = (start_gdd + end_gdd) / 2
                    ax.text(df['day'].iloc[0] + pd.Timedelta(days=5), mid_gdd,
                           phase_name, fontsize=8, fontweight='bold', va='center',
                           bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7))

            # Add DVS markers
            if 'DVS' in df.columns:
                # Flowering (DVS = 1.0)
                flowering_idx = (df['DVS'] - 1.0).abs().idxmin()
                if flowering_idx is not None:
                    ax.axvline(x=df.loc[flowering_idx, 'day'], color='orange',
                              linestyle='--', linewidth=2, alpha=0.8)
                    ax.annotate('Flowering\n(DVS=1.0)',
                               xy=(df.loc[flowering_idx, 'day'], gdd.iloc[flowering_idx]),
                               xytext=(10, 20), textcoords='offset points',
                               fontsize=9, fontweight='bold',
                               arrowprops=dict(arrowstyle='->', color='orange'))

                # Maturity (DVS = 2.0)
                if df['DVS'].max() >= 1.95:
                    maturity_idx = (df['DVS'] - 2.0).abs().idxmin()
                    ax.axvline(x=df.loc[maturity_idx, 'day'], color='red',
                              linestyle='--', linewidth=2, alpha=0.8)
                    ax.annotate('Maturity\n(DVS=2.0)',
                               xy=(df.loc[maturity_idx, 'day'], gdd.iloc[maturity_idx]),
                               xytext=(10, -30), textcoords='offset points',
                               fontsize=9, fontweight='bold',
                               arrowprops=dict(arrowstyle='->', color='red'))

            ax.set_xlabel('Date', fontweight='bold')
            ax.set_ylabel('Growing Degree Days (°C·day)', fontweight='bold')
            ax.set_title(f'{crop_info["name"]} - Growing Degree Days & Phenophases\n(Base temp: 0°C, Total: {total_gdd} GDD)',
                        fontweight='bold', fontsize=11)
            ax.set_ylim(0, y_max)
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
            ax.xaxis.set_major_locator(mdates.MonthLocator())
            ax.grid(True, alpha=0.3)

            # Add GDD info box
            info_text = f'Total GDD: {total_gdd}°C·d\nPhases: {len(phases)}'
            ax.text(0.98, 0.02, info_text, transform=ax.transAxes, ha='right', va='bottom',
                   fontsize=9, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

            self.graph6.canvas.fig.tight_layout()
            self.graph6.canvas.draw()

    def update_summary_table(self):
        """Update the results summary table."""
        if not self.results:
            return

        df = pd.DataFrame(
            [
                {
                    "Scenario": r["scenario"],
                    "N Rate (kg/ha)": r["n_rate"],
                    "Yield (t/ha)": f"{r['yield_t']:.2f}",
                    "Actual Yield (t/ha)": f"{r['yield_t'] * self.yield_gap_factor:.2f}",
                    "Biomass (t/ha)": f"{r['tagp'] / 1000:.2f}",
                    "LAI Max": f"{r['laimax']:.2f}",
                }
                for r in self.results
            ]
        )

        self.summary_table.setRowCount(len(df))
        self.summary_table.setColumnCount(len(df.columns))
        self.summary_table.setHorizontalHeaderLabels(df.columns)

        for i, row in df.iterrows():
            for j, val in enumerate(row):
                self.summary_table.setItem(i, j, QTableWidgetItem(str(val)))

        self.summary_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)


# =============================================================================
# MAIN WINDOW
# =============================================================================


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kenya Digital Farm Twin - WOFOST Crop Simulator")
        self.setMinimumSize(1400, 900)

        # Initialize state
        self.current_soil = "nitisol"
        self.soil_params = SOIL_TYPES["nitisol"].copy()
        self.fert_scenarios = {k: v.copy() for k, v in DEFAULT_FERT_SCENARIOS.items()}

        self.setup_ui()
        self.setup_menus()
        self.setup_statusbar()

    def setup_ui(self):
        """Setup the main UI layout."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)

        # Left panel - Configuration
        left_panel = QWidget()
        left_panel.setMaximumWidth(400)
        left_layout = QVBoxLayout(left_panel)

        # ========== Crop Selection ==========
        crop_group = QGroupBox("🌾 Crop Selection")
        crop_layout = QFormLayout(crop_group)

        # Crop dropdown
        self.crop_combo = QComboBox()
        for crop, config in CROP_OPTIONS.items():
            self.crop_combo.addItem(f"{crop.capitalize()}", crop)
        self.crop_combo.currentIndexChanged.connect(self.on_crop_changed)
        crop_layout.addRow("Crop:", self.crop_combo)

        # Variety dropdown
        self.variety_combo = QComboBox()
        self.update_variety_combo()
        crop_layout.addRow("Variety:", self.variety_combo)

        # Crop info label
        self.crop_info_label = QLabel()
        self.crop_info_label.setWordWrap(True)
        self.crop_info_label.setStyleSheet("color: #666; font-style: italic;")
        self.update_crop_info()
        crop_layout.addRow(self.crop_info_label)

        left_layout.addWidget(crop_group)

        # ========== Date Selection ==========
        date_group = QGroupBox("📅 Planting Date")
        date_layout = QFormLayout(date_group)

        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.set_default_date()
        date_layout.addRow("Start Date:", self.date_edit)

        left_layout.addWidget(date_group)

        # ========== Location Selection ==========
        location_group = QGroupBox("📍 Location")
        location_layout = QVBoxLayout(location_group)

        # Location dropdown
        loc_combo_layout = QHBoxLayout()
        self.location_combo = QComboBox()
        for key, loc in LOCATION_OPTIONS.items():
            self.location_combo.addItem(loc["name"], key)
        self.location_combo.currentIndexChanged.connect(self.on_location_changed)
        loc_combo_layout.addWidget(QLabel("Location:"))
        loc_combo_layout.addWidget(self.location_combo, 1)
        location_layout.addLayout(loc_combo_layout)

        # Map widget
        self.map_widget = LocationMapWidget()
        self.map_widget.location_selected.connect(self.on_map_location_selected)
        self.map_widget.setMinimumHeight(200)
        location_layout.addWidget(self.map_widget)

        # Location info
        self.location_info_label = QLabel()
        self.location_info_label.setWordWrap(True)
        self.location_info_label.setStyleSheet("color: #666; font-style: italic;")
        self.update_location_info()
        location_layout.addWidget(self.location_info_label)

        left_layout.addWidget(location_group)

        # ========== Yield Gap Factor ==========
        yield_group = QGroupBox("📊 Yield Gap Factor")
        yield_layout = QFormLayout(yield_group)

        self.yield_gap_spin = QDoubleSpinBox()
        self.yield_gap_spin.setRange(0.1, 1.0)
        self.yield_gap_spin.setSingleStep(0.05)
        self.yield_gap_spin.setValue(0.35)
        self.yield_gap_spin.setDecimals(2)
        self.yield_gap_spin.setToolTip(
            "Ratio of actual farmer yield to simulated potential yield"
        )
        yield_layout.addRow("Factor (0.1-1.0):", self.yield_gap_spin)

        yield_info = QLabel(
            "Typical smallholder: 0.25-0.40\nCommercial farms: 0.60-0.80"
        )
        yield_info.setStyleSheet("color: #666; font-size: 10px;")
        yield_layout.addRow(yield_info)

        left_layout.addWidget(yield_group)

        # ========== Settings Buttons ==========
        settings_group = QGroupBox("⚙️ Settings")
        settings_layout = QVBoxLayout(settings_group)

        soil_btn = QPushButton("🌍 Soil Parameters...")
        soil_btn.clicked.connect(self.show_soil_settings)
        settings_layout.addWidget(soil_btn)

        fert_btn = QPushButton("🧪 Fertilizer Scenarios...")
        fert_btn.clicked.connect(self.show_fert_settings)
        settings_layout.addWidget(fert_btn)

        left_layout.addWidget(settings_group)

        # ========== Run Button ==========
        self.run_btn = QPushButton("▶ Run Simulation")
        self.run_btn.setMinimumHeight(50)
        self.run_btn.setFont(QFont("Arial", 12, QFont.Bold))
        self.run_btn.setStyleSheet("""
            QPushButton {
                background-color: #27AE60;
                color: white;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2ECC71;
            }
            QPushButton:pressed {
                background-color: #1E8449;
            }
            QPushButton:disabled {
                background-color: #95A5A6;
            }
        """)
        self.run_btn.clicked.connect(self.run_simulation)
        left_layout.addWidget(self.run_btn)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        left_layout.addWidget(self.progress_bar)

        left_layout.addStretch()

        main_layout.addWidget(left_panel)

        # Right panel - Results
        self.results_panel = ResultsPanel()
        main_layout.addWidget(self.results_panel, 1)

    def setup_menus(self):
        """Setup application menus."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        export_action = QAction("Export Results...", self)
        export_action.triggered.connect(self.export_results)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Settings menu
        settings_menu = menubar.addMenu("Settings")

        soil_action = QAction("Soil Parameters...", self)
        soil_action.triggered.connect(self.show_soil_settings)
        settings_menu.addAction(soil_action)

        fert_action = QAction("Fertilizer Scenarios...", self)
        fert_action.triggered.connect(self.show_fert_settings)
        settings_menu.addAction(fert_action)

        # Help menu
        help_menu = menubar.addMenu("Help")

        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def setup_statusbar(self):
        """Setup status bar."""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage("Ready")

    def on_crop_changed(self):
        """Handle crop selection change."""
        self.update_variety_combo()
        self.update_crop_info()
        self.set_default_date()

    def update_variety_combo(self):
        """Update variety dropdown based on selected crop."""
        self.variety_combo.clear()
        crop = self.crop_combo.currentData()
        if crop in CROP_OPTIONS:
            variety = CROP_OPTIONS[crop]["variety"]
            self.variety_combo.addItem(variety, variety)

    def update_crop_info(self):
        """Update crop information label."""
        crop = self.crop_combo.currentData()
        if crop in CROP_OPTIONS:
            config = CROP_OPTIONS[crop]
            self.crop_info_label.setText(
                f"Kenya relevance: {config['kenya_relevance']}\n"
                f"N demand: {config['n_demand']}, Season: {config['season_days']} days"
            )

    def set_default_date(self):
        """Set default planting date based on crop."""
        crop = self.crop_combo.currentData()
        if crop in CROP_OPTIONS:
            config = CROP_OPTIONS[crop]
            default_date = QDate(2023, config["planting_month"], config["planting_day"])
            self.date_edit.setDate(default_date)

    def on_location_changed(self):
        """Handle location dropdown change."""
        location_key = self.location_combo.currentData()
        self.map_widget.set_location(location_key)
        self.update_location_info()

    def on_map_location_selected(self, location_key: str):
        """Handle location selection from map."""
        idx = self.location_combo.findData(location_key)
        if idx >= 0:
            self.location_combo.setCurrentIndex(idx)
        self.update_location_info()

    def update_location_info(self):
        """Update location information label."""
        location_key = self.location_combo.currentData()
        if location_key in LOCATION_OPTIONS:
            loc = LOCATION_OPTIONS[location_key]
            self.location_info_label.setText(
                f"Coordinates: {loc['lat']:.4f}°N, {loc['lon']:.4f}°E\n"
                f"Best for: {', '.join(loc['best_for'])}"
            )

    def show_soil_settings(self):
        """Show soil settings dialog."""
        dialog = SoilSettingsDialog(self.current_soil, self.soil_params, self)
        if dialog.exec_() == QDialog.Accepted:
            self.soil_params = dialog.get_soil_params()
            self.current_soil = dialog.get_soil_type()
            self.statusbar.showMessage(f"Soil parameters updated: {self.current_soil}")

    def show_fert_settings(self):
        """Show fertilizer settings dialog."""
        dialog = FertilizerSettingsDialog(self.fert_scenarios, self)
        if dialog.exec_() == QDialog.Accepted:
            self.fert_scenarios = dialog.get_scenarios()
            enabled_count = sum(
                1 for s in self.fert_scenarios.values() if s.get("enabled", True)
            )
            self.statusbar.showMessage(
                f"Fertilizer scenarios updated: {enabled_count} enabled"
            )

    def run_simulation(self):
        """Run the WOFOST simulation."""
        # Prepare configuration
        crop_name = self.crop_combo.currentData()
        location_key = self.location_combo.currentData()
        location = LOCATION_OPTIONS[location_key]

        q_date = self.date_edit.date()
        start_date = date(q_date.year(), q_date.month(), q_date.day())

        config = {
            "crop": crop_name,
            "location": location,
            "soil_params": self.soil_params,
            "fert_scenarios": self.fert_scenarios,
            "start_date": start_date,
        }

        # Disable UI during simulation
        self.run_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        # Create and start worker thread
        self.worker = SimulationWorker(config)
        self.worker.progress.connect(self.on_simulation_progress)
        self.worker.finished.connect(self.on_simulation_finished)
        self.worker.error.connect(self.on_simulation_error)
        self.worker.start()

    def on_simulation_progress(self, value: int, message: str):
        """Handle simulation progress updates."""
        self.progress_bar.setValue(value)
        self.statusbar.showMessage(message)

    def on_simulation_finished(self, results: List, dataframes: Dict):
        """Handle simulation completion."""
        self.run_btn.setEnabled(True)
        self.progress_bar.setVisible(False)

        if results:
            crop_name = self.crop_combo.currentData()
            location = LOCATION_OPTIONS[self.location_combo.currentData()]
            yield_gap = self.yield_gap_spin.value()

            self.results_panel.update_results(
                results, dataframes, yield_gap, crop_name, location["name"]
            )
            self.statusbar.showMessage(f"Simulation complete: {len(results)} scenarios")
        else:
            QMessageBox.warning(self, "Warning", "No results returned from simulation.")
            self.statusbar.showMessage("Simulation completed with no results")

    def on_simulation_error(self, error_msg: str):
        """Handle simulation error."""
        self.run_btn.setEnabled(True)
        self.progress_bar.setVisible(False)

        QMessageBox.critical(self, "Simulation Error", error_msg)
        self.statusbar.showMessage("Simulation failed")

    def export_results(self):
        """Export results to file."""
        QMessageBox.information(
            self, "Export", "Export functionality to be implemented"
        )

    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About Kenya Digital Farm Twin",
            "<h2>Kenya Digital Farm Twin</h2>"
            "<p>WOFOST 8.1 Crop Simulation Application</p>"
            "<p>This application simulates crop growth under nitrogen and water "
            "limitation for various locations in Kenya.</p>"
            "<p><b>Model:</b> WOFOST 8.1 NWLP_MLWB_CNB</p>"
            "<p><b>Features:</b></p>"
            "<ul>"
            "<li>Multiple crop types</li>"
            "<li>Customizable soil parameters</li>"
            "<li>Fertilizer scenario comparison</li>"
            "<li>Interactive visualizations</li>"
            "</ul>",
        )


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Set application palette
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(248, 249, 250))
    palette.setColor(QPalette.WindowText, QColor(33, 37, 41))
    palette.setColor(QPalette.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.AlternateBase, QColor(248, 249, 250))
    palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
    palette.setColor(QPalette.ToolTipText, QColor(33, 37, 41))
    palette.setColor(QPalette.Text, QColor(33, 37, 41))
    palette.setColor(QPalette.Button, QColor(248, 249, 250))
    palette.setColor(QPalette.ButtonText, QColor(33, 37, 41))
    palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
    palette.setColor(QPalette.Highlight, QColor(39, 174, 96))
    palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
