"""Фигура: Окружность."""

from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPen

from .base_shape import BaseShape, HandleType, ShapeType


class CircleShape(BaseShape):
    """Окружность, заданная центром и радиусом."""

    def __init__(
        self,
        cx: float,
        cy: float,
        radius: float,
        pen_color: tuple[int, int, int] = (0, 0, 0),
        pen_width: float = 2.0,
        brush_color: tuple[int, int, int] | None = None,
        selected: bool = False,
    ):
        super().__init__(pen_color, pen_width, brush_color, selected)
        self._cx = cx
        self._cy = cy
        self._radius = radius

    def set_size(self, width: float, height: float) -> None:
        self._radius = max(width, height) / 2

    def _get_shape_type(self) -> ShapeType:
        return ShapeType.CIRCLE

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
        if value > 0.1:
            self._radius = value

    # ------------------------------------------------------------------
    # Abstract methods
    # ------------------------------------------------------------------

    def draw(self, painter: QPainter) -> None:
        painter.save()
        try:
            pen = QPen(self.pen_color, self.pen_width)
            painter.setPen(pen)
            if self.brush_color:
                painter.setBrush(self.brush_color)

            # Применяем поворот вокруг центра окружности
            if abs(self._rotation) > 0.01:
                painter.translate(self._cx, self._cy)
                painter.rotate(self._rotation)
                painter.translate(-self._cx, -self._cy)

            if self._radius > 0.05:
                painter.drawEllipse(
                    QPointF(self._cx, self._cy),
                    self._radius,
                    self._radius,
                )
            else:
                painter.drawPoint(QPointF(self._cx, self._cy))

            if self._selected:
                pen.setColor(QColor(0, 120, 255))
                pen.setWidth(1)
                painter.setPen(pen)
                painter.setBrush(Qt.BrushStyle.NoBrush)
                for hx, hy in self._handle_positions():
                    painter.drawRect(int(hx) - 4, int(hy) - 4, 8, 8)
        finally:
            painter.restore()

    def contains_point(self, point: QPointF) -> bool:
        dx = point.x() - self._cx
        dy = point.y() - self._cy
        return dx * dx + dy * dy <= self._radius * self._radius

    def move(self, dx: float, dy: float) -> None:
        self._cx += dx
        self._cy += dy

    def scale(self, factor: float, center: QPointF | None = None) -> None:
        self._radius *= factor
        if self._radius < 0.1:
            self._radius = 0.1

    def bounding_rect(self) -> QRectF:
        pad = self._compute_bounding_padding(self.pen_width)
        r = self._radius
        return self._safe_rect(
            self._cx - r - pad,
            self._cy - r - pad,
            2 * r + pad * 2,
            2 * r + pad * 2,
        )

    # ------------------------------------------------------------------
    # Маркеры (handles)
    # ------------------------------------------------------------------

    def _handle_positions(self) -> list[tuple[float, float]]:
        """4 маркера: центр + 3 точки на окружности (0°, 90°, 180°)."""
        r = self._radius
        return [
            (self._cx, self._cy),  # центр
            (self._cx + r, self._cy),  # право
            (self._cx, self._cy - r),  # верх
            (self._cx - r, self._cy),  # лево
        ]

    def apply_handle_transform(
        self,
        handle: HandleType,
        point: QPointF,
        mouse_pos: QPointF,
        shift_pressed: bool = False,
    ) -> None:
        if handle == HandleType.TOP_LEFT:
            # Центр — перемещение
            dx = mouse_pos.x() - point.x()
            dy = mouse_pos.y() - point.y()
            self._cx += dx
            self._cy += dy
        elif handle == HandleType.BOTTOM_RIGHT:
            # Правая точка — изменение радиуса
            dx = mouse_pos.x() - self._cx
            dy = mouse_pos.y() - self._cy
            self._radius = (dx * dx + dy * dy) ** 0.5
            if self._radius < 0.1:
                self._radius = 0.1
        elif handle == HandleType.TOP_CENTER:
            # Верхняя точка — изменение радиуса
            dy = self._cy - mouse_pos.y()
            self._radius = abs(dy)
            if self._radius < 0.1:
                self._radius = 0.1
        elif handle == HandleType.LEFT_CENTER:
            # Левая точка — изменение радиуса
            dx = self._cx - mouse_pos.x()
            self._radius = abs(dx)
            if self._radius < 0.1:
                self._radius = 0.1

    # ------------------------------------------------------------------
    # Позиция для undo
    # ------------------------------------------------------------------

    def get_position_data(self) -> dict:
        return {
            "cx": self._cx,
            "cy": self._cy,
            "radius": self._radius,
        }

    def restore_position_data(self, data: dict) -> None:
        self._cx = data["cx"]
        self._cy = data["cy"]
        self._radius = data["radius"]

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
    def from_dict(cls, data: dict) -> CircleShape:
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
