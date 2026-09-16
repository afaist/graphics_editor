"""Главное окно графического редактора."""

from __future__ import annotations

from typing import Optional, TYPE_CHECKING, Any

from PySide6.QtCore import QPointF
from PySide6.QtWidgets import QMainWindow, QMessageBox

from shapes.base_shape import BaseShape
from manager.shape_manager import ShapeManager
from manager.autosaver import AutoSaver
from canvas.graphics_canvas import GraphicsCanvas
from tools.tool_manager import ToolManager, ToolType as ToolTypeEnum
from fileio.file_manager import FileManager
from settings.settings import Settings
from ui.window_canvas import CanvasManager
from ui.window_ui import UIManager
from ui.window_events import EventManager
from ui.window_project import ProjectManager
from ui.window_actions import ActionManager
from ui.window_shortcuts import ShortcutManager
if TYPE_CHECKING:
    from ui.scene_items import ShapeSceneItem


class MainWindow(QMainWindow):
    """Главное окно приложения — оркестратор подмодулей."""

    # Константы размеров
    WINDOW_WIDTH = 1400
    WINDOW_HEIGHT = 900
    DOCK_WIDTH = 250

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Графический редактор [*]")
        self.resize(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)

        # ---- Инициализация компонентов ----
        self._settings = Settings()
        self._manager = ShapeManager()
        self._tool_manager = ToolManager()
        self._file_manager = FileManager()

        # ---- UI компоненты (заполняются подмодулями) ----
        self._scene: Optional[QGraphicsScene] = None  # type: ignore[name-defined]
        self._canvas: Optional[GraphicsCanvas] = None
        self._property_panel: Any = None  # type: ignore[assignment]
        self._status: Any = None  # type: ignore[assignment]
        self._status_label: Any = None  # type: ignore[assignment]
        self._coords_label: Any = None  # type: ignore[assignment]
        self._zoom_label: Any = None  # type: ignore[assignment]
        self._tool_label: Any = None  # type: ignore[assignment]
        self._history_panel: Any = None  # type: ignore[assignment]

        # ---- Флаги состояния ----
        self._is_drawing = False
        self._is_dragging = False
        self._is_selecting = False
        self._last_mouse_pos: Optional[QPointF] = None
        self._selection_start_pos: Optional[QPointF] = None
        self._selection_rect_start: Optional[QPointF] = None
        self._temp_shape_item: Optional[ShapeSceneItem] = None

        # ---- Подмодули ----
        self._canvas_manager = CanvasManager(self)
        self._ui_manager = UIManager(self)
        self._event_manager = EventManager(self)
        self._project_manager = ProjectManager(self)
        self._action_manager = ActionManager(self)
        self._autosaver = AutoSaver(self)

        # ---- Порядок инициализации ----
        self._setup_canvas()
        self._setup_ui()
        self._setup_connections()
        self._setup_undo_redo()
        
        # Связь property panel <-> action manager
        self._manager.shapes_changed.connect(self._action_manager.update_property_panel)
        self._manager.selection_changed.connect(self._action_manager.update_property_panel)
        self._action_manager.update_property_panel()
        # Связь HistoryPanel
        self._connect_history_panel()
        # Обновим статусбар после полной инициализации
        self._update_statusbar()
        # Инициализируем лейбл выбранного инструмента
        self._action_manager.update_tool_label(self._tool_manager.current_tool.value)
        # Автосохранение
        self._setup_autosave()
        # Горячие клавиши
        self._setup_shortcuts()


    # ==================================================================
    # Инициализация подмодулей (обёртки)
    # ==================================================================

    def _setup_canvas(self):
        self._canvas_manager.setup_scene()

    def _setup_ui(self):
        self._ui_manager.setup_ui()

    def _setup_connections(self):
        self._action_manager.setup_connections()

    def _setup_undo_redo(self):
        self._action_manager.setup_undo_redo()
        # Подключаем отслеживание изменения чистоты стека для подсветки окна
        self._manager.undo_stack.cleanChanged.connect(
            self._action_manager.cleanChanged
            )

    def _setup_shortcuts(self):
        """Настройка горячих клавиш."""
        if not hasattr(self, "_shortcut_manager") or self._shortcut_manager is None:
            self._shortcut_manager = ShortcutManager(self)
        self._shortcut_manager.setup_shortcuts()

    def _setup_autosave(self):
        """Настройка автосохранения и восстановление при необходимости."""
        # Подключаем запуск автосохранения при изменении чистоты стека
        self._manager.undo_stack.cleanChanged.connect(self._on_undo_clean_changed)
        # Пытаемся восстановить из автосохранения
        self._try_restore_autosave()
        # Запускаем таймер автосохранения
        self._autosaver.start()

    def _on_undo_clean_changed(self, clean: bool):
        """Обработчик изменения чистоты undo-стека для автосохранения."""
        if not clean:
            self._autosaver.schedule_save()
        else:
            self._autosaver.stop()

    def _try_restore_autosave(self):
        """Пытается восстановить проект из автосохранения при запуске."""
        if not self._autosaver.has_autosave():
            return
        # Если проект уже был загружен — не восстанавливаем
        if self._file_manager.has_current_file:
            return
        # Если есть фигуры — не восстанавливаем (проект уже загружен)
        if self._manager.shapes:
            return
        reply = QMessageBox.question(
            self,
            "Обнаружен автосохранённый проект",
            "Найдено автосохранение проекта. Восстановить?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )
        if reply == QMessageBox.StandardButton.Yes:
            if self._autosaver.load_autosave(self._manager):
                # После восстановления помечаем как несохранённый
                self._manager.undo_stack.setClean()
                # Обновляем статусбар
                self._update_statusbar()
                QMessageBox.information(
                    self, "Восстановлено",
                    "Проект восстановлен из автосохранения.\n"
                    "Рекомендуется сохранить его под новым именем."
                )

    def _on_shapes_changed(self):
        self._action_manager.on_shapes_changed()

    def _connect_history_panel(self):
        """Подключение сигналов HistoryPanel к ShapeManager."""
        if not hasattr(self, '_history_panel') or self._history_panel is None:
            return
        self._manager.shapes_changed.connect(self._history_panel.update_shapes)
        self._history_panel.shape_selected.connect(self._manager.select_shape)
        self._history_panel.shape_deleted.connect(self._on_history_shape_deleted)
        self._history_panel.set_main_window(self)

    def _on_history_shape_deleted(self, shape_id: int):
        """Обработчик удаления фигуры из HistoryPanel."""
        self._manager.selection_changed.emit()

    def _on_selection_changed(self):
        self._action_manager.on_selection_changed()

    def _on_tool_changed(self, tool_type):
        self._action_manager.on_tool_changed(tool_type)

    def _on_mouse_position_changed(self, x: float, y: float):
        self._action_manager.on_mouse_position_changed(x, y)

    def _on_zoom_changed(self, zoom_factor: float):
        self._action_manager.on_zoom_changed(zoom_factor)

    def _on_properties_changed(self):
        self._action_manager.on_properties_changed()

    def _on_canvas_mouse_press(self, event):
        self._event_manager.on_canvas_mouse_press(event)

    def _on_canvas_mouse_move(self, event):
        self._event_manager.on_canvas_mouse_move(event)

    def _on_canvas_mouse_release(self, event):
        self._event_manager.on_canvas_mouse_release(event)

    # ==================================================================
    # Методы, вызываемые из UI (кнопки, меню)
    # ==================================================================

    def _set_tool(self, tool_type: ToolTypeEnum):
        self._action_manager.set_tool(tool_type)

    def _delete_selected(self):
        self._action_manager.delete_selected()

    def _copy_selected(self):
        self._action_manager.copy_selected()

    def _paste_clipboard(self):
        self._action_manager.paste_clipboard()

    def _cut_selected(self):
        self._action_manager.cut_selected()

    def _undo(self):
        self._action_manager.undo()

    def _redo(self):
        self._action_manager.redo()

    def _toggle_grid(self, state: int):
        self._action_manager.toggle_grid(state)

    def _toggle_snap(self, state: int):
        self._action_manager.toggle_snap(state)

    def _new_project(self):
        if self._has_unsaved_changes():
            reply = QMessageBox.question(
                self,
                "Подтверждение создания нового проекта",
                "В проекте есть несохранённые изменения. Сохранить изменения?",
                QMessageBox.StandardButton.Save
                | QMessageBox.StandardButton.Discard
                | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Cancel,
            )
            if reply == QMessageBox.StandardButton.Save:
                success = self._project_manager.save_project()
                # Если сохранение не удалось, не создаём новый проект
                if not success:
                    return
            elif reply == QMessageBox.StandardButton.Discard:
                pass  # Продолжаем создание нового проекта без сохранения
            else:
                return  # Cancel — ничего не делаем
        self._project_manager.new_project()

    def _open_project(self):
        self._project_manager.open_project()

    def _save_project(self):
        self._project_manager.save_project()

    def _save_project_as(self):
        self._project_manager.save_project_as()

    def _export_png(self):
        self._project_manager.export_png()

    def _export_svg(self):
        self._project_manager.export_svg()


    
    # ==================================================================
    # Публичные методы для внешнего использования
    # ==================================================================

    def add_shape(self, shape: BaseShape):
        """Публичный метод для добавления фигуры извне."""
        self._manager.add_shape(shape)
        # Убираем здесь update(), так как it будет сделано в on_shapes_changed
        # через сигнал shapes_changed
        # self._scene.update() <-- ЗАКОММЕНТИРОВАТЬ ИЛИ УДАЛИТЬ
        self._update_statusbar()

    def _refresh_canvas(self):
        """Принудительное обновление холста (перерисовка всех фигур)."""
        if self._canvas is None:
            return
        self._canvas_manager.sync_scene_with_manager()
        if self._scene is not None:
            self._scene.update()

    def clear_all(self):
        """Публичный метод для очистки всего холста."""
        reply = QMessageBox.question(
            self,
            "Подтверждение очистки",
            "Вы уверены, что хотите очистить весь холст?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._new_project()

    def export_to_png(self, file_path: str):
        """Публичный метод для экспорта в PNG."""
        if self._canvas is None:
            QMessageBox.warning(self, "Ошибка", "Нет активного canvas!")
            return
        try:
            self._canvas.export_to_png(file_path)
            QMessageBox.information(self, "Успех", "Файл успешно экспортирован в PNG")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось экспортировать в PNG: {str(e)}")

    def export_to_svg(self, file_path: str):
        """Публичный метод для экспорта в SVG."""
        if self._canvas is None:
            QMessageBox.warning(self, "Предупреждение", "Нет активного холста")
            return
        try:
            self._canvas.export_to_svg(file_path)
            QMessageBox.information(self, "Успех", "Файл успешно экспортирован в SVG")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось экспортировать в SVG: {str(e)}")

    # ==================================================================
    # Вспомогательные методы
    # ==================================================================

    def _update_statusbar(self):
        self._action_manager.update_statusbar()

    # ==================================================================
    # Переопределённые методы
    # ==================================================================

    def closeEvent(self, event):
        """Обработка закрытия окна приложения."""
        try:
            self._settings.save()
        except Exception as e:
            QMessageBox.warning(self, "Предупреждение", f"Не удалось сохранить настройки: {e}")

        if self._has_unsaved_changes():
            reply = QMessageBox.question(
                self,
                "Подтверждение закрытия",
                "Есть несохранённые изменения. Сохранить?",
                QMessageBox.StandardButton.Save
                | QMessageBox.StandardButton.Discard
                | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Cancel,
            )
            if reply == QMessageBox.StandardButton.Save:
                # Сохраняем перед закрытием — обновляется current_filepath
                self._project_manager.save_project()
            elif reply == QMessageBox.StandardButton.Discard:
                pass  # Игнорируем изменения
            else:
                event.ignore()
                return

        event.accept()

    def _has_unsaved_changes(self) -> bool:
        """Проверка наличия несохранённых изменений."""
        # Если файл не сохранён — всегда есть изменения
        if not self._file_manager.has_current_file:
            return len(self._manager.shapes) > 0
        # Если файл сохранён, проверяем чистоту undo-стека
        return not self._manager.undo_stack.isClean

    def resizeEvent(self, event):
        """Обработка изменения размера окна."""
        super().resizeEvent(event)
        self._refresh_canvas()

    def showEvent(self, event):
        """Обработка показа окна."""
        super().showEvent(event)
        self._update_statusbar()


# ==================================================================
# Фабрика
# ==================================================================

def create_main_window() -> MainWindow:
    """Фабрика для создания главного окна приложения."""
    return MainWindow()
