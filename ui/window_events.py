"""Модуль обработки событий мыши и рисования для MainWindow."""

from __future__ import annotations

from typing import TYPE_CHECKING


from PySide6.QtCore import Qt, QPointF, QRectF

from tools.tool_manager import ToolManager, ToolType as ToolTypeEnum

if TYPE_CHECKING:
    from ui.main_window import MainWindow


class EventManager:
    """Управление событиями мыши, рисованием и временными фигурами."""

    def __init__(self, main_window: "MainWindow"):
        self._mw = main_window

    # ------------------------------------------------------------------
    # Обработка мыши
    # ------------------------------------------------------------------

    def on_canvas_mouse_press(self, event):
        """Обработка нажатия мыши на холсте."""
        mw = self._mw
        if mw._canvas is None:
            return
        pos = mw._canvas.mapToScene(event.pos())
        shift_pressed = event.modifiers() & Qt.KeyboardModifier.ShiftModifier

        current_tool = mw._tool_manager.current_tool

        if current_tool == ToolTypeEnum.SELECT:
            self.handle_selection_press(pos, shift_pressed)
        else:
            mw._is_dragging = False
            mw._is_selecting = False
            self.start_drawing(pos, shift_pressed)

    def handle_selection_press(self, pos: QPointF, shift_pressed: bool):
        """Обработка выделения фигур."""
        mw = self._mw
        hit_shape = mw._manager.hit_test(pos)

        if hit_shape:
            if shift_pressed:
                mw._manager.toggle_selection(hit_shape.id)
            else:
                if hit_shape.id not in mw._manager.selected_ids:
                    mw._manager.select_shape(hit_shape.id)
                mw._selection_start_pos = pos
                mw._is_dragging = False
        else:
            if not shift_pressed:
                mw._manager.select_none()
            mw._selection_rect_start = pos
            mw._is_selecting = True

    def start_drawing(self, pos: QPointF, shift_pressed: bool):
        """Начало рисования новой фигуры."""
        mw = self._mw
        mw._is_drawing = True
        mw._tool_manager.start_shape(pos, mw._settings)
        self.update_temp_shape()

    def on_canvas_mouse_move(self, event):
        """Обработка движения мыши на холсте."""
        mw = self._mw
        if mw._canvas is None:
            return
        pos = mw._canvas.mapToScene(event.pos())
        mw._last_mouse_pos = pos
        shift_pressed = event.modifiers() & Qt.KeyboardModifier.ShiftModifier

        current_tool = mw._tool_manager.current_tool

        if current_tool == ToolTypeEnum.SELECT and mw._is_dragging:
            self.move_selected_shapes(pos)
        elif mw._is_drawing and mw._tool_manager.temp_shape is not None:
            self.continue_drawing(pos, shift_pressed)

    def move_selected_shapes(self, current_pos: QPointF):
        """Перемещение выделенных фигур."""
        mw = self._mw
        if mw._selection_start_pos is None:
            return
        dx = current_pos.x() - mw._selection_start_pos.x()
        dy = current_pos.y() - mw._selection_start_pos.y()

        if abs(dx) > 3 or abs(dy) > 3:
            mw._is_dragging = True
            mw._manager.move_selected(dx, dy)
            mw._selection_start_pos = current_pos

    def continue_drawing(self, pos: QPointF, shift_pressed: bool):
        """Продолжение рисования фигуры."""
        mw = self._mw
        mw._tool_manager.update_shape(pos, shift_pressed)
        self.update_temp_shape()

    def on_canvas_mouse_release(self, event):
        """Обработка отпускания кнопки мыши на холсте."""
        mw = self._mw
        if mw._canvas is None:
            return
        pos = mw._canvas.mapToScene(event.pos())
        shift_pressed = event.modifiers() & Qt.KeyboardModifier.ShiftModifier

        current_tool = mw._tool_manager.current_tool

        if current_tool == ToolTypeEnum.SELECT:
            if mw._is_selecting:
                self.finish_selection_rectangle()
            elif mw._is_dragging:
                mw._is_dragging = False
        else:
            if mw._is_drawing:
                self.finish_drawing(pos, shift_pressed)
            mw._is_drawing = False

    # ------------------------------------------------------------------
    # Завершение операций
    # ------------------------------------------------------------------

    def finish_selection_rectangle(self):
        """Завершение выделения рамкой."""
        mw = self._mw
        if mw._selection_rect_start is None or mw._last_mouse_pos is None:
            return
        start = mw._selection_rect_start
        end = mw._last_mouse_pos
        selection_rect = QRectF(
            min(start.x(), end.x()),
            min(start.y(), end.y()),
            abs(end.x() - start.x()),
            abs(end.y() - start.y()),
        )

        if selection_rect.width() > 5 or selection_rect.height() > 5:
            mw._manager.select_by_rect(selection_rect)

        mw._is_selecting = False

    def finish_drawing(self, pos: QPointF, shift_pressed: bool):
        """Завершение рисования фигуры."""
        mw = self._mw
        from shapes.point_shape import PointShape
        from shapes.line_shape import LineShape
        from shapes.polyline_shape import PolylineShape
        from tools.tool_manager import ToolType

        current_tool = mw._tool_manager.current_tool
        shape = None

        if current_tool in (ToolType.POLYGON, ToolType.POLYLINE):
            shape = mw._tool_manager.finish_current_shape()
        else:
            shape = mw._tool_manager.finish_shape(pos)

        if shape is None:
            mw._is_drawing = False
            return

        if isinstance(shape, PointShape):
            mw.add_shape(shape)
            self.clear_temp_shape()
        else:
            br = shape.bounding_rect()
            w = br.width()
            h = br.height()

            if isinstance(shape, (LineShape, PolylineShape)):
                if shape.length() > 1.0:
                    mw.add_shape(shape)
                    self.clear_temp_shape()
            elif w > 1 or h > 1:
                mw.add_shape(shape)
                self.clear_temp_shape()

        mw._is_drawing = False

    # ------------------------------------------------------------------
    # Временные фигуры
    # ------------------------------------------------------------------

    def update_temp_shape(self):
        """Обновление временной фигуры на сцене."""
        mw = self._mw
        from ui.scene_items import ShapeSceneItem

        self.clear_temp_shape()

        temp_shape = mw._tool_manager.temp_shape
        if temp_shape is None or mw._scene is None:
            return

        item = ShapeSceneItem(temp_shape)
        item.setZValue(1000)  # Поверх всех фигур
        mw._scene.addItem(item)
        mw._temp_shape_item = item

    def clear_temp_shape(self):
        """Очистка временной фигуры."""
        mw = self._mw
        if hasattr(mw, "_temp_shape_item") and mw._temp_shape_item is not None:
            try:
                if mw._scene and mw._temp_shape_item.scene() == mw._scene:
                    mw._scene.removeItem(mw._temp_shape_item)
            except RuntimeError:
                pass
            finally:
                mw._temp_shape_item = None

    # ------------------------------------------------------------------
    # Сброс состояния
    # ------------------------------------------------------------------

    def reset_drawing_state(self):
        """Сброс состояния рисования."""
        mw = self._mw
        mw._is_drawing = False
        mw._last_mouse_pos = None
        mw._selection_rect_start = None
        mw._selection_start_pos = None
        mw._is_dragging = False
        mw._is_selecting = False

        self.clear_temp_shape()
        mw._tool_manager.reset_current_shape()
