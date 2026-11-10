"""Фигура: Тригонометрическая окружность — справочная диаграмма."""

from __future__ import annotations

import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen

from .base_shape import BaseShape, HandleType, ShapeType

# Значения sin и cos для ключевых углов
_ANGLE_DATA: list[tuple[float, str, str, str, str]] = [
    # (угол_в_радианах, label_внешний, sin_value, cos_value, degrees)
    (0.0, "0", "0", "1", "0°"),
    (math.pi / 6, "π/6", "1/2", "√3/2", "30°"),
    (math.pi / 4, "π/4", "√2/2", "√2/2", "45°"),
    (math.pi / 3, "π/3", "√3/2", "1/2", "60°"),
    (math.pi / 2, "π/2", "1", "0", "90°"),
    (2 * math.pi / 3, "2π/3", "√3/2", "-1/2", "120°"),
    (3 * math.pi / 4, "3π/4", "√2/2", "-√2/2", "135°"),
    (5 * math.pi / 6, "5π/6", "1/2", "-√3/2", "150°"),
    (math.pi, "π", "0", "-1", "180°"),
    (7 * math.pi / 6, "7π/6", "-1/2", "-√3/2", "210°"),
    (5 * math.pi / 4, "5π/4", "-√2/2", "-√2/2", "225°"),
    (4 * math.pi / 3, "4π/3", "-√3/2", "-1/2", "240°"),
    (3 * math.pi / 2, "3π/2", "-1", "0", "270°"),
    (5 * math.pi / 3, "5π/3", "-√3/2", "1/2", "300°"),
    (7 * math.pi / 4, "7π/4", "-√2/2", "√2/2", "315°"),
    (11 * math.pi / 6, "11π/6", "-1/2", "√3/2", "330°"),
]


