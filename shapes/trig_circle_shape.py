"""Фигура: Тригонометрическая окружность — справочная диаграмма."""

from __future__ import annotations

import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen

from .base_shape import BaseShape, HandleType, ShapeType

# Значения sin и cos для ключевых углов
_ANGLE_DATA: list[tuple[float, str, str, str]] = [
    # (угол_в_радианах, label_внешний, sin_value, cos_value)
    (0.0, "0", "0", "1"),
    (math.pi / 6, "π/6", "1/2", "√3/2"),
    (math.pi / 4, "π/4", "√2/2", "√2/2"),
    (math.pi / 3, "π/3", "√3/2", "1/2"),
    (math.pi / 2, "π/2", "1", "0"),
    (2 * math.pi / 3, "2π/3", "√3/2", "-1/2"),
    (3 * math.pi / 4, "3π/4", "√2/2", "-√2/2"),
    (5 * math.pi / 6, "5π/6", "1/2", "-√3/2"),
    (math.pi, "π", "0", "-1"),
    (7 * math.pi / 6, "7π/6", "-1/2", "-√3/2"),
    (5 * math.pi / 4, "5π/4", "-√2/2", "-√2/2"),
    (4 * math.pi / 3, "4π/3", "-√3/2", "-1/2"),
    (3 * math.pi / 2, "3π/2", "-1", "0"),
    (5 * math.pi / 3, "5π/3", "-√3/2", "1/2"),
    (7 * math.pi / 4, "7π/4", "-√2/2", "√2/2"),
    (11 * math.pi / 6, "11π/6", "-1/2", "√3/2"),
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

    def draw(self, painter: QPainter) -> None:
        painter.save()
        try:
            self._draw_axes(painter)
            self._draw_circle(painter)
            self._draw_grid_lines(painter)
            self._draw_angle_lines(painter)
            self._draw_angle_labels(painter)
            self._draw_axis_labels(painter)
            self._draw_selection_box(painter)
        finally:
            painter.restore()

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

    def _draw_axes(self, painter: QPainter) -> None:
        """Рисует координатные оси."""
        pen = QPen(
            QColor(self.pen_color.red(), self.pen_color.green(), self.pen_color.blue()),
            max(self.pen_width, 1.5),
        )
        painter.setPen(pen)

        r = self._radius
        ext = r * 0.15  # выступ осей

        # Ось X
        painter.drawLine(
            QPointF(self._cx - r - ext, self._cy),
            QPointF(self._cx + r + ext, self._cy),
        )
        # Ось Y
        painter.drawLine(
            QPointF(self._cx, self._cy - r - ext),
            QPointF(self._cx, self._cy + r + ext),
        )

        # Стрелки
        arrow_size = 8
        # Стрелка X (вправо)
        painter.drawLine(
            QPointF(self._cx + r + ext, self._cy),
            QPointF(self._cx + r + ext - arrow_size, self._cy - arrow_size / 2),
        )
        painter.drawLine(
            QPointF(self._cx + r + ext, self._cy),
            QPointF(self._cx + r + ext - arrow_size, self._cy + arrow_size / 2),
        )
        # Стрелка Y (вверх)
        painter.drawLine(
            QPointF(self._cx, self._cy - r - ext),
            QPointF(self._cx - arrow_size / 2, self._cy - r - ext + arrow_size),
        )
        painter.drawLine(
            QPointF(self._cx, self._cy - r - ext),
            QPointF(self._cx + arrow_size / 2, self._cy - r - ext + arrow_size),
        )

    def _draw_circle(self, painter: QPainter) -> None:
        """Рисует единичную окружность."""
        pen = QPen(
            QColor(self.pen_color.red(), self.pen_color.green(), self.pen_color.blue()),
            max(self.pen_width, 2),
        )
        painter.setPen(pen)
        painter.drawEllipse(
            QPointF(self._cx, self._cy),
            self._radius,
            self._radius,
        )

    def _draw_grid_lines(self, painter: QPainter) -> None:
        """Рисует линии сетки (синусные и косинусные) для ключевых углов."""
        sin_color = QColor(200, 40, 40)
        cos_color = QColor(40, 80, 200)

        r = self._radius
        for angle_rad, _, sin_val, cos_val in _ANGLE_DATA:
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
        for angle_rad, _, _, _ in _ANGLE_DATA:
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

        for angle_rad, angle_label, sin_val, cos_val in _ANGLE_DATA:
            cos_a = math.cos(angle_rad)
            sin_a = math.sin(angle_rad)

            px = self._cx + cos_a * r
            py = self._cy - sin_a * r

            # Точка на окружности
            pen = QPen(
                QColor(self.pen_color.red(), self.pen_color.green(), self.pen_color.blue()), 2
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

            # -----------------------------------------------------------
            # Подписи sin/cos — рядом с точкой на окружности, смещены
            # наружу от центра, чтобы не накладывались друг на друга
            # -----------------------------------------------------------
            painter.setFont(font_val)

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

            # cos подпись: смещена от точки наружу по радиусу на 50 px
            cos_color = QColor(40, 80, 200)
            painter.setPen(cos_color)
            cos_px = self._cx + cos_a * (r + 50)
            cos_py = self._cy - sin_a * (r + 50)
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
        painter.drawText(int(self._cx + r + 12), int(self._cy) + 4, "x")
        painter.drawText(int(self._cx) + 4, int(self._cy - r - 12), "y")

        # Единицы на осях
        font_unit = QFont("Arial", 9)
        painter.setFont(font_unit)

        painter.drawText(int(self._cx + r) - 4, int(self._cy) + 14, "1")
        painter.drawText(int(self._cx - r) - 10, int(self._cy) + 14, "-1")
        painter.drawText(int(self._cx) + 6, int(self._cy - r) - 6, "1")
        painter.drawText(int(self._cx) + 6, int(self._cy + r) + 12, "-1")

        # Начало координат
        painter.drawText(int(self._cx) - 8, int(self._cy) + 14, "O")

    def _draw_selection_box(self, painter: QPainter) -> None:
        """Рисует рамку выделения."""
        if not self._selected:
            return
        pen = QPen(QColor(0, 120, 255), 1)
        painter.setPen(pen)
        painter.setBrush(Qt.PenStyle.NoBrush)
        for hx, hy in self._handle_positions():
            painter.drawRect(int(hx) - 4, int(hy) - 4, 8, 8)

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
    ) -> None:
        if handle == HandleType.TOP_LEFT:
            dx = mouse_pos.x() - point.x()
            dy = mouse_pos.y() - point.y()
            self._cx += dx
            self._cy += dy
        elif handle in (HandleType.BOTTOM_RIGHT, HandleType.TOP_CENTER, HandleType.LEFT_CENTER):
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
