"""Модуль операций с проектом: new/open/save/export."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtWidgets import QFileDialog, QMessageBox

if TYPE_CHECKING:
    from ui.main_window import MainWindow


class ProjectManager:
    """Управление проектами."""

    def __init__(self, main_window: "MainWindow"):
        self._mw = main_window

    def new_project(self):
        mw = self._mw
        mw._manager.remove_all()
        if mw._scene is not None:
            mw._scene.clear()
        mw._file_manager.current_filepath = None
        mw._manager.undo_stack.setClean()
        # Удаляем автосохранение при создании нового проекта
        mw._autosaver.remove_autosave()
        mw._update_statusbar()

    def open_project(self):
        mw = self._mw
        file_path, _ = QFileDialog.getOpenFileName(
            mw, "Открыть проект", "", "Графические проекты (*.gproj);;Все файлы (*.*)"
        )
        if file_path:
            try:
                mw._file_manager.load_project(mw._manager, file_path)
                mw._file_manager.current_filepath = file_path
                mw._manager.undo_stack.setClean()
                mw._update_statusbar()
            except Exception as e:
                QMessageBox.critical(mw, "Ошибка", f"Не удалось открыть файл: {str(e)}")

    def save_project(self) -> bool:
        mw = self._mw
        if not mw._file_manager.has_current_file:
            return self.save_project_as()
        else:
            try:
                if mw._file_manager.current_filepath:
                    success = mw._file_manager.save_project(
                        mw._manager, mw._file_manager.current_filepath
                    )
                    if success:
                        mw._manager.undo_stack.setClean()
                        # Удаляем автосохранение при успешном сохранении
                        mw._autosaver.remove_autosave()
                        return success
            except Exception as e:
                QMessageBox.critical(
                    mw, "Ошибка", f"Не удалось сохранить файл: {str(e)}"
                )
                return False
            return False

    def save_project_as(self) -> bool:
        mw = self._mw
        file_path, _ = QFileDialog.getSaveFileName(
            mw,
            "Сохранить проект как...",
            "",
            "Графические проекты (*.gproj);;Все файлы (*.*)",
        )
        if file_path:
            try:
                success = mw._file_manager.save_project_as(file_path, mw._manager)
                if success:
                    mw._manager.undo_stack.setClean()
                    # Удаляем автосохранение при успешном сохранении
                    mw._autosaver.remove_autosave()
                return success
            except Exception as e:
                QMessageBox.critical(
                    mw, "Ошибка", f"Не удалось сохранить файл: {str(e)}"
                )
                return False
        return False

    def export_png(self):
        mw = self._mw
        if mw._canvas is None:
            QMessageBox.warning(
                mw, "Предупреждение", "Нет активного холста для экспорта."
            )
            return
        file_path, _ = QFileDialog.getSaveFileName(
            mw, "Экспорт в PNG", "", "PNG изображения (*.png);;Все файлы (*.*)"
        )
        if file_path:
            try:
                mw._canvas.export_to_png(file_path)
            except Exception as e:
                QMessageBox.critical(
                    mw, "Ошибка", f"Не удалось экспортировать в PNG: {str(e)}"
                )

    def export_svg(self):
        mw = self._mw
        file_path, _ = QFileDialog.getSaveFileName(
            mw, "Экспорт в SVG", "", "SVG изображения (*.svg);;Все файлы (*.*)"
        )
        if file_path:
            if mw._canvas is None:
                QMessageBox.warning(mw, "Ошибка", "Нет активного холста.")
                return
            try:
                mw._canvas.export_to_svg(file_path)
            except Exception as e:
                QMessageBox.critical(
                    mw, "Ошибка", f"Не удалось экспортировать в SVG: {str(e)}"
                )
