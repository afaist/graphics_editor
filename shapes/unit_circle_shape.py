"""Фигура: Единичная окружность — интерактивная с подвижным радиусом."""

from __future__ import annotations

import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen

from .base_shape import BaseShape, HandleType, ShapeType


class UnitCircleShape(BaseShape):
    """Интерактивная единичная окружность с подвижным радиусом.

    При выделении можно перетаскивать точку на окружности,
    чтобы вращать радиус. Значения угла, sin и cos обновляются динамически.
    """

    def __init__(
        self,
        cx: float = 0.0,
        cy: float = 0.0,
        radius: float = 200.0,
        angle: float = math.pi / 4,
        pen_color: tuple[int, int, int] = (0, 0, 0),
        pen_width: float = 2.0,
        brush_color: tuple[int, int, int] | None = None,
        selected: bool = False,
    ):
        super().__init__(pen_color, pen_width, brush_color, selected)
        self._cx = cx
        self._cy = cy
        self._radius = radius
        # Угол радиуса в радианах (0 = вправо, против часовой стрелки)
        self._angle = angle

    def _get_shape_type(self) -> ShapeType:
        return ShapeType.UNIT_CIRCLE

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
    def angle(self) -> float:
        """Угол в радианах."""
        return self._angle

    @angle.setter
    def angle(self, value: float) -> None:
        self._angle = value

    def get_angle_degrees(self) -> float:
        """Угол в градусах (0..360)."""
        deg = math.degrees(self._angle) % 360
        if deg < 0:
            deg += 360
        return deg

    def get_sin(self) -> float:
        return math.sin(self._angle)

    def get_cos(self) -> float:
        return math.cos(self._angle)

    def get_point_on_circle(self) -> QPointF:
        """Возвращает точку на окружности, определяемую углом."""
        return QPointF(
            self._cx + self._radius * math.cos(self._angle),
            self._cy - self._radius * math.sin(self._angle),
        )

    def set_angle_from_point(self, point: QPointF) -> None:
        """Вычисляет угол из позиции мыши относительно центра."""
        dx = point.x() - self._cx
        dy = -(point.y() - self._cy)  # инвертируем Y (Qt Y вниз)
        self._angle = math.atan2(dy, dx)

    # ------------------------------------------------------------------
    # Abstract methods
    # ------------------------------------------------------------------

    def draw(self, painter: QPainter) -> None:
        painter.save()
        try:
            self._draw_axes(painter)
            self._draw_circle(painter)
            self._draw_radius(painter)
            self._draw_sin_cos_lines(painter)
            self._draw_angle_arc(painter)
            self._draw_labels(painter)
            self._draw_selection_box(painter)
        finally:
            painter.restore()

    def contains_point(self, point: QPointF) -> bool:
        dx = point.x() - self._cx
        dy = point.y() - self._cy
        return abs(dx) <= self._radius + 60 and abs(dy) <= self._radius + 60

    def move(self, dx: float, dy: float) -> None:
        self._cx += dx
        self._cy += dy

    def scale(self, factor: float, center: QPointF | None = None) -> None:
        self._radius *= factor
        if self._radius < 10.0:
            self._radius = 10.0

    def bounding_rect(self) -> QRectF:
        pad = self._radius + 60
        return self._safe_rect(
            self._cx - pad,
            self._cy - pad,
            2 * pad,
            2 * pad,
        )

    # ------------------------------------------------------------------
    # Отрисовка
    # ------------------------------------------------------------------

    def _draw_radius(self, painter: QPainter) -> None:
        """Рисует радиус до точки на окружности."""
        pen = QPen(QColor(0, 100, 200), max(self.pen_width + 1, 2.5))
        painter.setPen(pen)

        pt = self.get_point_on_circle()
        painter.drawLine(
            QPointF(self._cx, self._cy),
            pt,
        )

        # Точка на окружности
        painter.setPen(QColor(200, 50, 50))
        painter.drawEllipse(pt, 5, 5)

    def _draw_sin_cos_lines(self, painter: QPainter) -> None:
        """Рисует линии sin и cos от точки до осей."""
        pt = self.get_point_on_circle()

        # Линия cos (горизонтальная от центра до проекции на X)
        cos_color = QColor(40, 80, 200)
        pen = QPen(cos_color, 2)
        pen.setStyle(Qt.PenStyle.SolidLine)
        painter.setPen(pen)
        painter.drawLine(
            QPointF(self._cx, self._cy),
            QPointF(pt.x(), self._cy),
        )

        # Линия sin (вертикальная от проекции на X до точки)
        sin_color = QColor(200, 40, 40)
        pen = QPen(sin_color, 2)
        pen.setStyle(Qt.PenStyle.SolidLine)
        painter.setPen(pen)
        painter.drawLine(
            QPointF(pt.x(), self._cy),
            pt,
        )

    def _draw_angle_arc(self, painter: QPainter) -> None:
        """Рисует дугу угла."""
        pen = QPen(QColor(140, 80, 200), 2)
        painter.setPen(pen)

        arc_radius = min(self._radius * 0.2, 40)
        if arc_radius < 5:
            return

        # Qt drawArc: startAngle и spanAngle в 1/16 градуса,
        # положительный spanAngle рисует против часовой стрелки.
        # self._angle уже в математической системе (0 = вправо, + = против ЧС),
        # поэтому просто конвертируем в 1/16 градуса.
        start_angle = 0
        span_angle = math.degrees(self._angle) * 16

        painter.drawArc(
            int(self._cx - arc_radius),
            int(self._cy - arc_radius),
            int(2 * arc_radius),
            int(2 * arc_radius),
            int(start_angle),
            int(span_angle),
        )

    def _draw_labels(self, painter: QPainter) -> None:
        """Рисует подписи: угол, sin, cos, оси."""
        pt = self.get_point_on_circle()
        r = self._radius

        # Подписи осей
        font_axis = QFont("Arial", 10, QFont.Weight.Bold)
        painter.setFont(font_axis)
        painter.setPen(QColor(self.pen_color.red(), self.pen_color.green(), self.pen_color.blue()))
        painter.drawText(int(self._cx + r + 12), int(self._cy) + 4, "x")
        painter.drawText(int(self._cx) + 4, int(self._cy - r - 12), "y")

        # Единицы
        font_unit = QFont("Arial", 9)
        painter.setFont(font_unit)
        painter.drawText(int(self._cx + r) - 4, int(self._cy) + 14, "1")
        painter.drawText(int(self._cx - r) - 10, int(self._cy) + 14, "-1")
        painter.drawText(int(self._cx) + 6, int(self._cy - r) - 6, "1")
        painter.drawText(int(self._cx) + 6, int(self._cy + r) + 12, "-1")
        painter.drawText(int(self._cx) - 8, int(self._cy) + 14, "O")

        # Подпись точки M
        font_point = QFont("Arial", 10, QFont.Weight.Bold)
        painter.setFont(font_point)
        painter.setPen(QColor(200, 50, 50))
        offset_x = 10 if pt.x() >= self._cx else -25
        offset_y = -10 if pt.y() <= self._cy else 14
        painter.drawText(int(pt.x() + offset_x), int(pt.y() + offset_y), "M")

        # Значение угла
        angle_deg = self.get_angle_degrees()

        # Форматируем угол
        if abs(angle_deg - round(angle_deg)) < 0.01:
            angle_str = f"{int(angle_deg)}°"
        else:
            angle_str = f"{angle_deg:.1f}°"

        font_info = QFont("Arial", 10)
        font_info.setBold(True)
        painter.setFont(font_info)

        # Блок информации — правый верхний угол
        info_x = self._cx + r * 0.3
        info_y = self._cy - r * 0.5

        # Фон для блока
        painter.setPen(QPen(QColor(240, 240, 240, 220), 1))
        painter.setBrush(QColor(255, 255, 255, 200))
        rect = QRectF(info_x - 5, info_y - 15, 130, 55)
        painter.drawRect(rect)

        # Угол
        painter.setPen(QColor(140, 80, 200))
        painter.drawText(int(info_x), int(info_y) + 4, f"α = {angle_str}")

        # sin
        sin_color = QColor(200, 40, 40)
        painter.setPen(sin_color)
        painter.drawText(int(info_x), int(info_y) + 18, f"sin α = {self.get_sin():.3f}")

        # cos
        cos_color = QColor(40, 80, 200)
        painter.setPen(cos_color)
        painter.drawText(int(info_x), int(info_y) + 32, f"cos α = {self.get_cos():.3f}")

    # ------------------------------------------------------------------
    # Маркеры (handles)
    # ------------------------------------------------------------------

    def _handle_positions(self) -> list[tuple[float, float]]:
        """Центр + точка на окружности (для вращения радиуса)."""
        pt = self.get_point_on_circle()
        return [
            (self._cx, self._cy),  # центр — перемещение
            (pt.x(), pt.y()),  # точка на окружности — вращение
        ]

    def get_handle_type(self, point: QPointF, tolerance: float = 8.0) -> HandleType:
        """Определяет тип маркера под точкой.

        Точка на окружности — HandleType.BOTTOM_RIGHT (для вращения).
        Центр — HandleType.TOP_LEFT (для перемещения).
        """
        pt = self.get_point_on_circle()

        # Проверяем точку на окружности первой (она важнее)
        dx = point.x() - pt.x()
        dy = point.y() - pt.y()
        if math.sqrt(dx * dx + dy * dy) <= tolerance:
            return HandleType.BOTTOM_RIGHT

        # Проверяем центр
        dx = point.x() - self._cx
        dy = point.y() - self._cy
        if math.sqrt(dx * dx + dy * dy) <= tolerance:
            return HandleType.TOP_LEFT

        return HandleType.NONE

    def apply_handle_transform(
        self,
        handle: HandleType,
        point: QPointF,
        mouse_pos: QPointF,
        shift_pressed: bool = False,
    ) -> None:
        if handle == HandleType.TOP_LEFT:
            # Перемещение
            dx = mouse_pos.x() - point.x()
            dy = mouse_pos.y() - point.y()
            self._cx += dx
            self._cy += dy
        elif handle == HandleType.BOTTOM_RIGHT:
            # Вращение радиуса
            self.set_angle_from_point(mouse_pos)
            if shift_pressed:
                # Привязка к 15 градусам
                deg = math.degrees(self._angle)
                deg = round(deg / 15) * 15
                self._angle = math.radians(deg)

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
                "angle": self._angle,
            }
        )
        return d

    @classmethod
    def from_dict(cls, data: dict) -> UnitCircleShape:
        obj = cls(
            cx=data["cx"],
            cy=data["cy"],
            radius=data["radius"],
            angle=data.get("angle", math.pi / 4),
            pen_color=data["pen_color"],
            brush_color=data.get("brush_color"),
            pen_width=data.get("pen_width", 2.0),
        )
        obj._selected = data.get("selected", False)
        obj._rotation = data.get("rotation", 0.0)
        return obj
