#!/usr/bin/env python3
"""Точка входа графического редактора."""

import os
import signal
import sys
import time

# Fix for AppImage GIO/GVFS incompatibility (g_task_set_static_name undefined symbol)
# MUST be set BEFORE any PySide6/Qt imports - GIO modules load on first Qt import
os.environ["GIO_USE_VFS"] = "local"

from logging_config import setup_logging  # noqa: E402

logger = setup_logging()


class _Timer:
    """Простой таймер для замеров этапов."""

    def __init__(self, label: str):
        self.label = label
        self.start = time.monotonic()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        elapsed = time.monotonic() - self.start
        logger.info("  [%.3fs] %s", elapsed, self.label)


def _signal_handler(signum, frame):
    """Обработчик сигналов для graceful shutdown."""
    logger.info("Получен сигнал %d, завершение...", signum)
    # НЕ использовать sys.exit() — может вызвать segfault при cleanup
    # Используем os._exit() для немедленного выхода без Python-cleanup
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

from PySide6.QtCore import QLibraryInfo, QTranslator  # noqa: E402
from PySide6.QtGui import QFont  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

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
    import matplotlib  # noqa: E402

    # Force Agg backend before any pyplot usage — avoids GUI backend segfaults on exit
    matplotlib.use("Agg")
    import matplotlib.font_manager as fm  # noqa: E402

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
    logger.info("=" * 60)
    logger.info("НАЧАЛО ИНИЦИАЛИЗАЦИИ")
    logger.info("=" * 60)
    logger.info("DISPLAY=%s", os.environ.get("DISPLAY", "(not set)"))
    logger.info("WAYLAND_DISPLAY=%s", os.environ.get("WAYLAND_DISPLAY", "(not set)"))
    logger.info("QT_QPA_PLATFORM=%s", os.environ.get("QT_QPA_PLATFORM", "(not set)"))
    logger.info("GIO_USE_VFS=%s", os.environ.get("GIO_USE_VFS", "(not set)"))
    logger.info("LD_LIBRARY_PATH=%s", os.environ.get("LD_LIBRARY_PATH", "(not set)"))
    logger.info("QT_QPA_PLATFORMTHEME=%s", os.environ.get("QT_QPA_PLATFORMTHEME", "(not set)"))

    # 1. QApplication
    with _Timer("QApplication(sys.argv)"):
        logger.info("Вызов QApplication(sys.argv)...")
        try:
            app = QApplication(sys.argv)
            logger.info("QApplication создан успешно")
        except Exception as e:
            logger.critical("Не удалось создать QApplication: %s", e, exc_info=True)
            sys.exit(1)

    # 2. Event loop — включаем логирование событий Qt
    logger.info("Установка event filter для логирования фокуса...")
    _install_focus_logger(app)

    # 3. Локализация
    with _Timer("Qt локализация"):
        try:
            translator = QTranslator()
            trans_path = QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)
            logger.info("Translations path: %s", trans_path)
            translator.load("qt_ru", trans_path)
            app.installTranslator(translator)
            logger.info("Qt локализация загружена")
        except Exception as e:
            logger.warning("Не удалось загрузить Qt локализацию: %s", e)

    # 4. Шрифт
    with _Timer("Установка шрифта приложения"):
        try:
            font = QFont("Segoe UI", 10)
            logger.info(
                "Создан шрифт Segoe UI 10: family=%s, found=%s", font.family(), font.exactMatch()
            )
            app.setFont(font)
            logger.info("Шрифт приложения установлен")
        except Exception as e:
            logger.warning("Не удалось установить шрифт: %s", e)

    # 5. MainWindow
    with _Timer("Создание MainWindow"):
        try:
            logger.info("Создание MainWindow...")
            window = MainWindow()
            logger.info("MainWindow создан успешно")
        except Exception as e:
            logger.critical("Не удалось создать MainWindow: %s", e, exc_info=True)
            sys.exit(1)

    # 6. Регистрация фигур
    with _Timer("Регистрация фигур"):
        try:
            logger.info("Регистрация фигур...")
            from shapes.registry import ShapeRegistry  # noqa: E402

            ShapeRegistry.register_all()
            logger.info("Фигуры зарегистрированы")
        except Exception as e:
            logger.warning("Ошибка регистрации фигур: %s", e)

    # 7. Показ окна
    with _Timer("Показ окна"):
        try:
            logger.info("Показ окна...")
            window.show()
            logger.info("Окно показано, запускается event loop...")
            logger.info("=" * 60)
            logger.info("ИНИЦИАЛИЗАЦИЯ ЗАВЕРШЕНА, ЗАПУСК EVENT LOOP")
            logger.info("=" * 60)
            exit_code = app.exec()
            logger.info("Event loop завершён, код выхода: %d", exit_code)
            # НЕ вызывать sys.exit() — Qt уже начал cleanup, это вызывает segfault
            # Просто выходим из main(), Qt завершится корректно
        except Exception as e:
            logger.critical("Ошибка event loop: %s", e, exc_info=True)
            # sys.exit() здесь тоже опасен — выходим через Qt
            app.quit()


def _install_focus_logger(app: QApplication):
    """Устанавливает event filter для логирования событий фокуса окна."""
    from PySide6.QtCore import QObject  # noqa: E402

    class FocusLogger(QObject):
        def eventFilter(self, obj, event):
            from PySide6.QtCore import QEvent  # noqa: E402

            etype = event.type()
            if etype == QEvent.Type.WindowActivate:
                logger.info("WINDOW_ACTIVATE on %s", type(obj).__name__)
            elif etype == QEvent.Type.WindowDeactivate:
                logger.info("WINDOW_DEACTIVATE on %s", type(obj).__name__)
            elif etype == QEvent.Type.FocusIn:
                logger.info("FOCUS_IN on %s", type(obj).__name__)
            elif etype == QEvent.Type.FocusOut:
                logger.info("FOCUS_OUT on %s", type(obj).__name__)
            elif etype == QEvent.Type.Show:
                logger.info("SHOW on %s", type(obj).__name__)
            elif etype == QEvent.Type.Hide:
                logger.info("HIDE on %s", type(obj).__name__)
            return False

    _focus_logger = FocusLogger()
    app.installEventFilter(_focus_logger)
    logger.info("Event filter для фокуса установлен")


if __name__ == "__main__":
    main()
