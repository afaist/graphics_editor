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
        self._hovered_vertex_index: int = -1  # Индекс вершины под курсором

    def _get_shape_type(self) -> ShapeType:
        """Возвращает тип фигуры — POLYLINE."""
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
        """Проверить, находится ли точка близко к любому отрезку ломаной."""
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

    # ------------------------------------------------------------------
    # Трансформации
    # ------------------------------------------------------------------

    def move(self, dx: float, dy: float) -> None:
        for v in self._vertices:
            v.setX(v.x() + dx)
            v.setY(v.y() + dy)

    def rotate(self, angle: float, center: QPointF | None = None) -> None:
        """Повернуть ломаную на angle градусов."""
        if not self._vertices:
            return
        if center is None:
            cx, cy = self._center_of_vertices(self._vertices)
        else:
            cx, cy = center.x(), center.y()
        self._rotate_vertices(self._vertices, cx, cy, angle)

    def scale(self, factor: float, center: QPointF | None = None) -> None:
        """Масштабировать ломаную."""
        if not self._vertices:
            return
        if center is None:
            cx, cy = self._center_of_vertices(self._vertices)
        else:
            cx, cy = center.x(), center.y()
        self._scale_vertices(self._vertices, cx, cy, factor)

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
        return list(self._vertices)

    def get_handle_type(self, point: QPointF, tolerance: float = 5.0) -> HandleType:
        """Определить тип маркера под указанной точкой (оптимизированная версия)."""
        tolerance_squared = tolerance * tolerance  # Предвычисляем квадрат допуска
        for i, v in enumerate(self._vertices):
            dx = point.x() - v.x()
            dy = point.y() - v.y()
            distance_squared = dx * dx + dy * dy
            if distance_squared <= tolerance_squared:
                # Сохраняем индекс вершины в фигуре
                self._hovered_vertex_index = i
                return HandleType.MOVE
        self._hovered_vertex_index = -1
        return HandleType.NONE

    def apply_handle_transform(
        self, handle: HandleType, point: QPointF, mouse_pos: QPointF, shift_pressed: bool = False
    ) -> None:
        if handle == HandleType.MOVE:
            # Если есть hovered vertex, двигаем только его
            if self._hovered_vertex_index >= 0:
                self._vertices[self._hovered_vertex_index].setX(mouse_pos.x())
                self._vertices[self._hovered_vertex_index].setY(mouse_pos.y())
                return
            # Иначе двигаем все вершины
            dx = mouse_pos.x() - point.x()
            dy = mouse_pos.y() - point.y()
            for v in self._vertices:
                v.setX(v.x() + dx)
                v.setY(v.y() + dy)
            return

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
        """Добавить список вершин в конец ломаной."""
        self._vertices.extend(points)

    def clear(self) -> None:
        """Удалить все вершины ломаной."""
        self._vertices = []
