"""Detailed four-panel crop growth visualization."""

import matplotlib.dates as mdates

from widgets.results.plots.base import PlotContext


def plot_crop_growth(graph_widget, ctx: PlotContext):
    """Render Figure 3: Detailed four-panel crop growth."""
    fig = graph_widget.canvas.fig
    fig.clear()

    if not ctx.dataframes:
        return

    # Use recommended scenario or highest N
    scenario_name = None
    for name in ctx.dataframes.keys():
        if "recommended" in name.lower() or "Recommended" in name:
            scenario_name = name
            break
    if not scenario_name:
        scenario_name = list(ctx.dataframes.keys())[-1]

    df = ctx.dataframes[scenario_name]

    axes = fig.subplots(2, 2)

    # LAI over time
    if "LAI" in df.columns:
        axes[0, 0].fill_between(df["day"], 0, df["LAI"], color="green", alpha=0.3)
        axes[0, 0].plot(df["day"], df["LAI"], "g-", linewidth=2)
        axes[0, 0].set_ylabel("LAI (m2/m2)", fontweight="bold")
        axes[0, 0].set_title("(a) Leaf Area Development", fontweight="bold")

    # Biomass partitioning
    tagp_col = next(
        (c for c in ["TAGP", "tagp", "TAGBM", "WST", "WRT", "WLV"] if c in df.columns),
        None,
    )
    twso_col = next(
        (c for c in ["TWSO", "twso", "WSO", "TWSO_kg"] if c in df.columns), None
    )

    if tagp_col:
        axes[0, 1].fill_between(
            df["day"],
            0,
            df[tagp_col] / 1000,
            color="brown",
            alpha=0.3,
            label="Total Biomass",
        )
        axes[0, 1].plot(df["day"], df[tagp_col] / 1000, "brown", linewidth=2)

        if twso_col:
            axes[0, 1].fill_between(
                df["day"],
                0,
                df[twso_col] / 1000,
                color="gold",
                alpha=0.6,
                label="Storage Organs",
            )
            axes[0, 1].plot(df["day"], df[twso_col] / 1000, "gold", linewidth=2)

        axes[0, 1].set_ylabel("Biomass (t/ha)", fontweight="bold")
        axes[0, 1].set_title("(b) Biomass Partitioning", fontweight="bold")
        axes[0, 1].legend(fontsize=7)
    else:
        axes[0, 1].text(
            0.5,
            0.5,
            "Biomass data\nnot available",
            ha="center",
            va="center",
            transform=axes[0, 1].transAxes,
        )
        axes[0, 1].set_title("(b) Biomass Partitioning", fontweight="bold")

    # Development stage
    if "DVS" in df.columns:
        axes[1, 0].plot(df["day"], df["DVS"], "b-", linewidth=2)
        axes[1, 0].axhline(y=1.0, color="orange", linestyle="--", alpha=0.7)
        axes[1, 0].axhline(y=2.0, color="red", linestyle="--", alpha=0.7)
        axes[1, 0].fill_between(
            df["day"],
            0,
            df["DVS"],
            where=df["DVS"] <= 1,
            color="lightgreen",
            alpha=0.3,
        )
        axes[1, 0].fill_between(
            df["day"],
            0,
            df["DVS"],
            where=(df["DVS"] > 1) & (df["DVS"] <= 2),
            color="lightyellow",
            alpha=0.3,
        )
        axes[1, 0].set_ylabel("DVS", fontweight="bold")
        axes[1, 0].set_xlabel("Date", fontweight="bold")
        axes[1, 0].set_title("(c) Development Stage", fontweight="bold")
        axes[1, 0].text(df["day"].iloc[len(df) // 4], 0.5, "Vegetative", fontsize=8)
        axes[1, 0].text(
            df["day"].iloc[3 * len(df) // 4], 1.5, "Reproductive", fontsize=8
        )

    # Nitrogen uptake
    n_cols = ["NuptakeTotal", "NUPTAKE", "Nuptake"]
    n_found = False
    for col in n_cols:
        if col in df.columns:
            axes[1, 1].plot(df["day"], df[col], "g-", linewidth=2, label="N Uptake")
            axes[1, 1].fill_between(df["day"], 0, df[col], color="green", alpha=0.2)
            n_found = True
            break

    if not n_found and "TAGP" in df.columns:
        # Estimate N uptake from biomass (approx 2% N content)
        n_uptake = df["TAGP"] * 0.02
        axes[1, 1].plot(df["day"], n_uptake, "g-", linewidth=2, label="N Uptake (est.)")
        axes[1, 1].fill_between(df["day"], 0, n_uptake, color="green", alpha=0.2)
        n_found = True

    if n_found:
        axes[1, 1].set_ylabel("N Uptake (kg/ha)", fontweight="bold")
        axes[1, 1].set_title("(d) Nitrogen Uptake", fontweight="bold")
        axes[1, 1].legend(fontsize=7)
    else:
        axes[1, 1].text(
            0.5,
            0.5,
            "N uptake data\nnot available",
            ha="center",
            va="center",
            transform=axes[1, 1].transAxes,
        )
        axes[1, 1].set_title("(d) Nitrogen Uptake", fontweight="bold")

    for ax in axes.flat:
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.grid(True, alpha=0.3)

    fig.suptitle(
        f"{ctx.crop_name.upper()} Detailed Growth - {scenario_name}",
        fontsize=11,
        fontweight="bold",
    )

    fig.tight_layout(rect=[0, 0, 1, 0.95])
    graph_widget.canvas.draw()
