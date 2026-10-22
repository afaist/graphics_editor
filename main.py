#!/usr/bin/env python3
"""Точка входа графического редактора."""

import os
import sys
import traceback

from PySide6.QtCore import QLibraryInfo, QTranslator
from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtWidgets import QApplication

# Fix for Qt6 propagateSizeHints() hang on Windows
# This is a known issue with QSizePolicy::Expanding and QDialog
# Disabling it prevents the application from freezing
if os.name == "nt":
    import PySide6.QtWidgets as QtWidgets

    def _no_op_propagate_size_hints(self):
        """No-op replacement for propagateSizeHints to prevent Qt6 Windows hang."""
        pass

    # Patch QDialog to prevent propagateSizeHints hang
    QtWidgets.QDialog.propagateSizeHints = _no_op_propagate_size_hints

from ui.main_window import MainWindow

# Fix for AppImage GIO/GVFS incompatibility (g_task_set_static_name undefined symbol)
# Prevents loading system GIO modules that crash the AppImage (Linux only)
if os.name == "posix":
    if not os.environ.get("GIO_USE_VFS"):
        os.environ["GIO_USE_VFS"] = "local"

# Platform-specific display setup
if not os.environ.get("QT_QPA_PLATFORM"):
    if os.name == "nt":
        # Windows — no special display setup needed
        pass
    else:
        # Linux: Check if we are in a headless environment (common in CI/CD or servers)
        if not os.environ.get("DISPLAY") and not os.environ.get("WAYLAND_DISPLAY"):
            os.environ["QT_QPA_PLATFORM"] = "offscreen"
        else:
            # Wayland has known segfault issues with PySide6 QGraphicsScene.
            # Prefer X11/XCB when available as a fallback.
            if os.environ.get("WAYLAND_DISPLAY") and not os.environ.get("QT_QPA_PLATFORM"):
                if os.environ.get("DISPLAY"):
                    os.environ["QT_QPA_PLATFORM"] = "xcb"

# Add bundled fonts directory to QFontDatabase search path
_fonts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
if os.path.isdir(_fonts_dir):
    QFontDatabase.addApplicationFontFromData(b"")  # dummy call to init
    for f in os.listdir(_fonts_dir):
        if f.endswith(".ttf"):
            QFontDatabase.addApplicationFont(os.path.join(_fonts_dir, f))

    # Register bundled fonts with matplotlib font manager for mathtext rendering
    try:
        import matplotlib
        import matplotlib.font_manager as fm

        dejavu_found = False
        for f in os.listdir(_fonts_dir):
            if f.endswith(".ttf"):
                fm.fontManager.addfont(os.path.join(_fonts_dir, f))
                # Check if this is a DejaVu font
                if "DejaVu" in f:
                    dejavu_found = True

        # Set fontset: use dejavusans if fonts available, otherwise fallback to cm
        if dejavu_found:
            matplotlib.rcParams["mathtext.fontset"] = "dejavusans"
        else:
            # Fallback to Computer Modern (built-in, no external fonts needed)
            matplotlib.rcParams["mathtext.fontset"] = "cm"
    except Exception:
        pass  # matplotlib font registration is optional


def main():
    try:
        app = QApplication(sys.argv)
        # app.setStyle(QStyleFactory.create("Fusion"))  # кроссплатформенный стиль

        # Системная локализация Qt — автоматический перевод стандартных кнопок
        translator = QTranslator()
        translator.load("qt_ru", QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath))

        app.installTranslator(translator)

        # шрифт
        font = QFont("Segoe UI", 10)
        app.setFont(font)

        window = MainWindow()
        # Регистрируем все фигуры один раз при запуске
        from shapes.registry import ShapeRegistry

        ShapeRegistry.register_all()
        window.show()

        sys.exit(app.exec())
    except Exception as e:
        print(f"Ошибка запуска программы: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
