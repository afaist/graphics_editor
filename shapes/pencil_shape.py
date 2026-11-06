"""Фигура: Карандаш (свободное рисование)."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QPainter, QPen, QPolygonF

from .base_shape import BaseShape, HandleType, ShapeType


class PencilShape(BaseShape):
    """Карандаш — свободное рисование линией из точек."""

    def __init__(
        self,
        points: list[tuple[float, float]] | None = None,
        pen_color: tuple[int, int, int] = (0, 0, 0),
        pen_width: float = 2.0,
        pen_style: int = 1,  # Qt.PenStyle.SolidLine = 1
        brush_color: tuple[int, int, int] | None = None,
        selected: bool = False,
    ):
        # Устанавливаем _points ДО вызова super(), так как BaseShape.__init__
        # вызывает self._get_shape_type(), который его читает
        self._points: list[QPointF] = []
        if points:
            self._points = [QPointF(p[0], p[1]) for p in points]
        if hasattr(pen_style, "value"):
            self._pen_style = pen_style.value
        else:
            self._pen_style = int(pen_style)
        super().__init__(pen_color, pen_width, brush_color, selected)

    def _get_shape_type(self) -> ShapeType:
        """Возвращает тип фигуры — PENCIL."""
        return ShapeType.PENCIL

    def add_point(self, x: float, y: float) -> None:
        """Добавить точку к линии карандаша."""
        self._points.append(QPointF(x, y))

    def _rotation_center(self) -> tuple[float, float] | None:
        """Возвращает None — карандаш не поддерживает поворот."""
        return None

    def _draw_shape_content(self, painter: QPainter) -> None:
        """Рисует линию карандаша."""
        if len(self._points) < 2:
            return
        pen = QPen(self.pen_color, self.pen_width)
        pen.setStyle(Qt.PenStyle(self._pen_style))
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        if len(self._points) == 2:
            painter.drawLine(self._points[0], self._points[1])
        else:
            # Рисуем плавную кривую через polyline
            painter.drawPolyline(QPolygonF(self._points))

    def contains_point(self, point: QPointF) -> bool:
        """Проверить, принадлежит ли точка линии."""
        if len(self._points) < 2:
            return False
        # Проверяем близость к любому отрезку
        tolerance = self.pen_width / 2 + 3
        for i in range(len(self._points) - 1):
            p1 = self._points[i]
            p2 = self._points[i + 1]
            dist = self._dist_to_segment(point.x(), point.y(), p1.x(), p1.y(), p2.x(), p2.y())
            if dist <= tolerance:
                return True
        return False

    def move(self, dx: float, dy: float) -> None:
        for p in self._points:
            p.setX(p.x() + dx)
            p.setY(p.y() + dy)

    def rotate(self, angle: float, center: QPointF | None = None) -> None:
        """Повернуть линию карандаша на angle градусов."""
        if not self._points:
            return
        if center is None:
            cx, cy = self._center_of_vertices(self._points)
        else:
            cx, cy = center.x(), center.y()
        self._rotate_vertices(self._points, cx, cy, angle)

    def scale(self, factor: float, center: QPointF | None = None) -> None:
        """Масштабировать линию карандаша."""
        if not self._points:
            return
        if center is None:
            cx, cy = self._center_of_vertices(self._points)
        else:
            cx, cy = center.x(), center.y()
        self._scale_vertices(self._points, cx, cy, factor)

    def bounding_rect(self) -> QRectF:
        if not self._points:
            return QRectF()
        xs = [p.x() for p in self._points]
        ys = [p.y() for p in self._points]
        pad = self.pen_width / 2 + 2
        return QRectF(
            min(xs) - pad,
            min(ys) - pad,
            max(xs) - min(xs) + pad * 2,
            max(ys) - min(ys) + pad * 2,
        )

    def _handle_positions(self) -> list[tuple[float, float]]:
        return [(p.x(), p.y()) for p in self._points]

    def get_handles(self) -> list[QPointF]:
        return list(self._points)

    def get_handle_type(self, point: QPointF, tolerance: float = 5.0) -> HandleType:
        for i, p in enumerate(self._points):
            dx = point.x() - p.x()
            dy = point.y() - p.y()
            if (dx * dx + dy * dy) ** 0.5 <= tolerance:
                handle_val = i + 2
                if handle_val <= 10:
                    return HandleType(handle_val)
        return HandleType.NONE

    def apply_handle_transform(
        self, handle: HandleType, point: QPointF, mouse_pos: QPointF, shift_pressed: bool = False
    ) -> None:
        if handle == HandleType.MOVE:
            dx = mouse_pos.x() - point.x()
            dy = mouse_pos.y() - point.y()
            self.move(dx, dy)
            return
        idx = handle.value - 2
        if 0 <= idx < len(self._points):
            self._points[idx].setX(mouse_pos.x())
            self._points[idx].setY(mouse_pos.y())

    def get_position_data(self) -> dict[str, Any]:
        return {
            "points": [(p.x(), p.y()) for p in self._points],
        }

    def restore_position_data(self, data: dict[str, Any]) -> None:
        points_data = data["points"]
        self._points = [QPointF(p[0], p[1]) for p in points_data]

    def get_properties(self) -> dict[str, Any]:
        d = super().get_properties()
        d["_points_count"] = len(self._points)
        return d

    def apply_properties(self, properties: dict[str, Any]) -> None:
        super().apply_properties(properties)
        if "pen_style" in properties:
            self._pen_style = properties["pen_style"]

    def to_dict(self) -> dict[str, Any]:
        d = super().to_dict()
        d["points"] = [{"x": p.x(), "y": p.y()} for p in self._points]
        d["pen_style"] = self._pen_style
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PencilShape:
        points_data = data.get("points", [])
        points = [(p["x"], p["y"]) for p in points_data] if points_data else []
        obj = cls(
            points=points,
            pen_color=data["pen_color"],
            pen_width=data.get("pen_width", 2.0),
            pen_style=data.get("pen_style", 1),
            brush_color=data.get("brush_color"),
            selected=data.get("selected", False),
        )
        obj._rotation = data.get("rotation", 0.0)
        obj.id = data["id"]
        obj.group_id = data.get("group_id")
        return obj