class TrigCircleShape(BaseShape):
    """Тригонометрическая окружность — справочная диаграмма с углами и значениями sin/cos."""

    def __init__(
        self,
        cx: float = 0.0,
        cy: float = 0.0,
        radius: float = 200.0,
        pen_color: tuple[int, int, int] = (0, 0, 0),
        pen_width: float = 2.0,
        brush_color: tuple[int, int, int] | None = None,
        selected: bool = False,
    ):
        super().__init__(pen_color, pen_width, brush_color, selected)
        self._cx = cx
        self._cy = cy
        self._radius = radius

    def _get_shape_type(self) -> ShapeType:
        """Возвращает тип фигуры — TRIGONOMETRIC_CIRCLE."""
        return ShapeType.TRIGONOMETRIC_CIRCLE

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

    # ------------------------------------------------------------------
    # Abstract methods
    # ------------------------------------------------------------------

    def _rotation_center(self) -> tuple[float, float]:
        """Возвращает центр поворота — центр окружности."""
        return (self._cx, self._cy)

    def _draw_shape_content(self, painter: QPainter) -> None:
        """Рисует тригонометрическую окружность."""
        self._draw_axes(painter)
        self._draw_circle(painter)
        self._draw_grid_lines(painter)
        self._draw_angle_lines(painter)
        self._draw_angle_labels(painter)
        self._draw_axis_labels(painter)

    def contains_point(self, point: QPointF) -> bool:
        dx = point.x() - self._cx
        dy = point.y() - self._cy
        return abs(dx) <= self._radius + 80 and abs(dy) <= self._radius + 80

    def move(self, dx: float, dy: float) -> None:
        self._cx += dx
        self._cy += dy

    def scale(self, factor: float, center: QPointF | None = None) -> None:
        self._radius *= factor
        if self._radius < 10.0:
            self._radius = 10.0

    def bounding_rect(self) -> QRectF:
        pad = self._radius + 80
        return self._safe_rect(
            self._cx - pad,
            self._cy - pad,
            2 * pad,
            2 * pad,
        )

    # ------------------------------------------------------------------
    # Отрисовка
    # ------------------------------------------------------------------

    def _draw_grid_lines(self, painter: QPainter) -> None:
        """Рисует линии сетки (синусные и косинусные) для ключевых углов."""
        sin_color = QColor(200, 40, 40)
        cos_color = QColor(40, 80, 200)

        r = self._radius
        for angle_rad, _, sin_val, cos_val, _ in _ANGLE_DATA:
            cos_a = math.cos(angle_rad)
            sin_a = math.sin(angle_rad)

            # Горизонтальная линия cos
            pen = QPen(cos_color, 1)
            pen.setStyle(Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.drawLine(
                QPointF(self._cx, self._cy),
                QPointF(self._cx + cos_a * r, self._cy),
            )

            # Вертикальная линия sin
            pen = QPen(sin_color, 1)
            pen.setStyle(Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.drawLine(
                QPointF(self._cx, self._cy),
                QPointF(self._cx, self._cy - sin_a * r),
            )

    def _draw_angle_lines(self, painter: QPainter) -> None:
        """Рисует радиусы до ключевых точек."""
        pen = QPen(QColor(100, 100, 100), 1)
        pen.setStyle(Qt.PenStyle.DashLine)
        painter.setPen(pen)

        r = self._radius
        for angle_rad, _, _, _, _ in _ANGLE_DATA:
            cos_a = math.cos(angle_rad)
            sin_a = math.sin(angle_rad)
            painter.drawLine(
                QPointF(self._cx, self._cy),
                QPointF(self._cx + cos_a * r, self._cy - sin_a * r),
            )

    def _draw_angle_labels(self, painter: QPainter) -> None:
        """Рисует подписи углов и значений sin/cos."""
        r = self._radius
        font_angle = QFont("Arial", 10, QFont.Weight.Bold)
        font_val = QFont("Arial", 8)

        for angle_rad, angle_label, sin_val, cos_val, degrees in _ANGLE_DATA:
            cos_a = math.cos(angle_rad)
            sin_a = math.sin(angle_rad)

            px = self._cx + cos_a * r
            py = self._cy - sin_a * r

            # Точка на окружности
            pen = QPen(
                QColor(self.pen_color.red(), self.pen_color.green(), self.pen_color.blue()),
                2,
            )
            painter.setPen(pen)
            painter.drawEllipse(QPointF(px, py), 3, 3)

            # Подпись угла (внешняя)
            label_dist = r + 65
            lx = self._cx + cos_a * label_dist
            ly = self._cy - sin_a * label_dist

            painter.setFont(font_angle)
            painter.setPen(QColor(80, 40, 140))
            painter.drawText(int(lx) - 15, int(ly) + 4, angle_label)

            # Подпись градусов
            font_deg = QFont("Arial", 8)
            painter.setFont(font_deg)
            painter.setPen(QColor(80, 40, 140))
            painter.drawText(int(lx) - 10, int(ly) + 18, degrees)

            # -----------------------------------------------------------
            # Подписи sin/cos — рядом с точкой на окружности, смещены
            # наружу от центра, чтобы не накладывались друг на друга
            # -----------------------------------------------------------
            painter.setFont(font_val)

            # Для углов 0 и π — рисуем метки со смещением от оси
            if abs(sin_a) < 0.01:
                px = self._cx + cos_a * r
                py = self._cy - sin_a * r
                if cos_a > 0:
                    # Угол 0: cos внутри круга ближе к центру, sin снаружи ниже оси
                    cos_color = QColor(40, 80, 200)
                    painter.setPen(cos_color)
                    painter.drawText(int(px - 50), int(py - 15), f"cos={cos_val}")
                    sin_color = QColor(200, 40, 40)
                    painter.setPen(sin_color)
                    painter.drawText(int(px + 10), int(py + 25), f"sin={sin_val}")
                else:
                    # Угол π: sin снаружи выше оси, cos внутри ближе к центру
                    sin_color = QColor(200, 40, 40)
                    painter.setPen(sin_color)
                    painter.drawText(int(px - 30), int(py + 25), f"sin={sin_val}")
                    cos_color = QColor(40, 80, 200)
                    painter.setPen(cos_color)
                    painter.drawText(int(px + 10), int(py - 15), f"cos={cos_val}")
                continue

            # sin подпись: смещена от точки наружу по радиусу на 35 px
            sin_color = QColor(200, 40, 40)
            painter.setPen(sin_color)
            sin_px = self._cx + cos_a * (r + 35)
            sin_py = self._cy - sin_a * (r + 35)
            painter.drawText(
                int(sin_px) - 20,
                int(sin_py) + 4,
                f"sin={sin_val}",
            )

            # cos подпись: внутри круга, ближе к окружности
            cos_color = QColor(40, 80, 200)
            painter.setPen(cos_color)
            cos_px = self._cx + cos_a * r * 0.85
            cos_py = self._cy - sin_a * r * 0.85
            painter.drawText(
                int(cos_px) - 20,
                int(cos_py) + 4,
                f"cos={cos_val}",
            )

    def _draw_axis_labels(self, painter: QPainter) -> None:
        """Рисует подписи осей и ключевых точек."""
        r = self._radius
        font = QFont("Arial", 10, QFont.Weight.Bold)
        painter.setFont(font)
        painter.setPen(QColor(self.pen_color.red(), self.pen_color.green(), self.pen_color.blue()))

        # Оси
        painter.drawText(int(self._cx + r + 12), int(self._cy) - 10, "x")
        painter.drawText(int(self._cx) + 15, int(self._cy - r - 12), "y")

        # Единицы на осях
        font_unit = QFont("Arial", 9)
        painter.setFont(font_unit)

        painter.drawText(int(self._cx + r) - 4, int(self._cy) + 14, "1")
        painter.drawText(int(self._cx - r) - 25, int(self._cy) + 14, "-1")
        painter.drawText(int(self._cx) + 6, int(self._cy - r) - 6, "1")
        painter.drawText(int(self._cx) + 6, int(self._cy + r) + 12, "-1")

        # Начало координат
        painter.drawText(int(self._cx) - 8, int(self._cy) + 14, "O")

    # ------------------------------------------------------------------
    # Маркеры (handles)
    # ------------------------------------------------------------------

    def _handle_positions(self) -> list[tuple[float, float]]:
        return [
            (self._cx, self._cy),
            (self._cx + self._radius, self._cy),
            (self._cx, self._cy - self._radius),
            (self._cx - self._radius, self._cy),
        ]

    def apply_handle_transform(
        self,
        handle: HandleType,
        point: QPointF,
        mouse_pos: QPointF,
        shift_pressed: bool = False,
        vertex_index: int = -1,
    ) -> None:
        if handle == HandleType.TOP_LEFT:
            dx = mouse_pos.x() - point.x()
            dy = mouse_pos.y() - point.y()
            self._cx += dx
            self._cy += dy
        elif handle in (
            HandleType.BOTTOM_RIGHT,
            HandleType.TOP_CENTER,
            HandleType.LEFT_CENTER,
        ):
            dx = mouse_pos.x() - self._cx
            dy = mouse_pos.y() - self._cy
            self._radius = math.sqrt(dx * dx + dy * dy)
            if self._radius < 10.0:
                self._radius = 10.0

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
            }
        )
        return d

    @classmethod
    def from_dict(cls, data: dict) -> TrigCircleShape:
        obj = cls(
            cx=data["cx"],
            cy=data["cy"],
            radius=data["radius"],
            pen_color=data["pen_color"],
            brush_color=data.get("brush_color"),
            pen_width=data.get("pen_width", 2.0),
        )
        obj._selected = data.get("selected", False)
        obj._rotation = data.get("rotation", 0.0)
        return obj
