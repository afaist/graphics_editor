"""Фигура: Тригонометрическая окружность с осями тангенсов и котангенсов."""

from __future__ import annotations

import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen

from .base_shape import BaseShape, HandleType, ShapeType

# Ключевые углы и их значения
_ANGLE_DATA = [
    (0.0, "0", "0", "1", "0", "∞"),
    (math.pi / 6, "π/6", "1/2", "√3/2", "√3/3", "√3"),
    (math.pi / 4, "π/4", "√2/2", "√2/2", "1", "1"),
    (math.pi / 3, "π/3", "√3/2", "1/2", "√3", "√3/3"),
    (math.pi / 2, "π/2", "1", "0", "∞", "0"),
    (2 * math.pi / 3, "2π/3", "√3/2", "-1/2", "-√3", "-√3/3"),
    (3 * math.pi / 4, "3π/4", "√2/2", "-√2/2", "-1", "-1"),
    (5 * math.pi / 6, "5π/6", "1/2", "-√3/2", "-√3/3", "-√3"),
    (math.pi, "π", "0", "-1", "0", "∞"),
    (7 * math.pi / 6, "7π/6", "-1/2", "-√3/2", "√3/3", "√3"),
    (5 * math.pi / 4, "5π/4", "-√2/2", "-√2/2", "1", "1"),
    (4 * math.pi / 3, "4π/3", "-√3/2", "-1/2", "√3", "√3/3"),
    (3 * math.pi / 2, "3π/2", "-1", "0", "∞", "0"),
    (5 * math.pi / 3, "5π/3", "-√3/2", "1/2", "-√3", "-√3/3"),
    (7 * math.pi / 4, "7π/4", "-√2/2", "√2/2", "-1", "-1"),
    (11 * math.pi / 6, "11π/6", "-1/2", "√3/2", "-√3/3", "-√3"),
]


