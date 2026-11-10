"""Фигура: два подобных треугольника ABC и DEF."""

from __future__ import annotations

import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPen, QPolygonF

from .base_shape import BaseShape, HandleType, ShapeType


class SimilarTrianglesShape(BaseShape):
    """Два подобных треугольника ABC и DEF.

    Второй треугольник вычисляется динамически на основе первого,
    коэффициента подобия и вектора смещения центров.
    """

    def __init__(
        self,
        vertices1: list[tuple[float, float]],
        vertices2: list[tuple[float, float]],
        similarity_ratio: float = 2.0,
        pen_color: tuple[int, int, int] = (0, 0, 0),
        pen_width: float = 2.0,
        brush_color: tuple[int, int, int] | None = None,
        selected: bool = False,
    ):
        self._vertices1 = [QPointF(v[0], v[1]) for v in vertices1]
        self._similarity_ratio = similarity_ratio

        if vertices1 and vertices2:
            c1 = (
                sum(v[0] for v in vertices1) / len(vertices1),
                sum(v[1] for v in vertices1) / len(vertices1),
            )
            c2 = (
                sum(v[0] for v in vertices2) / len(vertices2),
                sum(v[1] for v in vertices2) / len(vertices2),
            )
            self._center_offset = QPointF(c2[0] - c1[0], c2[1] - c1[1])
        else:
            self._center_offset = QPointF(0, 0)

        super().__init__(pen_color, pen_width, brush_color, selected)

    def _get_shape_type(self) -> ShapeType:
        return ShapeType.TRIANGLE_SIMILAR

    @property
    def vertices2(self) -> list[QPointF]:
        if not self._vertices1:
            return []
        cx = sum(v.x() for v in self._vertices1) / len(self._vertices1)
        cy = sum(v.y() for v in self._vertices1) / len(self._vertices1)
        result = []
        for v in self._vertices1:
            sx = cx + (v.x() - cx) * self._similarity_ratio
            sy = cy + (v.y() - cy) * self._similarity_ratio
            result.append(QPointF(sx + self._center_offset.x(), sy + self._center_offset.y()))
        return result

    @property
    def _all_vertices(self) -> list[QPointF]:
        return self._vertices1 + self.vertices2

    def _rotation_center(self) -> tuple[float, float] | None:
        if not self._vertices1:
            return None
        return self._center_of_vertices(self._all_vertices)

    def _draw_shape_content(self, painter: QPainter) -> None:
        v1 = self._vertices1
        v2 = self.vertices2

        abc_color = QColor(0, 100, 255)
        abc_pen = QPen(abc_color, self.pen_width)
        painter.setPen(abc_pen)
        abc_brush = QBrush(QColor(0, 100, 255, 50))
        painter.setBrush(abc_brush)
        if len(v1) >= 3:
            painter.drawPolygon(QPolygonF(v1[:3]))

        def_color = QColor(0, 180, 0)
        def_pen = QPen(def_color, self.pen_width)
        painter.setPen(def_pen)
        def_brush = QBrush(QColor(0, 180, 0, 50))
        painter.setBrush(def_brush)
        if len(v2) >= 3:
            painter.drawPolygon(QPolygonF(v2[:3]))

        font = QFont()
        font.setFamily("Arial")
        font.setPointSizeF(9)
        painter.setFont(font)

        for i, v in enumerate(v1[:3]):
            self._draw_label(painter, v, ["A", "B", "C"][i], QColor(0, 50, 180), offset=18)

        for i, v in enumerate(v2[:3]):
            if i == 0:
                self._draw_label_left(painter, v, "D", QColor(0, 120, 0), offset=18)
            else:
                self._draw_label(painter, v, ["E", "F"][i - 1], QColor(0, 120, 0), offset=18)

        if len(v1) >= 3 and len(v2) >= 3:
            cx1 = sum(v.x() for v in v1[:3]) / 3
            cy1 = sum(v.y() for v in v1[:3]) / 3
            painter.setPen(QPen(QColor(100, 100, 100), 1))
            painter.drawText(
                QRectF(cx1 - 30, cy1 + 25, 60, 20),
                Qt.AlignmentFlag.AlignCenter,
                "k = " + str(self._similarity_ratio),
            )

    def _draw_label(
        self, painter: QPainter, pos: QPointF, label: str, color: QColor, offset: float = 16
    ) -> None:
        if not self._vertices1:
            return
        cx = sum(v.x() for v in self._vertices1) / len(self._vertices1)
        cy = sum(v.y() for v in self._vertices1) / len(self._vertices1)
        dx = pos.x() - cx
        dy = pos.y() - cy
        dist = math.sqrt(dx * dx + dy * dy)
        if dist < 0.01:
            return
        dx /= dist
        dy /= dist
        text_rect = QRectF(pos.x() + dx * offset - 10, pos.y() + dy * offset - 10, 20, 20)
        painter.setPen(QPen(color, 1))
        painter.drawText(
            text_rect, Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter, label
        )

    def _draw_label_left(
        self, painter: QPainter, pos: QPointF, label: str, color: QColor, offset: float = 16
    ) -> None:
        text_rect = QRectF(pos.x() - offset - 10, pos.y() - 10, 20, 20)
        painter.setPen(QPen(color, 1))
        painter.drawText(
            text_rect, Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter, label
        )

    def contains_point(self, point: QPointF) -> bool:
        v1 = self._vertices1
        v2 = self.vertices2
        if len(v1) >= 3 and self._point_in_triangle(point, v1[0], v1[1], v1[2]):
            return True
        if len(v2) >= 3 and self._point_in_triangle(point, v2[0], v2[1], v2[2]):
            return True
        return False

    @staticmethod
    def _point_in_triangle(p: QPointF, p1: QPointF, p2: QPointF, p3: QPointF) -> bool:
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

    def rotate(self, angle: float, center: QPointF | None = None) -> None:
        if not self._vertices1:
            return
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

    def scale(self, factor: float, center: QPointF | None = None) -> None:
        if factor <= 0:
            raise ValueError("Scale factor must be positive")
        if not self._vertices1:
            return
        if center is None:
            cx = sum(v.x() for v in self._vertices1) / len(self._vertices1)
            cy = sum(v.y() for v in self._vertices1) / len(self._vertices1)
            center = QPointF(cx, cy)
        for v in self._vertices1:
            v.setX(center.x() + (v.x() - center.x()) * factor)
            v.setY(center.y() + (v.y() - center.y()) * factor)

    def bounding_rect(self) -> QRectF:
        if not self._vertices1:
            return QRectF()
        all_v = self._all_vertices
        xs = [v.x() for v in all_v]
        ys = [v.y() for v in all_v]
        pad = max(self.pen_width / 2 + 12, 14)
        return self._safe_rect(
            min(xs) - pad, min(ys) - pad, max(xs) - min(xs) + 2 * pad, max(ys) - min(ys) + 2 * pad
        )

    def get_handles(self) -> list[QPointF]:
        return list(self._vertices1) + self.vertices2

    def get_handle_type(self, point: QPointF, tolerance: float = 5.0) -> HandleType:
        for i, v in enumerate(self._vertices1):
            dx = point.x() - v.x()
            dy = point.y() - v.y()
            if math.sqrt(dx * dx + dy * dy) <= tolerance:
                return {
                    0: HandleType.TOP_LEFT,
                    1: HandleType.BOTTOM_RIGHT,
                    2: HandleType.TOP_CENTER,
                }.get(i, HandleType.NONE)
        v2 = self.vertices2
        for i, v in enumerate(v2):
            dx = point.x() - v.x()
            dy = point.y() - v.y()
            if math.sqrt(dx * dx + dy * dy) <= tolerance:
                return {
                    0: HandleType.BOTTOM_LEFT,
                    1: HandleType.BOTTOM_RIGHT,
                    2: HandleType.TOP_CENTER,
                }.get(i, HandleType.NONE)
        return HandleType.NONE

    def apply_handle_transform(
        self,
        handle: HandleType,
        point: QPointF,
        mouse_pos: QPointF,
        shift_pressed: bool = False,
        vertex_index: int = -1,
    ) -> None:
        if handle == HandleType.MOVE:
            dx = mouse_pos.x() - point.x()
            dy = mouse_pos.y() - point.y()
            for v in self._vertices1:
                v.setX(v.x() + dx)
                v.setY(v.y() + dy)
            return

        tolerance = 5.0
        for v in self._vertices1:
            dx = point.x() - v.x()
            dy = point.y() - v.y()
            if math.sqrt(dx * dx + dy * dy) <= tolerance:
                v.setX(mouse_pos.x())
                v.setY(mouse_pos.y())
                return

    def _handle_positions(self) -> list[tuple[float, float]]:
        return [(v.x(), v.y()) for v in self._vertices1]

    def get_properties(self) -> dict:
        d = super().get_properties()
        d["_shape_type"] = self.shape_type.value
        d["_similarity_ratio"] = self._similarity_ratio
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
        if "_similarity_ratio" in properties:
            self._similarity_ratio = properties["_similarity_ratio"]

    def get_position_data(self) -> dict:
        return {"vertices1": [(v.x(), v.y()) for v in self._vertices1]}

    def restore_position_data(self, data: dict) -> None:
        for i, (vx, vy) in enumerate(data.get("vertices1", [])):
            if i < len(self._vertices1):
                self._vertices1[i].setX(vx)
                self._vertices1[i].setY(vy)

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update(
            {
                "vertices1": [{"x": v.x(), "y": v.y()} for v in self._vertices1],
                "similarity_ratio": self._similarity_ratio,
                "center_offset": {"x": self._center_offset.x(), "y": self._center_offset.y()},
            }
        )
        return d

    @classmethod
    def from_dict(cls, data: dict) -> SimilarTrianglesShape:
        v1_data = data.get("vertices1", [])
        ratio = data.get("similarity_ratio", 2.0)
        offset_data = data.get("center_offset", {"x": 0, "y": 0})

        vertices1 = (
            [(v["x"], v["y"]) for v in v1_data] if v1_data else [(0, 0), (100, 0), (50, 86.6)]
        )

        if vertices1:
            cx = sum(v[0] for v in vertices1) / len(vertices1)
            cy = sum(v[1] for v in vertices1) / len(vertices1)
            ox = float(offset_data["x"])
            oy = float(offset_data["y"])
            vertices2 = [(cx + ox, cy + oy) for _ in vertices1]
        else:
            vertices2 = [(0.0, 0.0), (0.0, 0.0), (0.0, 0.0)]

        obj = cls(
            vertices1=vertices1,
            vertices2=vertices2,
            similarity_ratio=ratio,
            pen_color=data["pen_color"],
            brush_color=data.get("brush_color"),
            pen_width=data.get("pen_width", 2.0),
        )
        obj._selected = data.get("selected", False)
        obj._rotation = data.get("rotation", 0.0)
        return obj
