"""Модуль действий: undo/redo, операции, свойства, подключения."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QColor, QUndoStack
from PySide6.QtWidgets import (
    QMessageBox,
    QGraphicsView,
    QUndoView,
    QDockWidget,
    QTabWidget,
)
from tools.tool_manager import ToolManager, ToolType as ToolTypeEnum

if TYPE_CHECKING:
    from shapes.base_shape import BaseShape
    from ui.main_window import MainWindow


class ActionManager:
    """Управление действиями: undo/redo, операции, свойства, подключения."""

    # Словарь отображения названия инструмента (str) -> читаемое название
    TOOL_NAMES = {
        "select": "Выделение",
        "point": "Точка",
        "line": "Отрезок",
        "ray": "Луч",
        "infinite_line": "Прямая",
        "rectangle": "Прямоугольник",
        "ellipse": "Эллипс",
        "polygon": "Многоугольник",
        "polyline": "Ломаная",
        }
    def __init__(self, main_window: "MainWindow"):
        self._mw = main_window

    # ==================================================================
    # Подключения сигналов
    # ==================================================================

    def setup_connections(self):
        """Настройка соединений сигналов."""
        mw = self._mw
        canvas = mw._canvas
        assert canvas is not None, "Canvas must be initialized before setup_connections"
        property_panel = mw._property_panel

        # Используем lambda или методы для перехвата аргументов, если нужно
        # Но так как сигнал mouse_position_changed передает аргументы, slot должен их принимать

        connections = [
            (mw._manager.shapes_changed, mw._on_shapes_changed),
            (mw._manager.selection_changed, mw._on_selection_changed),
            (mw._tool_manager.tool_changed, mw._on_tool_changed),
            (canvas.mouse_position_changed, mw._on_mouse_position_changed),
            (canvas.zoom_changed, mw._on_zoom_changed),
            (property_panel.properties_changed, mw._on_properties_changed),
            # События мыши
            (canvas.mouse_pressed, mw._on_canvas_mouse_press),
            (canvas.mouse_moved, mw._on_canvas_mouse_move),
            (canvas.mouse_released, mw._on_canvas_mouse_release),
        ]

        for signal, slot in connections:
            signal.connect(slot)

        # Привязка к сцене (event filter) - важно для перехвата кликов по viewport, если это не делается в canvas
        # if canvas.viewport():
        # # canvas.viewport().installEventFilter(mw)
        # Убрано: canvas.viewport().installEventFilter(mw)
        # Причина: Пункт 2.3 плана. Обработка Ctrl+Scroll должна быть в Canvas,
        # чтобы избежать дублирования и проблем с событийной моделью Qt.
        # MainWindow больше не нужен как filter для viewport.

    # ==================================================================
    # Инструменты
    # ==================================================================

    def set_tool(self, tool_type: ToolTypeEnum):
        """Установка текущего инструмента."""
        mw = self._mw
        mw._tool_manager.current_tool = tool_type
        self._update_tool_buttons(tool_type.value)
        self._update_canvas_drag_mode(tool_type)

    def _update_tool_buttons(self, tool_type: str):
        """Обновление состояния кнопок инструментов в UI."""
        mw = self._mw
        for tool in ToolTypeEnum:
            btn_attr = f"_btn_{tool.value.lower()}"
            if hasattr(mw, btn_attr):
                btn = getattr(mw, btn_attr)
                # Убедимся, что кнопка существует и переключается корректно
                if btn.isChecked() != (tool.value == tool_type):
                    btn.setChecked(tool.value == tool_type)

    def _update_canvas_drag_mode(self, tool_type: ToolTypeEnum):
        """Настройка режима перетаскивания холста."""
        mw = self._mw
        if not mw._canvas:
            return

        if tool_type == ToolTypeEnum.SELECT:
            # Для режима выбора обычно используют ScrollHandDrag для панорамирования,
            # если добавлена функция панорамирования, иначе NoDrag.
            # В оригинальном коде было ScrollHandDrag для SELECT.
            mw._canvas.set_drag_mode(QGraphicsView.DragMode.ScrollHandDrag)
        else:
            mw._canvas.set_drag_mode(QGraphicsView.DragMode.NoDrag)

    def get_tool_button(self, tool_type: ToolTypeEnum):
        """Получение кнопки инструмента по типу."""
        btn_attr = f"_btn_{tool_type.value.lower()}"
        return getattr(self._mw, btn_attr, None)

    def on_tool_changed(self, tool_type: str):
        """Обработчик смены инструмента (из ToolManager)."""
        self._update_tool_buttons(tool_type)
        self.update_tool_label(tool_type)

    def update_tool_label(self, tool_type: str):
        """Обновление подписи выбранного инструмента в статусбаре."""
        name = self.TOOL_NAMES.get(tool_type)
        if hasattr(self._mw, "_tool_label") and self._mw._tool_label is not None:
            self._mw._tool_label.setText(f"Инструмент: {name}")

    # ==================================================================
    # Обработчики сигналов
    # ==================================================================

    def on_shapes_changed(self):
        """Обработчик изменения списка фигур."""
        mw = self._mw
        mw._canvas_manager.sync_scene_with_manager()

        # Принудительная перерисовка сцены
        if mw._scene:
            mw._scene.update()

        self.update_statusbar()

    def on_selection_changed(self):
        """Обработчик изменения выделения."""
        mw = self._mw
        selected_count = len(mw._manager.selected_shapes)

        if selected_count == 0:
            mw._status_label.setText("Готово")
        else:
            mw._status_label.setText(f"Выбрано фигур: {selected_count}")

        # Обновляем панель свойств при изменении выделения
        self.update_property_panel()

    def on_mouse_position_changed(self, x: float, y: float):
        """Обновление координат курсора в статусбаре."""
        self._mw._coords_label.setText(f"X: {x:.1f}  Y: {y:.1f}")

    def on_zoom_changed(self, zoom_factor: float):
        """Обновление масштаба в статусбаре."""
        percentage = int(zoom_factor * 100)
        self._mw._zoom_label.setText(f"Масштаб: {percentage}%")

    # ==================================================================
    # Операции с фигурами
    # ==================================================================

    def delete_selected(self):
        """Удаление выделенных фигур с undo."""
        self._mw._manager.delete_selected_undo()

    def copy_selected(self):
        """Копирование выделенных фигур."""
        self._mw._manager.copy_selected()

    def paste_clipboard(self):
        """Вставка из буфера обмена."""
        self._mw._manager.paste_from_clipboard()

    def cut_selected(self):
        """Вырезание выделенных фигур."""
        self._mw._manager.cut_selected()

    # ==================================================================
    # Undo / Redo
    # ==================================================================

    def undo(self):
        """Отмена последнего действия."""
        if self._mw._manager.undo_stack.canUndo:
            self._mw._manager.undo_stack.undo()
            self.update_statusbar()

    def redo(self):
        """Повтор отменённого действия."""
        if self._mw._manager.undo_stack.canRedo:
            self._mw._manager.undo_stack.redo()
            self.update_statusbar()

    def setup_undo_redo(self):
        """Настройка стека отмены/повтора и UI панели истории."""
        mw = self._mw
        undo_stack = QUndoStack(mw)
        mw._manager.undo_stack = undo_stack

        # Создаём QUndoView и привязываем к стеку
        undo_view = QUndoView(undo_stack)
        undo_view.setWindowTitle("История действий")

        # Находим правый док по title и заменяем содержимое
        for dock in mw.findChildren(QDockWidget):
            if "История действий" in dock.windowTitle():
                widget = dock.widget()
                if isinstance(widget, QTabWidget):
                    # Убираем временную заглушку и вставляем настоящий виджет истории
                    # Индекс 1 предполагается на основе предшествующего кода создания Main Window
                    if widget.count() > 1:
                        widget.removeTab(1)
                    widget.insertTab(1, undo_view, "История действий")
                break

    def cleanChanged(self, clean: bool):
        """Обработчик изменения чистоты стека (можно использовать для обновления заголовка окна)."""
        mw = self._mw
        if not mw:
            return

        # Проверяем, существует ли объект.
        # Проверка onDestroyed или использование try/except для Qt объектов.
        # В PySide/PyQt, если объект уже удален, обращение к нему вызовет RuntimeError.
        # Можно попробовать поймать исключение или проверить валидность через Qt.
        # Самый надежный способ для Qt объектов - проверка на наличие родителя или статуса,
        # но так как QMainWindow может быть в процессе удаления, лучше обернуть в try/except.
        try:
            if self._mw._manager.undo_stack:
                if hasattr(mw, "setWindowModified"):
                    mw.setWindowModified(not clean)
        except RuntimeError:
            # Объект уже удален, игнорируем
            pass
        except AttributeError:
            # Атрибуты объекта могут быть уже недоступны
            pass

    # ==================================================================
    # Настройки вида
    # ==================================================================

    def toggle_grid(self, state: int):
        """Переключение видимости сетки."""
        visible = state == Qt.CheckState.Checked.value
        self._mw._settings.grid_visible = visible
        if self._mw._canvas:
            self._mw._canvas.viewport().update()
            self._mw._canvas.update()

    def toggle_snap(self, state: int):
        """Переключение привязки к сетке."""
        snap = state == Qt.CheckState.Checked.value
        self._mw._settings.snap_to_grid = snap
        # При переключении привязки можно пересчитать позиции текущих выделенных фигур, если нужно

    # ==================================================================
    # Панель свойств
    # ==================================================================

    def update_property_panel(self):
        """Обновление панели свойств для выделенных фигур."""
        mw = self._mw
        property_panel = mw._property_panel
        if property_panel is None:
            return

        selected_shapes = mw._manager.selected_shapes

        if selected_shapes:
            if len(selected_shapes) == 1:
                shape = selected_shapes[0]
                props = self.get_shape_properties_dict(shape)
                property_panel.set_properties(props)
            else:
                # Если выделено несколько фигур, панель может показывать "..." или общие свойства
                property_panel.set_multiple_shapes(selected_shapes)
        else:
            property_panel.clear()

    def get_shape_properties_dict(self, shape: "BaseShape") -> dict:
        """Преобразование фигуры в словарь свойств."""
        # Оптимизация работы с QColor
        pen_color = self._color_to_tuple(shape.pen_color, default=(0, 0, 0))
        pen_width = shape.pen_width

        brush_color = self._color_to_tuple(shape.brush_color, default=None)

        rotation = shape.rotation

        result = {
            "pen_color": pen_color,
            "pen_width": pen_width,
            "brush_color": brush_color,
            "rotation": rotation,
        }

        # Добавляем тип фигуры и координаты для прямоугольных фигур
        shape_type_val = shape.shape_type.value
        result["_shape_type"] = shape_type_val

        if shape_type_val in ("rectangle", "ellipse"):
            result["_x"] = shape.x
            result["_y"] = shape.y
            result["_width"] = shape.width
            result["_height"] = shape.height

        return result

    def _color_to_tuple(self, color, default=None):
        """Вспомогательный метод для преобразования QColor в кортеж RGB."""
        if color is None:
            return default
        if isinstance(color, QColor):
            return (color.red(), color.green(), color.blue())
        if isinstance(color, tuple):
            return color
        return default

    def on_properties_changed(self):
        """Обработчик изменения свойств фигуры через панель свойств."""
        mw = self._mw
        selected_shapes = mw._manager.selected_shapes
        if not selected_shapes:
            return

        try:
            property_panel = mw._property_panel
            if property_panel is None:
                QMessageBox.warning(mw, "Ошибка", "Панель свойств не активирована")
                return

            new_properties = property_panel.get_updated_properties()

            if not new_properties:
                return

            # Используем созданную команду для изменения свойств
            selected_ids = {s.id for s in selected_shapes}

            if hasattr(mw._manager, "undo_stack"):
                from manager.undo_commands import ChangePropertiesCommand

                cmd = ChangePropertiesCommand(mw._manager, selected_ids, new_properties)
                mw._manager.undo_stack.push(cmd)
            else:
                # Fallback, если undo_stack нет (например, при инициализации)
                for shape in selected_shapes:
                    shape.apply_properties(new_properties)

            self.refresh_canvas()
            self.update_statusbar()

        except Exception as e:
            QMessageBox.warning(
                mw, "Ошибка", f"Не удалось применить свойства: {str(e)}"
            )

    # ==================================================================
    # Привязка к сетке
    # ==================================================================

    def snap_to_grid(self, pos: QPointF) -> QPointF:
        """Привязка координат к сетке, если включена."""
        settings = self._mw._settings
        if settings.snap_to_grid and settings.grid_spacing > 0:
            spacing = settings.grid_spacing
            x = round(pos.x() / spacing) * spacing
            y = round(pos.y() / spacing) * spacing
            return QPointF(x, y)
        return pos

    def get_snapped_position(self, event) -> QPointF:
        """Получение позиции с учётом привязки к сетке."""
        if self._mw._canvas is None:
            return QPointF(0, 0)
        pos = self._mw._canvas.mapToScene(event.pos())
        return self.snap_to_grid(pos)

    # ==================================================================
    # Статусбар и холст
    # ==================================================================

    def update_statusbar(self):
        """Обновление статусбара."""
        shape_count = len(self._mw._manager.shapes)
        self._mw._status_label.setText(f"Фигур: {shape_count}")

    def refresh_canvas(self):
        """Принудительное обновление холста."""
        if self._mw._canvas:
            self._mw._canvas.update()

    def reset_drawing_state(self):
        """Сброс состояния рисования."""
        mw = self._mw
        mw._is_drawing = False
        mw._last_mouse_pos = None
        mw._selection_rect_start = None
        mw._selection_start_pos = None
        mw._is_dragging = False
        mw._is_selecting = False

        if mw._event_manager:
            mw._event_manager.clear_temp_shape()
        if mw._tool_manager:
            mw._tool_manager.reset_current_shape()
