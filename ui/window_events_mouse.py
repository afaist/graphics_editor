"""Обработчики событий мыши: выделение, перемещение, ресайз, курсоры."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QPointF, QRectF, Qt

from shapes.base_shape import HandleType
from tools.tool_types import ToolType as ToolTypeEnum

if TYPE_CHECKING:
    from ui.main_window import MainWindow


class MouseManager:
    """Управление обработкой мыши: press, move, release, курсоры."""

    def __init__(self, main_window: MainWindow):
        self._mw = main_window

    # ------------------------------------------------------------------
    # Точки входа
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
        elif current_tool == ToolTypeEnum.MOVE:
            self.handle_move_press(pos, shift_pressed)
        else:
            mw._is_dragging = False
            mw._is_selecting = False

    def on_canvas_mouse_move(self, event):
        """Обработка движения мыши на холсте."""
        mw = self._mw
        if mw._canvas is None:
            return
        pos = mw._canvas.mapToScene(event.pos())
        mw._last_mouse_pos = pos
        shift_pressed = event.modifiers() & Qt.KeyboardModifier.ShiftModifier

        current_tool = mw._tool_manager.current_tool

        if mw._is_resizing:
            self.handle_resize_move(pos, shift_pressed)
            self._set_resize_cursor()
        elif current_tool == ToolTypeEnum.SELECT and not mw._is_selecting:
            self._set_select_hover_cursor()
        elif current_tool == ToolTypeEnum.SELECT:
            if mw._is_selecting:
                self.update_cursor()
        elif current_tool == ToolTypeEnum.MOVE:
            if mw._is_moving:
                self.handle_move_move(pos)

    def on_canvas_mouse_release(self, event):
        """Обработка отпускания кнопки мыши на холсте."""
        mw = self._mw
        if mw._canvas is None:
            return
        _pos = mw._canvas.mapToScene(event.pos())
        _shift_pressed = event.modifiers() & Qt.KeyboardModifier.ShiftModifier

        current_tool = mw._tool_manager.current_tool

        if mw._is_resizing:
            self.handle_resize_release()
        elif current_tool == ToolTypeEnum.SELECT:
            if mw._is_selecting:
                self.finish_selection_rectangle()
                self.update_cursor()
        elif current_tool == ToolTypeEnum.MOVE:
            if mw._is_moving:
                self.handle_move_release()

    # ------------------------------------------------------------------
    # Выделение
    # ------------------------------------------------------------------

    def handle_selection_press(self, pos: QPointF, shift_pressed: bool):
        """Обработка выделения фигур."""
        mw = self._mw
        # Сначала проверяем, попали ли в ручку масштабирования
        if mw._manager.selected_shapes:
            self.handle_resize_press(pos)
            if mw._is_resizing:
                return
        hit_shape = mw._manager.hit_test(pos)

        if hit_shape and mw._manager.has_shape(hit_shape.id):
            if shift_pressed:
                mw._manager.toggle_selection(hit_shape.id)
            else:
                if hit_shape.id not in mw._manager.selected_ids:
                    mw._manager.select_shape(hit_shape.id)
        else:
            if not shift_pressed:
                mw._manager.select_none()
            mw._selection_rect_start = pos
            mw._is_selecting = True
            self.update_cursor()

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

    # ------------------------------------------------------------------
    # Перемещение
    # ------------------------------------------------------------------

    def handle_move_press(self, pos: QPointF, shift_pressed: bool):
        """Обработка нажатия мыши в инструменте перемещения."""
        mw = self._mw
        # Если перемещение уже активно — игнорируем повторное нажатие
        if mw._is_moving and mw._selection_start_pos is not None:
            return
        # Если есть выделенные фигуры — сразу начинаем перемещение
        if mw._manager.selected_ids:
            mw._is_moving = True
            mw._selection_start_pos = pos
        else:
            # Иначе выделяем фигуру под курсором
            hit_shape = mw._manager.hit_test(pos)
            if hit_shape:
                mw._manager.select_shape(hit_shape.id)
                mw._is_moving = True
                mw._selection_start_pos = pos
            else:
                # Клик по пустому месту — сбрасываем выделение
                mw._manager.select_none()
                mw._is_moving = False

    def handle_move_move(self, current_pos: QPointF):
        """Перемещение выделенных фигур."""
        mw = self._mw
        if mw._selection_start_pos is None:
            return
        dx = current_pos.x() - mw._selection_start_pos.x()
        dy = current_pos.y() - mw._selection_start_pos.y()
        if abs(dx) > 1 or abs(dy) > 1:
            mw._manager.move_selected(dx, dy)
            mw._selection_start_pos = current_pos

    def handle_move_release(self):
        """Завершение перемещения."""
        mw = self._mw
        mw._is_moving = False
        mw._selection_start_pos = None

    # ------------------------------------------------------------------
    # Ресайз
    # ------------------------------------------------------------------

    def handle_resize_press(self, pos: QPointF):
        """Начало масштабирования за ручку."""
        mw = self._mw
        if mw._is_resizing:
            return
        # Ищем ручку среди выделенных фигур
        for shape in mw._manager.selected_shapes:
            handle_type = shape.get_handle_type(pos)
            if handle_type != HandleType.NONE:
                mw._is_resizing = True
                mw._resize_shape = shape
                mw._selection_start_pos = pos
                mw._resize_handle_type = handle_type
                # Сохраняем состояние фигуры для undo
                mw._resize_shape_dict = shape.to_dict()
                return

    def handle_resize_move(self, current_pos: QPointF, shift_pressed: bool = False):
        """Масштабирование за ручку."""
        mw = self._mw
        if not mw._is_resizing or mw._resize_shape is None or mw._selection_start_pos is None:
            return
        mw._resize_shape.apply_handle_transform(
            mw._resize_handle_type,
            mw._selection_start_pos,
            current_pos,
            shift_pressed,
        )
        mw._selection_start_pos = current_pos
        mw._manager.shapes_changed.emit()

    def handle_resize_release(self):
        """Завершение масштабирования."""
        mw = self._mw
        if mw._is_resizing and mw._resize_shape is not None and mw._resize_shape_dict is not None:
            # Создаём undo-команду для изменения свойств фигуры
            from manager.undo_commands import ResizeShapeCommand

            cmd = ResizeShapeCommand(mw._manager, mw._resize_shape.id, mw._resize_shape_dict)
            mw._manager.undo_stack.push(cmd)
        mw._is_resizing = False
        mw._resize_shape = None
        mw._resize_shape_dict = None
        mw._resize_handle_type = HandleType.NONE
        mw._selection_start_pos = None

    # ------------------------------------------------------------------
    # Курсоры
    # ------------------------------------------------------------------

    def update_cursor(self):
        """Установить курсор в зависимости от текущего инструмента и состояния."""
        mw = self._mw
        if not mw._canvas:
            return
        tool = mw._tool_manager.current_tool
        if tool == ToolTypeEnum.MOVE:
            mw._canvas.setCursor(Qt.CursorShape.OpenHandCursor)
        elif tool == ToolTypeEnum.SELECT and mw._is_selecting:
            mw._canvas.setCursor(Qt.CursorShape.CrossCursor)
        elif tool == ToolTypeEnum.SELECT:
            mw._canvas.setCursor(Qt.CursorShape.PointingHandCursor)
        elif mw._tool_manager.is_drawing_tool:
            mw._canvas.setCursor(Qt.CursorShape.CrossCursor)
        else:
            mw._canvas.setCursor(Qt.CursorShape.ArrowCursor)

    def _set_resize_cursor(self):
        """Устанавливаем курсор в зависимости от типа ручки ресайза."""
        mw = self._mw
        ht = mw._resize_handle_type
        if ht in (HandleType.TOP_LEFT, HandleType.BOTTOM_RIGHT):
            mw._canvas.setCursor(Qt.CursorShape.SizeFDiagCursor)
        elif ht in (HandleType.TOP_RIGHT, HandleType.BOTTOM_LEFT):
            mw._canvas.setCursor(Qt.CursorShape.SizeBDiagCursor)
        elif ht in (HandleType.TOP_CENTER, HandleType.BOTTOM_CENTER):
            mw._canvas.setCursor(Qt.CursorShape.SizeVerCursor)
        elif ht in (HandleType.LEFT_CENTER, HandleType.RIGHT_CENTER):
            mw._canvas.setCursor(Qt.CursorShape.SizeHorCursor)
        else:
            mw._canvas.setCursor(Qt.CursorShape.PointingHandCursor)

    def _set_select_hover_cursor(self):
        """Устанавливаем курсор при наведении на фигуру/ручку в режиме SELECT."""
        mw = self._mw
        if mw._manager.selected_shapes:
            for shape in mw._manager.selected_shapes:
                handle_type = shape.get_handle_type(mw._last_mouse_pos or QPointF(0, 0))
                if handle_type != HandleType.NONE:
                    if handle_type in (HandleType.TOP_LEFT, HandleType.BOTTOM_RIGHT):
                        mw._canvas.setCursor(Qt.CursorShape.SizeFDiagCursor)
                    elif handle_type in (HandleType.TOP_RIGHT, HandleType.BOTTOM_LEFT):
                        mw._canvas.setCursor(Qt.CursorShape.SizeBDiagCursor)
                    elif handle_type in (HandleType.TOP_CENTER, HandleType.BOTTOM_CENTER):
                        mw._canvas.setCursor(Qt.CursorShape.SizeVerCursor)
                    elif handle_type in (HandleType.LEFT_CENTER, HandleType.RIGHT_CENTER):
                        mw._canvas.setCursor(Qt.CursorShape.SizeHorCursor)
                    else:
                        mw._canvas.setCursor(Qt.CursorShape.PointingHandCursor)
                    return
        mw._canvas.setCursor(Qt.CursorShape.PointingHandCursor)
