"""Interactive map widget for selecting locations in Kenya."""

from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import pyqtSignal

from widgets.canvas import MplCanvas
from config.locations import LOCATION_OPTIONS


class LocationMapWidget(QWidget):
    """Interactive map widget for selecting locations in Kenya."""

    location_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_location = "trans_nzoia"
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Canvas
        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)
        layout.addWidget(self.canvas)

        # Connect click event
        self.canvas.mpl_connect("button_press_event", self._on_click)

        # Draw initial map
        self._draw_map()

    def _draw_map(self):
        self.canvas.fig.clear()
        ax = self.canvas.fig.add_subplot(111)

        # Draw simplified Kenya outline
        kenya_outline_lon = [34, 42, 42, 41, 40, 34, 34]
        kenya_outline_lat = [4.5, 4.5, -1, -4.5, -4.5, -1, 4.5]
        ax.plot(kenya_outline_lon, kenya_outline_lat, "k-", linewidth=2, alpha=0.5)
        ax.fill(kenya_outline_lon, kenya_outline_lat, color="#e8f5e9", alpha=0.3)

        # Plot locations
        for key, loc in LOCATION_OPTIONS.items():
            color = "#2196F3" if key == self.selected_location else "#757575"
            size = 150 if key == self.selected_location else 80
            marker = "*" if key == self.selected_location else "o"

            ax.scatter(
                loc["lon"],
                loc["lat"],
                c=color,
                s=size,
                marker=marker,
                edgecolors="white",
                linewidths=2,
                zorder=5,
            )
            ax.annotate(
                loc["name"].split("(")[0].strip(),
                (loc["lon"], loc["lat"]),
                xytext=(5, 5),
                textcoords="offset points",
                fontsize=8,
                fontweight="bold" if key == self.selected_location else "normal",
            )

        ax.set_xlim(33, 43)
        ax.set_ylim(-5, 5)
        ax.set_xlabel("Longitude (E)", fontweight="bold")
        ax.set_ylabel("Latitude (N)", fontweight="bold")
        ax.set_title("Kenya - Click to Select Location", fontweight="bold")
        ax.grid(True, alpha=0.3)
        ax.set_aspect("equal")

        self.canvas.fig.tight_layout()
        self.canvas.draw()

    def _on_click(self, event):
        if event.xdata is None or event.ydata is None:
            return

        # Find closest location
        min_dist = float("inf")
        closest = None

        for key, loc in LOCATION_OPTIONS.items():
            dist = (
                (loc["lon"] - event.xdata) ** 2 + (loc["lat"] - event.ydata) ** 2
            ) ** 0.5
            if dist < min_dist:
                min_dist = dist
                closest = key

        if closest and min_dist < 2:  # Within 2 degrees
            self.selected_location = closest
            self._draw_map()
            self.location_selected.emit(closest)

    def set_location(self, location_key: str):
        if location_key in LOCATION_OPTIONS:
            self.selected_location = location_key
            self._draw_map()
