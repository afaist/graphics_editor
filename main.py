#!/usr/bin/env python3
"""Точка входа графического редактора."""

import os
import sys
import traceback

# Try to set a graphical platform if not already set and we are not in headless mode
if not os.environ.get("QT_QPA_PLATFORM"):
    # Check if we are in a headless environment (common in CI/CD or servers)
    if not os.environ.get("DISPLAY") and not os.environ.get("WAYLAND_DISPLAY"):
        os.environ["QT_QPA_PLATFORM"] = "offscreen"
    else:
        # Wayland has known segfault issues with PySide6 QGraphicsScene.
        # Prefer X11/XCB when available as a fallback.
        if os.environ.get("WAYLAND_DISPLAY") and not os.environ.get("QT_QPA_PLATFORM"):
            # Try to use XCB instead of Wayland to avoid Qt/PySide6 segfaults
            if os.environ.get("DISPLAY"):
                os.environ["QT_QPA_PLATFORM"] = "xcb"

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont

from ui.main_window import MainWindow


def main():
    try:
        app = QApplication(sys.argv)
        app.setStyle("Fusion")  # кроссплатформенный стиль

        # шрифт
        font = QFont("Segoe UI", 10)
        app.setFont(font)

        window = MainWindow()
        window.show()

        sys.exit(app.exec())
    except Exception as e:
        print(f"Error starting application: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
