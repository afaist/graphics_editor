#!/usr/bin/env python3
"""Точка входа графического редактора."""

import os
import sys

from PySide6.QtCore import QLibraryInfo, QTranslator
from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtWidgets import QApplication

from logging_config import setup_logging

# Инициализация логирования ДО всего остального
logger = setup_logging()

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

from ui.main_window import MainWindow  # noqa: E402 - импорт после патчинга QDialog для Windows

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
    logger.info("Загрузка шрифтов из %s...", _fonts_dir)
    QFontDatabase.addApplicationFontFromData(b"")  # dummy call to init
    font_count = 0
    font_errors = 0
    for f in os.listdir(_fonts_dir):
        if f.endswith(".ttf"):
            try:
                font_path = os.path.join(_fonts_dir, f)
                result = QFontDatabase.addApplicationFont(font_path)
                if result != -1:
                    font_count += 1
                    logger.debug("Загружен шрифт: %s", f)
                else:
                    font_errors += 1
                    logger.warning("Не удалось загрузить шрифт: %s", f)
            except Exception as e:
                font_errors += 1
                logger.warning("Ошибка загрузки шрифта %s: %s", f, e)
    logger.info("Загружено %d шрифтов, %d ошибок", font_count, font_errors)

    # Register bundled fonts with matplotlib font manager for mathtext rendering
    if font_count > 0:
        try:
            logger.info("Регистрация шрифтов в matplotlib...")
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
                logger.info("Использован mathtext fontset: dejavusans")
            else:
                # Fallback to Computer Modern (built-in, no external fonts needed)
                matplotlib.rcParams["mathtext.fontset"] = "cm"
                logger.info("DejaVu не найден, используется mathtext fontset: cm")
        except Exception:
            logger.warning("Не удалось зарегистрировать шрифты в matplotlib", exc_info=True)
else:
    logger.warning("Директория шрифтов не найдена: %s", _fonts_dir)


def main():
    logger.info("Начало инициализации QApplication...")
    try:
        app = QApplication(sys.argv)
        logger.info("QApplication создан успешно")
    except Exception as e:
        logger.critical("Не удалось создать QApplication: %s", e, exc_info=True)
        sys.exit(1)

    try:
        # Системная локализация Qt — автоматический перевод стандартных кнопок
        translator = QTranslator()
        translator.load("qt_ru", QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath))
        app.installTranslator(translator)
        logger.info("Qt локализация загружена")
    except Exception as e:
        logger.warning("Не удалось загрузить Qt локализацию: %s", e)

    try:
        # шрифт
        font = QFont("Segoe UI", 10)
        app.setFont(font)
        logger.info("Шрифт приложения установлен")
    except Exception as e:
        logger.warning("Не удалось установить шрифт: %s", e)

    try:
        logger.info("Создание MainWindow...")
        window = MainWindow()
        logger.info("MainWindow создан успешно")
    except Exception as e:
        logger.critical("Не удалось создать MainWindow: %s", e, exc_info=True)
        sys.exit(1)

    try:
        # Регистрируем все фигуры один раз при запуске
        from shapes.registry import ShapeRegistry

        logger.info("Регистрация фигур...")
        ShapeRegistry.register_all()
        logger.info("Фигуры зарегистрированы")
    except Exception as e:
        logger.warning("Ошибка регистрации фигур: %s", e)

    try:
        logger.info("Показ окна...")
        window.show()
        logger.info("Окно показано, запускается event loop...")
        sys.exit(app.exec())
    except Exception as e:
        logger.critical("Ошибка event loop: %s", e, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
