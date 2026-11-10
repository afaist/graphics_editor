"""Фигура: Многоугольник (замкнутый)."""

from __future__ import annotations

import math
from typing import Any

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QPainter, QPolygonF

from .base_shape import BaseShape, HandleType, ShapeType


class PolygonShape(BaseShape):
    """Контур — набор вершин, автоматически замыкается."""

    def __init__(
        self,
        vertices: list[tuple[float, float]] | None = None,
        pen_color: tuple[int, int, int] = (0, 0, 0),
        pen_width: float = 2.0,
        brush_color: tuple[int, int, int] | None = None,
        selected: bool = False,
    ):
        super().__init__(pen_color, pen_width, brush_color, selected)
        self._vertices: list[QPointF] = [QPointF(v[0], v[1]) for v in vertices] if vertices else []

    def _get_shape_type(self) -> ShapeType:
        """Возвращает тип фигуры — POLYGON."""
        return ShapeType.POLYGON

    # ------------------------------------------------------------------
    # Свойства
    # ------------------------------------------------------------------

    @property
    def vertices(self) -> list[QPointF]:
        """Вернуть список вершин многоугольника."""
        return list(self._vertices)

    @vertices.setter
    def vertices(self, verts: list[QPointF]) -> None:
        """Установить вершины многоугольника."""
        if not isinstance(verts, list):
            raise TypeError("Vertices must be a list of QPointF")
        self._vertices = list(verts)

    def vertex_count(self) -> int:
        """Количество вершин."""
        return len(self._vertices)

    def add_vertex(self, x: float, y: float) -> None:
        """Добавить вершину."""
        self._vertices.append(QPointF(x, y))

    def remove_vertex(self, index: int) -> None:
        """Удалить вершину по индексу."""
        if 0 <= index < len(self._vertices):
            self._vertices.pop(index)

    def insert_vertex(self, index: int, x: float, y: float) -> None:
        """Вставить вершину в указанную позицию."""
        self._vertices.insert(index, QPointF(x, y))

    # ------------------------------------------------------------------
    # Вычисления
    # ------------------------------------------------------------------

    def area(self) -> float:
        """Площадь по формуле Гаусса (shoelace)."""
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
        """Периметр многоугольника."""
        n = len(self._vertices)
        if n < 2:
            return 0.0
        p = 0.0
        for i in range(n):
            j = (i + 1) % n
            # Вычисляем расстояние вручную
            v1 = self._vertices[i]
            v2 = self._vertices[j]
            dx = v2.x() - v1.x()
            dy = v2.y() - v1.y()
            p += math.sqrt(dx * dx + dy * dy)
        return p

    # ------------------------------------------------------------------
    # Abstract methods implementation
    # ------------------------------------------------------------------

    def _rotation_center(self) -> tuple[float, float] | None:
        """Возвращает центр поворота — центр масс вершин."""
        if len(self._vertices) == 0:
            return None
        return self._center_of_vertices(self._vertices)

    def _draw_shape_content(self, painter: QPainter) -> None:
        """Рисует многоугольник."""
        if len(self._vertices) >= 2:
            poly = QPolygonF(self._vertices)
            painter.drawPolygon(poly)

    def contains_point(self, point: QPointF) -> bool:
        """Проверить, принадлежит ли точка фигуре."""
        if len(self._vertices) < 3:
            return False
        poly = QPolygonF(self._vertices)
        return poly.containsPoint(point, Qt.FillRule.OddEvenFill)

    def move(self, dx: float, dy: float) -> None:
        """Переместить многоугольник на (dx, dy)."""
        for v in self._vertices:
            v.setX(v.x() + dx)
            v.setY(v.y() + dy)

    def rotate(self, angle: float, center: QPointF | None = None) -> None:
        """Повернуть многоугольник на angle градусов."""
        if len(self._vertices) == 0:
            return

        if center is None:
            cx, cy = self._center_of_vertices(self._vertices)
        else:
            cx, cy = center.x(), center.y()

        self._rotate_vertices(self._vertices, cx, cy, angle)

    def scale(self, factor: float, center: QPointF | None = None) -> None:
        """Масштабировать многоугольник."""
        if factor <= 0:
            raise ValueError("Scale factor must be positive")
        if len(self._vertices) == 0:
            return

        if center is None:
            cx, cy = self._center_of_vertices(self._vertices)
        else:
            cx, cy = center.x(), center.y()

        self._scale_vertices(self._vertices, cx, cy, factor)

    def bounding_rect(self) -> QRectF:
        """Вернуть bounding box фигуры."""
        if not self._vertices:
            return QRectF(0, 0, 0, 0)

        x_min = min(v.x() for v in self._vertices)
        y_min = min(v.y() for v in self._vertices)
        x_max = max(v.x() for v in self._vertices)
        y_max = max(v.y() for v in self._vertices)

        pad = self._compute_bounding_padding(self.pen_width)
        return self._safe_rect(
            x_min - pad,
            y_min - pad,
            x_max - x_min + pad * 2,
            y_max - y_min + pad * 2,
        )

    def _handle_positions(self) -> list[tuple[float, float]]:
        return [(v.x(), v.y()) for v in self._vertices]

    def get_handles(self) -> list[QPointF]:
        """Вернуть список маркеров преобразования (вершин)."""
        return list(self._vertices)

    def get_handle_type(self, point: QPointF, tolerance: float = 5.0) -> HandleType:
        """Определить тип маркера под указанной точкой."""
        for i, v in enumerate(self._vertices):
            dx = point.x() - v.x()
            dy = point.y() - v.y()
            distance = (dx * dx + dy * dy) ** 0.5
            if distance <= tolerance:
                handle_val = i + 2
                if handle_val <= 10:
                    return HandleType(handle_val)
        return HandleType.NONE

    def apply_handle_transform(
        self,
        handle: HandleType,
        point: QPointF,
        mouse_pos: QPointF,
        shift_pressed: bool = False,
        vertex_index: int = -1,
    ) -> None:
        """Применить преобразование через маркер (перемещение/ресайз)."""
        if handle == HandleType.MOVE:
            dx = mouse_pos.x() - point.x()
            dy = mouse_pos.y() - point.y()
            for v in self._vertices:
                v.setX(v.x() + dx)
                v.setY(v.y() + dy)
            return
        # Resize: двигаем только активную вершину
        handle_idx = handle.value - 2  # HandleType вершины = handle - 2
        if 0 <= handle_idx < len(self._vertices):
            self._vertices[handle_idx].setX(mouse_pos.x())
            self._vertices[handle_idx].setY(mouse_pos.y())

    # ------------------------------------------------------------------
    # Позиция для undo
    # ------------------------------------------------------------------

    def get_position_data(self) -> dict[str, Any]:
        return {
            "vertices": [(v.x(), v.y()) for v in self._vertices],
        }

    def restore_position_data(self, data: dict[str, Any]) -> None:
        vertices_data = data["vertices"]
        for i, (vx, vy) in enumerate(vertices_data):
            if i < len(self._vertices):
                self._vertices[i].setX(vx)
                self._vertices[i].setY(vy)

    # ------------------------------------------------------------------
    # Сериализация
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Сериализовать фигуру в словарь."""
        d = super().to_dict()
        d["vertices"] = [{"x": v.x(), "y": v.y()} for v in self._vertices]
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PolygonShape:
        """Десериализовать многоугольник из словаря."""
        verts = [(v["x"], v["y"]) for v in data.get("vertices", [])]
        obj = cls(
            vertices=verts,
            pen_color=data["pen_color"],
            brush_color=data.get("brush_color"),
            pen_width=data.get("pen_width", 2.0),
            selected=data.get("selected", False),
        )
        # Устанавливаем дополнительные свойства
        obj._rotation = data.get("rotation", 0.0)
        obj.id = data["id"]
        obj.group_id = data.get("group_id")
        return obj
