"""Фигура: Парабола."""

from __future__ import annotations

import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QPainter, QPen

from .base_shape import BaseShape, HandleType, ShapeType


class ParabolaShape(BaseShape):
    """Парабола, заданная вершиной, фокальным параметром и направлением.

    Уравнение:
    - direction='up':    y = a*(x-h)^2 + k,  a = 1/(4p)
    - direction='down':  y = -a*(x-h)^2 + k, a = 1/(4p)
    - direction='right': x = a*(y-k)^2 + h,  a = 1/(4p)
    - direction='left':  x = -a*(y-k)^2 + h, a = 1/(4p)
    """

    VALID_DIRECTIONS = ("up", "down", "right", "left")

    def __init__(
        self,
        vertex_x: float,
        vertex_y: float,
        focal_length: float,
        direction: str = "up",
        pen_color: tuple[int, int, int] = (0, 0, 0),
        pen_width: float = 2.0,
        brush_color: tuple[int, int, int] | None = None,
        selected: bool = False,
    ):
        super().__init__(pen_color, pen_width, brush_color, selected)
        if direction not in self.VALID_DIRECTIONS:
            raise ValueError(f"direction must be one of {self.VALID_DIRECTIONS}")
        self._vertex_x = vertex_x
        self._vertex_y = vertex_y
        self._focal_length = focal_length
        self._direction = direction

    def set_end_point(self, x: float, y: float) -> None:
        pass

    def set_size(self, width: float, height: float) -> None:
        self._focal_length = max(width, height) / 4

    def add_vertex(self, x: float, y: float) -> None:
        pass

    def _get_shape_type(self) -> ShapeType:
        return ShapeType.PARABOLA

    # ------------------------------------------------------------------
    # Свойства
    # ------------------------------------------------------------------

    @property
    def vertex_x(self) -> float:
        return self._vertex_x

    @property
    def vertex_y(self) -> float:
        return self._vertex_y

    @property
    def focal_length(self) -> float:
        return self._focal_length

    @focal_length.setter
    def focal_length(self, value: float) -> None:
        if value > 0.1:
            self._focal_length = value

    @property
    def direction(self) -> str:
        return self._direction

    @property
    def a(self) -> float:
        """Коэффициент a = 1/(4p)."""
        return 1.0 / (4.0 * self._focal_length)

    # ------------------------------------------------------------------
    # Вычисление точек
    # ------------------------------------------------------------------

    def _compute_points(self, num_samples: int = 200) -> list[tuple[float, float]]:
        """Вычисляет точки параболы для отрисовки."""
        h, k = self._vertex_x, self._vertex_y
        a = self.a
        p = self._focal_length

        points: list[tuple[float, float]] = []

        if self._direction in ("up", "down"):
            # y = ±a*(x-h)^2 + k
            sign = 1 if self._direction == "up" else -1
            # Определяем диапазон x
            x_range = max(p * 6, 200)
            dx = 2 * x_range / num_samples
            x = h - x_range
            while x <= h + x_range:
                y = k + sign * a * (x - h) ** 2
                points.append((x, y))
                x += dx

        else:
            # x = ±a*(y-k)^2 + h
            sign = 1 if self._direction == "right" else -1
            y_range = max(p * 6, 200)
            dy = 2 * y_range / num_samples
            y = k - y_range
            while y <= k + y_range:
                x = h + sign * a * (y - k) ** 2
                points.append((x, y))
                y += dy

        return points

    def _bounding_rect_from_points(self, points: list[tuple[float, float]], pad: float) -> QRectF:
        if not points:
            return QRectF()
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        return self._safe_rect(
            min(xs) - pad,
            min(ys) - pad,
            max(xs) - min(xs) + 2 * pad,
            max(ys) - min(ys) + 2 * pad,
        )

    # ------------------------------------------------------------------
    # Abstract methods
    # ------------------------------------------------------------------

    def draw(self, painter: QPainter) -> None:
        painter.save()
        try:
            pen = QPen(self.pen_color, self.pen_width)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)

            points = self._compute_points()
            if len(points) < 2:
                return

            # Рисуем кривую через линии
            pen.setColor(self.pen_color)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)

            qt_points = [QPointF(x, y) for x, y in points]
            painter.drawPolyline(qt_points)

            # Рисуем вершину
            painter.setBrush(QBrush(self.pen_color))
            painter.drawEllipse(QPointF(self._vertex_x, self._vertex_y), 3, 3)

            if self._selected:
                pen.setColor(QColor(0, 120, 255))
                pen.setWidth(1)
                painter.setPen(pen)
                painter.setBrush(Qt.BrushStyle.NoBrush)
                for hx, hy in self._handle_positions():
                    painter.drawRect(int(hx) - 4, int(hy) - 4, 8, 8)
        finally:
            painter.restore()

    def contains_point(self, point: QPointF) -> bool:
        # Упрощённо — проверяем по bounding rect
        return self.bounding_rect().contains(point)

    def move(self, dx: float, dy: float) -> None:
        self._vertex_x += dx
        self._vertex_y += dy

    def rotate(self, angle: float, center: QPointF | None = None) -> None:
        self._rotation = (self._rotation + angle) % 360.0

    def scale(self, factor: float, center: QPointF | None = None) -> None:
        if center is None:
            center = QPointF(self._vertex_x, self._vertex_y)
        self._vertex_x = center.x() + (self._vertex_x - center.x()) * factor
        self._vertex_y = center.y() + (self._vertex_y - center.y()) * factor
        self._focal_length *= factor
        if self._focal_length < 0.1:
            self._focal_length = 0.1

    def bounding_rect(self) -> QRectF:
        pad = max(self.pen_width / 2 + 5, 6)
        points = self._compute_points()
        if not points:
            r = max(self._focal_length * 4, 50)
            return self._safe_rect(
                self._vertex_x - r - pad,
                self._vertex_y - r - pad,
                2 * r + 2 * pad,
                2 * r + 2 * pad,
            )
        return self._bounding_rect_from_points(points, pad)

    # ------------------------------------------------------------------
    # Маркеры (handles)
    # ------------------------------------------------------------------

    def _handle_positions(self) -> list[tuple[float, float]]:
        return [
            (self._vertex_x, self._vertex_y),  # вершина
        ]

    def get_handles(self) -> list[QPointF]:
        return [QPointF(hx, hy) for hx, hy in self._handle_positions()]

    def get_handle_type(self, point: QPointF, tolerance: float = 5.0) -> HandleType:
        for i, (hx, hy) in enumerate(self._handle_positions()):
            dx = point.x() - hx
            dy = point.y() - hy
            if math.sqrt(dx * dx + dy * dy) <= tolerance:
                return HandleType(i + 2)
        return HandleType.NONE

    def apply_handle_transform(
        self,
        handle: HandleType,
        point: QPointF,
        mouse_pos: QPointF,
        shift_pressed: bool = False,
    ) -> None:
        if handle == HandleType.TOP_LEFT:
            # Вершина — перемещение
            dx = mouse_pos.x() - point.x()
            dy = mouse_pos.y() - point.y()
            self._vertex_x += dx
            self._vertex_y += dy

    # ------------------------------------------------------------------
    # Позиция для undo
    # ------------------------------------------------------------------

    def get_position_data(self) -> dict:
        return {
            "vertex_x": self._vertex_x,
            "vertex_y": self._vertex_y,
            "focal_length": self._focal_length,
            "direction": self._direction,
        }

    def restore_position_data(self, data: dict) -> None:
        self._vertex_x = data["vertex_x"]
        self._vertex_y = data["vertex_y"]
        self._focal_length = data["focal_length"]
        self._direction = data["direction"]

    # ------------------------------------------------------------------
    # Сериализация
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update(
            {
                "vertex_x": self._vertex_x,
                "vertex_y": self._vertex_y,
                "focal_length": self._focal_length,
                "direction": self._direction,
            }
        )
        return d

    @classmethod
    def from_dict(cls, data: dict) -> ParabolaShape:
        obj = cls(
            vertex_x=data["vertex_x"],
            vertex_y=data["vertex_y"],
            focal_length=data["focal_length"],
            direction=data.get("direction", "up"),
            pen_color=data["pen_color"],
            brush_color=data.get("brush_color"),
            pen_width=data.get("pen_width", 2.0),
        )
        obj._selected = data.get("selected", False)
        obj._rotation = data.get("rotation", 0.0)
        return obj
