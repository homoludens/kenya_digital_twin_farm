"""Weather patterns visualization."""

import pandas as pd
import matplotlib.dates as mdates

from widgets.results.plots.base import PlotContext


def plot_weather(graph_widget, ctx: PlotContext):
    """Render Figure 7: Weather patterns."""
    fig = graph_widget.canvas.fig
    fig.clear()

    if ctx.weather_df is None or len(ctx.weather_df) == 0:
        ax = fig.add_subplot(111)
        ax.text(
            0.5,
            0.5,
            "Weather data not available",
            ha="center",
            va="center",
            transform=ax.transAxes,
            fontsize=12,
        )
        graph_widget.canvas.draw()
        return

    df_weather = ctx.weather_df
    year = ctx.weather_year

    axes = fig.subplots(3, 1, sharex=True)

    # Temperature
    axes[0].fill_between(
        df_weather.index,
        df_weather["tmin"],
        df_weather["tmax"],
        alpha=0.3,
        color="#E74C3C",
        label="Daily range",
    )
    axes[0].plot(
        df_weather.index,
        df_weather["tmax"],
        color="#E74C3C",
        linewidth=0.8,
        label="Max",
    )
    axes[0].plot(
        df_weather.index,
        df_weather["tmin"],
        color="#3498DB",
        linewidth=0.8,
        label="Min",
    )
    axes[0].set_ylabel("Temperature (C)", fontweight="bold")
    axes[0].legend(loc="upper right", framealpha=0.9, fontsize=8)
    axes[0].set_ylim(5, 35)
    axes[0].grid(True, alpha=0.3)

    # Rainfall with season markers
    axes[1].bar(
        df_weather.index, df_weather["rain"], width=1, color="#3498DB", alpha=0.7
    )
    axes[1].axvspan(
        f"{year}-03-01",
        f"{year}-05-31",
        alpha=0.15,
        color="green",
        label="Long Rains (Masika)",
    )
    axes[1].axvspan(
        f"{year}-10-01",
        f"{year}-12-15",
        alpha=0.15,
        color="orange",
        label="Short Rains (Vuli)",
    )
    axes[1].set_ylabel("Rainfall (mm/day)", fontweight="bold")
    axes[1].legend(loc="upper right", framealpha=0.9, fontsize=8)
    axes[1].set_ylim(0, 60)
    axes[1].grid(True, alpha=0.3)

    # Add annotations for total rainfall
    try:
        long_rain = df_weather.loc[f"{year}-03-01":f"{year}-05-31", "rain"].sum()
        short_rain = df_weather.loc[f"{year}-10-01":f"{year}-12-15", "rain"].sum()
        axes[1].annotate(
            f"{long_rain:.0f}mm",
            xy=(pd.Timestamp(f"{year}-04-15"), 55),
            fontsize=9,
            ha="center",
            color="darkgreen",
            fontweight="bold",
        )
        axes[1].annotate(
            f"{short_rain:.0f}mm",
            xy=(pd.Timestamp(f"{year}-11-07"), 55),
            fontsize=9,
            ha="center",
            color="darkorange",
            fontweight="bold",
        )
    except Exception:
        pass

    # Radiation
    axes[2].plot(
        df_weather.index, df_weather["radiation"], color="#F39C12", linewidth=0.8
    )
    axes[2].fill_between(
        df_weather.index, 0, df_weather["radiation"], alpha=0.3, color="#F39C12"
    )
    axes[2].set_ylabel("Solar Radiation\n(MJ/m2/day)", fontweight="bold")
    axes[2].set_xlabel("Date", fontweight="bold")
    axes[2].set_ylim(0, 30)
    axes[2].grid(True, alpha=0.3)

    # Format x-axis
    axes[2].xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    axes[2].xaxis.set_major_locator(mdates.MonthLocator())

    fig.suptitle(
        f"Weather Data: {ctx.location_name} ({year})", fontsize=12, fontweight="bold"
    )

    # Add summary text
    try:
        summary_text = f'Annual: {df_weather["rain"].sum():.0f}mm rain | '
        summary_text += (
            f'Temp: {df_weather["tmin"].mean():.1f}-{df_weather["tmax"].mean():.1f}C'
        )
        fig.text(
            0.5, 0.01, summary_text, ha="center", fontsize=9, style="italic", color="gray"
        )
    except Exception:
        pass

    fig.tight_layout(rect=[0, 0.03, 1, 0.95])
    graph_widget.canvas.draw()