class TrigCircleFullShape(BaseShape):
    """Тригонометрическая окружность с осями tg и ctg."""

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
        """Возвращает тип фигуры — TRIG_CIRCLE_FULL (тригонометрическая окружность с tg/ctg)."""
        return ShapeType.TRIG_CIRCLE_FULL

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

    def draw(self, painter: QPainter) -> None:
        painter.save()
        try:
            self._draw_axes(painter)
            self._draw_circle(painter)
            self._draw_angle_lines(painter)
            self._draw_extended_angle_lines(painter)
            self._draw_tangent_cotangent_axes(painter)
            self._draw_circle_points(painter)
            self._draw_sin_cos_labels(painter)
            self._draw_angle_labels(painter)
            self._draw_axis_labels(painter)
            self._draw_title(painter)
            self._draw_selection_box(painter)
        finally:
            painter.restore()

    def contains_point(self, point: QPointF) -> bool:
        dx = point.x() - self._cx
        dy = point.y() - self._cy
        return abs(dx) <= self._radius + 120 and abs(dy) <= self._radius + 160

    def move(self, dx: float, dy: float) -> None:
        self._cx += dx
        self._cy += dy

    def scale(self, factor: float, center: QPointF | None = None) -> None:
        self._radius *= factor
        if self._radius < 10.0:
            self._radius = 10.0

    def bounding_rect(self) -> QRectF:
        pad = self._radius + 120
        return self._safe_rect(self._cx - pad, self._cy - pad - 40, 2 * pad, 2 * pad + 80)

    def _draw_title(self, painter: QPainter) -> None:
        font = QFont("Arial", 12, QFont.Weight.Bold)
        painter.setFont(font)
        painter.setPen(QColor(self.pen_color.red(), self.pen_color.green(), self.pen_color.blue()))
        painter.drawText(
            int(self._cx) - 80,
            int(self._cy - self._radius - 100),
            "Тригонометрический круг",
        )
        font_eq = QFont("Arial", 10)
        painter.setFont(font_eq)
        painter.drawText(int(self._cx) - 40, int(self._cy - self._radius - 80), "x²+y²=1")

    def _draw_tangent_cotangent_axes(self, painter: QPainter) -> None:
        r = self._radius
        ext = r * 0.8  # Увеличили для отображения tg = ±√3

        tg_color = QColor(140, 80, 200)
        ctg_color = QColor(140, 80, 200)

        # Ось тангенсов — вертикальная линия справа (x = 1)
        pen = QPen(tg_color, 1.5)
        pen.setStyle(Qt.PenStyle.DashLine)
        painter.setPen(pen)
        painter.drawLine(
            QPointF(self._cx + r, self._cy - r - ext),
            QPointF(self._cx + r, self._cy + r + ext),
        )

        # Ось котангенсов — горизонтальная линия сверху (y = 1)
        pen = QPen(ctg_color, 1.5)
        pen.setStyle(Qt.PenStyle.DashLine)
        painter.setPen(pen)
        painter.drawLine(
            QPointF(self._cx - r - ext - 40, self._cy - r),
            QPointF(self._cx + r + ext + 40, self._cy - r),
        )

        # Подписи осей
        font = QFont("Arial", 9)
        painter.setFont(font)
        painter.setPen(tg_color)
        painter.drawText(int(self._cx + r + 20), int(self._cy - r - ext - 5), "ось tg")
        painter.setPen(ctg_color)
        painter.drawText(int(self._cx + r + ext + 5), int(self._cy - r - 5), "ось ctg")

        # Значения tg на оси tg — в точках пересечения лучей
        # Точка пересечения: (cx + r, cy - r * tg(angle))
        tg_font = QFont("Arial", 12, QFont.Weight.Bold)
        painter.setFont(tg_font)
        for angle_rad, _, _, _, tg_val, _ in _ANGLE_DATA:
            if tg_val == "∞":
                continue
            cos_a = math.cos(angle_rad)
            sin_a = math.sin(angle_rad)
            if abs(cos_a) < 0.01:
                continue
            # y = cy - r * sin/cos = cy - r * tg
            tg_val_float = sin_a / cos_a
            y = self._cy - r * tg_val_float
            # Рисуем только если точка в пределах оси
            if abs(tg_val_float) <= 3.0:
                painter.setPen(tg_color)
                # Для tg=0 опускаем ниже оси x
                offset_y = 15 if abs(tg_val_float) < 0.01 else 5
                painter.drawText(int(self._cx + r + 15), int(y) + offset_y, tg_val)

        # Значения ctg на оси ctg — в точках пересечения лучей
        # Точка пересечения: (cx + r * ctg(angle), cy - r)
        ctg_font = QFont("Arial", 12, QFont.Weight.Bold)
        painter.setFont(ctg_font)
        for angle_rad, _, _, _, _, ctg_val in _ANGLE_DATA:
            if ctg_val == "∞":
                continue
            cos_a = math.cos(angle_rad)
            sin_a = math.sin(angle_rad)
            if abs(sin_a) < 0.01:
                continue
            # x = cx + r * cos/sin = cx + r * ctg
            ctg_val_float = cos_a / sin_a
            x = self._cx + r * ctg_val_float
            # Рисуем только если точка в пределах оси
            if abs(ctg_val_float) <= 3.0:
                painter.setPen(ctg_color)
                painter.drawText(int(x) - 18, int(self._cy - r - 45), ctg_val)

    def _draw_angle_lines(self, painter: QPainter) -> None:
        pen = QPen(QColor(100, 100, 100), 1)
        pen.setStyle(Qt.PenStyle.DashLine)
        painter.setPen(pen)
        r = self._radius
        for angle_rad, _, _, _, _, _ in _ANGLE_DATA:
            cos_a = math.cos(angle_rad)
            sin_a = math.sin(angle_rad)
            painter.drawLine(
                QPointF(self._cx, self._cy),
                QPointF(self._cx + cos_a * r, self._cy - sin_a * r),
            )

    def _draw_extended_angle_lines(self, painter: QPainter) -> None:
        """Рисует линии углов от центра до пересечения с осями tg и ctg."""
        tg_color = QColor(140, 80, 200)
        pen = QPen(tg_color, 1)
        pen.setStyle(Qt.PenStyle.DashLine)
        painter.setPen(pen)

        r = self._radius
        for angle_rad, _, _, _, tg_val, _ in _ANGLE_DATA:
            cos_a = math.cos(angle_rad)
            sin_a = math.sin(angle_rad)

            # Пропускаем нулевые углы
            if abs(cos_a) < 0.01 and abs(sin_a) < 0.01:
                continue

            # Для тангенсов — рисуем линию до оси tg, если значение в пределах
            if tg_val != "∞" and abs(cos_a) > 0.01:
                tg_float = sin_a / cos_a
                if abs(tg_float) <= 3.0:
                    # Рисуем до оси tg
                    t_tg = r / cos_a
                    end_x = self._cx + cos_a * t_tg
                    end_y = self._cy - sin_a * t_tg
                    painter.drawLine(
                        QPointF(self._cx, self._cy),
                        QPointF(end_x, end_y),
                    )
                    continue

            # Для остальных — рисуем до ближайшей оси
            t_tg = float("inf")
            t_ctg = float("inf")

            if abs(cos_a) > 0.01:
                t_tg = r / cos_a
            if abs(sin_a) > 0.01:
                t_ctg = r / sin_a

            # Выбираем ближайшую ось (по модулю параметра)
            if abs(t_tg) <= abs(t_ctg) and abs(t_tg) > 1.0:
                end_x = self._cx + cos_a * t_tg
                end_y = self._cy - sin_a * t_tg
                painter.drawLine(
                    QPointF(self._cx, self._cy),
                    QPointF(end_x, end_y),
                )
            elif abs(t_ctg) > 1.0:
                end_x2 = self._cx + cos_a * t_ctg
                end_y2 = self._cy - sin_a * t_ctg
                painter.drawLine(
                    QPointF(self._cx, self._cy),
                    QPointF(end_x2, end_y2),
                )

    def _draw_circle_points(self, painter: QPainter) -> None:
        pen = QPen(
            QColor(self.pen_color.red(), self.pen_color.green(), self.pen_color.blue()),
            2,
        )
        painter.setPen(pen)
        r = self._radius
        for angle_rad, _, _, _, _, _ in _ANGLE_DATA:
            cos_a = math.cos(angle_rad)
            sin_a = math.sin(angle_rad)
            px = self._cx + cos_a * r
            py = self._cy - sin_a * r
            painter.drawEllipse(QPointF(px, py), 3, 3)

        # Подписи ключевых точек — пропускаем для 0, 90, 180, 270
        font = QFont("Arial", 9, QFont.Weight.Bold)
        painter.setFont(font)
        painter.setPen(QColor(self.pen_color.red(), self.pen_color.green(), self.pen_color.blue()))
        # Пропускаем (1;0), (0;1), (-1;0), (0;-1) — засоряют рисунок

    def _draw_angle_labels(self, painter: QPainter) -> None:
        r = self._radius
        font = QFont("Arial", 10, QFont.Weight.Bold)
        painter.setFont(font)
        painter.setPen(QColor(80, 40, 140))
        for angle_rad, angle_label, _, _, _, _ in _ANGLE_DATA:
            cos_a = math.cos(angle_rad)
            sin_a = math.sin(angle_rad)
            dist = r + 60
            lx = self._cx + cos_a * dist
            ly = self._cy - sin_a * dist
            painter.drawText(int(lx) - 15, int(ly) + 4, angle_label)

    def _draw_sin_cos_labels(self, painter: QPainter) -> None:
        r = self._radius
        font = QFont("Arial", 8)
        painter.setFont(font)
        for angle_rad, _, sin_val, cos_val, _, _ in _ANGLE_DATA:
            cos_a = math.cos(angle_rad)
            sin_a = math.sin(angle_rad)

            # Для углов 0 и π — рисуем метки со смещением от оси
            if abs(sin_a) < 0.01:
                px = self._cx + cos_a * r
                py = self._cy - sin_a * r
                if cos_a > 0:
                    # Угол 0: cos внутри круга ближе к центру, sin снаружи ниже оси
                    cos_color = QColor(40, 80, 200)
                    painter.setPen(cos_color)
                    painter.drawText(int(px - 50), int(py - 10), f"cos={cos_val}")
                    sin_color = QColor(200, 40, 40)
                    painter.setPen(sin_color)
                    painter.drawText(int(px - 50), int(py + 15), f"sin={sin_val}")
                else:
                    # Угол π: sin снаружи выше оси, cos внутри ближе к центру
                    sin_color = QColor(200, 40, 40)
                    painter.setPen(sin_color)
                    painter.drawText(int(px + 10), int(py + 15), f"sin={sin_val}")
                    cos_color = QColor(40, 80, 200)
                    painter.setPen(cos_color)
                    painter.drawText(int(px + 10), int(py - 10), f"cos={cos_val}")
                continue

            # cos — внутри круга, ближе к окружности
            cos_color = QColor(40, 80, 200)
            painter.setPen(cos_color)
            cos_px = self._cx + cos_a * r * 0.85
            cos_py = self._cy - sin_a * r * 0.85
            painter.drawText(int(cos_px) - 18, int(cos_py) + 4, f"cos={cos_val}")

            # sin — сразу под cos
            sin_color = QColor(200, 40, 40)
            painter.setPen(sin_color)
            painter.drawText(int(cos_px) - 18, int(cos_py) + 14, f"sin={sin_val}")

    def _draw_axis_labels(self, painter: QPainter) -> None:
        r = self._radius
        font = QFont("Arial", 10, QFont.Weight.Bold)
        painter.setFont(font)
        painter.setPen(QColor(self.pen_color.red(), self.pen_color.green(), self.pen_color.blue()))
        painter.drawText(int(self._cx + r + 12), int(self._cy) - 10, "x")
        painter.drawText(int(self._cx) + 12, int(self._cy - r - 20), "y")
        font_unit = QFont("Arial", 9)
        painter.setFont(font_unit)
        painter.drawText(int(self._cx + r) - 4, int(self._cy) + 14, "1")
        painter.drawText(int(self._cx - r) - 25, int(self._cy) + 14, "-1")
        painter.drawText(int(self._cx) + 6, int(self._cy - r) - 6, "1")
        painter.drawText(int(self._cx) + 6, int(self._cy + r) + 12, "-1")
        painter.drawText(int(self._cx) - 8, int(self._cy) + 14, "O")

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
    def from_dict(cls, data: dict) -> TrigCircleFullShape:
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
