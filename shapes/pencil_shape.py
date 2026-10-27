"""Фигура: Карандаш (свободное рисование)."""

from __future__ import annotations

import math
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
        brush_color: tuple[int, int, int] | None = None,
        selected: bool = False,
    ):
        # Устанавливаем _points ДО вызова super(), так как BaseShape.__init__
        # вызывает self._get_shape_type(), который его читает
        self._points: list[QPointF] = []
        if points:
            self._points = [QPointF(p[0], p[1]) for p in points]
        super().__init__(pen_color, pen_width, brush_color, selected)

    def _get_shape_type(self) -> ShapeType:
        return ShapeType.PENCIL

    def set_end_point(self, x: float, y: float) -> None:
        pass

    def set_size(self, width: float, height: float) -> None:
        pass

    def add_vertex(self, x: float, y: float) -> None:
        pass

    def add_point(self, x: float, y: float) -> None:
        """Добавить точку к линии карандаша."""
        self._points.append(QPointF(x, y))

    def draw(self, painter: QPainter) -> None:
        """Отрисовать линию карандаша."""
        if len(self._points) < 2:
            return
        painter.save()
        try:
            pen = QPen(self.pen_color, self.pen_width)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)

            if len(self._points) == 2:
                painter.drawLine(self._points[0], self._points[1])
            else:
                # Рисуем плавную кривую через polyline
                painter.drawPolyline(QPolygonF(self._points))
        finally:
            painter.restore()

    def contains_point(self, point: QPointF) -> bool:
        """Проверить, принадлежит ли точка линии."""
        if len(self._points) < 2:
            return False
        # Проверяем близость к любому отрезку
        tolerance = self.pen_width / 2 + 3
        for i in range(len(self._points) - 1):
            p1 = self._points[i]
            p2 = self._points[i + 1]
            dist = self._point_to_segment_distance(point, p1, p2)
            if dist <= tolerance:
                return True
        return False

    @staticmethod
    def _point_to_segment_distance(p: QPointF, a: QPointF, b: QPointF) -> float:
        """Расстояние от точки p до отрезка ab."""
        dx = b.x() - a.x()
        dy = b.y() - a.y()
        length_sq = dx * dx + dy * dy
        if length_sq < 1e-10:
            return math.sqrt((p.x() - a.x()) ** 2 + (p.y() - a.y()) ** 2)
        t = max(0, min(1, ((p.x() - a.x()) * dx + (p.y() - a.y()) * dy) / length_sq))
        proj_x = a.x() + t * dx
        proj_y = a.y() + t * dy
        return math.sqrt((p.x() - proj_x) ** 2 + (p.y() - proj_y) ** 2)

    def move(self, dx: float, dy: float) -> None:
        for p in self._points:
            p.setX(p.x() + dx)
            p.setY(p.y() + dy)

    def rotate(self, angle: float, center: QPointF | None = None) -> None:
        if center is None:
            cx = sum(p.x() for p in self._points) / len(self._points)
            cy = sum(p.y() for p in self._points) / len(self._points)
            center = QPointF(cx, cy)
        rad = math.radians(angle)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        for p in self._points:
            dx = p.x() - center.x()
            dy = p.y() - center.y()
            p.setX(center.x() + dx * cos_a - dy * sin_a)
            p.setY(center.y() + dx * sin_a + dy * cos_a)

    def scale(self, factor: float, center: QPointF | None = None) -> None:
        if center is None:
            cx = sum(p.x() for p in self._points) / len(self._points)
            cy = sum(p.y() for p in self._points) / len(self._points)
            center = QPointF(cx, cy)
        for p in self._points:
            p.setX(center.x() + (p.x() - center.x()) * factor)
            p.setY(center.y() + (p.y() - center.y()) * factor)

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

    def get_handles(self) -> list[QPointF]:
        return list(self._points)

    def get_handle_type(self, point: QPointF, tolerance: float = 5.0) -> HandleType:
        for i, p in enumerate(self._points):
            dx = point.x() - p.x()
            dy = point.y() - p.y()
            if math.sqrt(dx * dx + dy * dy) <= tolerance:
                return HandleType(i + 2)
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

    def to_dict(self) -> dict[str, Any]:
        d = super().to_dict()
        d["points"] = [{"x": p.x(), "y": p.y()} for p in self._points]
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PencilShape:
        points_data = data.get("points", [])
        points = [(p["x"], p["y"]) for p in points_data] if points_data else []
        obj = cls(
            points=points,
            pen_color=data["pen_color"],
            pen_width=data.get("pen_width", 2.0),
            brush_color=data.get("brush_color"),
            selected=data.get("selected", False),
        )
        obj._rotation = data.get("rotation", 0.0)
        obj.id = data["id"]
        obj.group_id = data.get("group_id")
        return obj
