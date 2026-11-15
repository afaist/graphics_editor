"""Фигура: Вписанный угол, опирающийся на хорду."""

from __future__ import annotations

import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPen

from .base_shape import BaseShape, HandleType, ShapeType


class InscribedAngleChordShape(BaseShape):
    """Вписанный угол, опирающийся на хорду.

    Элементы:
        - Окружность (синий цвет) с центром O
        - Хорда BC (зелёный цвет) — концы лежат на окружности
        - Вершина угла A на окружности (не на хорде) (красный цвет)
        - Стороны угла AB и AC

    Вершина A может перемещаться по окружности.
    Концы хорды B и C могут перемещаться по окружности.
    """

    def __init__(
        self,
        cx: float,
        cy: float,
        radius: float,
        vertex_angle: float,  # угол вершины A на окружности
        chord_angle_b: float,  # угол точки B на окружности
        chord_angle_c: float,  # угол точки C на окружности
        pen_color: tuple[int, int, int] = (0, 0, 0),
        pen_width: float = 2.0,
        brush_color: tuple[int, int, int] | None = None,
        selected: bool = False,
    ):
        super().__init__(pen_color, pen_width, brush_color, selected)
        self._cx = cx
        self._cy = cy
        self._radius = max(radius, 30.0)
        self._vertex_angle = vertex_angle
        self._chord_angle_b = chord_angle_b
        self._chord_angle_c = chord_angle_c

        # Цвета элементов
        self._circle_color: tuple[int, int, int] = (0, 0, 200)  # синий
        self._chord_color: tuple[int, int, int] = (0, 150, 0)  # зелёный
        self._angle_color: tuple[int, int, int] = (200, 0, 0)  # красный

    def _get_shape_type(self) -> ShapeType:
        return ShapeType.INSCRIBED_ANGLE_CHORD

    # ------------------------------------------------------------------
    # Свойства
    # ------------------------------------------------------------------

    @property
    def cx(self) -> float:
        return self._cx

    @property
    def cy(self) -> float:
        return self._cy

    @property
    def radius(self) -> float:
        return self._radius

    @radius.setter
    def radius(self, value: float) -> None:
        if value > 10.0:
            self._radius = value

    @property
    def vertex_angle(self) -> float:
        return self._vertex_angle

    @property
    def chord_angle_b(self) -> float:
        return self._chord_angle_b

    @property
    def chord_angle_c(self) -> float:
        return self._chord_angle_c

    # ------------------------------------------------------------------
    # Вычисляемые точки
    # ------------------------------------------------------------------

    def _point_on_circle(self, angle: float) -> QPointF:
        """Точка на окружности по углу."""
        return QPointF(
            self._cx + self._radius * math.cos(angle),
            self._cy + self._radius * math.sin(angle),
        )

    @property
    def center_o(self) -> QPointF:
        """Центр окружности O."""
        return QPointF(self._cx, self._cy)

    @property
    def vertex_a(self) -> QPointF:
        """Вершина угла A на окружности."""
        return self._point_on_circle(self._vertex_angle)

    @property
    def chord_b(self) -> QPointF:
        """Конец хорды B на окружности."""
        return self._point_on_circle(self._chord_angle_b)

    @property
    def chord_c(self) -> QPointF:
        """Конец хорды C на окружности."""
        return self._point_on_circle(self._chord_angle_c)

    @property
    def vertices(self) -> list[QPointF]:
        """Все управляемые точки."""
        return [self.vertex_a, self.chord_b, self.chord_c]

    # ------------------------------------------------------------------
    # Отрисовка
    # ------------------------------------------------------------------

    def _draw_shape_content(self, painter: QPainter) -> None:
        """Рисует вписанный угол на хорде."""
        o = self.center_o
        a = self.vertex_a
        b = self.chord_b
        c = self.chord_c

        # --- Окружность (синий) ---
        pen = QPen(QColor(*self._circle_color), self.pen_width)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(o, self._radius, self._radius)

        # --- Центр O (точка + подпись) ---
        pen.setColor(QColor(*self._circle_color))
        painter.setPen(pen)
        painter.setBrush(QBrush(QColor(*self._circle_color)))
        painter.drawEllipse(o, 3, 3)

        font = QFont("Arial", 10, QFont.Weight.Bold)
        painter.setFont(font)
        painter.setPen(QColor(*self._circle_color))
        painter.drawText(int(o.x()) + 6, int(o.y()) + 14, "O")

        # --- Хорда BC (зелёный) ---
        pen.setColor(QColor(*self._chord_color))
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawLine(b, c)

        # Точки B и C
        painter.setPen(QColor(*self._chord_color))
        painter.setBrush(QBrush(QColor(*self._chord_color)))
        painter.drawEllipse(b, 3, 3)
        painter.drawEllipse(c, 3, 3)

        # Подписи B и C
        font.setBold(False)
        font.setPointSize(9)
        painter.setFont(font)
        painter.setPen(QColor(*self._chord_color))
        dx_b = b.x() - self._cx
        dy_b = b.y() - self._cy
        dist_b = math.hypot(dx_b, dy_b)
        if dist_b > 0.01:
            dx_b /= dist_b
            dy_b /= dist_b
            painter.drawText(int(b.x() + dx_b * 14) - 6, int(b.y() + dy_b * 14) + 4, "B")

        dx_c = c.x() - self._cx
        dy_c = c.y() - self._cy
        dist_c = math.hypot(dx_c, dy_c)
        if dist_c > 0.01:
            dx_c /= dist_c
            dy_c /= dist_c
            painter.drawText(int(c.x() + dx_c * 14) - 6, int(c.y() + dy_c * 14) + 4, "C")

        # --- Стороны угла AB и AC (красный) ---
        pen.setColor(QColor(*self._angle_color))
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawLine(a, b)
        painter.drawLine(a, c)

        # Точка A
        painter.setPen(QColor(*self._angle_color))
        painter.setBrush(QBrush(QColor(*self._angle_color)))
        painter.drawEllipse(a, 3, 3)

        # Подпись A
        font.setPointSize(10)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QColor(*self._angle_color))
        dx_a = a.x() - self._cx
        dy_a = a.y() - self._cy
        dist_a = math.hypot(dx_a, dy_a)
        if dist_a > 0.01:
            dx_a /= dist_a
            dy_a /= dist_a
            painter.drawText(int(a.x() + dx_a * 14) - 6, int(a.y() + dy_a * 14) + 4, "A")

        # --- Дуга угла (внутри угла, по биссектрисе) ---
        arc_radius = min(self._radius * 0.2, 30.0)
        arc_radius = max(arc_radius, 12.0)

        # Единичные векторы сторон
        vec_ab = QPointF(b.x() - a.x(), b.y() - a.y())
        vec_ac = QPointF(c.x() - a.x(), c.y() - a.y())
        len_ab = math.hypot(vec_ab.x(), vec_ab.y())
        len_ac = math.hypot(vec_ac.x(), vec_ac.y())

        if len_ab > 0.01 and len_ac > 0.01:
            ux1, uy1 = vec_ab.x() / len_ab, vec_ab.y() / len_ab
            ux2, uy2 = vec_ac.x() / len_ac, vec_ac.y() / len_ac
            # Биссектриса — сумма единичных векторов
            mx, my = ux1 + ux2, uy1 + uy2
            mlen = math.hypot(mx, my)
            if mlen > 0.01:
                mid_angle = math.atan2(my, mx)
                half_span = math.acos(min(mlen / 2.0, 1.0))
            else:
                # Векторы противоположны (180°)
                mid_angle = math.atan2(uy1, ux1) + math.pi / 2
                half_span = math.pi / 2
        else:
            mid_angle = 0.0
            half_span = 0.0

        arc_pen = QPen(QColor(*self._angle_color), 1.0)
        painter.setPen(arc_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        rect = QRectF(
            a.x() - arc_radius,
            a.y() - arc_radius,
            arc_radius * 2,
            arc_radius * 2,
        )

        start_16 = int(-math.degrees(mid_angle + half_span) * 16)
        span_16 = int(math.degrees(2 * half_span) * 16)
        painter.drawArc(rect, start_16, span_16)

        # Вычисление вписанного угла
        # Вписанный угол = половина центрального угла, опирающегося на ту же дугу
        central_angle = abs(self._chord_angle_c - self._chord_angle_b)
        if central_angle > math.pi:
            central_angle = 2 * math.pi - central_angle
        inscribed_deg = math.degrees(central_angle) / 2.0

        # Текст угла (на биссектрисе)
        text_radius = arc_radius * 1.5
        tx = a.x() + text_radius * math.cos(mid_angle)
        ty = a.y() + text_radius * math.sin(mid_angle)

        angle_text = f"{inscribed_deg:.1f}°"
        font.setPointSize(9)
        painter.setFont(font)
        painter.setPen(QColor(*self._angle_color))
        text_rect = QRectF(tx - 20, ty - 8, 40, 16)
        painter.drawText(
            text_rect,
            Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter,
            angle_text,
        )

    # ------------------------------------------------------------------
    # Базовые методы
    # ------------------------------------------------------------------

    def contains_point(self, point: QPointF) -> bool:
        return self.bounding_rect().contains(point)

    def move(self, dx: float, dy: float) -> None:
        self._cx += dx
        self._cy += dy

    def scale(self, factor: float, center: QPointF | None = None) -> None:
        self._radius *= factor
        if self._radius < 10.0:
            self._radius = 10.0

    def bounding_rect(self) -> QRectF:
        pad = self._radius + 30
        return self._safe_rect(
            self._cx - pad,
            self._cy - pad,
            2 * pad,
            2 * pad,
        )

    # ------------------------------------------------------------------
    # Маркеры (handles)
    # ------------------------------------------------------------------

    def _handle_positions(self) -> list[tuple[float, float]]:
        return [
            (self.vertex_a.x(), self.vertex_a.y()),
            (self.chord_b.x(), self.chord_b.y()),
            (self.chord_c.x(), self.chord_c.y()),
        ]

    def get_handles(self) -> list[QPointF]:
        return list(self.vertices)

    def get_handle_type(self, point: QPointF, tolerance: float = 5.0) -> HandleType:
        for i, v in enumerate(self.vertices):
            dx = point.x() - v.x()
            dy = point.y() - v.y()
            if math.hypot(dx, dy) <= tolerance:
                if i == 0:
                    return HandleType.TOP_LEFT  # вершина A
                elif i == 1:
                    return HandleType.BOTTOM_RIGHT  # точка B
                else:
                    return HandleType.BOTTOM_CENTER  # точка C
        return HandleType.NONE

    def apply_handle_transform(
        self,
        handle: HandleType,
        point: QPointF,
        mouse_pos: QPointF,
        shift_pressed: bool = False,
        vertex_index: int = -1,
    ) -> None:
        # Если передан индекс вершины, используем его
        if vertex_index >= 0:
            dx = mouse_pos.x() - self._cx
            dy = mouse_pos.y() - self._cy
            new_angle = math.atan2(dy, dx)
            if vertex_index == 0:
                self._vertex_angle = new_angle
            elif vertex_index == 1:
                self._chord_angle_b = new_angle
            elif vertex_index == 2:
                self._chord_angle_c = new_angle
            return

        dx = mouse_pos.x() - self._cx
        dy = mouse_pos.y() - self._cy
        new_angle = math.atan2(dy, dx)

        if handle == HandleType.TOP_LEFT:
            self._vertex_angle = new_angle
        elif handle == HandleType.BOTTOM_RIGHT:
            self._chord_angle_b = new_angle
        elif handle == HandleType.BOTTOM_CENTER:
            self._chord_angle_c = new_angle

    # ------------------------------------------------------------------
    # Свойства для панели
    # ------------------------------------------------------------------

    def get_properties(self) -> dict:
        props = super().get_properties()
        props["_radius"] = self._radius
        return props

    def apply_properties(self, properties: dict) -> None:
        super().apply_properties(properties)
        if properties is None:
            return
        if "_radius" in properties:
            r = properties["_radius"]
            if r > 10.0:
                self._radius = r

    # ------------------------------------------------------------------
    # Позиция для undo
    # ------------------------------------------------------------------

    def get_position_data(self) -> dict:
        return {
            "cx": self._cx,
            "cy": self._cy,
            "radius": self._radius,
            "vertex_angle": self._vertex_angle,
            "chord_angle_b": self._chord_angle_b,
            "chord_angle_c": self._chord_angle_c,
        }

    def restore_position_data(self, data: dict) -> None:
        self._cx = data["cx"]
        self._cy = data["cy"]
        self._radius = data["radius"]
        if "vertex_angle" in data:
            self._vertex_angle = data["vertex_angle"]
        if "chord_angle_b" in data:
            self._chord_angle_b = data["chord_angle_b"]
        if "chord_angle_c" in data:
            self._chord_angle_c = data["chord_angle_c"]

    # ------------------------------------------------------------------
    # Сериализация
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update(
            {
                "cx": self._cx,
                "cy": self._cy,
                "radius": self._radius,
                "vertex_angle": self._vertex_angle,
                "chord_angle_b": self._chord_angle_b,
                "chord_angle_c": self._chord_angle_c,
            }
        )
        return d

    @classmethod
    def from_dict(cls, data: dict) -> InscribedAngleChordShape:
        obj = cls(
            cx=data["cx"],
            cy=data["cy"],
            radius=data["radius"],
            vertex_angle=data.get("vertex_angle", math.pi),
            chord_angle_b=data.get("chord_angle_b", -math.pi / 3),
            chord_angle_c=data.get("chord_angle_c", math.pi / 3),
            pen_color=data["pen_color"],
            brush_color=data.get("brush_color"),
            pen_width=data.get("pen_width", 2.0),
        )
        obj._selected = data.get("selected", False)
        obj._rotation = data.get("rotation", 0.0)
        return obj
