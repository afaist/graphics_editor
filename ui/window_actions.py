"""Модуль действий: undo/redo, операции, свойства, подключения."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QColor, QUndoStack
from PySide6.QtWidgets import QUndoView, QDockWidget, QMessageBox

from tools.tool_manager import ToolManager, ToolType as ToolTypeEnum

if TYPE_CHECKING:
    from shapes.base_shape import BaseShape
    from ui.main_window import MainWindow


class ActionManager:
    """Управление действиями: undo/redo, операции, свойства, подключения."""

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
            # Привязка к сцене
            canvas.viewport().installEventFilter(mw)

    # ==================================================================
    # Инструменты
    # ==================================================================

    def set_tool(self, tool_type):
        """Установка текущего инструмента."""
        mw = self._mw
        mw._tool_manager.current_tool = tool_type

        from tools.tool_manager import ToolType
        
        for tool in ToolType:
            btn_attr = f"_btn_{tool.value.lower()}"
            if hasattr(mw, btn_attr):
                btn = getattr(mw, btn_attr)
                btn.setChecked(tool == tool_type)
        if tool_type == ToolTypeEnum.SELECT:
            if mw._canvas:
                from PySide6.QtWidgets import QGraphicsView
                mw._canvas.set_drag_mode(QGraphicsView.DragMode.ScrollHandDrag)
        else:
            if mw._canvas:
                from PySide6.QtWidgets import QGraphicsView
                mw._canvas.set_drag_mode(QGraphicsView.DragMode.NoDrag)

    def get_tool_button(self, tool_type):
        """Получение кнопки инструмента по типу."""
        btn_attr = f"_btn_{tool_type.value.lower()}"
        return getattr(self._mw, btn_attr, None)

    def on_tool_changed(self, tool_type):
        """Обработчик смены инструмента."""
        mw = self._mw
        from tools.tool_manager import ToolType
        for tool in ToolType:
            btn_attr = f"_btn_{tool.value.lower()}"
            if hasattr(mw, btn_attr):
                btn = getattr(mw, btn_attr)
                btn.setChecked(tool == tool_type)

    # ==================================================================
    # Обработчики сигналов
    # ==================================================================

    def on_shapes_changed(self):
        """Обработчик изменения списка фигур."""
        mw = self._mw
        mw._canvas_manager.sync_scene_with_manager()
        self.update_statusbar()

    def on_selection_changed(self):
        """Обработчик изменения выделения."""
        mw = self._mw
        selected_count = len(mw._manager.selected_shapes)
        if selected_count == 0:
            mw._status_label.setText("Готово")
        else:
            mw._status_label.setText(f"Выбрано фигур: {selected_count}")

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
        """Настройка стека отмены/повтора."""
        mw = self._mw
        undo_stack = QUndoStack(mw)
        mw._manager.undo_stack = undo_stack

        undo_view = QUndoView(undo_stack)
        undo_dock = QDockWidget("История действий", mw)
        undo_dock.setWidget(undo_view)
        undo_dock.setFixedWidth(200)
        from PySide6.QtCore import Qt
        mw.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, undo_dock)

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
                property_panel.set_multiple_shapes(selected_shapes)
        else:
            property_panel.clear()

    def get_shape_properties_dict(self, shape: "BaseShape") -> dict:
        """Преобразование фигуры в словарь свойств."""
        pen_color = shape.pen_color
        if isinstance(pen_color, QColor):
            pen_color = (pen_color.red(), pen_color.green(), pen_color.blue())
        elif not isinstance(pen_color, tuple):
            pen_color = (0, 0, 0)

        pen_width = shape.pen_width

        brush_color = shape.brush_color
        if isinstance(brush_color, QColor):
            brush_color = (brush_color.red(), brush_color.green(), brush_color.blue())
        elif brush_color is None:
            brush_color = None
        elif not isinstance(brush_color, tuple):
            brush_color = None

        rotation = shape.rotation

        return {
            "pen_color": pen_color,
            "pen_width": pen_width,
            "brush_color": brush_color,
            "rotation": rotation,
        }

    def on_properties_changed(self):
        """Обработчик изменения свойств фигуры через панель свойств."""
        mw = self._mw
        selected_shapes = mw._manager.selected_shapes
        if not selected_shapes:
            return

        try:
            property_panel = mw._property_panel
            if property_panel is None:
                QMessageBox.warning(mw, "Ошибка", "Не активирована property_panel")
                return
            new_properties = property_panel.get_updated_properties()

            for shape in selected_shapes:
                shape.apply_properties(new_properties)

            self.refresh_canvas()
            self.update_statusbar()

        except Exception as e:
            QMessageBox.warning(mw, "Ошибка", f"Не удалось применить свойства: {str(e)}")

    # ==================================================================
    # Привязка к сетке
    # ==================================================================

    def snap_to_grid(self, pos: QPointF) -> QPointF:
        """Привязка координат к сетке, если включена."""
        if self._mw._settings.snap_to_grid and self._mw._settings.grid_spacing > 0:
            spacing = self._mw._settings.grid_spacing
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
        mw._event_manager.clear_temp_shape()
        mw._tool_manager.reset_current_shape()
