from __future__ import annotations

import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPen, QPolygonF

from .base_shape import BaseShape, HandleType, ShapeType


class PolylineShape(BaseShape):
    """Ломаная линия — набор вершин, НЕ замыкается."""

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
        return ShapeType.POLYLINE

    # ------------------------------------------------------------------
    # Свойства
    # ------------------------------------------------------------------

    @property
    def vertices(self) -> list[QPointF]:
        return self._vertices

    @vertices.setter
    def vertices(self, verts: list[QPointF]):
        self._vertices = verts

    def vertex_count(self) -> int:
        return len(self._vertices)

    def set_end_point(self, x: float, y: float) -> None:
        pass  # Ломаная не использует set_end_point

    def set_size(self, width: float, height: float) -> None:
        pass  # Ломаная не использует set_size

    def add_vertex(self, x: float, y: float) -> None:
        self._vertices.append(QPointF(x, y))

    def remove_vertex(self, index: int) -> None:
        if 0 <= index < len(self._vertices) - 1:
            self._vertices.pop(index)

    # ------------------------------------------------------------------
    # Вычисления
    # ------------------------------------------------------------------

    def length(self) -> float:
        """Вычислить длину ломаной линии."""
        l = 0.0
        for i in range(len(self._vertices) - 1):
            # Получаем две последовательные вершины
            v1 = self._vertices[i]
            v2 = self._vertices[i + 1]

            # Вычисляем расстояние между вершинами вручную
            dx = v2.x() - v1.x()
            dy = v2.y() - v1.y()
            distance = math.sqrt(dx * dx + dy * dy)
            l += distance
        return l

    # ------------------------------------------------------------------
    # Отрисовка
    # ------------------------------------------------------------------

    def draw(self, painter: QPainter) -> None:
        painter.save()
        pen = QPen(self.pen_color, self.pen_width)
        painter.setPen(pen)

        # Применяем поворот вокруг центра ломаной
        if abs(self._rotation) > 0.01 and len(self._vertices) > 0:
            cx = sum(v.x() for v in self._vertices) / len(self._vertices)
            cy = sum(v.y() for v in self._vertices) / len(self._vertices)
            painter.translate(cx, cy)
            painter.rotate(self._rotation)
            painter.translate(-cx, -cy)

        if len(self._vertices) >= 2:
            poly = QPolygonF(self._vertices)
            painter.drawPolyline(poly)

        if self._selected:
            pen.setColor(QColor(0, 120, 255))
            pen.setWidth(1)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            for hx, hy in self._handle_positions():
                painter.drawRect(int(hx) - 4, int(hy) - 4, 8, 8)

        painter.restore()

    # ------------------------------------------------------------------
    # Логика работы с точками
    # ------------------------------------------------------------------

    def contains_point(self, point: QPointF, tolerance: float = 6.0) -> bool:
        for i in range(len(self._vertices) - 1):
            if (
                self._dist_to_segment(
                    point.x(),
                    point.y(),
                    self._vertices[i].x(),
                    self._vertices[i].y(),
                    self._vertices[i + 1].x(),
                    self._vertices[i + 1].y(),
                )
                <= tolerance
            ):
                return True
        return False

    @staticmethod
    def _dist_to_segment(
        px: float,
        py: float,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
    ) -> float:
        dx, dy = x2 - x1, y2 - y1
        lsq = dx * dx + dy * dy
        if lsq == 0:
            return math.hypot(px - x1, py - y1)
        t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / lsq))
        proj_x = x1 + t * dx
        proj_y = y1 + t * dy
        return math.hypot(px - proj_x, py - proj_y)

    # ------------------------------------------------------------------
    # Трансформации
    # ------------------------------------------------------------------

    def move(self, dx: float, dy: float) -> None:
        for v in self._vertices:
            v.setX(v.x() + dx)
            v.setY(v.y() + dy)

    def rotate(self, angle: float, center: QPointF | None = None) -> None:
        if center is None and self._vertices:
            cx = sum(v.x() for v in self._vertices) / len(self._vertices)
            cy = sum(v.y() for v in self._vertices) / len(self._vertices)
            center = QPointF(cx, cy)
        if center is None:
            return
        rad = math.radians(angle)
        cos_a, sin_a = math.cos(rad), math.sin(rad)
        for v in self._vertices:
            dx, dy = v.x() - center.x(), v.y() - center.y()
            v.setX(center.x() + dx * cos_a - dy * sin_a)
            v.setY(center.y() + dx * sin_a + dy * cos_a)

    def scale(self, factor: float, center: QPointF | None = None) -> None:
        if center is None and self._vertices:
            cx = sum(v.x() for v in self._vertices) / len(self._vertices)
            cy = sum(v.y() for v in self._vertices) / len(self._vertices)
            center = QPointF(cx, cy)
        if center is None:
            return
        for v in self._vertices:
            v.setX(center.x() + (v.x() - center.x()) * factor)
            v.setY(center.y() + (v.y() - center.y()) * factor)

    # ------------------------------------------------------------------
    # Геометрия
    # ------------------------------------------------------------------

    def bounding_rect(self) -> QRectF:
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

    def _handle_positions(self) -> list[tuple[float, float]]:
        return [(v.x(), v.y()) for v in self._vertices]

    def get_handles(self) -> list[QPointF]:
        return list(self._vertices)

    def get_handle_type(self, point: QPointF, tolerance: float = 5.0) -> HandleType:
        """Определить тип маркера под указанной точкой (оптимизированная версия)."""
        tolerance_squared = tolerance * tolerance  # Предвычисляем квадрат допуска
        for i, v in enumerate(self._vertices):
            dx = point.x() - v.x()
            dy = point.y() - v.y()
            distance_squared = dx * dx + dy * dy
            if distance_squared <= tolerance_squared:
                return HandleType(i + 2)
        return HandleType.NONE

    def apply_handle_transform(
        self, handle: HandleType, point: QPointF, mouse_pos: QPointF
    ) -> None:
        idx = handle.value - 2
        if 0 <= idx < len(self._vertices):
            self._vertices[idx].setX(mouse_pos.x())
            self._vertices[idx].setY(mouse_pos.y())

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
        """Сериализация объекта PolylineShape в словарь."""
        # Сначала вызываем метод to_dict родительского класса
        base_dict = super().to_dict()

        # Добавляем в словарь список вершин
        base_dict["vertices"] = [{"x": v.x(), "y": v.y()} for v in self._vertices]

        return base_dict

    @classmethod
    def from_dict(cls, data: dict) -> PolylineShape:
        verts = [(v["x"], v["y"]) for v in data.get("vertices", [])]
        obj = cls(
            vertices=verts,
            pen_color=data["pen_color"],
            brush_color=data.get("brush_color"),
            pen_width=data.get("pen_width", 2.0),
        )
        obj._selected = data.get("selected", False)
        return obj

    # ------------------------------------------------------------------
    # Дополнительные методы
    # ------------------------------------------------------------------

    def add_points_from_list(self, points: list[QPointF]) -> None:
        self._vertices.extend(points)

    def clear(self) -> None:
        self._vertices = []

    def update_bounds(self) -> None:
        self._bounds = self.bounding_rect()

    # Пример использования update_bounds
    def draw_updated(self, painter: QPainter) -> None:
        self.update_bounds()
        self.draw(painter)

    # ------------------------------------------------------------------
    # Методы для работы с событиями
    # ------------------------------------------------------------------

    def mousePressEvent(self, event: QPointF) -> None:
        # Реализация обработки нажатия мыши
        pass

    def mouseMoveEvent(self, event: QPointF) -> None:
        # Реализация обработки перемещения мыши
        pass

    def mouseReleaseEvent(self, event: QPointF) -> None:
        # Реализация обработки отпускания мыши
        pass


# ------------------------------------------------------------------
# Дополнительные свойства и методы можно добавить по необходимости
# ------------------------------------------------------------------
