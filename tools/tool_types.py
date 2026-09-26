"""Типы инструментов графического редактора."""

from __future__ import annotations

from enum import Enum


class ToolType(Enum):
    """Типы инструментов."""

    SELECT = "select"
    MOVE = "move"
    POINT = "point"
    LINE = "line"
    RAY = "ray"
    INFINITE_LINE = "infinite_line"
    RECTANGLE = "rectangle"
    ELLIPSE = "ellipse"
    POLYGON = "polygon"
    POLYLINE = "polyline"
    ARC = "arc"
    TEXT = "text"
    TRIANGLE_EQUILATERAL = "triangle_equilateral"
    TRIANGLE_ISOSCELES = "triangle_isosceles"
    TRIANGLE_RIGHT = "triangle_right"
    TRIANGLE_OBTUSE = "triangle_obtuse"
    PARALLELOGRAM = "parallelogram"
    TRAPEZOID_ISOSCELES = "trapezoid_isosceles"
    TRAPEZOID = "trapezoid"
    ANGLE = "angle"
