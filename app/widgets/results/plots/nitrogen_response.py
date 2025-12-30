"""Nitrogen response curve visualization."""

from widgets.results.plots.base import PlotContext, get_scenario_colors


def plot_nitrogen_response(graph_widget, ctx: PlotContext):
    """Render Figure 1: Nitrogen response curve."""
    fig = graph_widget.canvas.fig
    fig.clear()

    df_results = ctx.get_results_df()
    colors = get_scenario_colors(len(df_results))

    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)

    # (a) Bar chart
    bars = ax1.bar(
        range(len(df_results)),
        df_results["yield_t"],
        color=colors,
        edgecolor="white",
        linewidth=2,
    )
    ax1.set_xticks(range(len(df_results)))
    ax1.set_xticklabels(df_results["scenario"], rotation=20, ha="right", fontsize=8)

    for bar, val in zip(bars, df_results["yield_t"]):
        ax1.annotate(
            f"{val:.2f}",
            xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            fontsize=8,
            fontweight="bold",
        )

    ax1.set_ylabel("Yield (t/ha)", fontweight="bold")
    ax1.set_xlabel("Fertilizer Scenario", fontweight="bold")
    ax1.set_title(
        f"(a) {ctx.crop_name.capitalize()} Yield by N Rate",
        fontweight="bold",
        fontsize=10,
    )
    ax1.set_ylim(0, max(df_results["yield_t"]) * 1.25)
    ax1.grid(True, axis="y", alpha=0.3)

    # (b) Response curve
    ax2.plot(
        df_results["n_rate"],
        df_results["yield_t"],
        "o-",
        color="#27AE60",
        linewidth=2,
        markersize=10,
        markeredgecolor="white",
        markeredgewidth=2,
    )
    ax2.fill_between(
        df_results["n_rate"], 0, df_results["yield_t"], alpha=0.2, color="#27AE60"
    )

    for _, row in df_results.iterrows():
        ax2.annotate(
            f"{row['yield_t']:.2f}",
            xy=(row["n_rate"], row["yield_t"]),
            xytext=(5, 5),
            textcoords="offset points",
            fontsize=8,
        )

    ax2.set_xlabel("Nitrogen Applied (kg N/ha)", fontweight="bold")
    ax2.set_ylabel("Yield (t/ha)", fontweight="bold")
    ax2.set_title("(b) Nitrogen Response Curve", fontweight="bold", fontsize=10)
    ax2.set_xlim(-5, max(df_results["n_rate"]) * 1.1)
    ax2.set_ylim(0, max(df_results["yield_t"]) * 1.25)
    ax2.grid(True, alpha=0.3)

    fig.suptitle(
        f"{ctx.crop_name.upper()} Nitrogen Response - {ctx.location_name}",
        fontsize=11,
        fontweight="bold",
    )

    fig.tight_layout(rect=[0, 0, 1, 0.95])
    graph_widget.canvas.draw()
