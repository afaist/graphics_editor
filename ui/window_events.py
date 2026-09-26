"""Обёртка EventManager — делегирует подменеджерам."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt

from tools.tool_types import ToolType as ToolTypeEnum

if TYPE_CHECKING:
    from ui.main_window import MainWindow

from ui.window_events_dialogs import DialogManager
from ui.window_events_drawing import DrawingManager
from ui.window_events_mouse import MouseManager


class EventManager:
    """Управление событиями мыши, рисованием и временными фигурами.

    Делегирует работу подменеджерам:
    - MouseManager — press/move/release, выделение, перемещение, ресайз
    - DrawingManager — рисование, временные фигуры, сброс состояния
    - DialogManager — диалоги параметров фигур, фабрика фигур
    """

    def __init__(self, main_window: MainWindow):
        self._mw = main_window
        self._mouse = MouseManager(main_window)
        self._drawing = DrawingManager(main_window)
        self._dialogs = DialogManager(main_window)

    # ------------------------------------------------------------------
    # Точки входа — делегирование
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
            self._mouse.handle_selection_press(pos, shift_pressed)
        elif current_tool == ToolTypeEnum.MOVE:
            self._mouse.handle_move_press(pos, shift_pressed)
        else:
            mw._is_dragging = False
            mw._is_selecting = False
            self._drawing.start_drawing(pos, shift_pressed)

    def on_canvas_mouse_move(self, event):
        """Обработка движения мыши на холсте."""
        self._mouse.on_canvas_mouse_move(event)

    def on_canvas_mouse_release(self, event):
        """Обработка отпускания кнопки мыши на холсте."""
        mw = self._mw
        if mw._canvas is None:
            return
        pos = mw._canvas.mapToScene(event.pos())
        shift_pressed = event.modifiers() & Qt.KeyboardModifier.ShiftModifier

        current_tool = mw._tool_manager.current_tool

        if mw._is_resizing:
            self._mouse.handle_resize_release()
        elif current_tool == ToolTypeEnum.SELECT:
            if mw._is_selecting:
                self._mouse.finish_selection_rectangle()
                self._mouse.update_cursor()
        elif current_tool == ToolTypeEnum.MOVE:
            if mw._is_moving:
                self._mouse.handle_move_release()
        else:
            if mw._is_drawing:
                self._drawing.finish_drawing(pos, shift_pressed)
            mw._is_drawing = False

    # ------------------------------------------------------------------
    # Публичные методы для внешнего использования
    # ------------------------------------------------------------------

    def update_cursor(self):
        """Обновить курсор — делегирование MouseManager."""
        self._mouse.update_cursor()
