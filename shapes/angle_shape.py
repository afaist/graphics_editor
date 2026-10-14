"""Фигура: Угол (два отрезка из общей вершины под заданным углом)."""

from __future__ import annotations

import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPen

from .base_shape import BaseShape, HandleType, ShapeType


class AngleShape(BaseShape):
    """Угол — два отрезка, выходящих из общей вершины.

    Параметры:
        vertex: общая вершина угла
        side_a: длина первой стороны (горизонтально вправо от вершины)
        side_b: длина второй стороны
        angle_deg: угол между сторонами в градусах (0..360)

    Геометрия (координатная система Qt, Y вниз):
        - Первая сторона: горизонтально вправо от вершины
        - Вторая сторона: под углом angle_deg против часовой стрелки
          (в Qt Y вниз это отрицательный угол atan2)
    """

    def __init__(
        self,
        vertex: tuple[float, float],
        side_a: float,
        side_b: float,
        angle_deg: float,
        pen_color: tuple[int, int, int] = (0, 0, 0),
        pen_width: float = 2.0,
        brush_color: tuple[int, int, int] | None = None,
        selected: bool = False,
        angle_type: str = "single",  # NEW
        side_c: float = 100.0,  # NEW
        parallel_distance: float = 100.0,  # NEW
    ):
        super().__init__(pen_color, pen_width, brush_color, selected)
        self._vertex = QPointF(vertex[0], vertex[1])
        self._side_a = max(side_a, 0.1)
        self._side_b = max(side_b, 0.1)
        self._angle_deg = angle_deg % 360.0
        # НЕТ таких строк:
        self._angle_type = angle_type
        self._side_c = side_c
        self._parallel_distance = parallel_distance

    def _get_shape_type(self) -> ShapeType:
        return ShapeType.ANGLE

    def set_end_point(self, x: float, y: float) -> None:
        pass

    def set_size(self, width: float, height: float) -> None:
        pass

    def add_vertex(self, x: float, y: float) -> None:
        pass

    @property
    def angle_type(self) -> str:
        return self._angle_type

    @property
    def side_c(self) -> float:
        return self._side_c

    @property
    def parallel_distance(self) -> float:
        return self._parallel_distance

    # ------------------------------------------------------------------
    # Вычисляемые координаты
    # ------------------------------------------------------------------

    @property
    def vertex(self) -> QPointF:
        return self._vertex

    @property
    def side_a(self) -> float:
        return self._side_a

    @property
    def side_b(self) -> float:
        return self._side_b

    @property
    def angle_deg(self) -> float:
        return self._angle_deg

    @side_a.setter  # type: ignore[no-redef]
    def side_a(self, value: float) -> None:
        self._side_a = max(value, 0.1)

    @side_b.setter  # type: ignore[no-redef]
    def side_b(self, value: float) -> None:
        self._side_b = max(value, 0.1)

    @angle_deg.setter  # type: ignore[no-redef]
    def angle_deg(self, value: float) -> None:
        self._angle_deg = value % 360.0

    def end_point_a(self) -> QPointF:
        """Конец первой стороны (горизонтально вправо)."""
        return QPointF(self._vertex.x() + self._side_a, self._vertex.y())

    def end_point_b(self) -> QPointF:
        """Конец второй стороны (под углом angle_deg против ЧС)."""
        rad = math.radians(self._angle_deg)
        # В Qt Y вниз: против часовой стрелки = -rad
        return QPointF(
            self._vertex.x() + self._side_b * math.cos(-rad),
            self._vertex.y() + self._side_b * math.sin(-rad),
        )

    def end_point_c(self) -> QPointF:
        """Конец третьей стороны.

        Для adjacent: горизонтально влево (180° от стороны A, так как A и C образуют прямую).
        Для vertical: противоположна стороне A (горизонтально влево, длина = side_a).
        """
        if self._angle_type == "adjacent":
            # Сторона C горизонтально влево (противоположна A)
            return QPointF(self._vertex.x() - self._side_c, self._vertex.y())
        else:  # vertical
            # Сторона C противоположна A (горизонтально влево)
            return QPointF(self._vertex.x() - self._side_a, self._vertex.y())

    def end_point_d(self) -> QPointF:
        """Конец четвёртой стороны (противоположная второй).

        Для vertical: под углом angle_deg - 180° (или angle_deg + 180°).
        """
        rad = math.radians(self._angle_deg + 180.0)
        return QPointF(
            self._vertex.x() + self._side_b * math.cos(-rad),
            self._vertex.y() + self._side_b * math.sin(-rad),
        )

    def _bisector_angle(self) -> float:
        """Угол биссектрисы (в радианах, система Qt)."""
        return -math.radians(self._angle_deg / 2.0)

    def _bisector_angle_deg(self, angle1: float, angle2: float) -> float:
        """Вычисляет угол биссектрисы между двумя углами в градусах."""
        # Нормализуем углы
        a1 = math.radians(angle1)
        a2 = math.radians(angle2)
        # Биссектриса
        mid = (a1 + a2) / 2.0
        return math.degrees(-mid)  # отрицательный для Qt

    # ------------------------------------------------------------------
    # Абстрактные методы
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

            # Применяем поворот вокруг вершины угла
            if abs(self._rotation) > 0.01:
                painter.translate(self._vertex.x(), self._vertex.y())
                painter.rotate(self._rotation)
                painter.translate(-self._vertex.x(), -self._vertex.y())

            if self._angle_type == "single":
                self._draw_single(painter)
            elif self._angle_type == "adjacent":
                self._draw_adjacent(painter)
            elif self._angle_type == "vertical":
                self._draw_vertical(painter)
            elif self._angle_type == "transversal":
                self._draw_transversal(painter)

            if self._selected:
                pen.setColor(QColor(0, 120, 255))
                pen.setWidth(1)
                painter.setPen(pen)
                painter.setBrush(Qt.BrushStyle.NoBrush)
                for hx, hy in self._handle_positions():
                    painter.drawRect(int(hx) - 4, int(hy) - 4, 8, 8)
        finally:
            painter.restore()

    def _draw_single(self, painter: QPainter) -> None:
        """Рисует обычный угол (2 стороны)."""
        v = self._vertex
        va = self.end_point_a()
        vb = self.end_point_b()
        painter.drawLine(v, va)
        painter.drawLine(v, vb)
        self._draw_annotation(painter, v, va, vb)

    def _draw_adjacent(self, painter: QPainter) -> None:
        """Рисует смежные углы (3 стороны)."""
        v = self._vertex
        va = self.end_point_a()
        vb = self.end_point_b()
        vc = self.end_point_c()
        painter.drawLine(v, va)
        painter.drawLine(v, vb)
        painter.drawLine(v, vc)
        self._draw_annotations_adjacent(painter, v, va, vb, vc)

    def _draw_vertical(self, painter: QPainter) -> None:
        """Рисует вертикальные углы (4 стороны)."""
        v = self._vertex
        va = self.end_point_a()
        vb = self.end_point_b()
        vc = self.end_point_c()
        vd = self.end_point_d()
        painter.drawLine(v, va)
        painter.drawLine(v, vb)
        painter.drawLine(v, vc)
        painter.drawLine(v, vd)
        self._draw_annotations_vertical(painter, v, va, vb, vc, vd)

    def _draw_transversal(self, painter: QPainter) -> None:
        """Рисует трансверсаль (2 параллельные + трансверсаль)."""
        v = self._vertex
        parallel_dist = self._parallel_distance
        angle_rad = math.radians(self._angle_deg)

        # Длина лучей трансверсали
        ray_len = max(self._side_a, self._side_b, parallel_dist * 3)

        # Направление трансверсали
        tx = math.cos(-angle_rad)
        ty = math.sin(-angle_rad)

        # Точки пересечения трансверсали с параллельными
        # Верхняя точка пересечения — это v
        # Нижняя точка пересечения — сдвигаем по направлению трансверсали
        # Расстояние между параллельными = parallel_dist
        # Проекция вектора трансверсали на вертикаль = ty
        # Расстояние вдоль трансверсали = parallel_dist / |ty|
        if abs(ty) > 1e-6:
            t = parallel_dist / ty
        else:
            t = parallel_dist / 0.001  # fallback

        v2 = QPointF(v.x() + t * tx, v.y() + t * ty)  # вторая точка пересечения

        # Длина параллельных прямых (горизонтальных)
        h_len = ray_len * 2

        # Рисуем параллельные прямые
        pen = QPen(self.pen_color, self.pen_width)
        painter.setPen(pen)

        # Верхняя параллельная
        painter.drawLine(
            QPointF(v.x() - h_len, v.y()),
            QPointF(v.x() + h_len, v.y()),
        )

        # Нижняя параллельная
        painter.drawLine(
            QPointF(v2.x() - h_len, v2.y()),
            QPointF(v2.x() + h_len, v2.y()),
        )

        # Рисуем трансверсаль
        painter.drawLine(
            QPointF(v.x() - ray_len * tx, v.y() - ray_len * ty),
            QPointF(v.x() + ray_len * tx, v.y() + ray_len * ty),
        )

        # Рисуем аннотации для 8 углов
        self._draw_annotations_transversal(painter, v, v2, tx, ty)

        # Рисуем выделенные ручки
        if self._selected:
            pen.setColor(QColor(0, 120, 255))
            pen.setWidth(1)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            for hx, hy in self._handle_positions():
                painter.drawRect(int(hx) - 4, int(hy) - 4, 8, 8)

    def _draw_annotations_adjacent(
        self, painter: QPainter, v: QPointF, va: QPointF, vb: QPointF, vc: QPointF
    ) -> None:
        """Рисует аннотации для смежных углов (α + β = 180°)."""
        # Угол α между сторонами va и vb
        arc_radius = min(self._side_a, self._side_b, self._side_c) * 0.35
        arc_radius = max(arc_radius, 15.0)
        arc_radius = min(arc_radius, 60.0)

        # Первый угол α
        start_16 = 0
        span_16 = int(self._angle_deg * 16)
        rect = QRectF(
            v.x() - arc_radius,
            v.y() - arc_radius,
            arc_radius * 2,
            arc_radius * 2,
        )
        arc_pen = QPen(QColor(120, 120, 120), 1.0)
        painter.setPen(arc_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawArc(rect, start_16, span_16)

        # Текст для α
        text_radius = arc_radius * 1.5
        bis_rad = self._bisector_angle()
        tx = v.x() + text_radius * math.cos(bis_rad)
        ty = v.y() + text_radius * math.sin(bis_rad)
        angle_text = f"{self._angle_deg:.1f}°"
        font = QFont()
        font.setFamily("Arial")
        font.setPointSizeF(9)
        painter.setFont(font)
        painter.setPen(QColor(80, 80, 80))
        text_rect = QRectF(tx - 18, ty - 8, 36, 16)
        painter.drawText(
            text_rect,
            Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter,
            angle_text,
        )

        # Второй угол β = 180° - α
        beta_deg = 180.0 - self._angle_deg
        # Дуга для β между vb и vc
        # Угол vb = angle_deg, угол vc = 180°
        # В Qt Y-down: negative angles
        start_16_beta = int(self._angle_deg * 16)
        span_16_beta = int(beta_deg * 16)
        painter.drawArc(rect, start_16_beta, span_16_beta)

        # Текст для β
        # Биссектриса между стороной B (angle_deg) и стороной C (180°)
        bis_beta = -math.radians((180.0 + self._angle_deg) / 2.0)
        tx2 = v.x() + text_radius * math.cos(bis_beta)
        ty2 = v.y() + text_radius * math.sin(bis_beta)
        angle_text2 = f"{beta_deg:.1f}°"
        text_rect2 = QRectF(tx2 - 18, ty2 - 8, 36, 16)
        painter.drawText(
            text_rect2,
            Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter,
            angle_text2,
        )

    def _draw_annotations_vertical(
        self, painter: QPainter, v: QPointF, va: QPointF, vb: QPointF, vc: QPointF, vd: QPointF
    ) -> None:
        """Рисует аннотации для вертикальных углов (α = γ, β = δ)."""
        arc_radius = min(self._side_a, self._side_b, self._side_c) * 0.35
        arc_radius = max(arc_radius, 15.0)
        arc_radius = min(arc_radius, 60.0)

        rect = QRectF(
            v.x() - arc_radius,
            v.y() - arc_radius,
            arc_radius * 2,
            arc_radius * 2,
        )
        arc_pen = QPen(QColor(120, 120, 120), 1.0)
        painter.setPen(arc_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        # Угол α между va и vb
        start_16 = 0
        span_16 = int(self._angle_deg * 16)
        painter.drawArc(rect, start_16, span_16)

        # Текст для α
        text_radius = arc_radius * 1.5
        bis_rad = self._bisector_angle()
        tx = v.x() + text_radius * math.cos(bis_rad)
        ty = v.y() + text_radius * math.sin(bis_rad)
        angle_text = f"{self._angle_deg:.1f}°"
        font = QFont()
        font.setFamily("Arial")
        font.setPointSizeF(9)
        painter.setFont(font)
        painter.setPen(QColor(80, 80, 80))
        text_rect = QRectF(tx - 18, ty - 8, 36, 16)
        painter.drawText(
            text_rect,
            Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter,
            angle_text,
        )

        # Угол γ (вертикальный к α) между vc и vd
        # vc горизонтально влево (180°), vd под углом angle_deg + 180°
        start_16_gamma = 180 * 16  # сторона C горизонтально влево
        painter.drawArc(rect, start_16_gamma, span_16)

        # Текст для γ — биссектриса противоположна биссектрисе α (+180°)
        bis_gamma = bis_rad + math.pi
        tx2 = v.x() + text_radius * math.cos(bis_gamma)
        ty2 = v.y() + text_radius * math.sin(bis_gamma)
        text_rect2 = QRectF(tx2 - 18, ty2 - 8, 36, 16)
        painter.drawText(
            text_rect2,
            Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter,
            angle_text,
        )

    def _draw_annotations_transversal(
        self, painter: QPainter, v1: QPointF, v2: QPointF, tx_dir: float, ty_dir: float
    ) -> None:
        """Рисует аннотации для 8 углов трансверсали.

        В каждой точке пересечения образуется 4 угла.
        Всего 8 углов: 4 в v1 и 4 в v2.
        """
        arc_radius = 25.0  # фиксированный радиус для дуг
        font = QFont()
        font.setFamily("Arial")
        font.setPointSizeF(8)

        # Направление трансверсали
        angle_rad = math.atan2(-ty_dir, tx_dir)
        angle_deg = math.degrees(angle_rad)

        # --- Точка пересечения v1 (верхняя) ---
        # 4 угла: α1, α2, α3, α4
        # Углы между горизонталью (0°) и трансверсалью (angle_deg)
        arc_pen = QPen(QColor(120, 120, 120), 1.0)
        painter.setPen(arc_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        # Угол 1: между горизонталью вправо и трансверсалью вниз
        if angle_deg > 0:
            start_16_1 = 0
            span_16_1 = int(angle_deg * 16)
        else:
            start_16_1 = int(angle_deg * 16)
            span_16_1 = int(-angle_deg * 16)

        rect1 = QRectF(v1.x() - arc_radius, v1.y() - arc_radius, arc_radius * 2, arc_radius * 2)
        painter.drawArc(rect1, start_16_1, span_16_1)

        # Текст для угла 1
        mid_angle_1 = angle_deg / 2.0
        text_r = arc_radius * 1.4
        tx_text = v1.x() + text_r * math.cos(math.radians(-mid_angle_1))
        ty_text = v1.y() + text_r * math.sin(math.radians(-mid_angle_1))
        angle_text = f"{abs(angle_deg):.0f}°"
        painter.setFont(font)
        painter.setPen(QColor(80, 80, 80))
        text_rect = QRectF(tx_text - 15, ty_text - 7, 30, 14)
        painter.drawText(
            text_rect, Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter, angle_text
        )

        # --- Точка пересечения v2 (нижняя) ---
        # Аналогичные углы (соответственные)
        rect2 = QRectF(v2.x() - arc_radius, v2.y() - arc_radius, arc_radius * 2, arc_radius * 2)
        painter.drawArc(rect2, start_16_1, span_16_1)
        painter.drawText(
            text_rect, Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter, angle_text
        )

    def _draw_annotation(self, painter: QPainter, v: QPointF, va: QPointF, vb: QPointF) -> None:
        """Рисует дугу и текст с углом внутри."""
        arc_radius = min(self._side_a, self._side_b) * 0.35
        arc_radius = max(arc_radius, 15.0)
        arc_radius = min(arc_radius, 60.0)

        # Дуга от первой стороны ко второй (внутри угла)
        # Qt drawArc: positive span = clockwise, negative = counter-clockwise
        # Угол рисуется от 3 часов против ЧС (в Qt Y-down это отрицательный угол atan2)
        # Чтобы дуга шла внутри угла (против ЧС), нужен POSITIVE span в drawArc
        arc_pen = QPen(QColor(120, 120, 120), 1.0)
        painter.setPen(arc_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        start_16 = 0  # первая сторона горизонтально вправо = 0°
        span_16 = int(self._angle_deg * 16)  # положительный span = внутри угла
        rect = QRectF(
            v.x() - arc_radius,
            v.y() - arc_radius,
            arc_radius * 2,
            arc_radius * 2,
        )
        painter.drawArc(rect, start_16, span_16)

        # Текст на биссектрисе
        text_radius = arc_radius * 1.5
        bis_rad = self._bisector_angle()
        tx = v.x() + text_radius * math.cos(bis_rad)
        ty = v.y() + text_radius * math.sin(bis_rad)

        angle_text = f"{self._angle_deg:.1f}°"
        font = QFont()
        font.setFamily("Arial")
        font.setPointSizeF(9)
        painter.setFont(font)
        painter.setPen(QColor(80, 80, 80))

        text_rect = QRectF(tx - 18, ty - 8, 36, 16)
        painter.drawText(
            text_rect,
            Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter,
            angle_text,
        )

    def contains_point(self, point: QPointF) -> bool:
        """Проверяет близость точки к любому из двух отрезков."""
        va = self.end_point_a()
        vb = self.end_point_b()
        tolerance = max(self.pen_width / 2 + 4, 6.0)

        return (
            self._point_to_segment_distance(point, self._vertex, va) <= tolerance
            or self._point_to_segment_distance(point, self._vertex, vb) <= tolerance
        )

    @staticmethod
    def _point_to_segment_distance(p: QPointF, a: QPointF, b: QPointF) -> float:
        """Расстояние от точки до отрезка [a, b]."""
        dx = b.x() - a.x()
        dy = b.y() - a.y()
        length_sq = dx * dx + dy * dy

        if length_sq < 1e-10:
            return math.sqrt((p.x() - a.x()) ** 2 + (p.y() - a.y()) ** 2)

        # Проекция на отрезок
        t = ((p.x() - a.x()) * dx + (p.y() - a.y()) * dy) / length_sq
        t = max(0.0, min(1.0, t))

        proj_x = a.x() + t * dx
        proj_y = a.y() + t * dy
        return math.sqrt((p.x() - proj_x) ** 2 + (p.y() - proj_y) ** 2)

    def move(self, dx: float, dy: float) -> None:
        self._vertex.setX(self._vertex.x() + dx)
        self._vertex.setY(self._vertex.y() + dy)

    def rotate(self, angle: float, center: QPointF | None = None) -> None:
        if center is None:
            center = self._vertex
        rad = math.radians(angle)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        self._vertex = QPointF(
            center.x()
            + (self._vertex.x() - center.x()) * cos_a
            - (self._vertex.y() - center.y()) * sin_a,
            center.y()
            + (self._vertex.x() - center.x()) * sin_a
            + (self._vertex.y() - center.y()) * cos_a,
        )

    def scale(self, factor: float, center: QPointF | None = None) -> None:
        self._side_a *= factor
        self._side_b *= factor
        if self._side_a < 0.1:
            self._side_a = 0.1
        if self._side_b < 0.1:
            self._side_b = 0.1

    def bounding_rect(self) -> QRectF:
        v = self._vertex
        va = self.end_point_a()
        vb = self.end_point_b()

        xs = [v.x(), va.x(), vb.x()]
        ys = [v.y(), va.y(), vb.y()]

        if self._angle_type in ("adjacent", "vertical"):
            vc = self.end_point_c()
            xs.append(vc.x())
            ys.append(vc.y())
        if self._angle_type == "vertical":
            vd = self.end_point_d()
            xs.append(vd.x())
            ys.append(vd.y())

        # Для трансверсали нужно учесть параллельные прямые
        if self._angle_type == "transversal":
            parallel_dist = self._parallel_distance
            angle_rad = math.radians(self._angle_deg)
            tx = math.cos(-angle_rad)
            ty = math.sin(-angle_rad)

            if abs(ty) > 1e-6:
                t = parallel_dist / ty
            else:
                t = parallel_dist / 0.001

            v2 = QPointF(v.x() + t * tx, v.y() + t * ty)
            xs.append(v2.x())
            ys.append(v2.y())

            # Параллельные прямые горизонтальные, длина = ray_len * 2
            ray_len = max(self._side_a, self._side_b, parallel_dist * 3)
            h_len = ray_len * 2
            xs.append(v.x() - h_len)
            xs.append(v.x() + h_len)
            xs.append(v2.x() - h_len)
            xs.append(v2.x() + h_len)

        pad = max(self.pen_width / 2 + 8, 10)
        x_min = min(xs) - pad
        y_min = min(ys) - pad
        x_max = max(xs) + pad
        y_max = max(ys) + pad

        return self._safe_rect(x_min, y_min, x_max - x_min, y_max - y_min)

    # ------------------------------------------------------------------
    # Handles
    # ------------------------------------------------------------------

    def _handle_positions(self) -> list[tuple[float, float]]:
        if self._angle_type == "single":
            return [
                (self._vertex.x(), self._vertex.y()),
                (self.end_point_a().x(), self.end_point_a().y()),
                (self.end_point_b().x(), self.end_point_b().y()),
            ]
        elif self._angle_type == "adjacent":
            return [
                (self._vertex.x(), self._vertex.y()),
                (self.end_point_a().x(), self.end_point_a().y()),
                (self.end_point_b().x(), self.end_point_b().y()),
                (self.end_point_c().x(), self.end_point_c().y()),
            ]
        elif self._angle_type == "vertical":
            return [
                (self._vertex.x(), self._vertex.y()),
                (self.end_point_a().x(), self.end_point_a().y()),
                (self.end_point_b().x(), self.end_point_b().y()),
                (self.end_point_c().x(), self.end_point_c().y()),
                (self.end_point_d().x(), self.end_point_d().y()),
            ]
        elif self._angle_type == "transversal":
            return [
                (self._vertex.x(), self._vertex.y()),
                (self.end_point_a().x(), self.end_point_a().y()),
                (self.end_point_b().x(), self.end_point_b().y()),
            ]
        return []

    def get_handles(self) -> list[QPointF]:
        if self._angle_type == "single":
            return [
                self._vertex,
                self.end_point_a(),
                self.end_point_b(),
            ]
        elif self._angle_type == "adjacent":
            return [
                self._vertex,
                self.end_point_a(),
                self.end_point_b(),
                self.end_point_c(),
            ]
        elif self._angle_type == "vertical":
            return [
                self._vertex,
                self.end_point_a(),
                self.end_point_b(),
                self.end_point_c(),
                self.end_point_d(),
            ]
        elif self._angle_type == "transversal":
            return [
                self._vertex,
                self.end_point_a(),
                self.end_point_b(),
            ]
        return []

    def get_handle_type(self, point: QPointF, tolerance: float = 5.0) -> HandleType:
        for i, (hx, hy) in enumerate(self._handle_positions()):
            dx = point.x() - hx
            dy = point.y() - hy
            if math.sqrt(dx * dx + dy * dy) <= tolerance:
                if i == 0:
                    return HandleType.TOP_LEFT
                elif i == 1:
                    return HandleType.BOTTOM_RIGHT
                else:
                    return HandleType.BOTTOM_CENTER
        return HandleType.NONE

    def apply_handle_transform(
        self, handle: HandleType, point: QPointF, mouse_pos: QPointF, shift_pressed: bool = False
    ) -> None:
        if handle == HandleType.TOP_LEFT:
            self._vertex = mouse_pos
        elif handle == HandleType.BOTTOM_RIGHT:
            if self._angle_type == "transversal":
                dx = mouse_pos.x() - self._vertex.x()
                dy = mouse_pos.y() - self._vertex.y()
                self._parallel_distance = max(math.sqrt(dx * dx + dy * dy), 0.1)
            else:
                dx = mouse_pos.x() - self._vertex.x()
                dy = mouse_pos.y() - self._vertex.y()
                self._side_a = max(math.sqrt(dx * dx + dy * dy), 0.1)
        elif handle == HandleType.BOTTOM_CENTER:
            dx = mouse_pos.x() - self._vertex.x()
            dy = mouse_pos.y() - self._vertex.y()
            self._side_b = max(math.sqrt(dx * dx + dy * dy), 0.1)
        elif handle == HandleType.TOP_RIGHT:
            if self._angle_type in ("adjacent", "vertical"):
                dx = mouse_pos.x() - self._vertex.x()
                dy = mouse_pos.y() - self._vertex.y()
                self._side_c = max(math.sqrt(dx * dx + dy * dy), 0.1)
        elif handle == HandleType.TOP_CENTER:
            if self._angle_type == "vertical":
                dx = mouse_pos.x() - self._vertex.x()
                dy = mouse_pos.y() - self._vertex.y()
                self._side_b = max(math.sqrt(dx * dx + dy * dy), 0.1)

    # ------------------------------------------------------------------
    # Позиция для undo
    # ------------------------------------------------------------------

    def get_position_data(self) -> dict:
        data = {
            "vertex_x": self._vertex.x(),
            "vertex_y": self._vertex.y(),
            "side_a": self._side_a,
            "side_b": self._side_b,
            "angle_type": self._angle_type,
        }
        if self._angle_type in ("adjacent", "vertical"):
            data["side_c"] = self._side_c
        elif self._angle_type == "transversal":
            data["parallel_distance"] = self._parallel_distance
        return data

    def restore_position_data(self, data: dict) -> None:
        self._vertex.setX(data["vertex_x"])
        self._vertex.setY(data["vertex_y"])
        self._side_a = data["side_a"]
        self._side_b = data["side_b"]
        if "side_c" in data:
            self._side_c = data["side_c"]
        if "parallel_distance" in data:
            self._parallel_distance = data["parallel_distance"]

    # ------------------------------------------------------------------
    # Свойства для панели
    # ------------------------------------------------------------------

    def get_properties(self) -> dict:
        d = super().get_properties()
        d["_shape_type"] = self.shape_type.value
        d["_side_a"] = self._side_a
        d["_side_b"] = self._side_b
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

        if "_side_a" in properties:
            self._side_a = max(properties["_side_a"], 0.1)
        if "_side_b" in properties:
            self._side_b = max(properties["_side_b"], 0.1)
        if "_angle_deg" in properties:
            self._angle_deg = properties["_angle_deg"] % 360.0
        if "_x" in properties and "_y" in properties:
            dx = properties["_x"] - self.bounding_rect().left()
            dy = properties["_y"] - self.bounding_rect().top()
            self.move(dx, dy)

    # ------------------------------------------------------------------
    # Сериализация
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update(
            {
                "vertex": {"x": self._vertex.x(), "y": self._vertex.y()},
                "side_a": self._side_a,
                "side_b": self._side_b,
                "angle_deg": self._angle_deg,
                "angle_type": self._angle_type,
            }
        )
        if self._angle_type in ("adjacent", "vertical"):
            d["side_c"] = self._side_c
        elif self._angle_type == "transversal":
            d["parallel_distance"] = self._parallel_distance
        return d

    @classmethod
    def from_dict(cls, data: dict) -> AngleShape:
        vertex_data = data.get("vertex", {"x": 0.0, "y": 0.0})
        vertex = (vertex_data.get("x", 0.0), vertex_data.get("y", 0.0))
        angle_type = data.get("angle_type", "single")

        obj = cls(
            vertex=vertex,
            side_a=data.get("side_a", 100.0),
            side_b=data.get("side_b", 100.0),
            angle_deg=data.get("angle_deg", 90.0),
            pen_color=data["pen_color"],
            brush_color=data.get("brush_color"),
            pen_width=data.get("pen_width", 2.0),
            angle_type=angle_type,
        )

        if angle_type in ("adjacent", "vertical"):
            obj._side_c = data.get("side_c", 100.0)
        elif angle_type == "transversal":
            obj._parallel_distance = data.get("parallel_distance", 100.0)

        obj.id = data.get("id", -1)
        obj._selected = data.get("selected", False)
        obj._rotation = data.get("rotation", 0.0)
        return obj
