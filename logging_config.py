"""Конфигурация логирования приложения."""

from __future__ import annotations

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from platformdirs import user_log_dir

# Директория для логов — пользовательская директория (кроссплатформенно)
# Windows:      C:\Users\<User>\AppData\Local\graphics_editor\
# Linux:        ~/.local/state/graphics_editor/
# macOS:        ~/Library/Logs/graphics_editor/
LOG_DIR = Path(user_log_dir("graphics_editor", "afaist"))
LOG_FILE = LOG_DIR / "graphics_editor.log"
MAX_LOG_SIZE_MB = 5  # ротация при превышении размера
BACKUP_COUNT = 3  # количество резервных файлов


def setup_logging(
    level: int = logging.DEBUG,
    console: bool = True,
    file: bool = True,
) -> logging.Logger:
    """Настраивает логирование и возвращает корневой логгер.

    Args:
        level: Уровень логирования (по умолчанию DEBUG).
        console: Выводить логи в консоль/stderr.
        file: Записывать логи в файл.

    Returns:
        Настроенный логгер.
    """
    logger = logging.getLogger("graphics_editor")
    logger.setLevel(level)

    # Очистка предыдущих handler'ов (для тестов)
    logger.handlers.clear()

    # Форматтер с датой, уровнем, именем модуля и сообщением
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)-8s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # --- Handler для файла (с ротацией) ---
    if file:
        try:
            LOG_DIR.mkdir(parents=True, exist_ok=True)

            file_handler = RotatingFileHandler(
                LOG_FILE,
                mode="a",
                encoding="utf-8",
                maxBytes=MAX_LOG_SIZE_MB * 1024 * 1024,
                backupCount=BACKUP_COUNT,
            )
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except OSError as e:
            print(f"Не удалось создать лог-файл {LOG_FILE}: {e}", file=sys.stderr)

    # --- Handler для консоли (stderr) ---
    if console:
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(logging.WARNING)  # в консоль только WARNING+
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # Логируем старт приложения
    logger.info("=" * 60)
    logger.info("Graphics Editor запускается")
    logger.info("Лог-файл: %s", LOG_FILE)
    logger.info("Python: %s", sys.version.split()[0])
    logger.info("Платформа: %s", sys.platform)
    if getattr(sys, "frozen", False):
        logger.info("Режим: PyInstaller (frozen)")
        logger.info("Executable: %s", sys.executable)
    else:
        logger.info("Режим: исходный код")
    logger.info("=" * 60)

    return logger


def get_logger(name: str) -> logging.Logger:
    """Возвращает именованный логгер для модуля."""
    return logging.getLogger(f"graphics_editor.{name}")
