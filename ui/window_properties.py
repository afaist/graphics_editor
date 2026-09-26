"""Свойства DrawingContext — обёртки для обратной совместимости."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QPointF

from shapes.base_shape import BaseShape, HandleType

if TYPE_CHECKING:
    from ui.main_window import MainWindow


class DrawingContextProperties:
    """Обёртки свойств DrawingContext для MainWindow.

    Все property-обёртки над self._drawing.xxx вынесены сюда
    для уменьшения размера main_window.py.
    """

    def __init__(self, main_window: MainWindow):
        self._mw = main_window

    # ------------------------------------------------------------------
    # Свойства DrawingContext (обёртки для обратной совместимости)
    # ------------------------------------------------------------------

    @property
    def is_drawing(self) -> bool:
        return self._mw._drawing.is_drawing

    @is_drawing.setter
    def is_drawing(self, value: bool) -> None:
        self._mw._drawing.is_drawing = value

    @property
    def is_dragging(self) -> bool:
        return self._mw._drawing.is_dragging

    @is_dragging.setter
    def is_dragging(self, value: bool) -> None:
        self._mw._drawing.is_dragging = value

    @property
    def is_selecting(self) -> bool:
        return self._mw._drawing.is_selecting

    @is_selecting.setter
    def is_selecting(self, value: bool) -> None:
        self._mw._drawing.is_selecting = value

    @property
    def is_moving(self) -> bool:
        return self._mw._drawing.is_moving

    @is_moving.setter
    def is_moving(self, value: bool) -> None:
        self._mw._drawing.is_moving = value

    @property
    def is_resizing(self) -> bool:
        return self._mw._drawing.is_resizing

    @is_resizing.setter
    def is_resizing(self, value: bool) -> None:
        self._mw._drawing.is_resizing = value

    @property
    def resize_shape(self) -> BaseShape | None:
        return self._mw._drawing.resize_shape

    @resize_shape.setter
    def resize_shape(self, value: BaseShape | None) -> None:
        self._mw._drawing.resize_shape = value

    @property
    def resize_shape_dict(self) -> dict | None:
        return self._mw._drawing.resize_shape_dict

    @resize_shape_dict.setter
    def resize_shape_dict(self, value: dict | None) -> None:
        self._mw._drawing.resize_shape_dict = value

    @property
    def resize_handle_type(self) -> HandleType:
        return self._mw._drawing.resize_handle_type

    @resize_handle_type.setter
    def resize_handle_type(self, value: HandleType) -> None:
        self._mw._drawing.resize_handle_type = value

    @property
    def start_point(self) -> QPointF | None:
        return self._mw._drawing.start_point

    @start_point.setter
    def start_point(self, value: QPointF | None) -> None:
        self._mw._drawing.start_point = value

    @property
    def last_mouse_pos(self) -> QPointF | None:
        return self._mw._drawing.last_mouse_pos

    @last_mouse_pos.setter
    def last_mouse_pos(self, value: QPointF | None) -> None:
        self._mw._drawing.last_mouse_pos = value

    @property
    def selection_start_pos(self) -> QPointF | None:
        return self._mw._drawing.selection_start_pos

    @selection_start_pos.setter
    def selection_start_pos(self, value: QPointF | None) -> None:
        self._mw._drawing.selection_start_pos = value

    @property
    def selection_rect_start(self) -> QPointF | None:
        return self._mw._drawing.selection_rect_start

    @selection_rect_start.setter
    def selection_rect_start(self, value: QPointF | None) -> None:
        self._mw._drawing.selection_rect_start = value

    @property
    def temp_shape_item(self) -> object | None:
        return self._mw._drawing.temp_shape_item

    @temp_shape_item.setter
    def temp_shape_item(self, value: object | None) -> None:
        self._mw._drawing.temp_shape_item = value

    def reset_drawing_state(self) -> None:
        """Сбросить состояние рисования (вызывается из EventManager)."""
        self._mw._drawing.reset_drawing()
