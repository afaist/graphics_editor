"""Фигура: два равных треугольника ABC и DEF."""

from __future__ import annotations

import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPen, QPolygonF

from .base_shape import BaseShape, HandleType, ShapeType


class CongruentTrianglesShape(BaseShape):
    """Два равных треугольника ABC и DEF.

    Параметры:
        vertices1: вершины первого треугольника ABC
        vertices2: вершины второго треугольника DEF
        pen_color: цвет контура
        pen_width: толщина контура
        brush_color: цвет заливки
        selected: выделена ли фигура
    """

    def __init__(
        self,
        vertices1: list[tuple[float, float]],
        vertices2: list[tuple[float, float]],
        pen_color: tuple[int, int, int] = (0, 0, 0),
        pen_width: float = 2.0,
        brush_color: tuple[int, int, int] | None = None,
        selected: bool = False,
    ):
        self._vertices1 = [QPointF(v[0], v[1]) for v in vertices1]  # ABC
        self._vertices2 = [QPointF(v[0], v[1]) for v in vertices2]  # DEF

        super().__init__(pen_color, pen_width, brush_color, selected)

    def _get_shape_type(self) -> ShapeType:
        return ShapeType.TRIANGLE_CONGRUENT

    # ------------------------------------------------------------------
    # Отрисовка
    # ------------------------------------------------------------------

    def draw(self, painter: QPainter) -> None:
        painter.save()
        try:
            # 1. Первый треугольник ABC (синий)
            abc_color = QColor(0, 100, 255)
            abc_pen = QPen(abc_color, self.pen_width)
            painter.setPen(abc_pen)
            abc_brush = QBrush(QColor(0, 100, 255, 50))
            painter.setBrush(abc_brush)

            if len(self._vertices1) >= 3:
                abc_polygon = QPolygonF(self._vertices1[:3])
                painter.drawPolygon(abc_polygon)

            # 2. Второй треугольник DEF (зелёный)
            def_color = QColor(0, 180, 0)
            def_pen = QPen(def_color, self.pen_width)
            painter.setPen(def_pen)
            def_brush = QBrush(QColor(0, 180, 0, 50))
            painter.setBrush(def_brush)

            if len(self._vertices2) >= 3:
                def_polygon = QPolygonF(self._vertices2[:3])
                painter.drawPolygon(def_polygon)

            # 3. Подписи вершин
            font = QFont()
            font.setFamily("Arial")
            font.setPointSizeF(9)
            painter.setFont(font)

            # Подписи ABC
            labels1 = ["A", "B", "C"]
            for i, v in enumerate(self._vertices1[:3]):
                self._draw_label(painter, v, labels1[i], QColor(0, 50, 180), offset=18)

            # Подписи DEF
            labels2 = ["D", "E", "F"]
            for i, v in enumerate(self._vertices2[:3]):
                if i == 0:
                    # D рисуем слева от вершины
                    self._draw_label_left(painter, v, labels2[i], QColor(0, 120, 0), offset=18)
                else:
                    self._draw_label(painter, v, labels2[i], QColor(0, 120, 0), offset=18)

            # 4. Маркеры выделения
            if self._selected:
                pen = QPen(QColor(0, 120, 255), 1)
                painter.setPen(pen)
                painter.setBrush(Qt.BrushStyle.NoBrush)
                for hx, hy in self._handle_positions():
                    painter.drawRect(int(hx) - 4, int(hy) - 4, 8, 8)

        finally:
            painter.restore()

    def _draw_label(
        self, painter: QPainter, pos: QPointF, label: str, color: QColor, offset: float = 16
    ) -> None:
        """Рисует подпись с смещением от точки."""
        cx = sum(v.x() for v in self._vertices1) / len(self._vertices1)
        cy = sum(v.y() for v in self._vertices1) / len(self._vertices1)

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

    def _draw_label_left(
        self, painter: QPainter, pos: QPointF, label: str, color: QColor, offset: float = 16
    ) -> None:
        """Рисует подпись слева от вершины."""
        label_x = pos.x() - offset
        label_y = pos.y()

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
        if len(self._vertices1) >= 3:
            if self._point_in_triangle(
                point,
                self._vertices1[0],
                self._vertices1[1],
                self._vertices1[2],
            ):
                return True
        if len(self._vertices2) >= 3:
            if self._point_in_triangle(
                point,
                self._vertices2[0],
                self._vertices2[1],
                self._vertices2[2],
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
        for v in self._vertices1:
            v.setX(v.x() + dx)
            v.setY(v.y() + dy)
        for v in self._vertices2:
            v.setX(v.x() + dx)
            v.setY(v.y() + dy)

    def rotate(self, angle: float, center: QPointF | None = None) -> None:
        if center is None:
            cx = sum(v.x() for v in self._vertices1) / len(self._vertices1)
            cy = sum(v.y() for v in self._vertices1) / len(self._vertices1)
            center = QPointF(cx, cy)

        rad = math.radians(angle)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)

        for v in self._vertices1:
            vx = v.x() - center.x()
            vy = v.y() - center.y()
            v.setX(center.x() + vx * cos_a - vy * sin_a)
            v.setY(center.y() + vx * sin_a + vy * cos_a)

        for v in self._vertices2:
            vx = v.x() - center.x()
            vy = v.y() - center.y()
            v.setX(center.x() + vx * cos_a - vy * sin_a)
            v.setY(center.y() + vx * sin_a + vy * cos_a)

    def scale(self, factor: float, center: QPointF | None = None) -> None:
        if factor <= 0:
            raise ValueError("Scale factor must be positive")
        if center is None:
            cx = sum(v.x() for v in self._vertices1) / len(self._vertices1)
            cy = sum(v.y() for v in self._vertices1) / len(self._vertices1)
            center = QPointF(cx, cy)

        for v in self._vertices1:
            v.setX(center.x() + (v.x() - center.x()) * factor)
            v.setY(center.y() + (v.y() - center.y()) * factor)

        for v in self._vertices2:
            v.setX(center.x() + (v.x() - center.x()) * factor)
            v.setY(center.y() + (v.y() - center.y()) * factor)

    def bounding_rect(self) -> QRectF:
        all_vertices = self._vertices1 + self._vertices2
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
        return list(self._vertices1) + list(self._vertices2)

    def get_handle_type(self, point: QPointF, tolerance: float = 5.0) -> HandleType:
        for i, v in enumerate(self._vertices1):
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
        for i, v in enumerate(self._vertices2):
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
            for v in self._vertices1:
                v.setX(v.x() + dx)
                v.setY(v.y() + dy)
            for v in self._vertices2:
                v.setX(v.x() + dx)
                v.setY(v.y() + dy)
            return

        # TOP_LEFT -> A (вершина 0 первого треугольника)
        if handle.value == 2:
            self._vertices1[0].setX(mouse_pos.x())
            self._vertices1[0].setY(mouse_pos.y())
        # TOP_RIGHT -> C (вершина 2 первого треугольника)
        elif handle.value == 3:
            self._vertices1[2].setX(mouse_pos.x())
            self._vertices1[2].setY(mouse_pos.y())
        # BOTTOM_LEFT -> B (вершина 1 первого треугольника)
        elif handle.value == 4:
            self._vertices1[1].setX(mouse_pos.x())
            self._vertices1[1].setY(mouse_pos.y())
        # BOTTOM_RIGHT -> F (вершина 2 второго треугольника)
        elif handle.value == 5:
            self._vertices2[2].setX(mouse_pos.x())
            self._vertices2[2].setY(mouse_pos.y())

    def _handle_positions(self) -> list[tuple[float, float]]:
        return [(v.x(), v.y()) for v in self._vertices1]

    # ------------------------------------------------------------------
    # Свойства для панели
    # ------------------------------------------------------------------

    def get_properties(self) -> dict:
        d = super().get_properties()
        d["_shape_type"] = self.shape_type.value
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

    # ------------------------------------------------------------------
    # Позиция для undo
    # ------------------------------------------------------------------

    def get_position_data(self) -> dict:
        return {
            "vertices1": [(v.x(), v.y()) for v in self._vertices1],
            "vertices2": [(v.x(), v.y()) for v in self._vertices2],
        }

    def restore_position_data(self, data: dict) -> None:
        v1_data = data.get("vertices1", [])
        v2_data = data.get("vertices2", [])
        for i, (vx, vy) in enumerate(v1_data):
            if i < len(self._vertices1):
                self._vertices1[i].setX(vx)
                self._vertices1[i].setY(vy)
        for i, (vx, vy) in enumerate(v2_data):
            if i < len(self._vertices2):
                self._vertices2[i].setX(vx)
                self._vertices2[i].setY(vy)

    # ------------------------------------------------------------------
    # Сериализация
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update(
            {
                "vertices1": [{"x": v.x(), "y": v.y()} for v in self._vertices1],
                "vertices2": [{"x": v.x(), "y": v.y()} for v in self._vertices2],
            }
        )
        return d

    @classmethod
    def from_dict(cls, data: dict) -> CongruentTrianglesShape:
        v1_data = data.get("vertices1", [])
        v2_data = data.get("vertices2", [])
        vertices1 = (
            [(v["x"], v["y"]) for v in v1_data] if v1_data else [(0, 0), (100, 0), (50, 86.6)]
        )
        vertices2 = (
            [(v["x"], v["y"]) for v in v2_data] if v2_data else [(200, 0), (300, 0), (250, 86.6)]
        )

        obj = cls(
            vertices1=vertices1,
            vertices2=vertices2,
            pen_color=data["pen_color"],
            brush_color=data.get("brush_color"),
            pen_width=data.get("pen_width", 2.0),
        )
        obj._selected = data.get("selected", False)
        obj._rotation = data.get("rotation", 0.0)
        return obj
