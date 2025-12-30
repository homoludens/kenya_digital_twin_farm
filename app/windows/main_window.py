"""Main application window."""

from datetime import date
from typing import Dict, List

from PyQt5.QtCore import QDate
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QAction,
    QComboBox,
    QDateEdit,
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from config import (
    CROP_OPTIONS,
    LOCATION_OPTIONS,
    SOIL_TYPES,
    DEFAULT_FERT_SCENARIOS,
)
from dialogs import SoilSettingsDialog, FertilizerSettingsDialog
from simulation import SimulationWorker
from widgets import LocationMapWidget
from widgets.results import ResultsPanel


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

        self._setup_ui()
        self._setup_menus()
        self._setup_statusbar()

    def _setup_ui(self):
        """Setup the main UI layout."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)

        # Left panel - Configuration
        left_panel = QWidget()
        left_panel.setMaximumWidth(400)
        left_layout = QVBoxLayout(left_panel)

        # ========== Crop Selection ==========
        crop_group = QGroupBox("Crop Selection")
        crop_layout = QFormLayout(crop_group)

        # Crop dropdown
        self.crop_combo = QComboBox()
        for crop, config in CROP_OPTIONS.items():
            self.crop_combo.addItem(f"{crop.capitalize()}", crop)
        self.crop_combo.currentIndexChanged.connect(self._on_crop_changed)
        crop_layout.addRow("Crop:", self.crop_combo)

        # Variety dropdown
        self.variety_combo = QComboBox()
        self._update_variety_combo()
        crop_layout.addRow("Variety:", self.variety_combo)

        # Crop info label
        self.crop_info_label = QLabel()
        self.crop_info_label.setWordWrap(True)
        self.crop_info_label.setStyleSheet("color: #666; font-style: italic;")
        self._update_crop_info()
        crop_layout.addRow(self.crop_info_label)

        left_layout.addWidget(crop_group)

        # ========== Date Selection ==========
        date_group = QGroupBox("Planting Date")
        date_layout = QFormLayout(date_group)

        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self._set_default_date()
        date_layout.addRow("Start Date:", self.date_edit)

        left_layout.addWidget(date_group)

        # ========== Location Selection ==========
        location_group = QGroupBox("Location")
        location_layout = QVBoxLayout(location_group)

        # Location dropdown
        loc_combo_layout = QHBoxLayout()
        self.location_combo = QComboBox()
        for key, loc in LOCATION_OPTIONS.items():
            self.location_combo.addItem(loc["name"], key)
        self.location_combo.currentIndexChanged.connect(self._on_location_changed)
        loc_combo_layout.addWidget(QLabel("Location:"))
        loc_combo_layout.addWidget(self.location_combo, 1)
        location_layout.addLayout(loc_combo_layout)

        # Map widget
        self.map_widget = LocationMapWidget()
        self.map_widget.location_selected.connect(self._on_map_location_selected)
        self.map_widget.setMinimumHeight(200)
        location_layout.addWidget(self.map_widget)

        # Location info
        self.location_info_label = QLabel()
        self.location_info_label.setWordWrap(True)
        self.location_info_label.setStyleSheet("color: #666; font-style: italic;")
        self._update_location_info()
        location_layout.addWidget(self.location_info_label)

        left_layout.addWidget(location_group)

        # ========== Yield Gap Factor ==========
        yield_group = QGroupBox("Yield Gap Factor")
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
        settings_group = QGroupBox("Settings")
        settings_layout = QVBoxLayout(settings_group)

        soil_btn = QPushButton("Soil Parameters...")
        soil_btn.clicked.connect(self._show_soil_settings)
        settings_layout.addWidget(soil_btn)

        fert_btn = QPushButton("Fertilizer Scenarios...")
        fert_btn.clicked.connect(self._show_fert_settings)
        settings_layout.addWidget(fert_btn)

        left_layout.addWidget(settings_group)

        # ========== Run Button ==========
        self.run_btn = QPushButton("Run Simulation")
        self.run_btn.setMinimumHeight(50)
        self.run_btn.setFont(QFont("Arial", 12, QFont.Bold))
        self.run_btn.setStyleSheet(
            """
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
        """
        )
        self.run_btn.clicked.connect(self._run_simulation)
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

    def _setup_menus(self):
        """Setup application menus."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        export_action = QAction("Export Results...", self)
        export_action.triggered.connect(self._export_results)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Settings menu
        settings_menu = menubar.addMenu("Settings")

        soil_action = QAction("Soil Parameters...", self)
        soil_action.triggered.connect(self._show_soil_settings)
        settings_menu.addAction(soil_action)

        fert_action = QAction("Fertilizer Scenarios...", self)
        fert_action.triggered.connect(self._show_fert_settings)
        settings_menu.addAction(fert_action)

        # Help menu
        help_menu = menubar.addMenu("Help")

        about_action = QAction("About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _setup_statusbar(self):
        """Setup status bar."""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage("Ready")

    def _on_crop_changed(self):
        """Handle crop selection change."""
        self._update_variety_combo()
        self._update_crop_info()
        self._set_default_date()

    def _update_variety_combo(self):
        """Update variety dropdown based on selected crop."""
        self.variety_combo.clear()
        crop = self.crop_combo.currentData()
        if crop in CROP_OPTIONS:
            variety = CROP_OPTIONS[crop]["variety"]
            self.variety_combo.addItem(variety, variety)

    def _update_crop_info(self):
        """Update crop information label."""
        crop = self.crop_combo.currentData()
        if crop in CROP_OPTIONS:
            config = CROP_OPTIONS[crop]
            self.crop_info_label.setText(
                f"Kenya relevance: {config['kenya_relevance']}\n"
                f"N demand: {config['n_demand']}, Season: {config['season_days']} days"
            )

    def _set_default_date(self):
        """Set default planting date based on crop."""
        crop = self.crop_combo.currentData()
        if crop in CROP_OPTIONS:
            config = CROP_OPTIONS[crop]
            default_date = QDate(2023, config["planting_month"], config["planting_day"])
            self.date_edit.setDate(default_date)

    def _on_location_changed(self):
        """Handle location dropdown change."""
        location_key = self.location_combo.currentData()
        self.map_widget.set_location(location_key)
        self._update_location_info()

    def _on_map_location_selected(self, location_key: str):
        """Handle location selection from map."""
        idx = self.location_combo.findData(location_key)
        if idx >= 0:
            self.location_combo.setCurrentIndex(idx)
        self._update_location_info()

    def _update_location_info(self):
        """Update location information label."""
        location_key = self.location_combo.currentData()
        if location_key in LOCATION_OPTIONS:
            loc = LOCATION_OPTIONS[location_key]
            self.location_info_label.setText(
                f"Coordinates: {loc['lat']:.4f}N, {loc['lon']:.4f}E\n"
                f"Best for: {', '.join(loc['best_for'])}"
            )

    def _show_soil_settings(self):
        """Show soil settings dialog."""
        dialog = SoilSettingsDialog(self.current_soil, self.soil_params, self)
        if dialog.exec_() == QDialog.Accepted:
            self.soil_params = dialog.get_soil_params()
            self.current_soil = dialog.get_soil_type()
            self.statusbar.showMessage(f"Soil parameters updated: {self.current_soil}")

    def _show_fert_settings(self):
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

    def _run_simulation(self):
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
        self.worker.progress.connect(self._on_simulation_progress)
        self.worker.finished.connect(self._on_simulation_finished)
        self.worker.error.connect(self._on_simulation_error)
        self.worker.start()

    def _on_simulation_progress(self, value: int, message: str):
        """Handle simulation progress updates."""
        self.progress_bar.setValue(value)
        self.statusbar.showMessage(message)

    def _on_simulation_finished(
        self,
        results: List,
        dataframes: Dict,
        weather_df=None,
        weather_year=None,
        weather_location=None,
    ):
        """Handle simulation completion."""
        self.run_btn.setEnabled(True)
        self.progress_bar.setVisible(False)

        if results:
            crop_name = self.crop_combo.currentData()
            location = LOCATION_OPTIONS[self.location_combo.currentData()]
            yield_gap = self.yield_gap_spin.value()

            self.results_panel.update_results(
                results,
                dataframes,
                yield_gap,
                crop_name,
                location["name"],
                weather_df,
                weather_year,
            )
            self.statusbar.showMessage(f"Simulation complete: {len(results)} scenarios")
        else:
            QMessageBox.warning(self, "Warning", "No results returned from simulation.")
            self.statusbar.showMessage("Simulation completed with no results")

    def _on_simulation_error(self, error_msg: str):
        """Handle simulation error."""
        self.run_btn.setEnabled(True)
        self.progress_bar.setVisible(False)

        QMessageBox.critical(self, "Simulation Error", error_msg)
        self.statusbar.showMessage("Simulation failed")

    def _export_results(self):
        """Export results to file."""
        QMessageBox.information(
            self, "Export", "Export functionality to be implemented"
        )

    def _show_about(self):
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
