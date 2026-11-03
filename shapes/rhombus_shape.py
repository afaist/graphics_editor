"""Фигура: Ромб."""

from __future__ import annotations

import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QPainter, QPen, QPolygonF

from tools.quadrilateral_tools import (
    draw_angles as _draw_angles,
)
from tools.quadrilateral_tools import (
    draw_bisectors as _draw_bisectors,
)
from tools.quadrilateral_tools import (
    draw_circumcircle as _draw_circumcircle,
)
from tools.quadrilateral_tools import (
    draw_heights as _draw_heights_tool,
)

from .base_shape import BaseShape, HandleType, ShapeType


class RhombusShape(BaseShape):
    """Ромб, заданный центром и полу-диагоналями dx и dy."""

    def __init__(
        self,
        vertices: list[tuple[float, float]] | None = None,
        center: tuple[float, float] | None = None,
        dx: float = 100.0,
        dy: float = 75.0,
        pen_color: tuple[int, int, int] = (0, 0, 0),
        pen_width: float = 2.0,
        brush_color: tuple[int, int, int] | None = None,
        selected: bool = False,
        show_heights: bool = False,
        show_diagonals: bool = False,
        height_from_vertex: int = -1,
    ):
        if center is None:
            center = (0.0, 0.0)
        self._center_x = center[0]
        self._center_y = center[1]
        self._dx = dx
        self._dy = dy
        self._labels = ["A", "B", "C", "D"]

        # Дополнительные линии
        self._show_heights = show_heights
        self._show_diagonals = show_diagonals
        self._height_from_vertex = height_from_vertex

        super().__init__(pen_color, pen_width, brush_color, selected)
        self._vertices: list[QPointF] = []
        self._rebuild_vertices()

    def _get_shape_type(self) -> ShapeType:
        return ShapeType.RHOMBUS

    # ------------------------------------------------------------------
    # Свойства
    # ------------------------------------------------------------------

    @property
    def vertices(self) -> list[QPointF]:
        return self._vertices

    @property
    def dx(self) -> float:
        return self._dx

    @property
    def dy(self) -> float:
        return self._dy

    @property
    def center_x(self) -> float:
        return self._center_x

    @property
    def center_y(self) -> float:
        return self._center_y

    @property
    def labels(self) -> list[str]:
        return self._labels

    @property
    def show_heights(self) -> bool:
        return self._show_heights

    @show_heights.setter
    def show_heights(self, value: bool) -> None:
        self._show_heights = value

    @property
    def show_diagonals(self) -> bool:
        return self._show_diagonals

    @show_diagonals.setter
    def show_diagonals(self, value: bool) -> None:
        self._show_diagonals = value

    @property
    def height_from_vertex(self) -> int:
        return self._height_from_vertex

    @height_from_vertex.setter
    def height_from_vertex(self, value: int) -> None:
        self._height_from_vertex = value

    # ------------------------------------------------------------------
    # Построение вершин
    # ------------------------------------------------------------------

    def _rebuild_vertices(self) -> None:
        """Построить вершины ромба из центра и полу-диагоналей.

        A (V0) = leftmost, затем по часовой стрелке:
        B (V1) = top, C (V2) = right, D (V3) = bottom.
        """
        self._vertices = [
            QPointF(self._center_x - self._dx, self._center_y),  # A — левая
            QPointF(self._center_x, self._center_y - self._dy),  # B — верхняя
            QPointF(self._center_x + self._dx, self._center_y),  # C — правая
            QPointF(self._center_x, self._center_y + self._dy),  # D — нижняя
        ]

    @staticmethod
    def build(
        dx: float, dy: float, center: tuple[float, float] | None = None
    ) -> list[tuple[float, float]]:
        """Построить вершины ромба. Порядок: A=left, B=top, C=right, D=bottom."""
        if center is None:
            center = (0.0, 0.0)
        cx, cy = center
        return [
            (cx - dx, cy),  # A — левая
            (cx, cy - dy),  # B — верхняя
            (cx + dx, cy),  # C — правая
            (cx, cy + dy),  # D — нижняя
        ]

    @staticmethod
    def center_vertices(vertices: list[tuple[float, float]]) -> list[tuple[float, float]]:
        """Центрировать фигуру относительно (0, 0)."""
        cx = sum(v[0] for v in vertices) / len(vertices)
        cy = sum(v[1] for v in vertices) / len(vertices)
        return [(v[0] - cx, v[1] - cy) for v in vertices]

    @staticmethod
    def order_vertices_clockwise(vertices: list[tuple[float, float]]) -> list[tuple[float, float]]:
        """Пересортировать вершины по часовой стрелке, начиная с левой."""
        if len(vertices) < 3:
            return vertices

        cx = sum(v[0] for v in vertices) / len(vertices)
        cy = sum(v[1] for v in vertices) / len(vertices)

        # В Qt-координатах (Y вниз) atan2 = по часовой стрелке
        def angle_key(v):
            return math.atan2(v[1] - cy, v[0] - cx)

        sorted_vertices = sorted(vertices, key=angle_key, reverse=True)
        return sorted_vertices

    # ------------------------------------------------------------------
    # Abstract methods
    # ------------------------------------------------------------------

    def draw(self, painter: QPainter) -> None:
        painter.save()
        try:
            pen = QPen(self.pen_color, self.pen_width)
            painter.setPen(pen)
            if self.brush_color:
                painter.setBrush(QBrush(self.brush_color))
            else:
                painter.setBrush(Qt.BrushStyle.NoBrush)

            if abs(self._rotation) > 0.01:
                painter.translate(self._center_x, self._center_y)
                painter.rotate(self._rotation)
                painter.translate(-self._center_x, -self._center_y)

            if len(self._vertices) >= 4:
                polygon = QPolygonF(self._vertices)
                painter.drawPolygon(polygon)

            self._draw_common(painter, (self._center_x, self._center_y))

            # Дополнительные линии
            if self._show_heights:
                self._draw_heights(painter, self._height_from_vertex)
            if self._show_diagonals:
                self._draw_diagonals(painter)
        finally:
            painter.restore()

    def contains_point(self, point: QPointF) -> bool:
        return self.bounding_rect().contains(point) and self._point_in_polygon(point)

    def move(self, dx: float, dy: float) -> None:
        self._center_x += dx
        self._center_y += dy
        self._rebuild_vertices()

    def rotate(self, angle: float, center: QPointF | None = None) -> None:
        if center is None:
            center = QPointF(self._center_x, self._center_y)
        rad = math.radians(angle)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        for v in self._vertices:
            dx = v.x() - center.x()
            dy = v.y() - center.y()
            v.setX(center.x() + dx * cos_a - dy * sin_a)
            v.setY(center.y() + dx * sin_a + dy * cos_a)

    def scale(self, factor: float, center: QPointF | None = None) -> None:
        if center is None:
            center = QPointF(self._center_x, self._center_y)
        for v in self._vertices:
            v.setX(center.x() + (v.x() - center.x()) * factor)
            v.setY(center.y() + (v.y() - center.y()) * factor)

    def bounding_rect(self) -> QRectF:
        if not self._vertices:
            return QRectF()

        xs = [v.x() for v in self._vertices]
        ys = [v.y() for v in self._vertices]

        pad = max(self.pen_width / 2 + 8, 10)
        x_min = min(xs) - pad
        y_min = min(ys) - pad
        x_max = max(xs) + pad
        y_max = max(ys) + pad

        return self._safe_rect(x_min, y_min, x_max - x_min, y_max - y_min)

    def get_handles(self) -> list[QPointF]:
        return list(self._vertices)

    def get_handle_type(self, point: QPointF, tolerance: float = 5.0) -> HandleType:
        for i, v in enumerate(self._vertices):
            dx = point.x() - v.x()
            dy = point.y() - v.y()
            distance = math.sqrt(dx * dx + dy * dy)
            if distance <= tolerance:
                handle_map = [
                    HandleType.TOP_LEFT,
                    HandleType.LEFT_CENTER,
                    HandleType.BOTTOM_RIGHT,
                    HandleType.RIGHT_CENTER,
                ]
                return handle_map[i]
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
            v = self._vertices[handle_idx]
            self._center_x = sum(ver.x() for ver in self._vertices) / len(self._vertices)
            self._center_y = sum(ver.y() for ver in self._vertices) / len(self._vertices)

            dx = v.x() - self._center_x
            dy = v.y() - self._center_y
            self._dx = abs(dx)
            self._dy = abs(dy)

            self._rebuild_vertices()

    def _handle_positions(self) -> list[tuple[float, float]]:
        return [(v.x(), v.y()) for v in self._vertices]

    def area(self) -> float:
        return 2 * self._dx * self._dy

    def side_length(self) -> float:
        return math.sqrt(self._dx**2 + self._dy**2)

    def perimeter(self) -> float:
        return 4 * self.side_length()

    def is_cyclic(self) -> bool:
        return False

    def _draw_heights(self, painter: QPainter, vertex_index: int | None = None) -> None:
        """Рисует высоты ромба."""
        if len(self._vertices) < 4:
            return
        _draw_heights_tool(painter, self, vertex_index)

    def draw_diagonals(self, painter: QPainter) -> None:
        self._draw_diagonals(painter)

    def draw_heights(self, painter: QPainter, vertex_index: int | None = None) -> None:
        self._draw_heights(painter, vertex_index)

    def draw_bisectors(self, painter: QPainter, vertex_indices: list[int] | None = None) -> None:
        _draw_bisectors(painter, self, vertex_indices)

    def draw_angles(self, painter: QPainter) -> None:
        _draw_angles(painter, self)

    def draw_circumcircle(self, painter: QPainter) -> None:
        _draw_circumcircle(painter, self)

    # ------------------------------------------------------------------
    # Позиция для undo
    # ------------------------------------------------------------------

    def get_position_data(self) -> dict:
        return {
            "center": (self._center_x, self._center_y),
            "dx": self._dx,
            "dy": self._dy,
        }

    def restore_position_data(self, data: dict) -> None:
        self._center_x, self._center_y = data["center"]
        self._dx = data["dx"]
        self._dy = data["dy"]
        self._rebuild_vertices()

    # ------------------------------------------------------------------
    # Сериализация
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        d = super().to_dict()
        d["center"] = (self._center_x, self._center_y)
        d["dx"] = self._dx
        d["dy"] = self._dy
        d["show_heights"] = self._show_heights
        d["show_diagonals"] = self._show_diagonals
        d["height_from_vertex"] = self._height_from_vertex
        return d

    @classmethod
    def from_dict(cls, data: dict) -> RhombusShape:
        obj = cls(
            center=data["center"],
            dx=data["dx"],
            dy=data["dy"],
            pen_color=data["pen_color"],
            brush_color=data.get("brush_color"),
            pen_width=data.get("pen_width", 2.0),
            selected=data.get("selected", False),
            show_heights=data.get("show_heights", False),
            show_diagonals=data.get("show_diagonals", False),
            height_from_vertex=data.get("height_from_vertex", -1),
        )
        obj._rotation = data.get("rotation", 0.0)
        obj.id = data["id"]
        obj.group_id = data.get("group_id")
        return obj
