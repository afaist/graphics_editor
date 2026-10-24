#!/usr/bin/env python3
"""Точка входа графического редактора."""

import os
import signal
import sys

# Fix for AppImage GIO/GVFS incompatibility (g_task_set_static_name undefined symbol)
# MUST be set BEFORE any PySide6/Qt imports - GIO modules load on first Qt import
os.environ["GIO_USE_VFS"] = "local"

from PySide6.QtCore import QLibraryInfo, QTranslator
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

from logging_config import setup_logging

# Инициализация логирования ДО всего остального
logger = setup_logging()


def _signal_handler(signum, frame):
    """Обработчик сигналов для graceful shutdown."""
    logger.info("Получен сигнал %d, завершение...", signum)
    # НЕ использовать sys.exit() — может вызвать segfault при cleanup
    # Используем os._exit() для немедленного выхода без Python-cleanup
    import os

    os._exit(0)


# Регистрируем обработчики сигналов
signal.signal(signal.SIGINT, _signal_handler)
signal.signal(signal.SIGTERM, _signal_handler)

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

# Регистрация шрифтов для matplotlib (безопасно для Python)
try:
    import matplotlib

    # Force Agg backend before any pyplot usage — avoids GUI backend segfaults on exit
    matplotlib.use("Agg")
    import matplotlib.font_manager as fm

    _fonts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
    if os.path.isdir(_fonts_dir):
        dejavu_found = False
        for f in os.listdir(_fonts_dir):
            if f.endswith(".ttf"):
                try:
                    fm.fontManager.addfont(os.path.join(_fonts_dir, f))
                    if "DejaVu" in f:
                        dejavu_found = True
                except Exception:
                    pass

        if dejavu_found:
            matplotlib.rcParams["mathtext.fontset"] = "dejavusans"
        else:
            matplotlib.rcParams["mathtext.fontset"] = "cm"
except Exception:
    pass  # matplotlib шрифты не критичны


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
        exit_code = app.exec()
        logger.info("Event loop завершён, код выхода: %d", exit_code)
        # НЕ вызывать sys.exit() — Qt уже начал cleanup, это вызывает segfault
        # Просто выходим из main(), Qt завершится корректно
    except Exception as e:
        logger.critical("Ошибка event loop: %s", e, exc_info=True)
        # sys.exit() здесь тоже опасен — выходим через Qt
        app.quit()


if __name__ == "__main__":
    main()
