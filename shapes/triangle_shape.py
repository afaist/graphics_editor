"""Фигура: Треугольник (4 типа: равносторонний, равнобедренный, прямоугольный, тупоугольный)."""

from __future__ import annotations

import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPen, QPolygonF

from .base_shape import BaseShape, HandleType, ShapeType


class TriangleShape(BaseShape):
    """Треугольник с поддержкой 4 типов: equilateral, isosceles, right, obtuse.

    Параметры построения:
    - equilateral: side (сторона)
    - isosceles: base (основание), height (высота)
    - right: leg_a, leg_b (катеты)
    - obtuse: side_a, side_b, angle_deg (две стороны и угол между ними)
    """

    VALID_TYPES = ("equilateral", "isosceles", "right", "obtuse")

    def __init__(
        self,
        vertices: list[tuple[float, float]],
        triangle_type: str = "equilateral",
        side_a: float = 100.0,
        side_b: float = 100.0,
        height: float = 86.6,
        angle_deg: float = 60.0,
        labels: list[str] | None = None,
        pen_color: tuple[int, int, int] = (0, 0, 0),
        pen_width: float = 2.0,
        brush_color: tuple[int, int, int] | None = None,
        selected: bool = False,
        # Дополнительные линии
        draw_height: bool = True,
        draw_median: bool = False,
        draw_bisector: bool = False,
        vertex_index: int = 0,
    ):
        # Устанавливаем _triangle_type ДО вызова super().__init__()
        # т.к. BaseShape.__init__ вызывает _get_shape_type()
        if triangle_type not in self.VALID_TYPES:
            raise ValueError(f"triangle_type must be one of {self.VALID_TYPES}")
        self._triangle_type = triangle_type

        super().__init__(pen_color, pen_width, brush_color, selected)

        self._vertices = [QPointF(v[0], v[1]) for v in vertices]
        self._side_a = side_a
        self._side_b = side_b
        self._height = height
        self._angle_deg = angle_deg

        if labels is None:
            self._labels = ["A", "B", "C"]
        else:
            self._labels = labels[:3]

        # Дополнительные линии
        self._draw_height = draw_height
        self._draw_median = draw_median
        self._draw_bisector = draw_bisector
        self._vertex_index = vertex_index
        self._aux_points: list[tuple[QPointF, str]] = []  # (точка, метка)

    def set_end_point(self, x: float, y: float) -> None:
        pass

    def set_size(self, width: float, height: float) -> None:
        pass

    def add_vertex(self, x: float, y: float) -> None:
        pass

    def _get_shape_type(self) -> ShapeType:
        type_map = {
            "equilateral": ShapeType.TRIANGLE_EQUILATERAL,
            "isosceles": ShapeType.TRIANGLE_ISOSCELES,
            "right": ShapeType.TRIANGLE_RIGHT,
            "obtuse": ShapeType.TRIANGLE_OBTUSE,
        }
        return type_map[self._triangle_type]

    # ------------------------------------------------------------------
    # Свойства
    # ------------------------------------------------------------------

    @property
    def vertices(self) -> list[QPointF]:
        return self._vertices

    @property
    def triangle_type(self) -> str:
        return self._triangle_type

    @property
    def side_a(self) -> float:
        return self._side_a

    @property
    def side_b(self) -> float:
        return self._side_b

    @property
    def height(self) -> float:
        return self._height

    @property
    def angle_deg(self) -> float:
        return self._angle_deg

    @property
    def labels(self) -> list[str]:
        return self._labels

    @property
    def draw_height(self) -> bool:
        return self._draw_height

    @draw_height.setter
    def draw_height(self, value: bool) -> None:
        self._draw_height = value

    @property
    def draw_median(self) -> bool:
        return self._draw_median

    @draw_median.setter
    def draw_median(self, value: bool) -> None:
        self._draw_median = value

    @property
    def draw_bisector(self) -> bool:
        return self._draw_bisector

    @draw_bisector.setter
    def draw_bisector(self, value: bool) -> None:
        self._draw_bisector = value

    @property
    def vertex_index(self) -> int:
        return self._vertex_index

    @vertex_index.setter
    def vertex_index(self, value: int) -> None:
        self._vertex_index = value

    # ------------------------------------------------------------------
    # Статические методы построения
    # ------------------------------------------------------------------

    @staticmethod
    def build_equilateral(side: float) -> list[tuple[float, float]]:
        """Построить вершины равностороннего треугольника со стороной side."""
        h = side * math.sqrt(3) / 2
        return [
            (0, 0),
            (side, 0),
            (side / 2, h),
        ]

    @staticmethod
    def build_isosceles(base: float, height: float) -> list[tuple[float, float]]:
        """Построить вершины равнобедренного треугольника."""
        return [
            (-base / 2, 0),
            (base / 2, 0),
            (0, height),
        ]

    @staticmethod
    def build_right(leg_a: float, leg_b: float) -> list[tuple[float, float]]:
        """Построить вершины прямоугольного треугольника."""
        return [
            (0, 0),
            (leg_a, 0),
            (0, leg_b),
        ]

    @staticmethod
    def build_obtuse(side_a: float, side_b: float, angle_deg: float) -> list[tuple[float, float]]:
        """Построить вершины тупоугольного треугольника по двум сторонам и углу между ними."""
        angle_rad = math.radians(angle_deg)
        return [
            (0, 0),
            (side_a, 0),
            (side_b * math.cos(angle_rad), side_b * math.sin(angle_rad)),
        ]

    @staticmethod
    def center_vertices(vertices: list[tuple[float, float]]) -> list[tuple[float, float]]:
        """Центрировать треугольник относительно (0, 0)."""
        cx = sum(v[0] for v in vertices) / 3
        cy = sum(v[1] for v in vertices) / 3
        return [(v[0] - cx, v[1] - cy) for v in vertices]

    @staticmethod
    def flip_y(vertices: list[tuple[float, float]]) -> list[tuple[float, float]]:
        """Инвертировать Y для всех вершин (треугольник смотрит вверх)."""
        return [(v[0], -v[1]) for v in vertices]

    @staticmethod
    def order_vertices_clockwise(vertices: list[tuple[float, float]]) -> list[tuple[float, float]]:
        """Пересортировать вершины по часовой стрелке, начиная с левого нижнего угла.

        В экранных координатах Qt: Y=0 сверху, растёт вниз.
        Левый нижний = max Y (низ), затем min X (лево).
        """
        if len(vertices) < 3:
            return vertices

        cx = sum(v[0] for v in vertices) / len(vertices)
        cy = sum(v[1] for v in vertices) / len(vertices)

        # Найти левый нижний угол: max Y (низ экрана), затем min X (лево)
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

        # Найти стартовую точку и начать с неё
        for i, v in enumerate(sorted_vertices):
            if (
                abs(v[0] - vertices[start_idx][0]) < 0.001
                and abs(v[1] - vertices[start_idx][1]) < 0.001
            ):
                return sorted_vertices[i:] + sorted_vertices[:i]

        return sorted_vertices

    # ------------------------------------------------------------------
    # Вспомогательные линии (высота, медиана, биссектриса)
    # ------------------------------------------------------------------

    @staticmethod
    def _project_point_to_line(point: QPointF, line_start: QPointF, line_end: QPointF) -> QPointF:
        """Проецирует точку на прямую, проходящую через line_start и line_end."""
        dx = line_end.x() - line_start.x()
        dy = line_end.y() - line_start.y()
        length_sq = dx * dx + dy * dy
        if length_sq < 1e-10:
            return line_start
        t = ((point.x() - line_start.x()) * dx + (point.y() - line_start.y()) * dy) / length_sq
        return QPointF(line_start.x() + t * dx, line_start.y() + t * dy)

    @staticmethod
    def _point_on_segment(p: QPointF, t: float) -> QPointF:
        """Возвращает точку на отрезке [QPointF(0,0), p] с параметром t."""
        return QPointF(p.x() * t, p.y() * t)

    def _compute_auxiliary_lines(self) -> list[tuple[QPointF, QPointF, str, QColor]]:
        """Вычисляет вспомогательные линии.

        Возвращает список кортежей: (начало, конец, метка, цвет)
        """
        if len(self._vertices) < 3:
            return []

        result = []
        v = self._vertices  # [A, B, C]
        vi = self._vertex_index % 3  # индекс вершины, из которой проводим линии

        # Противоположная сторона: вершины после vi
        v1 = self._vertices[(vi + 1) % 3]
        v2 = self._vertices[(vi + 2) % 3]

        # --- Высота ---
        if self._draw_height:
            foot = self._project_point_to_line(v[vi], v1, v2)
            color = QColor(255, 0, 0)  # Красный
            result.append((v[vi], foot, "H", color))

        # --- Медиана ---
        if self._draw_median:
            mid = QPointF((v1.x() + v2.x()) / 2, (v1.y() + v2.y()) / 2)
            color = QColor(0, 120, 255)  # Синий
            result.append((v[vi], mid, "M", color))

        # --- Биссектриса ---
        if self._draw_bisector:
            # Делим противоположную сторону в отношении длин прилежащих сторон
            len_ab = math.sqrt((v[vi].x() - v1.x()) ** 2 + (v[vi].y() - v1.y()) ** 2)
            len_ac = math.sqrt((v[vi].x() - v2.x()) ** 2 + (v[vi].y() - v2.y()) ** 2)
            total = len_ab + len_ac
            if total > 1e-10:
                t = len_ac / total
                bisector_point = QPointF(
                    v1.x() + t * (v2.x() - v1.x()),
                    v1.y() + t * (v2.y() - v1.y()),
                )
                color = QColor(0, 180, 0)  # Зелёный
                result.append((v[vi], bisector_point, "B", color))

        return result

    def _draw_auxiliary_lines(self, painter: QPainter) -> None:
        """Рисует вспомогательные линии и их точки пересечения."""
        aux_lines = self._compute_auxiliary_lines()

        font = QFont()
        font.setFamily("Arial")
        font.setPointSizeF(9)
        painter.setFont(font)

        for start, end, label, color in aux_lines:
            # Рисуем линию (пунктир для высоты, сплошная для остальных)
            pen = QPen(color, self.pen_width - 0.5)
            if label == "H":
                pen.setStyle(Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawLine(start, end)

            # Рисуем точку пересечения с противоположной стороной
            painter.setBrush(QBrush(color))
            painter.drawEllipse(end, 3, 3)

            # Рисуем метку со смещением, чтобы не сливалась с точкой
            # Смещаем метку в сторону от центра треугольника
            cx = sum(v.x() for v in self._vertices) / 3
            cy = sum(v.y() for v in self._vertices) / 3
            dx = end.x() - cx
            dy = end.y() - cy
            dist = math.sqrt(dx * dx + dy * dy)
            if dist > 0.01:
                dx /= dist
                dy /= dist
                offset = 10
                mx = end.x() + dx * offset
                my = end.y() + dy * offset
            else:
                mx, my = end.x(), end.y() - 10
            painter.setPen(QPen(color, 1))
            painter.drawText(int(mx - 6), int(my + 4), label)

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

            # Применяем поворот вокруг центра треугольника
            if abs(self._rotation) > 0.01 and len(self._vertices) > 0:
                cx = sum(v.x() for v in self._vertices) / len(self._vertices)
                cy = sum(v.y() for v in self._vertices) / len(self._vertices)
                painter.translate(cx, cy)
                painter.rotate(self._rotation)
                painter.translate(-cx, -cy)

            if len(self._vertices) >= 3:
                polygon = QPolygonF(self._vertices[:3])
                painter.drawPolygon(polygon)

            # Отрисовка маркеров вершин
            pen.setColor(QColor(80, 80, 80))
            pen.setWidth(1)
            painter.setPen(pen)
            painter.setBrush(QBrush(QColor(255, 255, 255)))
            for v in self._vertices:
                painter.drawEllipse(v, 3, 3)

            # Подпись вершин
            self._draw_vertex_labels(painter)

            # Вспомогательные линии
            self._draw_auxiliary_lines(painter)

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
        """Отрисовать подписи вершин (A, B, C)."""
        if not self._vertices:
            return

        # Вычисляем центр треугольника
        cx = sum(v.x() for v in self._vertices) / 3
        cy = sum(v.y() for v in self._vertices) / 3

        font = QFont()
        font.setFamily("Arial")
        font.setPointSizeF(9)
        painter.setFont(font)
        painter.setPen(QColor(50, 50, 50))

        offset = 16

        for i, v in enumerate(self._vertices):
            # Направление от центра к вершине
            dx = v.x() - cx
            dy = v.y() - cy
            dist = math.sqrt(dx * dx + dy * dy)
            if dist < 0.01:
                continue
            dx /= dist
            dy /= dist

            label_x = v.x() + dx * offset
            label_y = v.y() + dy * offset

            # Рисуем текст по центру в прямоугольнике
            text_rect = QRectF(label_x - 10, label_y - 10, 20, 20)
            painter.drawText(
                text_rect,
                Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter,
                self._labels[i],
            )

    def contains_point(self, point: QPointF) -> bool:
        # Проверка точки в треугольнике (barycentric coordinates)
        p1 = self._vertices[0]
        p2 = self._vertices[1]
        p3 = self._vertices[2]

        def sign(p, a, b):
            return (p.x() - b.x()) * (a.y() - b.y()) - (a.x() - b.x()) * (p.y() - b.y())

        d1 = sign(point, p1, p2)
        d2 = sign(point, p2, p3)
        d3 = sign(point, p3, p1)

        has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
        has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)

        return not (has_neg and has_pos)

    def move(self, dx: float, dy: float) -> None:
        for v in self._vertices:
            v.setX(v.x() + dx)
            v.setY(v.y() + dy)

    def rotate(self, angle: float, center: QPointF | None = None) -> None:
        if center is None:
            cx = sum(v.x() for v in self._vertices) / 3
            cy = sum(v.y() for v in self._vertices) / 3
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
            cx = sum(v.x() for v in self._vertices) / 3
            cy = sum(v.y() for v in self._vertices) / 3
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
                # HandleType для вершин: TOP_LEFT=2, TOP_RIGHT=3, BOTTOM_LEFT=4
                if i == 0:
                    return HandleType.TOP_LEFT
                elif i == 1:
                    return HandleType.BOTTOM_RIGHT
                else:
                    return HandleType.TOP_CENTER
        return HandleType.NONE

    def apply_handle_transform(
        self, handle: HandleType, point: QPointF, mouse_pos: QPointF, shift_pressed: bool = False
    ) -> None:
        """При ресайзе — двигаем только активную вершину."""
        if handle == HandleType.MOVE:
            dx = mouse_pos.x() - point.x()
            dy = mouse_pos.y() - point.y()
            for v in self._vertices:
                v.setX(v.x() + dx)
                v.setY(v.y() + dy)
            return
        # Двигаем только активную вершину
        if handle == HandleType.TOP_LEFT:
            self._vertices[0].setX(mouse_pos.x())
            self._vertices[0].setY(mouse_pos.y())
        elif handle == HandleType.BOTTOM_RIGHT:
            self._vertices[1].setX(mouse_pos.x())
            self._vertices[1].setY(mouse_pos.y())
        elif handle == HandleType.TOP_CENTER:
            self._vertices[2].setX(mouse_pos.x())
            self._vertices[2].setY(mouse_pos.y())

    def _handle_positions(self) -> list[tuple[float, float]]:
        return [(v.x(), v.y()) for v in self._vertices]

    # ------------------------------------------------------------------
    # Свойства для панели
    # ------------------------------------------------------------------

    def get_properties(self) -> dict:
        d = super().get_properties()
        d["_shape_type"] = self.shape_type.value
        d["_triangle_type"] = self._triangle_type
        d["_side_a"] = self._side_a
        d["_side_b"] = self._side_b
        d["_height"] = self._height
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

        # Обновляем параметры треугольника
        if "_side_a" in properties:
            self._side_a = properties["_side_a"]
        if "_side_b" in properties:
            self._side_b = properties["_side_b"]
        if "_height" in properties:
            self._height = properties["_height"]
        if "_angle_deg" in properties:
            self._angle_deg = properties["_angle_deg"]

        # Перестраиваем вершины
        self._rebuild_vertices()

    def _rebuild_vertices(self) -> None:
        """Перестроить вершины на основе параметров."""
        if self._triangle_type == "equilateral":
            raw = self.build_equilateral(self._side_a)
        elif self._triangle_type == "isosceles":
            raw = self.build_isosceles(self._side_a, self._height)
        elif self._triangle_type == "right":
            raw = self.build_right(self._side_a, self._side_b)
        elif self._triangle_type == "obtuse":
            raw = self.build_obtuse(self._side_a, self._side_b, self._angle_deg)
        else:
            return

        centered = self.center_vertices(raw)
        centered = self.flip_y(centered)  # Вершина вверх
        centered = self.order_vertices_clockwise(centered)  # A=левый нижний, по часовой стрелке
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
                "triangle_type": self._triangle_type,
                "side_a": self._side_a,
                "side_b": self._side_b,
                "height": self._height,
                "angle_deg": self._angle_deg,
                "draw_height": self._draw_height,
                "draw_median": self._draw_median,
                "draw_bisector": self._draw_bisector,
                "vertex_index": self._vertex_index,
                "vertices": [{"x": v.x(), "y": v.y()} for v in self._vertices],
            }
        )
        return d

    @classmethod
    def from_dict(cls, data: dict) -> TriangleShape:
        vertices_data = data.get("vertices", [])
        vertices = (
            [(v["x"], v["y"]) for v in vertices_data]
            if vertices_data
            else cls.center_vertices(cls.build_equilateral(data.get("side_a", 100)))
        )

        obj = cls(
            vertices=vertices,
            triangle_type=data.get("triangle_type", "equilateral"),
            side_a=data.get("side_a", 100),
            side_b=data.get("side_b", 100),
            height=data.get("height", 86.6),
            angle_deg=data.get("angle_deg", 60),
            pen_color=data["pen_color"],
            brush_color=data.get("brush_color"),
            pen_width=data.get("pen_width", 2.0),
            draw_height=data.get("draw_height", True),
            draw_median=data.get("draw_median", False),
            draw_bisector=data.get("draw_bisector", False),
            vertex_index=data.get("vertex_index", 0),
        )
        obj._selected = data.get("selected", False)
        obj._rotation = data.get("rotation", 0.0)
        return obj
