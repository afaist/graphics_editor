"""Фигура: Правильный многоугольник (regular polygon)."""

from __future__ import annotations

import math
from typing import Any

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QPainter, QPen, QPolygonF

from .base_shape import BaseShape, HandleType, ShapeType


class RegularPolygonShape(BaseShape):
    """Правильный n-угольник — все стороны и углы равны."""

    def __init__(
        self,
        num_sides: int = 6,
        radius: float = 50.0,
        center: tuple[float, float] | None = None,
        pen_color: tuple[int, int, int] = (0, 0, 0),
        pen_width: float = 2.0,
        brush_color: tuple[int, int, int] | None = None,
        selected: bool = False,
    ):
        # Устанавливаем num_sides ДО super(), так как BaseShape.__init__
        # вызывает self._get_shape_type(), который его читает
        self._num_sides = max(3, num_sides)
        self._radius = max(1.0, radius)
        self._center_x = center[0] if center else 0.0
        self._center_y = center[1] if center else 0.0
        self._vertices: list[QPointF] = []
        self._labels: list[str] = []
        super().__init__(pen_color, pen_width, brush_color, selected)
        self._rebuild_vertices()

    def _rebuild_vertices(self) -> None:
        """Пересчитать вершины правильного n-угольника.

        Начинаем с крайней левой вершины и идём по часовой стрелке.
        Для квадрата — сторона AD горизонтальна и внизу.
        """
        self._vertices = []
        self._labels = []
        # Левая точка круга = угол π. По часовой стрелке в экранных координатах
        # (Y вниз) — угол увеличивается.
        # Для квадрата сдвигаем на -π/4, чтобы сторона AD была горизонтальна внизу
        if self._num_sides == 4:
            start_angle = math.pi - math.pi / 4  # 3π/4 — левый нижний угол
        else:
            start_angle = math.pi

        for i in range(self._num_sides):
            angle = start_angle + 2 * math.pi * i / self._num_sides  # по часовой стрелке
            x = self._center_x + self._radius * math.cos(angle)
            y = self._center_y + self._radius * math.sin(angle)
            self._vertices.append(QPointF(x, y))
        # Буквенные обозначения вершин
        self._labels = [chr(ord("A") + i) for i in range(self._num_sides)]

    def _get_shape_type(self) -> ShapeType:
        if self._num_sides == 3:
            return ShapeType.REGULAR_TRIANGLE
        elif self._num_sides == 4:
            return ShapeType.SQUARE
        elif self._num_sides == 5:
            return ShapeType.REGULAR_PENTAGON
        elif self._num_sides == 6:
            return ShapeType.REGULAR_HEXAGON
        return ShapeType.POLYGON

    # ------------------------------------------------------------------
    # Свойства
    # ------------------------------------------------------------------

    @property
    def num_sides(self) -> int:
        return self._num_sides

    @num_sides.setter
    def num_sides(self, value: int) -> None:
        self._num_sides = max(3, value)
        self._rebuild_vertices()

    @property
    def radius(self) -> float:
        return self._radius

    @radius.setter
    def radius(self, value: float) -> None:
        self._radius = max(1.0, value)
        self._rebuild_vertices()

    @property
    def center_x(self) -> float:
        return self._center_x

    @property
    def center_y(self) -> float:
        return self._center_y

    @property
    def vertices(self) -> list[QPointF]:
        return list(self._vertices)

    @property
    def labels(self) -> list[str]:
        return list(self._labels)

    # ------------------------------------------------------------------
    # Вычисления
    # ------------------------------------------------------------------

    def area(self) -> float:
        """Площадь правильного n-угольника."""
        n = self._num_sides
        r = self._radius
        return 0.5 * n * r * r * math.sin(2 * math.pi / n)

    def side_length(self) -> float:
        """Длина стороны."""
        r = self._radius
        n = self._num_sides
        return 2 * r * math.sin(math.pi / n)

    # ------------------------------------------------------------------
    # Abstract methods
    # ------------------------------------------------------------------

    def draw(self, painter: QPainter) -> None:
        """Отрисовать правильный многоугольник."""
        painter.save()
        try:
            pen = QPen(self.pen_color, self.pen_width)
            painter.setPen(pen)

            if self.brush_color is not None:
                painter.setBrush(QBrush(self.brush_color))
            else:
                painter.setBrush(Qt.BrushStyle.NoBrush)

            # Поворот вокруг центра
            if abs(self._rotation) > 0.01:
                painter.translate(self._center_x, self._center_y)
                painter.rotate(self._rotation)
                painter.translate(-self._center_x, -self._center_y)

            if len(self._vertices) >= 3:
                poly = QPolygonF(self._vertices)
                painter.drawPolygon(poly)

                # Буквенные обозначения вершин — всегда
                painter.setPen(QPen(self.pen_color, 1))
                painter.setBrush(Qt.BrushStyle.NoBrush)
                for i, v in enumerate(self._vertices):
                    label = self._labels[i]
                    # Смещаем букву наружу от центра
                    dx = v.x() - self._center_x
                    dy = v.y() - self._center_y
                    dist = math.sqrt(dx * dx + dy * dy)
                    if dist > 0:
                        offset = 12.0
                        lx = v.x() + (dx / dist) * offset
                        ly = v.y() + (dy / dist) * offset
                    else:
                        lx, ly = v.x(), v.y()
                    painter.drawText(int(lx - 5), int(ly + 5), label)

                # Маркеры вершин — только при выделении
                if self._selected:
                    selection_pen = QPen(QColor(0, 120, 255), 1)
                    painter.setPen(selection_pen)
                    painter.setBrush(Qt.BrushStyle.NoBrush)
                    for v in self._vertices:
                        painter.drawRect(int(v.x() - 4), int(v.y() - 4), 8, 8)
        finally:
            painter.restore()

    def contains_point(self, point: QPointF) -> bool:
        if len(self._vertices) < 3:
            return False
        poly = QPolygonF(self._vertices)
        return poly.containsPoint(point, Qt.FillRule.OddEvenFill)

    def move(self, dx: float, dy: float) -> None:
        self._center_x += dx
        self._center_y += dy
        self._rebuild_vertices()

    def rotate(self, angle: float, center: QPointF | None = None) -> None:
        self._rotation = (self._rotation + angle) % 360
        self._rebuild_vertices()

    def scale(self, factor: float, center: QPointF | None = None) -> None:
        if factor <= 0:
            raise ValueError("Scale factor must be positive")
        self._radius *= factor
        self._radius = max(1.0, self._radius)
        self._rebuild_vertices()

    def bounding_rect(self) -> QRectF:
        pad = self._radius + max(self.pen_width / 2 + 5, 6)
        return self._safe_rect(
            self._center_x - self._radius - pad,
            self._center_y - self._radius - pad,
            self._radius * 2 + pad * 2,
            self._radius * 2 + pad * 2,
        )

    def _handle_positions(self) -> list[tuple[float, float]]:
        return [(v.x(), v.y()) for v in self._vertices]

    def get_handles(self) -> list[QPointF]:
        return list(self._vertices)

    def get_handle_type(self, point: QPointF, tolerance: float = 5.0) -> HandleType:
        for i, v in enumerate(self._vertices):
            dx = point.x() - v.x()
            dy = point.y() - v.y()
            distance = math.sqrt(dx * dx + dy * dy)
            if distance <= tolerance:
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
        handle_idx = handle.value - 2
        if 0 <= handle_idx < len(self._vertices):
            # Пересчитываем радиус и центр от перетащенной вершины
            v = self._vertices[handle_idx]
            self._center_x = sum(ver.x() for ver in self._vertices) / len(self._vertices)
            self._center_y = sum(ver.y() for ver in self._vertices) / len(self._vertices)
            dx = v.x() - self._center_x
            dy = v.y() - self._center_y
            self._radius = math.sqrt(dx * dx + dy * dy)
            self._radius = max(1.0, self._radius)
            self._rebuild_vertices()

    # ------------------------------------------------------------------
    # Позиция для undo
    # ------------------------------------------------------------------

    def get_position_data(self) -> dict[str, Any]:
        return {
            "num_sides": self._num_sides,
            "radius": self._radius,
            "center": (self._center_x, self._center_y),
        }

    def restore_position_data(self, data: dict[str, Any]) -> None:
        self._num_sides = data["num_sides"]
        self._radius = data["radius"]
        self._center_x, self._center_y = data["center"]
        self._rebuild_vertices()

    # ------------------------------------------------------------------
    # Свойства для панели
    # ------------------------------------------------------------------

    def get_properties(self) -> dict[str, Any]:
        props = super().get_properties()
        props["num_sides"] = self._num_sides
        props["radius"] = self._radius
        props["center_x"] = self._center_x
        props["center_y"] = self._center_y
        return props

    def apply_properties(self, properties: dict[str, Any]) -> None:
        super().apply_properties(properties)
        if "num_sides" in properties:
            self._num_sides = max(3, properties["num_sides"])
        if "radius" in properties:
            self._radius = max(1.0, properties["radius"])
        if "center_x" in properties:
            self._center_x = properties["center_x"]
        if "center_y" in properties:
            self._center_y = properties["center_y"]
        if any(k in properties for k in ("num_sides", "radius", "center_x", "center_y")):
            self._rebuild_vertices()

    # ------------------------------------------------------------------
    # Сериализация
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        d = super().to_dict()
        d["num_sides"] = self._num_sides
        d["radius"] = self._radius
        d["center_x"] = self._center_x
        d["center_y"] = self._center_y
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RegularPolygonShape:
        obj = cls(
            num_sides=data["num_sides"],
            radius=data["radius"],
            center=(data["center_x"], data["center_y"]),
            pen_color=data["pen_color"],
            brush_color=data.get("brush_color"),
            pen_width=data.get("pen_width", 2.0),
            selected=data.get("selected", False),
        )
        obj._rotation = data.get("rotation", 0.0)
        obj.id = data["id"]
        obj.group_id = data.get("group_id")
        return obj
