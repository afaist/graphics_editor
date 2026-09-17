"""Автосохранение проекта (autosave)."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from PySide6.QtCore import QTimer

from fileio.file_manager import FileManager

if TYPE_CHECKING:
    from ui.main_window import MainWindow


class AutoSaver:
    """Периодическое сохранение проекта в временный файл."""

    AUTOSAVE_INTERVAL_MS = 60000  # 1 минута
    AUTOSAVE_FILENAME = ".project.autosave.gproj"

    def __init__(self, main_window: MainWindow):
        self._mw = main_window
        self._timer = QTimer(self._mw)
        self._timer.setSingleShot(False)
        self._timer.setInterval(self.AUTOSAVE_INTERVAL_MS)
        self._timer.timeout.connect(self._do_save)
        self._dirty = False

    @property
    def autosave_path(self) -> str:
        """Возвращает путь к файлу автосохранения."""
        filepath = self._mw._file_manager.current_filepath
        if filepath:
            basedir = os.path.dirname(filepath)
        else:
            basedir = os.getcwd()
        return os.path.join(basedir, self.AUTOSAVE_FILENAME)

    def start(self):
        """Запускает таймер автосохранения."""
        self._timer.start()

    def stop(self):
        """Останавливает таймер автосохранения."""
        self._timer.stop()

    def schedule_save(self):
        """Отмечает, что нужно сохранить (сбрасывает таймер при активности)."""
        self._dirty = True
        # Перезапускаем таймер, чтобы не сохранять слишком часто при активной работе
        self._timer.start()

    def _do_save(self):
        """Выполняет фактическое сохранение."""
        mw = self._mw
        filepath = mw._file_manager.current_filepath
        if not filepath:
            return
        if not mw._manager.shapes:
            return
        try:
            success = mw._file_manager.save_project(mw._manager, self.autosave_path)
            if success:
                self._dirty = False
        except Exception:
            pass

    def has_autosave(self) -> bool:
        """Проверяет наличие файла автосохранения."""
        return os.path.isfile(self.autosave_path)

    def load_autosave(self, manager) -> bool:
        """Загружает проект из файла автосохранения."""
        path = self.autosave_path
        if not os.path.isfile(path):
            return False
        try:
            result = FileManager.load_json(manager, path)
            if result:
                manager.undo_stack.setClean()
            return result
        except Exception:
            return False

    def remove_autosave(self):
        """Удаляет файл автосохранения."""
        path = self.autosave_path
        if os.path.isfile(path):
            try:
                os.remove(path)
            except OSError:
                pass
