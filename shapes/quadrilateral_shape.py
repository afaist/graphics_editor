"""Фигура: Неправильный четырёхугольник."""

from __future__ import annotations

import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPen, QPolygonF

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
    draw_diagonals as _draw_diagonals,
)
from tools.quadrilateral_tools import (
    draw_heights as _draw_heights,
)
from tools.quadrilateral_tools import (
    is_cyclic_quadrilateral as _is_cyclic,
)

from .base_shape import BaseShape, HandleType, ShapeType


class QuadrilateralShape(BaseShape):
    """Произвольный четырёхугольник с 4 независимыми вершинами."""

    def __init__(
        self,
        vertices: list[tuple[float, float]] | None = None,
        pen_color: tuple[int, int, int] = (0, 0, 0),
        pen_width: float = 2.0,
        brush_color: tuple[int, int, int] | None = None,
        selected: bool = False,
        show_heights: bool = False,
        show_diagonals: bool = False,
        show_bisectors: bool = False,
        show_angles: bool = False,
        show_circumcircle: bool = False,
        height_from_vertex: int = -1,
    ):
        super().__init__(pen_color, pen_width, brush_color, selected)
        self._vertices: list[QPointF] = [QPointF(v[0], v[1]) for v in vertices] if vertices else []
        self._labels = ["A", "B", "C", "D"]
        self._show_heights = show_heights
        self._show_diagonals = show_diagonals
        self._show_bisectors = show_bisectors
        self._show_angles = show_angles
        self._show_circumcircle = show_circumcircle
        self._height_from_vertex = height_from_vertex

    def _get_shape_type(self) -> ShapeType:
        return ShapeType.QUADRILATERAL_IRREGULAR

    # ------------------------------------------------------------------
    # Свойства
    # ------------------------------------------------------------------

    @property
    def vertices(self) -> list[QPointF]:
        return list(self._vertices)

    @vertices.setter
    def vertices(self, verts: list[QPointF]) -> None:
        self._vertices = list(verts)

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
    def show_bisectors(self) -> bool:
        return self._show_bisectors

    @show_bisectors.setter
    def show_bisectors(self, value: bool) -> None:
        self._show_bisectors = value

    @property
    def show_angles(self) -> bool:
        return self._show_angles

    @show_angles.setter
    def show_angles(self, value: bool) -> None:
        self._show_angles = value

    @property
    def show_circumcircle(self) -> bool:
        return self._show_circumcircle

    @show_circumcircle.setter
    def show_circumcircle(self, value: bool) -> None:
        self._show_circumcircle = value

    @property
    def height_from_vertex(self) -> int:
        return self._height_from_vertex

    @height_from_vertex.setter
    def height_from_vertex(self, value: int) -> None:
        self._height_from_vertex = value

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

            if abs(self._rotation) > 0.01 and len(self._vertices) > 0:
                cx = sum(v.x() for v in self._vertices) / len(self._vertices)
                cy = sum(v.y() for v in self._vertices) / len(self._vertices)
                painter.translate(cx, cy)
                painter.rotate(self._rotation)
                painter.translate(-cx, -cy)

            if len(self._vertices) >= 4:
                polygon = QPolygonF(self._vertices)
                painter.drawPolygon(polygon)

            pen.setColor(QColor(80, 80, 80))
            pen.setWidth(1)
            painter.setPen(pen)
            painter.setBrush(QBrush(QColor(255, 255, 255)))
            for v in self._vertices:
                painter.drawEllipse(v, 3, 3)

            self._draw_vertex_labels(painter)

            if self._show_heights:
                _draw_heights(
                    painter,
                    self,
                    self._height_from_vertex if self._height_from_vertex >= 0 else None,
                )
            if self._show_diagonals:
                _draw_diagonals(painter, self)
            if self._show_bisectors:
                _draw_bisectors(painter, self, None)
            if self._show_angles:
                _draw_angles(painter, self)
            if self._show_circumcircle:
                _draw_circumcircle(painter, self)

            if self._selected:
                pen.setColor(QColor(0, 120, 255))
                pen.setWidth(1)
                painter.setPen(pen)
                painter.setBrush(Qt.BrushStyle.NoBrush)
                for hx, hy in self._handle_positions():
                    painter.drawRect(int(hx) - 4, int(hy) - 4, 8, 8)
        finally:
            painter.restore()

    def _draw_vertex_labels(self, painter: QPainter) -> None:
        if not self._vertices:
            return
        cx = sum(v.x() for v in self._vertices) / 4
        cy = sum(v.y() for v in self._vertices) / 4
        font = QFont()
        font.setFamily("Arial")
        font.setPointSizeF(9)
        painter.setFont(font)
        painter.setPen(QColor(50, 50, 50))
        offset = 16
        for i, v in enumerate(self._vertices):
            dx = v.x() - cx
            dy = v.y() - cy
            dist = math.sqrt(dx * dx + dy * dy)
            if dist < 0.01:
                continue
            dx /= dist
            dy /= dist
            label_x = v.x() + dx * offset
            label_y = v.y() + dy * offset
            text_rect = QRectF(label_x - 10, label_y - 10, 20, 20)
            painter.drawText(
                text_rect,
                Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter,
                self._labels[i],
            )

    def contains_point(self, point: QPointF) -> bool:
        return self.bounding_rect().contains(point) and self._point_in_polygon(point)

    def _point_in_polygon(self, point: QPointF) -> bool:
        n = len(self._vertices)
        inside = False
        x, y = point.x(), point.y()
        p1x, p1y = self._vertices[0].x(), self._vertices[0].y()
        for i in range(1, n + 1):
            p2x, p2y = self._vertices[i % n].x(), self._vertices[i % n].y()
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        return inside

    def move(self, dx: float, dy: float) -> None:
        for v in self._vertices:
            v.setX(v.x() + dx)
            v.setY(v.y() + dy)

    def add_vertex(self, x: float, y: float) -> None:
        """Добавить вершину (используется при интерактивном рисовании)."""
        self._vertices.append(QPointF(x, y))

    def rotate(self, angle: float, center: QPointF | None = None) -> None:
        if len(self._vertices) == 0:
            return
        if center is None:
            cx = sum(v.x() for v in self._vertices) / len(self._vertices)
            cy = sum(v.y() for v in self._vertices) / len(self._vertices)
            center = QPointF(cx, cy)
        rad = math.radians(angle)
        cos_a, sin_a = math.cos(rad), math.sin(rad)
        for v in self._vertices:
            dx = v.x() - center.x()
            dy = v.y() - center.y()
            v.setX(center.x() + dx * cos_a - dy * sin_a)
            v.setY(center.y() + dx * sin_a + dy * cos_a)

    def scale(self, factor: float, center: QPointF | None = None) -> None:
        if factor <= 0:
            raise ValueError("Scale factor must be positive")
        if len(self._vertices) == 0:
            return
        if center is None:
            cx = sum(v.x() for v in self._vertices) / len(self._vertices)
            cy = sum(v.y() for v in self._vertices) / len(self._vertices)
            center = QPointF(cx, cy)
        for v in self._vertices:
            v.setX(center.x() + (v.x() - center.x()) * factor)
            v.setY(center.y() + (v.y() - center.y()) * factor)

    def bounding_rect(self) -> QRectF:
        if not self._vertices:
            return QRectF(0, 0, 0, 0)
        x_min = min(v.x() for v in self._vertices)
        y_min = min(v.y() for v in self._vertices)
        x_max = max(v.x() for v in self._vertices)
        y_max = max(v.y() for v in self._vertices)
        pad = self._compute_bounding_padding(self.pen_width) + 8
        return self._safe_rect(
            x_min - pad,
            y_min - pad,
            x_max - x_min + pad * 2,
            y_max - y_min + pad * 2,
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
            for v in self._vertices:
                v.setX(v.x() + dx)
                v.setY(v.y() + dy)
            return
        handle_idx = handle.value - 2
        if 0 <= handle_idx < len(self._vertices):
            self._vertices[handle_idx].setX(mouse_pos.x())
            self._vertices[handle_idx].setY(mouse_pos.y())

    def area(self) -> float:
        n = len(self._vertices)
        if n < 3:
            return 0.0
        s = 0.0
        for i in range(n):
            j = (i + 1) % n
            s += self._vertices[i].x() * self._vertices[j].y()
            s -= self._vertices[j].x() * self._vertices[i].y()
        return abs(s) / 2.0

    def perimeter(self) -> float:
        n = len(self._vertices)
        if n < 2:
            return 0.0
        p = 0.0
        for i in range(n):
            j = (i + 1) % n
            v1 = self._vertices[i]
            v2 = self._vertices[j]
            dx = v2.x() - v1.x()
            dy = v2.y() - v1.y()
            p += math.sqrt(dx * dx + dy * dy)
        return p

    def is_cyclic(self) -> bool:
        return _is_cyclic(self)

    def draw_diagonals(self, painter: QPainter) -> None:
        _draw_diagonals(painter, self)

    def draw_heights(self, painter: QPainter, vertex_index: int | None = None) -> None:
        _draw_heights(painter, self, vertex_index)

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
            "vertices": [(v.x(), v.y()) for v in self._vertices],
        }

    def restore_position_data(self, data: dict) -> None:
        vertices_data = data["vertices"]
        for i, (vx, vy) in enumerate(vertices_data):
            if i < len(self._vertices):
                self._vertices[i].setX(vx)
                self._vertices[i].setY(vy)

    # ------------------------------------------------------------------
    # Сериализация
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        d = super().to_dict()
        d["vertices"] = [{"x": v.x(), "y": v.y()} for v in self._vertices]
        d["show_heights"] = self._show_heights
        d["show_diagonals"] = self._show_diagonals
        d["show_bisectors"] = self._show_bisectors
        d["show_angles"] = self._show_angles
        d["show_circumcircle"] = self._show_circumcircle
        d["height_from_vertex"] = self._height_from_vertex
        return d

    @classmethod
    def from_dict(cls, data: dict) -> QuadrilateralShape:
        verts = [(v["x"], v["y"]) for v in data.get("vertices", [])]
        obj = cls(
            vertices=verts,
            pen_color=data["pen_color"],
            brush_color=data.get("brush_color"),
            pen_width=data.get("pen_width", 2.0),
            selected=data.get("selected", False),
            show_heights=data.get("show_heights", False),
            show_diagonals=data.get("show_diagonals", False),
            show_bisectors=data.get("show_bisectors", False),
            show_angles=data.get("show_angles", False),
            show_circumcircle=data.get("show_circumcircle", False),
            height_from_vertex=data.get("height_from_vertex", -1),
        )
        obj._rotation = data.get("rotation", 0.0)
        obj.id = data["id"]
        obj.group_id = data.get("group_id")
        return obj
