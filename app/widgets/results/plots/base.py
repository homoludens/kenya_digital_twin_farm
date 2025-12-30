"""Shared plotting utilities and data structures."""

from dataclasses import dataclass
from typing import Dict, List, Optional

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


@dataclass
class PlotContext:
    """Data context passed to all plotting functions."""

    results: List[Dict]
    dataframes: Dict[str, pd.DataFrame]
    yield_gap_factor: float
    crop_name: str
    location_name: str
    weather_df: Optional[pd.DataFrame]
    weather_year: Optional[int]

    def get_results_df(self) -> pd.DataFrame:
        """Convert results list to DataFrame."""
        return pd.DataFrame(
            [
                {
                    "scenario": r["scenario"],
                    "n_rate": r["n_rate"],
                    "yield_t": r["yield_t"],
                    "tagp": r.get("tagp", 0) / 1000,
                    "laimax": r.get("laimax", 0),
                }
                for r in self.results
            ]
        )


def format_date_axis(ax):
    """Apply standard date formatting to axis."""
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    ax.xaxis.set_major_locator(mdates.MonthLocator())


def get_scenario_colors(n: int):
    """Generate consistent colors for n scenarios."""
    return plt.cm.viridis(np.linspace(0.2, 0.8, n))
