"""Growth dynamics comparison visualization."""

import matplotlib.dates as mdates
import matplotlib.pyplot as plt

from widgets.results.plots.base import PlotContext, get_scenario_colors


def plot_growth_dynamics(graph_widget, ctx: PlotContext):
    """Render Figure 2: Growth dynamics comparison."""
    fig = graph_widget.canvas.fig
    fig.clear()

    if not ctx.dataframes:
        return

    axes = fig.subplots(2, 2)

    colors = get_scenario_colors(len(ctx.dataframes))
    color_map = dict(zip(ctx.dataframes.keys(), colors))

    for name, df in ctx.dataframes.items():
        c = color_map[name]

        # LAI
        if "LAI" in df.columns:
            axes[0, 0].plot(df["day"], df["LAI"], color=c, linewidth=2, label=name)

        # Biomass
        if "TAGP" in df.columns:
            axes[0, 1].plot(
                df["day"], df["TAGP"] / 1000, color=c, linewidth=2, label=name
            )

        # Yield component
        twso_col = next(
            (col for col in ["TWSO", "twso", "WSO", "TWSO_kg"] if col in df.columns),
            None,
        )
        if twso_col:
            axes[1, 0].plot(
                df["day"], df[twso_col] / 1000, color=c, linewidth=2, label=name
            )

        # DVS
        if "DVS" in df.columns:
            axes[1, 1].plot(df["day"], df["DVS"], color=c, linewidth=2, label=name)

    # Format axes
    axes[0, 0].set_ylabel("LAI (m2/m2)", fontweight="bold")
    axes[0, 0].set_title("(a) Leaf Area Index", fontweight="bold", fontsize=10)
    axes[0, 0].legend(loc="upper right", fontsize=7)

    axes[0, 1].set_ylabel("Total Biomass (t/ha)", fontweight="bold")
    axes[0, 1].set_title("(b) Above-ground Biomass", fontweight="bold", fontsize=10)

    axes[1, 0].set_ylabel("Yield (t/ha)", fontweight="bold")
    axes[1, 0].set_xlabel("Date", fontweight="bold")
    axes[1, 0].set_title("(c) Yield Accumulation", fontweight="bold", fontsize=10)

    axes[1, 1].set_ylabel("DVS", fontweight="bold")
    axes[1, 1].set_xlabel("Date", fontweight="bold")
    axes[1, 1].set_title("(d) Development Stage", fontweight="bold", fontsize=10)
    axes[1, 1].axhline(y=1.0, color="orange", linestyle="--", alpha=0.7, label="Flowering")
    axes[1, 1].axhline(y=2.0, color="red", linestyle="--", alpha=0.7, label="Maturity")
    axes[1, 1].legend(loc="upper left", fontsize=7)

    for ax in axes.flat:
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.grid(True, alpha=0.3)

    fig.suptitle(
        f"{ctx.crop_name.upper()} Growth Under Different N Scenarios",
        fontsize=11,
        fontweight="bold",
    )

    fig.tight_layout(rect=[0, 0, 1, 0.95])
    graph_widget.canvas.draw()
