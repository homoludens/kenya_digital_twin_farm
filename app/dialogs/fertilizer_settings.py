"""Dialog for configuring fertilizer scenarios."""

from typing import Dict, List

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QHeaderView,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from config.fertilizers import DEFAULT_FERT_SCENARIOS


class FertilizerSettingsDialog(QDialog):
    """Dialog for configuring fertilizer scenarios."""

    def __init__(self, fert_scenarios: Dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Fertilizer Scenarios Settings")
        self.setMinimumSize(700, 500)

        self.fert_scenarios = {k: v.copy() for k, v in fert_scenarios.items()}
        self._setup_ui()

    def _setup_ui(self):
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

        self._populate_table()
        layout.addWidget(self.table)

        # Edit buttons
        btn_layout = QHBoxLayout()

        edit_btn = QPushButton("Edit Selected")
        edit_btn.clicked.connect(self._edit_scenario)
        btn_layout.addWidget(edit_btn)

        add_btn = QPushButton("Add New")
        add_btn.clicked.connect(self._add_scenario)
        btn_layout.addWidget(add_btn)

        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.clicked.connect(self._reset_defaults)
        btn_layout.addWidget(reset_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # Dialog buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _populate_table(self):
        self.table.setRowCount(len(self.fert_scenarios))

        for row, (key, scenario) in enumerate(self.fert_scenarios.items()):
            # Enabled checkbox
            checkbox = QCheckBox()
            checkbox.setChecked(scenario.get("enabled", True))
            checkbox.stateChanged.connect(
                lambda state, k=key: self._toggle_enabled(k, state)
            )

            widget = QWidget()
            cb_layout = QHBoxLayout(widget)
            cb_layout.addWidget(checkbox)
            cb_layout.setAlignment(Qt.AlignCenter)
            cb_layout.setContentsMargins(0, 0, 0, 0)
            self.table.setCellWidget(row, 0, widget)

            # Other columns
            self.table.setItem(row, 1, QTableWidgetItem(scenario["name"]))
            self.table.setItem(row, 2, QTableWidgetItem(str(scenario["total_n"])))
            self.table.setItem(
                row,
                3,
                QTableWidgetItem(self._format_applications(scenario["applications"])),
            )
            self.table.setItem(row, 4, QTableWidgetItem(scenario["description"]))

    def _format_applications(self, apps: List) -> str:
        if not apps:
            return "None"
        return "; ".join([f"Day {d}: {n}kg@{r * 100:.0f}%" for d, n, r in apps])

    def _toggle_enabled(self, key: str, state: int):
        self.fert_scenarios[key]["enabled"] = state == Qt.Checked

    def _edit_scenario(self):
        row = self.table.currentRow()
        if row < 0:
            return
        key = list(self.fert_scenarios.keys())[row]
        # Show edit dialog (simplified for now)
        QMessageBox.information(
            self, "Edit", f"Edit scenario: {key}\n(Full editor to be implemented)"
        )

    def _add_scenario(self):
        # Simplified - would normally show a dialog
        QMessageBox.information(
            self, "Add", "Add new scenario\n(Full editor to be implemented)"
        )

    def _reset_defaults(self):
        self.fert_scenarios = {k: v.copy() for k, v in DEFAULT_FERT_SCENARIOS.items()}
        self._populate_table()

    def get_scenarios(self) -> Dict:
        return self.fert_scenarios
