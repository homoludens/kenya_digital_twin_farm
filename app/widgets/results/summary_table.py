"""Summary table widget for displaying simulation results."""

from typing import Dict, List

import pandas as pd
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView


class SummaryTableWidget(QTableWidget):
    """Table widget for displaying simulation results summary."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMaximumHeight(150)

    def update_data(self, results: List[Dict], yield_gap_factor: float):
        """Update the table with simulation results."""
        if not results:
            return

        df = pd.DataFrame(
            [
                {
                    "Scenario": r["scenario"],
                    "N Rate (kg/ha)": r["n_rate"],
                    "Yield (t/ha)": f"{r['yield_t']:.2f}",
                    "Actual Yield (t/ha)": f"{r['yield_t'] * yield_gap_factor:.2f}",
                    "Biomass (t/ha)": f"{r['tagp'] / 1000:.2f}",
                    "LAI Max": f"{r['laimax']:.2f}",
                }
                for r in results
            ]
        )

        self.setRowCount(len(df))
        self.setColumnCount(len(df.columns))
        self.setHorizontalHeaderLabels(df.columns)

        for i, row in df.iterrows():
            for j, val in enumerate(row):
                self.setItem(i, j, QTableWidgetItem(str(val)))

        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
