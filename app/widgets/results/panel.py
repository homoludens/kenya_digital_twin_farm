"""Main results panel that coordinates all visualizations."""

from typing import Dict, List, Optional

import pandas as pd
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget

from widgets.canvas import GraphWidget
from widgets.results.summary_table import SummaryTableWidget
from widgets.results.plots import (
    PlotContext,
    plot_nitrogen_response,
    plot_growth_dynamics,
    plot_crop_growth,
    plot_multiyear_analysis,
    plot_yield_gap,
    plot_gdd,
    plot_weather,
)


class ResultsPanel(QWidget):
    """Panel displaying simulation results and interactive graphs."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.results: List[Dict] = []
        self.dataframes: Dict[str, pd.DataFrame] = {}
        self.yield_gap_factor: float = 0.35
        self.crop_name: str = "barley"
        self.location_name: str = ""
        self.weather_df: Optional[pd.DataFrame] = None
        self.weather_year: Optional[int] = None

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Tabs for different graphs
        self.tabs = QTabWidget()

        # Create graph widgets
        self.graph_widgets = {
            "n_response": GraphWidget("Figure 1: Nitrogen Response Curve"),
            "growth": GraphWidget("Figure 2: Growth Dynamics Comparison"),
            "crop": GraphWidget("Figure 3: Detailed Crop Growth"),
            "multiyear": GraphWidget("Figure 4: Multi-Year Analysis"),
            "yield_gap": GraphWidget("Figure 5: Yield Gap Comparison"),
            "gdd": GraphWidget("Figure 6: Growing Degree Days & Phenophases"),
            "weather": GraphWidget("Figure 7: Weather Patterns"),
        }

        # Add tabs
        self.tabs.addTab(self.graph_widgets["n_response"], "N Response")
        self.tabs.addTab(self.graph_widgets["growth"], "Growth Dynamics")
        self.tabs.addTab(self.graph_widgets["crop"], "Crop Growth")
        self.tabs.addTab(self.graph_widgets["multiyear"], "Multi-Year")
        self.tabs.addTab(self.graph_widgets["yield_gap"], "Yield Gap")
        self.tabs.addTab(self.graph_widgets["gdd"], "GDD")
        self.tabs.addTab(self.graph_widgets["weather"], "Weather")

        layout.addWidget(self.tabs)

        # Results summary table
        self.summary_table = SummaryTableWidget()
        layout.addWidget(self.summary_table)

    def update_results(
        self,
        results: List[Dict],
        dataframes: Dict[str, pd.DataFrame],
        yield_gap_factor: float = 0.35,
        crop_name: str = "barley",
        location_name: str = "",
        weather_df: Optional[pd.DataFrame] = None,
        weather_year: Optional[int] = None,
    ):
        """Update all visualizations with new simulation results."""
        self.results = results
        self.dataframes = dataframes
        self.yield_gap_factor = yield_gap_factor
        self.crop_name = crop_name
        self.location_name = location_name
        self.weather_df = weather_df
        self.weather_year = weather_year

        if not results:
            return

        # Context object passed to all plot functions
        ctx = PlotContext(
            results=results,
            dataframes=dataframes,
            yield_gap_factor=yield_gap_factor,
            crop_name=crop_name,
            location_name=location_name,
            weather_df=weather_df,
            weather_year=weather_year,
        )

        # Render all plots
        plot_nitrogen_response(self.graph_widgets["n_response"], ctx)
        plot_growth_dynamics(self.graph_widgets["growth"], ctx)
        plot_crop_growth(self.graph_widgets["crop"], ctx)
        plot_multiyear_analysis(self.graph_widgets["multiyear"], ctx)
        plot_yield_gap(self.graph_widgets["yield_gap"], ctx)
        plot_gdd(self.graph_widgets["gdd"], ctx)
        plot_weather(self.graph_widgets["weather"], ctx)

        # Update summary table
        self.summary_table.update_data(results, yield_gap_factor)
