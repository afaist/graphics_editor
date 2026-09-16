"""Фигура: Дуга (Arc)."""

from __future__ import annotations

import math
from typing import List, Optional, Tuple

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPen, QBrush

from .base_shape import BaseShape, HandleType, ShapeType


class ArcShape(BaseShape):
    """Дуга окружности, заданная центром, радиусом, начальным и конечным углами.

    Углы измеряются в градусах по часовой стрелке от оси X (0° = 3 часа).
    """

    def __init__(
        self,
        cx: float,
        cy: float,
        radius: float,
        start_angle: float = 0.0,
        end_angle: float = 90.0,
        pen_color: Tuple[int, int, int] = (0, 0, 0),
        pen_width: float = 2.0,
        brush_color: Optional[Tuple[int, int, int]] = None,
        selected: bool = False,
    ):
        super().__init__(pen_color, pen_width, brush_color, selected)
        self._cx = cx
        self._cy = cy
        self._radius = radius
        self._start_angle = start_angle % 360.0
        self._end_angle = end_angle % 360.0

    def _get_shape_type(self) -> ShapeType:
        return ShapeType.ARC

    def set_end_point(self, x: float, y: float) -> None:
        pass

    def set_size(self, width: float, height: float) -> None:
        pass

    def add_vertex(self, x: float, y: float) -> None:
        pass

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

    @property
    def start_angle(self) -> float:
        return self._start_angle

    @start_angle.setter
    def start_angle(self, angle: float) -> None:
        self._start_angle = angle % 360.0

    @property
    def end_angle(self) -> float:
        return self._end_angle

    @end_angle.setter
    def end_angle(self, angle: float) -> None:
        self._end_angle = angle % 360.0

    # ------------------------------------------------------------------
    # Вычисляемые свойства
    # ------------------------------------------------------------------

    @property
    def span_angle(self) -> float:
        """Положительный угол дуги (по часовой стрелке)."""
        span = self._end_angle - self._start_angle
        if span <= 0:
            span += 360.0
        return span

    def _bounding_rect(self) -> QRectF:
        """Ограничивающий прямоугольник окружности."""
        r = self._radius
        return QRectF(self._cx - r, self._cy - r, 2 * r, 2 * r)

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

            rect = self._bounding_rect()
            w = rect.width()
            h = rect.height()

            if w > 0.1 and h > 0.1:
                # Qt использует углы в единицах 1/16 градуса
                # start_angle — смещение от 0 (3 часа)
                # span_angle — протяжённость по часовой стрелке
                start_16 = int(self._start_angle * 16)
                span_16 = int(self.span_angle * 16)
                painter.drawArc(rect, start_16, span_16)
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
        # Упрощённо — проверяем по bounding rect.
        return self.bounding_rect().contains(point)

    def move(self, dx: float, dy: float) -> None:
        self._cx += dx
        self._cy += dy

    def rotate(self, angle: float, center: Optional[QPointF] = None) -> None:
        if center is None:
            center = QPointF(self._cx, self._cy)
        self._rotation = (self._rotation + angle) % 360.0

    def scale(self, factor: float, center: Optional[QPointF] = None) -> None:
        self._radius *= factor
        if self._radius < 0.1:
            self._radius = 0.1

    def bounding_rect(self) -> QRectF:
        pad = max(self.pen_width / 2 + 5, 6)
        rect = self._bounding_rect()
        return QRectF(
            rect.left() - pad,
            rect.top() - pad,
            rect.width() + pad * 2,
            rect.height() + pad * 2,
        )

    # ------------------------------------------------------------------
    # Маркеры (handles)
    # ------------------------------------------------------------------

    def _handle_positions(self) -> List[Tuple[float, float]]:
        """4 угловых маркера как у прямоугольника."""
        br = self.bounding_rect()
        return [
            (br.left(), br.top()),
            (br.right(), br.top()),
            (br.left(), br.bottom()),
            (br.right(), br.bottom()),
        ]

    def get_handles(self) -> List[QPointF]:
        return [QPointF(hx, hy) for hx, hy in self._handle_positions()]

    def get_handle_type(self, point: QPointF, tolerance: float = 5.0) -> HandleType:
        import math
        for i, (hx, hy) in enumerate(self._handle_positions()):
            dx = point.x() - hx
            dy = point.y() - hy
            if math.sqrt(dx * dx + dy * dy) <= tolerance:
                return HandleType(i + 2)  # 2..5
        return HandleType.NONE

    def apply_handle_transform(
        self, handle: HandleType, point: QPointF, mouse_pos: QPointF
    ) -> None:
        if handle == HandleType.TOP_LEFT:
            self._cx = mouse_pos.x()
            self._cy = mouse_pos.y()
        elif handle == HandleType.BOTTOM_RIGHT:
            self._radius = abs(mouse_pos.x() - self._cx)

    # ------------------------------------------------------------------
    # Сериализация
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update({
            "cx": self._cx,
            "cy": self._cy,
            "radius": self._radius,
            "start_angle": self._start_angle,
            "end_angle": self._end_angle,
        })
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "ArcShape":
        obj = cls(
            cx=data["cx"],
            cy=data["cy"],
            radius=data["radius"],
            start_angle=data.get("start_angle", 0.0),
            end_angle=data.get("end_angle", 90.0),
            pen_color=data["pen_color"],
            brush_color=data.get("brush_color"),
            pen_width=data.get("pen_width", 2.0),
        )
        obj._selected = data.get("selected", False)
        obj._rotation = data.get("rotation", 0.0)
        return obj
