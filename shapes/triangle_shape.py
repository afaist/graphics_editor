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
        draw_height: bool = False,
        draw_median: bool = False,
        draw_bisector: bool = False,
        vertex_index: int = 0,
        # Окружности
        draw_circumscribed: bool = False,
        draw_inscribed: bool = False,
        # Размеры углов
        draw_angles: bool = False,
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

        # Окружности
        self._draw_circumscribed = draw_circumscribed
        self._draw_inscribed = draw_inscribed
        self._circumcenter: QPointF | None = None
        self._incenter: QPointF | None = None
        self._circumradius: float = 0.0
        self._inradius: float = 0.0
        self._compute_circles()

        # Размеры углов
        self._draw_angles = draw_angles

    # ------------------------------------------------------------------
    # Abstract methods (базовые)
    # ------------------------------------------------------------------

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
    # Вычисление окружностей
    # ------------------------------------------------------------------

    def _compute_circles(self) -> None:
        """Вычисляет центр и радиус описанной и вписанной окружностей."""
        if len(self._vertices) < 3:
            return

        A, B, C = self._vertices[0], self._vertices[1], self._vertices[2]

        # --- Описанная окружность ---
        # Центр описанной окружности — пересечение серединных перпендикуляров
        self._circumcenter, self._circumradius = self._compute_circumcircle(A, B, C)

        # --- Вписанная окружность ---
        # Центр вписанной окружности — пересечение биссектрис
        self._incenter, self._inradius = self._compute_incircle(A, B, C)

    @staticmethod
    def _compute_circumcircle(A: QPointF, B: QPointF, C: QPointF) -> tuple[QPointF, float]:
        """Вычисляет центр и радиус описанной окружности.

        Использует решение системы уравнений: центр равноудалён от всех вершин.
        """
        # Система уравнений:
        # 2*(B.x - A.x)*cx + 2*(B.y - A.y)*cy = B.x² + B.y² - A.x² - A.y²
        # 2*(C.x - A.x)*cx + 2*(C.y - A.y)*cy = C.x² + C.y² - A.x² - A.y²
        dx1 = 2 * (B.x() - A.x())
        dy1 = 2 * (B.y() - A.y())
        dx2 = 2 * (C.x() - A.x())
        dy2 = 2 * (C.y() - A.y())

        rhs1 = B.x() ** 2 + B.y() ** 2 - A.x() ** 2 - A.y() ** 2
        rhs2 = C.x() ** 2 + C.y() ** 2 - A.x() ** 2 - A.y() ** 2

        # Определитель
        det = dx1 * dy2 - dy1 * dx2
        if abs(det) < 1e-10:
            # Треугольник вырожденный
            return QPointF((A.x() + B.x() + C.x()) / 3, (A.y() + B.y() + C.y()) / 3), 0.0

        cx = (rhs1 * dy2 - rhs2 * dy1) / det
        cy = (dx1 * rhs2 - dx2 * rhs1) / det

        circumcenter = QPointF(cx, cy)
        radius = math.sqrt((cx - A.x()) ** 2 + (cy - A.y()) ** 2)
        return circumcenter, radius

    @staticmethod
    def _compute_incircle(A: QPointF, B: QPointF, C: QPointF) -> tuple[QPointF, float]:
        """Вычисляет центр и радиус вписанной окружности."""
        a = math.sqrt((B.x() - C.x()) ** 2 + (B.y() - C.y()) ** 2)
        b = math.sqrt((A.x() - C.x()) ** 2 + (A.y() - C.y()) ** 2)
        c = math.sqrt((A.x() - B.x()) ** 2 + (A.y() - B.y()) ** 2)

        perimeter = a + b + c
        if perimeter < 1e-10:
            return QPointF((A.x() + B.x() + C.x()) / 3, (A.y() + B.y() + C.y()) / 3), 0.0

        # Центр вписанной окружности
        incenter = QPointF(
            (a * A.x() + b * B.x() + c * C.x()) / perimeter,
            (a * A.y() + b * B.y() + c * C.y()) / perimeter,
        )

        # Площадь треугольника (формула Герона)
        s = perimeter / 2
        area_sq = s * (s - a) * (s - b) * (s - c)
        if area_sq < 0:
            area_sq = 0
        area = math.sqrt(area_sq)

        if area < 1e-10:
            return incenter, 0.0

        # Радиус вписанной окружности
        inradius = area / s
        return incenter, inradius

    # ------------------------------------------------------------------
    # Вспомогательные линии (высота, медиана, биссектриса)
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

    @property
    def draw_circumscribed(self) -> bool:
        return self._draw_circumscribed

    @draw_circumscribed.setter
    def draw_circumscribed(self, value: bool) -> None:
        self._draw_circumscribed = value

    @property
    def draw_inscribed(self) -> bool:
        return self._draw_inscribed

    @draw_inscribed.setter
    def draw_inscribed(self, value: bool) -> None:
        self._draw_inscribed = value

    @property
    def draw_angles(self) -> bool:
        return self._draw_angles

    @draw_angles.setter
    def draw_angles(self, value: bool) -> None:
        self._draw_angles = value

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
                t = len_ab / total
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
    # Отрисовка окружностей
    # ------------------------------------------------------------------

    def _draw_circumscribed_circle(self, painter: QPainter) -> None:
        """Рисует описанную окружность с серединными перпендикулярами."""
        if self._circumcenter is None or self._circumradius < 1e-5:
            return

        A, B, C = self._vertices[0], self._vertices[1], self._vertices[2]

        # Серединные перпендикуляры (тонкий пунктир, от стороны до центра)
        perp_color = QColor(255, 165, 0, 120)
        perp_pen = QPen(perp_color, 1.0)
        perp_pen.setStyle(Qt.PenStyle.DashLine)
        painter.setPen(perp_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        # Рисуем серединные перпендикуляры от середины стороны до центра
        self._draw_perpendicular_to_center(painter, A, B, self._circumcenter)
        self._draw_perpendicular_to_center(painter, B, C, self._circumcenter)
        self._draw_perpendicular_to_center(painter, A, C, self._circumcenter)

        # Описанная окружность (синий)
        circle_color = QColor(0, 100, 255)
        circle_pen = QPen(circle_color, self.pen_width)
        painter.setPen(circle_pen)
        painter.drawEllipse(self._circumcenter, self._circumradius, self._circumradius)

        # Центр окружности O
        painter.setBrush(QBrush(circle_color))
        painter.drawEllipse(self._circumcenter, 4, 4)
        font = QFont()
        font.setFamily("Arial")
        font.setPointSizeF(12)
        painter.setFont(font)
        painter.setPen(QPen(circle_color, 1))
        painter.drawText(
            int(self._circumcenter.x() + 6),
            int(self._circumcenter.y() - 6),
            "O",
        )

    def _draw_inscribed_circle(self, painter: QPainter) -> None:
        """Рисует вписанную окружность с биссектрисами."""
        if self._incenter is None or self._inradius < 1e-5:
            return

        A, B, C = self._vertices[0], self._vertices[1], self._vertices[2]

        # Биссектрисы (тонкий пунктир)
        bisector_color = QColor(0, 180, 0, 120)
        bisector_pen = QPen(bisector_color, 1.0)
        bisector_pen.setStyle(Qt.PenStyle.DashLine)
        painter.setPen(bisector_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        # Рисуем биссектрисы от вершины до противоположной стороны
        self._draw_angle_bisector(painter, A, B, C)
        self._draw_angle_bisector(painter, B, A, C)
        self._draw_angle_bisector(painter, C, A, B)

        # Вписанная окружность (красный)
        circle_color = QColor(255, 50, 50)
        circle_pen = QPen(circle_color, self.pen_width)
        painter.setPen(circle_pen)
        painter.drawEllipse(self._incenter, self._inradius, self._inradius)

        # Центр окружности O
        painter.setBrush(QBrush(circle_color))
        painter.drawEllipse(self._incenter, 4, 4)
        font = QFont()
        font.setFamily("Arial")
        font.setPointSizeF(10)
        painter.setFont(font)
        painter.setPen(QPen(circle_color, 1))
        painter.drawText(
            int(self._incenter.x() + 6),
            int(self._incenter.y() - 6),
            "O",
        )

    def _draw_perpendicular_to_center(
        self, painter: QPainter, A: QPointF, B: QPointF, center: QPointF
    ) -> None:
        """Рисует серединный перпендикуляр от середины стороны до центра окружности."""
        mid = QPointF((A.x() + B.x()) / 2, (A.y() + B.y()) / 2)

        # Рисуем линию от середины стороны до центра
        painter.drawLine(mid, center)

        # Маркер прямого угла (маленький квадратик) в середине стороны
        self._draw_right_angle_marker(painter, mid, A, B, 6)

    def _draw_angle_bisector(
        self, painter: QPainter, vertex: QPointF, p1: QPointF, p2: QPointF
    ) -> None:
        """Рисует биссектрису от вершины до противоположной стороны."""
        # Направления к другим вершинам
        d1x = p1.x() - vertex.x()
        d1y = p1.y() - vertex.y()
        d2x = p2.x() - vertex.x()
        d2y = p2.y() - vertex.y()

        len1 = math.sqrt(d1x * d1x + d1y * d1y)
        len2 = math.sqrt(d2x * d2x + d2y * d2y)

        if len1 < 1e-10 or len2 < 1e-10:
            return

        # Нормализованные направления
        n1x, n1y = d1x / len1, d1y / len1
        n2x, n2y = d2x / len2, d2y / len2

        # Биссектриса — сумма единичных векторов
        bx = n1x + n2x
        by = n1y + n2y
        blen = math.sqrt(bx * bx + by * by)

        if blen < 1e-10:
            return

        bx, by = bx / blen, by / blen

        # Находим точку пересечения с отрезком p1-p2
        intersect = self._line_segment_intersect(vertex, bx, by, p1, p2)
        if intersect is None:
            # Если не нашли пересечение, рисуем до ближайшей стороны
            d_to_p1 = math.sqrt((p1.x() - vertex.x()) ** 2 + (p1.y() - vertex.y()) ** 2)
            d_to_p2 = math.sqrt((p2.x() - vertex.x()) ** 2 + (p2.y() - vertex.y()) ** 2)
            min_dist = min(d_to_p1, d_to_p2) * 0.9
            intersect = QPointF(
                vertex.x() + bx * min_dist,
                vertex.y() + by * min_dist,
            )

        painter.drawLine(vertex, intersect)

    @staticmethod
    def _line_segment_intersect(
        origin: QPointF,
        dx: float,
        dy: float,
        p1: QPointF,
        p2: QPointF,
    ) -> QPointF | None:
        """Находит точку пересечения луча с отрезком."""
        ex = p2.x() - p1.x()
        ey = p2.y() - p1.y()
        denom = dx * ey - dy * ex

        if abs(denom) < 1e-10:
            return None

        t = ((p1.x() - origin.x()) * ey - (p1.y() - origin.y()) * ex) / denom
        if t < 0:
            return None

        u = ((p1.x() - origin.x()) * dy - (p1.y() - origin.y()) * dx) / denom
        if u < 0 or u > 1:
            return None

        return QPointF(origin.x() + t * dx, origin.y() + t * dy)

    def _draw_right_angle_marker(
        self, painter: QPainter, vertex: QPointF, p1: QPointF, p2: QPointF, size: float = 6
    ) -> None:
        """Рисует маркер прямого угла (L-образный) в точке vertex."""
        # Направления от vertex к концам отрезка p1-p2
        d1x = p1.x() - vertex.x()
        d1y = p1.y() - vertex.y()
        d2x = p2.x() - vertex.x()
        d2y = p2.y() - vertex.y()

        len1 = math.sqrt(d1x * d1x + d1y * d1y)
        len2 = math.sqrt(d2x * d2x + d2y * d2y)

        if len1 < 1e-10 or len2 < 1e-10:
            return

        # Единичные векторы вдоль сторон
        u1x, u1y = d1x / len1, d1y / len1
        u2x, u2y = d2x / len2, d2y / len2

        # Точки L-образного маркера
        p_a = QPointF(vertex.x() + u1x * size, vertex.y() + u1y * size)
        p_b = QPointF(p_a.x() + u2x * size, p_a.y() + u2y * size)
        p_c = QPointF(vertex.x() + u2x * size, vertex.y() + u2y * size)

        # Рисуем L-образный маркер
        color = QColor(255, 165, 0, 180)
        pen = QPen(color, 1.0)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawLine(vertex, p_a)
        painter.drawLine(p_a, p_b)
        painter.drawLine(p_b, p_c)

    def _draw_equal_angle_marker(
        self, painter: QPainter, vertex: QPointF, p1: QPointF, p2: QPointF, bisector_end: QPointF
    ) -> None:
        """Рисует маркер равных углов (две дуги) у вершины."""
        radius = 12

        # Углы между сторонами и биссектрисой
        angle_p1 = math.atan2(p1.y() - vertex.y(), p1.x() - vertex.x())
        angle_p2 = math.atan2(p2.y() - vertex.y(), p2.x() - vertex.x())
        angle_bis = math.atan2(bisector_end.y() - vertex.y(), bisector_end.x() - vertex.x())

        # Рисуем две дуги
        color = QColor(0, 180, 0, 180)
        pen = QPen(color, 1.0)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        # Дуга 1: от p1 до bisector
        rect = QRectF(
            vertex.x() - radius,
            vertex.y() - radius,
            radius * 2,
            radius * 2,
        )
        start_angle1 = int(math.degrees(angle_p1) * 16)
        end_angle1 = int(math.degrees(angle_bis) * 16)
        painter.drawArc(rect, start_angle1, end_angle1 - start_angle1)

        # Дуга 2: от bisector до p2
        start_angle2 = int(math.degrees(angle_bis) * 16)
        end_angle2 = int(math.degrees(angle_p2) * 16)
        painter.drawArc(rect, start_angle2, end_angle2 - start_angle2)

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

            # Окружности
            if self._draw_circumscribed:
                self._draw_circumscribed_circle(painter)
            if self._draw_inscribed:
                self._draw_inscribed_circle(painter)

            # Размеры углов
            if self._draw_angles:
                self._draw_angle_measures(painter)

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
            self._compute_circles()
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
        # Пересчитываем окружности при изменении вершин
        self._compute_circles()

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
    # Отрисовка размеров углов
    # ------------------------------------------------------------------

    @staticmethod
    def _compute_angle(vertex: QPointF, p1: QPointF, p2: QPointF) -> float:
        """Вычисляет угол в градусах между векторами vertex->p1 и vertex->p2."""
        v1x, v1y = p1.x() - vertex.x(), p1.y() - vertex.y()
        v2x, v2y = p2.x() - vertex.x(), p2.y() - vertex.y()

        dot = v1x * v2x + v1y * v2y
        mag1 = math.sqrt(v1x * v1x + v1y * v1y)
        mag2 = math.sqrt(v2x * v2x + v2y * v2y)

        if mag1 < 1e-10 or mag2 < 1e-10:
            return 0.0

        cos_angle = dot / (mag1 * mag2)
        # Защита от численных ошибок
        cos_angle = max(-1.0, min(1.0, cos_angle))
        return math.degrees(math.acos(cos_angle))

    def _draw_angle_measures(self, painter: QPainter) -> None:
        """Рисует дуги и градусные меры углов в вершинах."""
        if len(self._vertices) < 3:
            return

        A, B, C = self._vertices[0], self._vertices[1], self._vertices[2]

        # Углы в вершинах A, B, C
        angles_info = [
            (A, B, C, "A"),
            (B, A, C, "B"),
            (C, A, B, "C"),
        ]

        font = QFont()
        font.setFamily("Arial")
        font.setPointSizeF(8)
        painter.setFont(font)

        for vertex, p1, p2, label in angles_info:
            angle_deg = self._compute_angle(vertex, p1, p2)

            # Векторы от вершины к другим точкам
            v1x, v1y = p1.x() - vertex.x(), p1.y() - vertex.y()
            v2x, v2y = p2.x() - vertex.x(), p2.y() - vertex.y()

            # Углы сторон в радианах (относительно оси X)
            angle_p1 = math.atan2(-v1y, v1x)  # инвертируем Y для Qt
            angle_p2 = math.atan2(-v2y, v2x)

            # Разница углов в градусах
            angle_diff_deg = math.degrees(angle_p2 - angle_p1)

            # Нормализуем в [-180, 180]
            while angle_diff_deg > 180:
                angle_diff_deg -= 360
            while angle_diff_deg < -180:
                angle_diff_deg += 360

            # Углы в формате Qt (1/16 градуса)
            start_16 = int(math.degrees(angle_p1) * 16)
            span_16 = int(angle_diff_deg * 16)

            radius = 20
            text_radius = radius + 14

            # Рисуем дугу
            angle_color = QColor(100, 100, 100, 180)
            pen = QPen(angle_color, 1.0)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)

            rect = QRectF(
                vertex.x() - radius,
                vertex.y() - radius,
                radius * 2,
                radius * 2,
            )
            painter.drawArc(rect, start_16, span_16)

            # Рисуем текст с градусной мерой
            # Средний угол для размещения текста
            mid_angle_deg = math.degrees(angle_p1) + angle_diff_deg / 2
            text_x = vertex.x() + math.cos(math.radians(mid_angle_deg)) * text_radius
            text_y = vertex.y() - math.sin(math.radians(mid_angle_deg)) * text_radius

            angle_text = f"{angle_deg:.1f}°"
            painter.setPen(QPen(angle_color, 1))
            painter.drawText(
                int(text_x - 15),
                int(text_y - 6),
                30,
                12,
                Qt.AlignmentFlag.AlignCenter,
                angle_text,
            )

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
                "draw_circumscribed": self._draw_circumscribed,
                "draw_inscribed": self._draw_inscribed,
                "draw_angles": self._draw_angles,
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
            draw_height=data.get("draw_height", False),
            draw_median=data.get("draw_median", False),
            draw_bisector=data.get("draw_bisector", False),
            vertex_index=data.get("vertex_index", 0),
            draw_circumscribed=data.get("draw_circumscribed", False),
            draw_inscribed=data.get("draw_inscribed", False),
            draw_angles=data.get("draw_angles", False),
        )
        obj._selected = data.get("selected", False)
        obj._rotation = data.get("rotation", 0.0)
        return obj
