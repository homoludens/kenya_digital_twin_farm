"""Growing Degree Days visualization with phenophase overlays."""

import numpy as np
import pandas as pd
import matplotlib.dates as mdates

from widgets.results.plots.base import PlotContext
from config.crops import PHENOPHASES


def plot_gdd(graph_widget, ctx: PlotContext):
    """Render Figure 6: Growing Degree Days with phenophases."""
    fig = graph_widget.canvas.fig
    fig.clear()

    if not ctx.dataframes:
        return

    # Get one scenario for GDD display
    scenario_name = list(ctx.dataframes.keys())[-1]
    df = ctx.dataframes[scenario_name]

    ax = fig.add_subplot(111)

    # Get crop phenophases or use default
    crop_info = PHENOPHASES.get(ctx.crop_name, PHENOPHASES["barley"])
    total_gdd = crop_info["total_gdd"]
    phases = crop_info["phases"]

    # Use calculated GDD from weather data
    if "GDD" in df.columns:
        gdd = df["GDD"]
        total_gdd = gdd.iloc[-1]  # Use actual accumulated GDD
    else:
        # Fallback: estimate from DVS
        if "DVS" in df.columns:
            gdd = df["DVS"] / 2.0 * total_gdd
        else:
            gdd = np.linspace(0, total_gdd, len(df))

    # Plot GDD accumulation
    ax.plot(df["day"], gdd, "b-", linewidth=2.5, label="Accumulated GDD")
    ax.fill_between(df["day"], 0, gdd, alpha=0.1, color="blue")

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
            ax.text(
                df["day"].iloc[0] + pd.Timedelta(days=5),
                mid_gdd,
                phase_name,
                fontsize=8,
                fontweight="bold",
                va="center",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.7),
            )

    # Add DVS markers
    if "DVS" in df.columns:
        # Flowering (DVS = 1.0)
        flowering_idx = (df["DVS"] - 1.0).abs().idxmin()
        if flowering_idx is not None:
            ax.axvline(
                x=df.loc[flowering_idx, "day"],
                color="orange",
                linestyle="--",
                linewidth=2,
                alpha=0.8,
            )
            ax.annotate(
                "Flowering\n(DVS=1.0)",
                xy=(df.loc[flowering_idx, "day"], gdd.iloc[flowering_idx]),
                xytext=(10, 20),
                textcoords="offset points",
                fontsize=9,
                fontweight="bold",
                arrowprops=dict(arrowstyle="->", color="orange"),
            )

        # Maturity (DVS = 2.0)
        if df["DVS"].max() >= 1.95:
            maturity_idx = (df["DVS"] - 2.0).abs().idxmin()
            ax.axvline(
                x=df.loc[maturity_idx, "day"],
                color="red",
                linestyle="--",
                linewidth=2,
                alpha=0.8,
            )
            ax.annotate(
                "Maturity\n(DVS=2.0)",
                xy=(df.loc[maturity_idx, "day"], gdd.iloc[maturity_idx]),
                xytext=(10, -30),
                textcoords="offset points",
                fontsize=9,
                fontweight="bold",
                arrowprops=dict(arrowstyle="->", color="red"),
            )

    ax.set_xlabel("Date", fontweight="bold")
    ax.set_ylabel("Growing Degree Days (C-day)", fontweight="bold")
    ax.set_title(
        f'{crop_info["name"]} - Growing Degree Days & Phenophases\n'
        f"(Base temp: 0C, Total: {total_gdd:.0f} GDD)",
        fontweight="bold",
        fontsize=11,
    )
    ax.set_ylim(0, y_max)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.grid(True, alpha=0.3)

    # Add GDD info box
    info_text = f"Total GDD: {total_gdd:.0f}C-d\nPhases: {len(phases)}"
    ax.text(
        0.98,
        0.02,
        info_text,
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        fontsize=9,
        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
    )

    fig.tight_layout()
    graph_widget.canvas.draw()
