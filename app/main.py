#!/usr/bin/env python3
"""Kenya Digital Farm Twin - WOFOST Crop Simulation Application.

Entry point for the PyQt5 application.
"""

import sys

import matplotlib
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtWidgets import QApplication

matplotlib.use("Qt5Agg")

from windows import MainWindow


def main():
    """Main entry point for the application."""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Set application palette
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(248, 249, 250))
    palette.setColor(QPalette.WindowText, QColor(33, 37, 41))
    palette.setColor(QPalette.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.AlternateBase, QColor(248, 249, 250))
    palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
    palette.setColor(QPalette.ToolTipText, QColor(33, 37, 41))
    palette.setColor(QPalette.Text, QColor(33, 37, 41))
    palette.setColor(QPalette.Button, QColor(248, 249, 250))
    palette.setColor(QPalette.ButtonText, QColor(33, 37, 41))
    palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
    palette.setColor(QPalette.Highlight, QColor(39, 174, 96))
    palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
