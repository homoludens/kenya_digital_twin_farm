"""Yield gap comparison visualization."""

import numpy as np

from widgets.results.plots.base import PlotContext


def plot_yield_gap(graph_widget, ctx: PlotContext):
    """Render Figure 5: Yield gap comparison."""
    fig = graph_widget.canvas.fig
    fig.clear()

    if not ctx.results:
        return

    df_results = ctx.get_results_df()

    ax = fig.add_subplot(111)

    # Calculate actual yields using yield gap factor
    df_results["actual_yield"] = df_results["yield_t"] * ctx.yield_gap_factor
    df_results["yield_gap"] = df_results["yield_t"] - df_results["actual_yield"]

    x = np.arange(len(df_results))
    width = 0.35

    # Stacked bar chart
    ax.bar(
        x,
        df_results["actual_yield"],
        width,
        label=f"Actual Yield ({ctx.yield_gap_factor * 100:.0f}%)",
        color="#27AE60",
    )
    ax.bar(
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
        f"Yield Gap Analysis - {ctx.crop_name.capitalize()}",
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
        f"Yield Gap Factor: {ctx.yield_gap_factor:.0%}\n(Actual / Potential)",
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        fontsize=8,
        style="italic",
        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
    )

    fig.tight_layout()
    graph_widget.canvas.draw()
