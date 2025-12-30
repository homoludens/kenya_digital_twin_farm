"""Matplotlib canvas widgets for embedding in PyQt5."""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


class MplCanvas(FigureCanvas):
    """A Matplotlib canvas for embedding in PyQt."""

    def __init__(self, parent=None, width=8, height=6, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.fig.set_facecolor("#f8f9fa")
        super().__init__(self.fig)
        self.setParent(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)


class GraphWidget(QWidget):
    """Widget containing a matplotlib canvas with navigation toolbar."""

    def __init__(self, title="Graph", parent=None):
        super().__init__(parent)
        self.title = title

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Title label
        self.title_label = QLabel(title)
        self.title_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)

        # Canvas
        self.canvas = MplCanvas(self, width=8, height=5, dpi=100)
        layout.addWidget(self.canvas)

        # Toolbar
        self.toolbar = NavigationToolbar(self.canvas, self)
        layout.addWidget(self.toolbar)

    def clear(self):
        self.canvas.fig.clear()
        self.canvas.draw()
