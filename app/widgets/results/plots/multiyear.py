"""Multi-year analysis visualization."""

import numpy as np

from widgets.results.plots.base import PlotContext


def plot_multiyear_analysis(graph_widget, ctx: PlotContext):
    """Render Figure 4: Multi-year analysis visualization."""
    fig = graph_widget.canvas.fig
    fig.clear()

    if not ctx.results:
        return

    df_results = ctx.get_results_df()

    axes = fig.subplots(1, 2)

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

    # Add shaded region for simulated variability (+/-10% as example)
    y_upper = y * 1.1
    y_lower = y * 0.9
    ax1.fill_between(
        x, y_lower, y_upper, alpha=0.2, color="#3498DB", label="+/-10% Range"
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

    ax2.bar(
        x_pos - width / 2,
        df_results["yield_t"],
        width,
        label="Grain Yield",
        color="#27AE60",
    )
    ax2.bar(
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

    fig.suptitle(
        f"{ctx.crop_name.upper()} Multi-Year Analysis Summary",
        fontsize=11,
        fontweight="bold",
    )

    fig.tight_layout(rect=[0, 0, 1, 0.95])
    graph_widget.canvas.draw()
