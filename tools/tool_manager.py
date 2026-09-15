"""Инструменты рисования."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from PySide6.QtCore import Qt, QPointF, Signal, QObject
from PySide6.QtGui import QColor, QCursor

from shapes.base_shape import BaseShape


class ToolType(Enum):
    """Типы инструментов."""

    SELECT = "select"
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
    BEZIER = "bezier"
    TRIANGLE_EQUILATERAL = "triangle_equilateral"
    TRIANGLE_ISOSCELES = "triangle_isosceles"
    TRIANGLE_RIGHT = "triangle_right"
    TRIANGLE_OBTUSE = "triangle_obtuse"
    PARALLELOGRAM = "parallelogram"
    TRAPEZOID_ISOSCELES = "trapezoid_isosceles"
    TRAPEZOID = "trapezoid"


class ToolManager(QObject):
    """Управление активным инструментом и временными фигурами."""

    tool_changed = Signal(str)
    temp_shape_updated = Signal()
    temp_shape_started = Signal()

    def __init__(self):
        super().__init__()
        self._current_tool: ToolType = ToolType.SELECT
        self._temp_shape: Optional[BaseShape] = None
        self._start_point: Optional[QPointF] = None
        self._polyline_vertices: list = []
        self._polygon_vertices: list = []

    # ------------------------------------------------------------------
    # Свойства
    # ------------------------------------------------------------------

    @property
    def current_tool(self) -> ToolType:
        return self._current_tool

    @current_tool.setter
    def current_tool(self, tool: ToolType) -> None:
        self._current_tool = tool
        self._clear_temp()
        self.tool_changed.emit(tool.value)

    @property
    def is_drawing_tool(self) -> bool:
        return self._current_tool not in (ToolType.SELECT,)

    @property
    def start_point(self) -> Optional[QPointF]:
        return self._start_point

    @property
    def temp_shape(self) -> Optional[BaseShape]:
        return self._temp_shape

    # ------------------------------------------------------------------
    # Старт рисования
    # ------------------------------------------------------------------



    def start_shape(self, point: QPointF, settings) -> None:
        self._clear_temp()
        self._start_point = point
        self.temp_shape_started.emit()

        pen_color = settings.default_pen_color
        pen_width = settings.default_pen_width

        if self._current_tool == ToolType.POINT:
            from shapes.point_shape import PointShape

            self._temp_shape = PointShape(
                point.x(),
                point.y(),
                pen_color=pen_color,
                pen_width=pen_width,
                brush_color=settings.default_brush_color,
            )

        elif self._current_tool == ToolType.LINE:
            from shapes.line_shape import LineShape
            from shapes.base_shape import ShapeType

            self._temp_shape = LineShape(
                point.x(),
                point.y(),
                point.x(),
                point.y(),
                shape_type=ShapeType.LINE,
                pen_color=pen_color,
                pen_width=pen_width,
            )

        elif self._current_tool == ToolType.RAY:
            from shapes.line_shape import LineShape
            from shapes.base_shape import ShapeType

            self._temp_shape = LineShape(
                point.x(),
                point.y(),
                point.x(),
                point.y(),
                shape_type=ShapeType.RAY,
                pen_color=pen_color,
                pen_width=pen_width,
            )

        elif self._current_tool == ToolType.INFINITE_LINE:
            from shapes.line_shape import LineShape
            from shapes.base_shape import ShapeType

            self._temp_shape = LineShape(
                point.x(),
                point.y(),
                point.x(),
                point.y(),
                shape_type=ShapeType.INFINITE_LINE,
                pen_color=pen_color,
                pen_width=pen_width,
            )

        elif self._current_tool == ToolType.RECTANGLE:
            from shapes.rectangle_shape import RectangleShape

            self._temp_shape = RectangleShape(
                point.x(),
                point.y(),
                0,
                0,
                pen_color=pen_color,
                pen_width=pen_width,
                brush_color=settings.default_brush_color,
            )

        elif self._current_tool == ToolType.ELLIPSE:
            from shapes.ellipse_shape import EllipseShape

            self._temp_shape = EllipseShape(
                point.x(),
                point.y(),
                0,
                0,
                pen_color=pen_color,
                pen_width=pen_width,
                brush_color=settings.default_brush_color,
            )

        elif self._current_tool == ToolType.POLYGON:
            self._polygon_vertices = [point]
            from shapes.polygon_shape import PolygonShape

            self._temp_shape = PolygonShape(
                vertices=[(point.x(), point.y())],
                pen_color=pen_color,
                pen_width=pen_width,
                brush_color=settings.default_brush_color,
            )

        elif self._current_tool == ToolType.POLYLINE:
            self._polyline_vertices = [point]
            from shapes.polyline_shape import PolylineShape

            self._temp_shape = PolylineShape(
                vertices=[(point.x(), point.y())],
                pen_color=pen_color,
                pen_width=pen_width,
            )

        elif self._current_tool == ToolType.TEXT:
            from shapes.text_shape import TextShape

            self._temp_shape = TextShape(
                point.x(),
                point.y(),
                text="",
                pen_color=pen_color,
                pen_width=pen_width,
            )

        elif self._current_tool == ToolType.ARC:
            from shapes.arc_shape import ArcShape

            self._temp_shape = ArcShape(
                point.x(),
                point.y(),
                0,
                0,
                start_angle=0.0,
                span_angle=90.0,
                pen_color=pen_color,
                pen_width=pen_width,
                brush_color=settings.default_brush_color,
            )

        elif self._current_tool == ToolType.BEZIER:
            from shapes.bezier_shape import BezierShape

            # Важно: создаём 4 РАЗНЫХ QPointF, иначе все точки будут одним объектом
            p0 = QPointF(point)
            p1 = QPointF(point)
            p2 = QPointF(point)
            p3 = QPointF(point)
            self._temp_shape = BezierShape(
                points=[p0, p1, p2, p3],
                pen_color=pen_color,
                pen_width=pen_width,
            )

    def update_shape(self, point: QPointF, shift_pressed: bool = False) -> None:
        if self._temp_shape is None or self._start_point is None:
            return

        x, y = point.x(), point.y()
        sx, sy = self._start_point.x(), self._start_point.y()

        if self._current_tool in (ToolType.LINE, ToolType.RAY, ToolType.INFINITE_LINE):
            if shift_pressed:
                x, y = self._constrain_angle(sx, sy, x, y)
            if hasattr(self._temp_shape, "set_end_point"):
                self._temp_shape.set_end_point(x, y)

        elif self._current_tool == ToolType.RECTANGLE:
            if shift_pressed:
                size = max(abs(x - sx), abs(y - sy))
                x = sx + size * (1 if x >= sx else -1)
                y = sy + size * (1 if y >= sy else -1)
            if hasattr(self._temp_shape, "set_size"):
                self._temp_shape.set_size(x - sx, y - sy)

        elif self._current_tool == ToolType.ELLIPSE:
            if shift_pressed:
                size = max(abs(x - sx), abs(y - sy))
                x = sx + size * (1 if x >= sx else -1)
                y = sy + size * (1 if y >= sy else -1)
            if hasattr(self._temp_shape, "set_size"):
                self._temp_shape.set_size(x - sx, y - sy)

        elif self._current_tool == ToolType.POLYGON:
            self._polygon_vertices.append(point)
            if hasattr(self._temp_shape, "add_vertex"):
                self._temp_shape.add_vertex(point.x(), point.y())

        elif self._current_tool == ToolType.POLYLINE:
            self._polyline_vertices.append(point)
            if hasattr(self._temp_shape, "add_vertex"):
                self._temp_shape.add_vertex(point.x(), point.y())

        elif self._current_tool == ToolType.TEXT:
            # Текст — одно нажатие, обновление не требуется
            pass

        elif self._current_tool == ToolType.ARC:
            if hasattr(self._temp_shape, "set_arc_params"):
                w = x - sx
                h = y - sy
                if shift_pressed:
                    size = max(abs(w), abs(h))
                    w = size * (1 if w >= 0 else -1)
                    h = size
                self._temp_shape.set_arc_params(sx, sy, w, h)

        elif self._current_tool == ToolType.BEZIER:
            # Для Безье: P0 = start_point (фиксирован),
            # P1/P2 следуют за мышью, P3 остаётся на месте до финального клика
            if self._temp_shape and hasattr(self._temp_shape, 'points'):
                pts = self._temp_shape.points
                if len(pts) >= 4:
                    pts[1].setX(point.x())
                    pts[1].setY(point.y())
                    pts[2].setX(point.x())
                    pts[2].setY(point.y())

        self.temp_shape_updated.emit()

    def finish_current_shape(self) -> Optional[BaseShape]:
        """Завершает рисование текущей фигуры, учитывая её тип."""
        if self._current_tool == ToolType.TEXT:
            return self.finish_text()
        elif self._current_tool == ToolType.BEZIER:
            return self.finish_shape()
        elif self._current_tool in (ToolType.POLYGON,):
            return self.finish_polygon()
        elif self._current_tool in (ToolType.POLYLINE,):
            return self.finish_polyline()
        else:
            # Для остальных инструментов (line, rect, ellipse, point)
            # finish_shape просто возвращает текущую временную фигуру
            return self.finish_shape()

    def finish_shape(self, point: Optional[QPointF] = None) -> Optional[BaseShape]:
        if self._temp_shape is None:
            return None
        shape = self._temp_shape

        # Для Безье: устанавливаем финальную точку P3
        if self._current_tool == ToolType.BEZIER and point is not None:
            if hasattr(shape, 'points') and len(shape.points) >= 4:
                shape.points[3].setX(point.x())
                shape.points[3].setY(point.y())

        self._clear_temp()
        return shape

    def add_polyline_vertex(self, point: QPointF) -> None:
        if self._temp_shape and self._current_tool == ToolType.POLYLINE:
            if hasattr(self._temp_shape, "add_vertex"):
                self._temp_shape.add_vertex(point.x(), point.y())
            self.temp_shape_updated.emit()

    def finish_polyline(self) -> Optional[BaseShape]:
        if self._temp_shape and self._current_tool == ToolType.POLYLINE:
            shape = self._temp_shape
            self._clear_temp()
            return shape
        return None

    def finish_polygon(self, close: bool = True) -> Optional[BaseShape]:
        if self._temp_shape and self._current_tool == ToolType.POLYGON:
            # Если нужно замкнуть полигон, добавляем первую вершину в конец
            if close and len(self._polygon_vertices) >= 3:
                first_point = self._polygon_vertices[0]
                if hasattr(self._temp_shape, "add_vertex"):
                    self._temp_shape.add_vertex(first_point.x(), first_point.y())
            shape = self._temp_shape
            self._clear_temp()
            return shape
        return None

    def can_finish_polygon(self) -> bool:
        if self._current_tool != ToolType.POLYGON:
            return False
        if not self._polygon_vertices:  # явно проверяем на пустоту
            return False
        return len(self._polygon_vertices) >= 3

    def can_finish_polyline(self) -> bool:
        if self._current_tool != ToolType.POLYLINE:
            return False
        if not self._polyline_vertices:
            return False
        return len(self._polyline_vertices) >= 2

    def finish_text(self) -> Optional[BaseShape]:
        """Завершает создание текстовой фигуры."""
        if self._current_tool == ToolType.TEXT and self._temp_shape:
            shape = self._temp_shape
            self._clear_temp()
            return shape
        return None

    # ------------------------------------------------------------------
    # Сервисные методы
    # ------------------------------------------------------------------

    def reset_current_shape(self) -> None:
        """Публичный метод для сброса состояния рисования."""
        self._clear_temp()

    def _clear_temp(self) -> None:
        """Очищает временные данные рисования."""
        self._temp_shape = None
        self._start_point = None
        self._polygon_vertices.clear()
        self._polyline_vertices.clear()

    @staticmethod
    def _constrain_angle(
        x1: float, y1: float, x2: float, y2: float
    ) -> tuple[float, float]:
        """Привязка к углам 0, 45, 90, 135, 180, 225, 270, 315 градусов."""
        import math

        angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
        angles = [0, 45, 90, 135, 180, 225, 270, 315]
        best = min(angles, key=lambda a: abs(angle - a))
        rad = math.radians(best)
        dist = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        return (
            x1 + dist * math.cos(rad),
            y1 + dist * math.sin(rad),
        )