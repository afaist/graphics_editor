"""Контекст состояния рисования — вынесен из MainWindow для чистоты архитектуры."""

from __future__ import annotations

from PySide6.QtCore import QPointF

from shapes.base_shape import BaseShape


class DrawingContext:
    """Централизованное состояние взаимодействия пользователя с холстом.

    Включает флаги режимов, координаты мыши и временные объекты,
    связанные с текущей операцией рисования/перемещения/выделения.
    """

    # ---- Флаги режимов ----
    is_drawing: bool
    is_dragging: bool
    is_selecting: bool
    is_moving: bool
    is_resizing: bool

    # ---- Объекты, связанные с текущей операцией ----
    resize_shape: BaseShape | None
    resize_shape_dict: dict | None
    start_point: QPointF | None
    last_mouse_pos: QPointF | None
    selection_start_pos: QPointF | None
    selection_rect_start: QPointF | None

    # ---- Временные UI-объекты ----
    temp_shape_item: object | None  # ShapeSceneItem | None

    def __init__(self) -> None:
        self.reset()

    # ------------------------------------------------------------------
    # Сброс состояния
    # ------------------------------------------------------------------

    def reset(self) -> None:
        """Полный сброс всех флагов и координат."""
        self.is_drawing = False
        self.is_dragging = False
        self.is_selecting = False
        self.is_moving = False
        self.is_resizing = False
        self.resize_shape = None
        self.resize_shape_dict = None
        self.start_point = None
        self.last_mouse_pos = None
        self.selection_start_pos = None
        self.selection_rect_start = None
        self.temp_shape_item = None

    def reset_drawing(self) -> None:
        """Сбросить только состояние рисования (не сбрасывать selection/moving)."""
        self.is_drawing = False
        self.start_point = None
        self.last_mouse_pos = None
        self.selection_rect_start = None
        self.selection_start_pos = None
        self.is_dragging = False
        self.is_selecting = False
        self.is_moving = False
        self.is_resizing = False
        self.resize_shape = None
        self.resize_shape_dict = None
