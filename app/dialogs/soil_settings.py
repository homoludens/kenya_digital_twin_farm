"""Dialog for configuring soil parameters."""

from typing import Dict

from PyQt5.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from config.soils import SOIL_TYPES, SOIL_PARAM_INFO


class SoilSettingsDialog(QDialog):
    """Dialog for configuring soil parameters."""

    def __init__(self, current_soil: str, soil_params: Dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Soil Parameters Settings")
        self.setMinimumSize(600, 500)

        self.current_soil = current_soil
        self.soil_params = soil_params.copy()
        self.param_spinboxes = {}

        self._setup_ui()

    def _setup_ui(self):
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

        self.soil_combo.currentIndexChanged.connect(self._load_preset)
        type_layout.addWidget(QLabel("Preset:"))
        type_layout.addWidget(self.soil_combo, 1)

        load_btn = QPushButton("Load Preset")
        load_btn.clicked.connect(self._load_preset)
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

    def _load_preset(self):
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
