"""Plot functions for results visualization."""

from widgets.results.plots.base import PlotContext
from widgets.results.plots.nitrogen_response import plot_nitrogen_response
from widgets.results.plots.growth_dynamics import plot_growth_dynamics
from widgets.results.plots.crop_growth import plot_crop_growth
from widgets.results.plots.multiyear import plot_multiyear_analysis
from widgets.results.plots.yield_gap import plot_yield_gap
from widgets.results.plots.gdd import plot_gdd
from widgets.results.plots.weather import plot_weather

__all__ = [
    "PlotContext",
    "plot_nitrogen_response",
    "plot_growth_dynamics",
    "plot_crop_growth",
    "plot_multiyear_analysis",
    "plot_yield_gap",
    "plot_gdd",
    "plot_weather",
]
