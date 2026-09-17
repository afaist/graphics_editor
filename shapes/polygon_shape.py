"""Фигура: Многоугольник (замкнутый)."""

from __future__ import annotations

import math
from typing import Any

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QPainter, QPen, QPolygonF

from .base_shape import BaseShape, HandleType, ShapeType


class PolygonShape(BaseShape):
    """Многоугольник — набор вершин, автоматически замыкается."""

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

    def set_end_point(self, x: float, y: float) -> None:
        pass  # Полигон не использует set_end_point

    def set_size(self, width: float, height: float) -> None:
        pass  # Полигон не использует set_size

    def _get_shape_type(self) -> ShapeType:
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
        """Добавить вершину в конец списка."""
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

    def draw(self, painter: QPainter) -> None:
        """Отрисовать многоугольник на QPainter."""
        painter.save()
        try:
            # Настройка пера и кисти
            pen = QPen(self.pen_color, self.pen_width)
            painter.setPen(pen)

            if self.brush_color is not None:
                painter.setBrush(QBrush(self.brush_color))
            else:
                painter.setBrush(Qt.BrushStyle.NoBrush)

            # Отрисовка многоугольника
            if len(self._vertices) >= 2:
                poly = QPolygonF(self._vertices)
                painter.drawPolygon(poly)

                # Если многоугольник выделен, рисуем маркеры вершин
                if self._selected:
                    selection_pen = QPen(QColor(0, 120, 255), 1)
                    painter.setPen(selection_pen)
                    painter.setBrush(Qt.BrushStyle.NoBrush)

                    for v in self._vertices:
                        painter.drawRect(
                            int(v.x() - 4),  # Приводим к int
                            int(v.y() - 4),  # Приводим к int
                            8,
                            8,
                        )
        finally:
            painter.restore()

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

        # Определяем центр вращения
        if center is None:
            cx = sum(v.x() for v in self._vertices) / len(self._vertices)
            cy = sum(v.y() for v in self._vertices) / len(self._vertices)
            center = QPointF(cx, cy)

        rad = math.radians(angle)
        cos_a, sin_a = math.cos(rad), math.sin(rad)

        for v in self._vertices:
            dx, dy = v.x() - center.x(), v.y() - center.y()
            v.setX(center.x() + dx * cos_a - dy * sin_a)
            v.setY(center.y() + dx * sin_a + dy * cos_a)

    def scale(self, factor: float, center: QPointF | None = None) -> None:
        """Масштабировать многоугольник."""
        if factor <= 0:
            raise ValueError("Scale factor must be positive")
        if len(self._vertices) == 0:
            return

        # Определяем центр масштабирования
        if center is None:
            cx = sum(v.x() for v in self._vertices) / len(self._vertices)
            cy = sum(v.y() for v in self._vertices) / len(self._vertices)
            center = QPointF(cx, cy)

        for v in self._vertices:
            v.setX(center.x() + (v.x() - center.x()) * factor)
            v.setY(center.y() + (v.y() - center.y()) * factor)

    def bounding_rect(self) -> QRectF:
        """Вернуть bounding box фигуры."""
        if not self._vertices:
            return QRectF(0, 0, 0, 0)

        x_min = min(v.x() for v in self._vertices)
        y_min = min(v.y() for v in self._vertices)
        x_max = max(v.x() for v in self._vertices)
        y_max = max(v.y() for v in self._vertices)

        pad = max(self.pen_width / 2 + 5, 6)
        return self._safe_rect(
            x_min - pad,
            y_min - pad,
            x_max - x_min + pad * 2,
            y_max - y_min + pad * 2,
        )

    def get_handles(self) -> list[QPointF]:
        """Вернуть список маркеров преобразования (вершин)."""
        return list(self._vertices)

    def get_handle_type(self, point: QPointF, tolerance: float = 5.0) -> HandleType:
        """Определить тип маркера под указанной точкой."""
        for i, v in enumerate(self._vertices):
            # Вычисляем расстояние между точками вручную
            dx = point.x() - v.x()
            dy = point.y() - v.y()
            distance = math.sqrt(dx * dx + dy * dy)
            if distance <= tolerance:
                return HandleType(i + 2)  # 2, 3, 4... соответствуют вершинам
        return HandleType.NONE

    def apply_handle_transform(
        self, handle: HandleType, point: QPointF, mouse_pos: QPointF
    ) -> None:
        """Применить преобразование через маркер (перемещение вершины)."""
        # Вычисляем индекс вершины: handle.value - 2, т. к. HandleType начинается с 2 для вершин
        idx = handle.value - 2
        if 0 <= idx < len(self._vertices):
            self._vertices[idx].setX(mouse_pos.x())
            self._vertices[idx].setY(mouse_pos.y())

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
