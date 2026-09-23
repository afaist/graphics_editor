"""Фигура: Трапеция (равнобедренная и произвольная)."""

from __future__ import annotations

import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPen, QPolygonF

from .base_shape import BaseShape, HandleType, ShapeType


class TrapezoidShape(BaseShape):
    """Трапеция с поддержкой двух типов: isosceles (равнобедренная) и scalene (произвольная).

    Параметры:
    - isosceles: base_a, base_b, angle_deg — вычисляется высота из угла
    - scalene: base_a, base_b, height, offset — смещение верхнего основания
    """

    VALID_TYPES = ("isosceles", "scalene")

    def __init__(
        self,
        vertices: list[tuple[float, float]],
        trapezoid_type: str = "scalene",
        # Для isosceles
        base_a: float = 200.0,
        base_b: float = 100.0,
        angle_deg: float = 60.0,
        # Для scalene
        top_width: float = 100.0,
        bottom_width: float = 200.0,
        height: float = 100.0,
        offset_left: float = 0.0,
        labels: list[str] | None = None,
        pen_color: tuple[int, int, int] = (0, 0, 0),
        pen_width: float = 2.0,
        brush_color: tuple[int, int, int] | None = None,
        selected: bool = False,
    ):
        # Устанавливаем _trapezoid_type ДО вызова super().__init__()
        if trapezoid_type not in self.VALID_TYPES:
            raise ValueError(f"trapezoid_type must be one of {self.VALID_TYPES}")
        self._trapezoid_type = trapezoid_type

        super().__init__(pen_color, pen_width, brush_color, selected)

        self._vertices = [QPointF(v[0], v[1]) for v in vertices]
        # Для isosceles
        self._base_a = base_a
        self._base_b = base_b
        self._angle_deg = angle_deg
        # Для scalene
        self._top_width = top_width
        self._bottom_width = bottom_width
        self._height = height
        self._offset_left = offset_left

        if labels is None:
            self._labels = ["A", "B", "C", "D"]
        else:
            self._labels = labels[:4]

    def set_end_point(self, x: float, y: float) -> None:
        pass

    def set_size(self, width: float, height: float) -> None:
        pass

    def add_vertex(self, x: float, y: float) -> None:
        pass

    def _get_shape_type(self) -> ShapeType:
        type_map = {
            "isosceles": ShapeType.TRAPEZOID_ISOSCELES,
            "scalene": ShapeType.TRAPEZOID,
        }
        return type_map[self._trapezoid_type]

    # ------------------------------------------------------------------
    # Свойства
    # ------------------------------------------------------------------

    @property
    def vertices(self) -> list[QPointF]:
        return self._vertices

    @property
    def trapezoid_type(self) -> str:
        return self._trapezoid_type

    @property
    def base_a(self) -> float:
        return self._base_a

    @property
    def base_b(self) -> float:
        return self._base_b

    @property
    def top_width(self) -> float:
        return self._top_width

    @property
    def bottom_width(self) -> float:
        return self._bottom_width

    @property
    def height(self) -> float:
        return self._height

    @property
    def offset_left(self) -> float:
        return self._offset_left

    @property
    def angle_deg(self) -> float:
        return self._angle_deg

    @property
    def labels(self) -> list[str]:
        return self._labels

    # ------------------------------------------------------------------
    # Статические методы построения
    # ------------------------------------------------------------------

    @staticmethod
    def build_isosceles(
        base_a: float, base_b: float, angle_deg: float
    ) -> list[tuple[float, float]]:
        """Построить равнобедренную трапецию.

        base_a — нижнее основание, base_b — верхнее, angle_deg — угол при основании.
        Высота вычисляется: h = (base_a - base_b) / 2 * tan(angle)
        """
        if base_a <= base_b:
            base_a, base_b = base_b, base_a

        angle_rad = math.radians(angle_deg)
        h = ((base_a - base_b) / 2) * math.tan(angle_rad)

        if h < 1.0:
            h = 1.0

        # Центрируем нижнее основание
        return [
            (-base_a / 2, 0),
            (base_a / 2, 0),
            (base_b / 2, -h),
            (-base_b / 2, -h),
        ]

    @staticmethod
    def build_scalene(
        top_width: float, bottom_width: float, height: float, offset_left: float = 0.0
    ) -> list[tuple[float, float]]:
        """Построить произвольную трапецию.

        top_width — верхнее основание, bottom_width — нижнее,
        height — высота, offset_left — смещение левого края верхнего основания.

        Вершины в локальной системе (начало в левом нижнем, Y вверх):
        A (левый нижний): (0, 0)
        B (правый нижний): (bottom_width, 0)
        C (правый верхний): (bottom_width - offset_right, height)
        D (левый верхний): (offset_left, height)

        offset_right = bottom_width - top_width - offset_left

        Возвращает в координатах Qt (Y вниз): верхние вершины имеют отрицательный Y.
        """
        if height < 1.0:
            height = 1.0

        offset_right = bottom_width - top_width - offset_left

        return [
            (0, 0),
            (bottom_width, 0),
            (bottom_width - offset_right, -height),
            (offset_left, -height),
        ]

    @staticmethod
    def center_vertices(vertices: list[tuple[float, float]]) -> list[tuple[float, float]]:
        """Центрировать фигуру относительно (0, 0)."""
        cx = sum(v[0] for v in vertices) / len(vertices)
        cy = sum(v[1] for v in vertices) / len(vertices)
        return [(v[0] - cx, v[1] - cy) for v in vertices]

    @staticmethod
    def order_vertices_clockwise(vertices: list[tuple[float, float]]) -> list[tuple[float, float]]:
        """Пересортировать вершины по часовой стрелке, начиная с левого нижнего угла."""
        if len(vertices) < 3:
            return vertices

        cx = sum(v[0] for v in vertices) / len(vertices)
        cy = sum(v[1] for v in vertices) / len(vertices)

        # Левый нижний: max Y, затем min X
        start_idx = 0
        for i in range(1, len(vertices)):
            if vertices[i][1] > vertices[start_idx][1] or (
                vertices[i][1] == vertices[start_idx][1]
                and vertices[i][0] < vertices[start_idx][0]
            ):
                start_idx = i

        # В Qt-координатах (Y вниз) atan2 = по часовой стрелке
        def angle_key(v):
            return math.atan2(v[1] - cy, v[0] - cx)

        sorted_vertices = sorted(vertices, key=angle_key)

        for i, v in enumerate(sorted_vertices):
            if (
                abs(v[0] - vertices[start_idx][0]) < 0.001
                and abs(v[1] - vertices[start_idx][1]) < 0.001
            ):
                return sorted_vertices[i:] + sorted_vertices[:i]

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

            # Применяем поворот вокруг центра трапеции
            if abs(self._rotation) > 0.01 and len(self._vertices) > 0:
                cx = sum(v.x() for v in self._vertices) / len(self._vertices)
                cy = sum(v.y() for v in self._vertices) / len(self._vertices)
                painter.translate(cx, cy)
                painter.rotate(self._rotation)
                painter.translate(-cx, -cy)

            if len(self._vertices) >= 4:
                polygon = QPolygonF(self._vertices)
                painter.drawPolygon(polygon)

            # Маркеры вершин
            pen.setColor(QColor(80, 80, 80))
            pen.setWidth(1)
            painter.setPen(pen)
            painter.setBrush(QBrush(QColor(255, 255, 255)))
            for v in self._vertices:
                painter.drawEllipse(v, 3, 3)

            # Подпись вершин
            self._draw_vertex_labels(painter)

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
        """Отрисовать подписи вершин (A, B, C, D)."""
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
        """Проверка точки в выпуклом полигоне (ray casting)."""
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

    def rotate(self, angle: float, center: QPointF | None = None) -> None:
        if center is None:
            cx = sum(v.x() for v in self._vertices) / 4
            cy = sum(v.y() for v in self._vertices) / 4
            center = QPointF(cx, cy)

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
            cx = sum(v.x() for v in self._vertices) / 4
            cy = sum(v.y() for v in self._vertices) / 4
            center = QPointF(cx, cy)

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
                    HandleType.BOTTOM_RIGHT,
                    HandleType.BOTTOM_LEFT,
                    HandleType.TOP_RIGHT,
                ]
                return handle_map[i]
        return HandleType.NONE

    def apply_handle_transform(
        self, handle: HandleType, point: QPointF, mouse_pos: QPointF
    ) -> None:
        idx = handle.value - 2
        if 0 <= idx < len(self._vertices):
            self._vertices[idx].setX(mouse_pos.x())
            self._vertices[idx].setY(mouse_pos.y())

    def _handle_positions(self) -> list[tuple[float, float]]:
        return [(v.x(), v.y()) for v in self._vertices]

    # ------------------------------------------------------------------
    # Свойства для панели
    # ------------------------------------------------------------------

    def get_properties(self) -> dict:
        d = super().get_properties()
        d["_shape_type"] = self.shape_type.value
        d["_trapezoid_type"] = self._trapezoid_type
        d["_base_a"] = self._base_a
        d["_base_b"] = self._base_b
        d["_top_width"] = self._top_width
        d["_bottom_width"] = self._bottom_width
        d["_height"] = self._height
        d["_offset_left"] = self._offset_left
        d["_angle_deg"] = self._angle_deg

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

        if "_base_a" in properties:
            self._base_a = properties["_base_a"]
        if "_base_b" in properties:
            self._base_b = properties["_base_b"]
        if "_top_width" in properties:
            self._top_width = properties["_top_width"]
        if "_bottom_width" in properties:
            self._bottom_width = properties["_bottom_width"]
        if "_height" in properties:
            self._height = properties["_height"]
        if "_offset_left" in properties:
            self._offset_left = properties["_offset_left"]
        if "_angle_deg" in properties:
            self._angle_deg = properties["_angle_deg"]

        self._rebuild_vertices()

    def _rebuild_vertices(self) -> None:
        if self._trapezoid_type == "isosceles":
            raw = self.build_isosceles(self._base_a, self._base_b, self._angle_deg)
        else:
            raw = self.build_scalene(
                self._top_width, self._bottom_width, self._height, self._offset_left
            )

        centered = self.center_vertices(raw)
        centered = self.order_vertices_clockwise(centered)
        self._vertices = [QPointF(v[0], v[1]) for v in centered]

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
        d.update(
            {
                "trapezoid_type": self._trapezoid_type,
                "base_a": self._base_a,
                "base_b": self._base_b,
                "top_width": self._top_width,
                "bottom_width": self._bottom_width,
                "height": self._height,
                "offset_left": self._offset_left,
                "angle_deg": self._angle_deg,
                "vertices": [{"x": v.x(), "y": v.y()} for v in self._vertices],
            }
        )
        return d

    @classmethod
    def from_dict(cls, data: dict) -> TrapezoidShape:
        vertices_data = data.get("vertices", [])
        trapezoid_type = data.get("trapezoid_type", "scalene")

        if vertices_data:
            vertices = [(v["x"], v["y"]) for v in vertices_data]
        else:
            if trapezoid_type == "isosceles":
                vertices = cls.center_vertices(
                    cls.build_isosceles(
                        data.get("base_a", 200), data.get("base_b", 100), data.get("angle_deg", 60)
                    )
                )
            else:
                vertices = cls.center_vertices(
                    cls.build_scalene(
                        data.get("top_width", 100),
                        data.get("bottom_width", 200),
                        data.get("height", 100),
                        data.get("offset_left", 0),
                    )
                )

        obj = cls(
            vertices=vertices,
            trapezoid_type=trapezoid_type,
            base_a=data.get("base_a", 200),
            base_b=data.get("base_b", 100),
            top_width=data.get("top_width", 100),
            bottom_width=data.get("bottom_width", 200),
            height=data.get("height", 100),
            offset_left=data.get("offset_left", 0),
            angle_deg=data.get("angle_deg", 60),
            pen_color=data["pen_color"],
            brush_color=data.get("brush_color"),
            pen_width=data.get("pen_width", 2.0),
        )
        obj._selected = data.get("selected", False)
        obj._rotation = data.get("rotation", 0.0)
        return obj
