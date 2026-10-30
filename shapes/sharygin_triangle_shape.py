"""Фигура: Треугольник Шарыгина (образован основаниями биссектрис)."""

from __future__ import annotations

import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPen, QPolygonF

from .base_shape import BaseShape, HandleType, ShapeType


class SharyginTriangleShape(BaseShape):
    """Треугольник Шарыгина — треугольник, образованный основаниями биссектрис.

    Параметры:
        vertices: вершины исходного треугольника ABC в формате [(x, y), ...]
        size: масштаб для центрирования и позиционирования
        pen_color: цвет контура
        pen_width: толщина контура
        brush_color: цвет заливки
        selected: выделена ли фигура
    """

    def __init__(
        self,
        vertices: list[tuple[float, float]],
        size: float = 200.0,
        pen_color: tuple[int, int, int] = (0, 0, 0),
        pen_width: float = 2.0,
        brush_color: tuple[int, int, int] | None = None,
        selected: bool = False,
    ):
        # Вычисляем точки основания биссектрис до вызова super().__init__()
        self._original_vertices = [QPointF(v[0], v[1]) for v in vertices]
        self._sharygin_vertices = self._compute_sharygin_triangle(self._original_vertices)
        self._bisector_endpoints = self._compute_bisector_endpoints(self._original_vertices)
        self._center_point = self._compute_center(self._original_vertices)
        self._size = size

        super().__init__(pen_color, pen_width, brush_color, selected)

    @staticmethod
    def _distance(p1: QPointF, p2: QPointF) -> float:
        """Расстояние между двумя точками."""
        dx = p2.x() - p1.x()
        dy = p2.y() - p1.y()
        return math.sqrt(dx * dx + dy * dy)

    @staticmethod
    def _compute_sharygin_triangle(vertices: list[QPointF]) -> list[QPointF]:
        """Вычисляет вершины треугольника Шарыгина.

        Точка A1 (основание биссектрисы из A) делит сторону BC в отношении AB:AC.
        A1 = B + (AB / (AB + AC)) * (C - B)
        """
        A, B, C = vertices[0], vertices[1], vertices[2]

        # Основание биссектрисы из A на стороне BC
        AB = SharyginTriangleShape._distance(A, B)
        AC = SharyginTriangleShape._distance(A, C)
        t_a = AB / (AB + AC) if (AB + AC) > 0 else 0.5
        A1 = QPointF(B.x() + t_a * (C.x() - B.x()), B.y() + t_a * (C.y() - B.y()))

        # Основание биссектрисы из B на стороне AC
        BA = SharyginTriangleShape._distance(B, A)
        BC = SharyginTriangleShape._distance(B, C)
        t_b = BC / (BC + BA) if (BC + BA) > 0 else 0.5
        B1 = QPointF(C.x() + t_b * (A.x() - C.x()), C.y() + t_b * (A.y() - C.y()))

        # Основание биссектрисы из C на стороне AB
        CA = SharyginTriangleShape._distance(C, A)
        CB = SharyginTriangleShape._distance(C, B)
        t_c = CA / (CA + CB) if (CA + CB) > 0 else 0.5
        C1 = QPointF(A.x() + t_c * (B.x() - A.x()), A.y() + t_c * (B.y() - A.y()))

        return [A1, B1, C1]

    @staticmethod
    def _compute_bisector_endpoints(vertices: list[QPointF]) -> list[tuple[QPointF, QPointF]]:
        """Вычисляет концы биссектрис (от вершины до основания)."""
        A, B, C = vertices[0], vertices[1], vertices[2]
        A1, B1, C1 = vertices  # placeholder

        # Пересчитываем A1, B1, C1
        AB = SharyginTriangleShape._distance(A, B)
        AC = SharyginTriangleShape._distance(A, C)
        t_a = AB / (AB + AC) if (AB + AC) > 0 else 0.5
        A1 = QPointF(B.x() + t_a * (C.x() - B.x()), B.y() + t_a * (C.y() - B.y()))

        BA = SharyginTriangleShape._distance(B, A)
        BC = SharyginTriangleShape._distance(B, C)
        t_b = BC / (BC + BA) if (BC + BA) > 0 else 0.5
        B1 = QPointF(C.x() + t_b * (A.x() - C.x()), C.y() + t_b * (A.y() - C.y()))

        CA = SharyginTriangleShape._distance(C, A)
        CB = SharyginTriangleShape._distance(C, B)
        t_c = CA / (CA + CB) if (CA + CB) > 0 else 0.5
        C1 = QPointF(A.x() + t_c * (B.x() - A.x()), A.y() + t_c * (B.y() - A.y()))

        return [
            (A, A1),  # биссектриса из A
            (B, B1),  # биссектриса из B
            (C, C1),  # биссектриса из C
        ]

    @staticmethod
    def _compute_center(vertices: list[QPointF]) -> QPointF:
        """Вычисляет центр треугольника (среднее арифметическое вершин)."""
        cx = sum(v.x() for v in vertices) / len(vertices)
        cy = sum(v.y() for v in vertices) / len(vertices)
        return QPointF(cx, cy)

    def add_vertex(self, x: float, y: float) -> None:
        """Добавление вершины не поддерживается для треугольника Шарыгина."""
        pass

    def _get_shape_type(self) -> ShapeType:
        return ShapeType.TRIANGLE_SHARYGIN

    # ------------------------------------------------------------------
    # Свойства
    # ------------------------------------------------------------------

    @property
    def original_vertices(self) -> list[QPointF]:
        """Вершины исходного треугольника ABC."""
        return list(self._original_vertices)

    @property
    def sharygin_vertices(self) -> list[QPointF]:
        """Вершины треугольника Шарыгина A1B1C1."""
        return list(self._sharygin_vertices)

    @property
    def size(self) -> float:
        return self._size

    # ------------------------------------------------------------------
    # Отрисовка
    # ------------------------------------------------------------------

    def draw(self, painter: QPainter) -> None:
        painter.save()
        try:
            # Применяем поворот вокруг центра
            if abs(self._rotation) > 0.01 and len(self._original_vertices) > 0:
                cx = sum(v.x() for v in self._original_vertices) / len(self._original_vertices)
                cy = sum(v.y() for v in self._original_vertices) / len(self._original_vertices)
                painter.translate(cx, cy)
                painter.rotate(self._rotation)
                painter.translate(-cx, -cy)

            # 1. Рисуем исходный треугольник ABC (полупрозрачный синий)
            abc_color = QColor(100, 100, 255, 150)
            abc_pen = QPen(abc_color, self.pen_width - 0.5)
            painter.setPen(abc_pen)
            abc_brush = QBrush(QColor(100, 100, 255, 40))
            painter.setBrush(abc_brush)

            if len(self._original_vertices) >= 3:
                abc_polygon = QPolygonF(self._original_vertices[:3])
                painter.drawPolygon(abc_polygon)

            # 2. Рисуем треугольник Шарыгина A1B1C1 (яркий розовый/маджента)
            sharygin_color = QColor(255, 0, 255)
            sharygin_pen = QPen(sharygin_color, self.pen_width)
            painter.setPen(sharygin_pen)
            sharygin_brush = QBrush(QColor(255, 0, 255, 80))
            painter.setBrush(sharygin_brush)

            if len(self._sharygin_vertices) >= 3:
                sharygin_polygon = QPolygonF(self._sharygin_vertices[:3])
                painter.drawPolygon(sharygin_polygon)

            # 3. Рисуем биссектрисы (пунктирные зелёные)
            bisector_color = QColor(0, 180, 0, 180)
            bisector_pen = QPen(bisector_color, self.pen_width - 0.5)
            bisector_pen.setStyle(Qt.PenStyle.DashLine)
            painter.setPen(bisector_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)

            for start, end in self._bisector_endpoints:
                painter.drawLine(start, end)

            # 4. Рисуем точки вершин
            font = QFont()
            font.setFamily("Arial")
            font.setPointSizeF(9)
            painter.setFont(font)

            # Точки исходного треугольника A, B, C (красные)
            painter.setBrush(QBrush(QColor(255, 0, 0)))
            for v in self._original_vertices[:3]:
                painter.drawEllipse(v, 4, 4)

            # Точки треугольника Шарыгина A1, B1, C1 (синие)
            painter.setBrush(QBrush(QColor(0, 0, 255)))
            for v in self._sharygin_vertices[:3]:
                painter.drawEllipse(v, 4, 4)

            # 5. Подписи вершин
            self._draw_vertex_labels(painter)

            # 6. Маркеры выделения
            if self._selected:
                pen = QPen(QColor(0, 120, 255), 1)
                painter.setPen(pen)
                painter.setBrush(Qt.BrushStyle.NoBrush)
                for hx, hy in self._handle_positions():
                    painter.drawRect(int(hx) - 4, int(hy) - 4, 8, 8)

        finally:
            painter.restore()

    def _draw_vertex_labels(self, painter: QPainter) -> None:
        """Отрисовка подписей вершин."""
        font = QFont()
        font.setFamily("Arial")
        font.setPointSizeF(9)
        painter.setFont(font)

        # Подписи A, B, C
        labels_original = ["A", "B", "C"]
        for i, v in enumerate(self._original_vertices[:3]):
            self._draw_label(painter, v, labels_original[i], QColor(80, 0, 0), offset=18)

        # Подписи A1, B1, C1
        labels_sharygin = ["A₁", "B₁", "C₁"]
        for i, v in enumerate(self._sharygin_vertices[:3]):
            self._draw_label(painter, v, labels_sharygin[i], QColor(0, 0, 80), offset=18)

    def _draw_label(
        self, painter: QPainter, pos: QPointF, label: str, color: QColor, offset: float = 16
    ) -> None:
        """Рисует подпись с смещением от точки."""
        cx = sum(v.x() for v in self._original_vertices) / len(self._original_vertices)
        cy = sum(v.y() for v in self._original_vertices) / len(self._original_vertices)

        dx = pos.x() - cx
        dy = pos.y() - cy
        dist = math.sqrt(dx * dx + dy * dy)
        if dist < 0.01:
            return

        dx /= dist
        dy /= dist

        label_x = pos.x() + dx * offset
        label_y = pos.y() + dy * offset

        text_rect = QRectF(label_x - 10, label_y - 10, 20, 20)
        painter.setPen(QPen(color, 1))
        painter.drawText(
            text_rect,
            Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter,
            label,
        )

    # ------------------------------------------------------------------
    # Abstract methods
    # ------------------------------------------------------------------

    def contains_point(self, point: QPointF) -> bool:
        """Проверяет, принадлежит ли точка хотя бы одному из треугольников."""
        # Проверяем исходный треугольник ABC
        if len(self._original_vertices) >= 3:
            if self._point_in_triangle(
                point,
                self._original_vertices[0],
                self._original_vertices[1],
                self._original_vertices[2],
            ):
                return True
        # Проверяем треугольник Шарыгина A1B1C1
        if len(self._sharygin_vertices) >= 3:
            if self._point_in_triangle(
                point,
                self._sharygin_vertices[0],
                self._sharygin_vertices[1],
                self._sharygin_vertices[2],
            ):
                return True
        return False

    @staticmethod
    def _point_in_triangle(p: QPointF, p1: QPointF, p2: QPointF, p3: QPointF) -> bool:
        """Проверка принадлежности точки треугольнику (barycentric coordinates)."""

        def sign(pt: QPointF, a: QPointF, b: QPointF) -> float:
            return (pt.x() - b.x()) * (a.y() - b.y()) - (a.x() - b.x()) * (pt.y() - b.y())

        d1 = sign(p, p1, p2)
        d2 = sign(p, p2, p3)
        d3 = sign(p, p3, p1)

        has_neg = d1 < 0 or d2 < 0 or d3 < 0
        has_pos = d1 > 0 or d2 > 0 or d3 > 0

        return not (has_neg and has_pos)

    def move(self, dx: float, dy: float) -> None:
        for v in self._original_vertices:
            v.setX(v.x() + dx)
            v.setY(v.y() + dy)
        for v in self._sharygin_vertices:
            v.setX(v.x() + dx)
            v.setY(v.y() + dy)

    def rotate(self, angle: float, center: QPointF | None = None) -> None:
        if center is None:
            cx = sum(v.x() for v in self._original_vertices) / len(self._original_vertices)
            cy = sum(v.y() for v in self._original_vertices) / len(self._original_vertices)
            center = QPointF(cx, cy)

        rad = math.radians(angle)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)

        for v in self._original_vertices:
            dx = v.x() - center.x()
            dy = v.y() - center.y()
            v.setX(center.x() + dx * cos_a - dy * sin_a)
            v.setY(center.y() + dx * sin_a + dy * cos_a)

        for v in self._sharygin_vertices:
            dx = v.x() - center.x()
            dy = v.y() - center.y()
            v.setY(center.y() + dx * sin_a + dy * cos_a)

    def scale(self, factor: float, center: QPointF | None = None) -> None:
        if factor <= 0:
            raise ValueError("Scale factor must be positive")
        if center is None:
            cx = sum(v.x() for v in self._original_vertices) / len(self._original_vertices)
            cy = sum(v.y() for v in self._original_vertices) / len(self._original_vertices)
            center = QPointF(cx, cy)

        for v in self._original_vertices:
            v.setX(center.x() + (v.x() - center.x()) * factor)
            v.setY(center.y() + (v.y() - center.y()) * factor)

        for v in self._sharygin_vertices:
            v.setX(center.x() + (v.x() - center.x()) * factor)
            v.setY(center.y() + (v.y() - center.y()) * factor)

    def bounding_rect(self) -> QRectF:
        all_vertices = self._original_vertices + self._sharygin_vertices
        if not all_vertices:
            return QRectF()

        xs = [v.x() for v in all_vertices]
        ys = [v.y() for v in all_vertices]

        pad = max(self.pen_width / 2 + 12, 14)
        x_min = min(xs) - pad
        y_min = min(ys) - pad
        x_max = max(xs) + pad
        y_max = max(ys) + pad

        return self._safe_rect(x_min, y_min, x_max - x_min, y_max - y_min)

    def get_handles(self) -> list[QPointF]:
        return list(self._original_vertices) + list(self._sharygin_vertices)

    def get_handle_type(self, point: QPointF, tolerance: float = 5.0) -> HandleType:
        for i, v in enumerate(self._original_vertices):
            dx = point.x() - v.x()
            dy = point.y() - v.y()
            distance = math.sqrt(dx * dx + dy * dy)
            if distance <= tolerance:
                handle_map = {
                    0: HandleType.TOP_LEFT,
                    1: HandleType.BOTTOM_RIGHT,
                    2: HandleType.TOP_CENTER,
                }
                return handle_map.get(i, HandleType.NONE)
        for i, v in enumerate(self._sharygin_vertices):
            dx = point.x() - v.x()
            dy = point.y() - v.y()
            distance = math.sqrt(dx * dx + dy * dy)
            if distance <= tolerance:
                handle_map = {
                    0: HandleType.BOTTOM_LEFT,
                    1: HandleType.BOTTOM_RIGHT,
                    2: HandleType.TOP_CENTER,
                }
                return handle_map.get(i, HandleType.NONE)
        return HandleType.NONE

    def apply_handle_transform(
        self, handle: HandleType, point: QPointF, mouse_pos: QPointF, shift_pressed: bool = False
    ) -> None:
        if handle == HandleType.MOVE:
            dx = mouse_pos.x() - point.x()
            dy = mouse_pos.y() - point.y()
            for v in self._original_vertices:
                v.setX(v.x() + dx)
                v.setY(v.y() + dy)
            for v in self._sharygin_vertices:
                v.setX(v.x() + dx)
                v.setY(v.y() + dy)
            return

        # HandleType для вершин: TOP_LEFT=2, TOP_RIGHT=3, BOTTOM_LEFT=4, BOTTOM_RIGHT=5
        if handle.value == 2:  # TOP_LEFT -> A
            self._original_vertices[0].setX(mouse_pos.x())
            self._original_vertices[0].setY(mouse_pos.y())
            self._recompute_sharygin()
        elif handle.value == 3:  # TOP_RIGHT -> C
            self._original_vertices[2].setX(mouse_pos.x())
            self._original_vertices[2].setY(mouse_pos.y())
            self._recompute_sharygin()
        elif handle.value == 4:  # BOTTOM_LEFT -> B
            self._original_vertices[1].setX(mouse_pos.x())
            self._original_vertices[1].setY(mouse_pos.y())
            self._recompute_sharygin()
        elif handle.value == 5:  # BOTTOM_RIGHT -> B1 (или другая вершина)
            # Ресайз вершин Шарыгина не меняет геометрию, игнорируем
            pass

    def _recompute_sharygin(self) -> None:
        """Пересчитывает треугольник Шарыгина при изменении вершин ABC."""
        self._sharygin_vertices = self._compute_sharygin_triangle(self._original_vertices)
        self._bisector_endpoints = self._compute_bisector_endpoints(self._original_vertices)

    def _handle_positions(self) -> list[tuple[float, float]]:
        return [(v.x(), v.y()) for v in self._original_vertices]

    # ------------------------------------------------------------------
    # Свойства для панели
    # ------------------------------------------------------------------

    def get_properties(self) -> dict:
        d = super().get_properties()
        d["_shape_type"] = self.shape_type.value
        d["_size"] = self._size
        br = self.bounding_rect()
        d["_x"] = br.left()
        d["_y"] = br.top()
        d["_width"] = br.width()
        d["_height"] = br.height()
        return d

    def apply_properties(self, properties: dict) -> None:
        super().apply_properties(properties)
        if properties is None:
            return
        if "_size" in properties:
            self._size = properties["_size"]

    # ------------------------------------------------------------------
    # Позиция для undo
    # ------------------------------------------------------------------

    def get_position_data(self) -> dict:
        return {
            "original_vertices": [(v.x(), v.y()) for v in self._original_vertices],
            "sharygin_vertices": [(v.x(), v.y()) for v in self._sharygin_vertices],
        }

    def restore_position_data(self, data: dict) -> None:
        orig_data = data.get("original_vertices", [])
        sharygin_data = data.get("sharygin_vertices", [])
        for i, (vx, vy) in enumerate(orig_data):
            if i < len(self._original_vertices):
                self._original_vertices[i].setX(vx)
                self._original_vertices[i].setY(vy)
        for i, (vx, vy) in enumerate(sharygin_data):
            if i < len(self._sharygin_vertices):
                self._sharygin_vertices[i].setX(vx)
                self._sharygin_vertices[i].setY(vy)

    # ------------------------------------------------------------------
    # Сериализация
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update(
            {
                "original_vertices": [{"x": v.x(), "y": v.y()} for v in self._original_vertices],
                "sharygin_vertices": [{"x": v.x(), "y": v.y()} for v in self._sharygin_vertices],
                "size": self._size,
            }
        )
        return d

    @classmethod
    def from_dict(cls, data: dict) -> SharyginTriangleShape:
        orig_data = data.get("original_vertices", [])
        vertices = (
            [(v["x"], v["y"]) for v in orig_data] if orig_data else [(0, 0), (100, 0), (50, 86.6)]
        )
        size = data.get("size", 200)

        obj = cls(
            vertices=vertices,
            size=size,
            pen_color=data["pen_color"],
            brush_color=data.get("brush_color"),
            pen_width=data.get("pen_width", 2.0),
        )
        obj._selected = data.get("selected", False)
        obj._rotation = data.get("rotation", 0.0)
        return obj
