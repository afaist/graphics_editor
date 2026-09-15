"""Фигура: Дуга (Arc)."""

from __future__ import annotations

import math
from typing import List, Optional, Tuple

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPen, QBrush

from .base_shape import BaseShape, HandleType, ShapeType


class ArcShape(BaseShape):
    """Дуга эллипса, заданная bounding rect, начальным и конечным углами.

    Углы измеряются в градусах по часовой стрелке от оси X (0° = правый край).
    Для отрисовки используется Qt::Arc (отрицательный span = против часовой).
    """

    def __init__(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        start_angle: float = 0.0,
        span_angle: float = 90.0,
        pen_color: Tuple[int, int, int] = (0, 0, 0),
        pen_width: float = 2.0,
        brush_color: Optional[Tuple[int, int, int]] = None,
        selected: bool = False,
    ):
        super().__init__(pen_color, pen_width, brush_color, selected)
        self._x = x
        self._y = y
        self._width = width
        self._height = height
        # Начальная точка клика для правильного вычисления bounding rect
        self._start_x = x
        self._start_y = y
        self._start_angle = start_angle
        self._span_angle = span_angle

    def _get_shape_type(self) -> ShapeType:
        return ShapeType.ARC

    def set_end_point(self, x: float, y: float) -> None:
        pass

    def set_size(self, width: float, height: float) -> None:
        self._width = width
        self._height = height

    def set_arc_params(self, sx: float, sy: float, width: float, height: float) -> None:
        """Устанавливает размер и углы дуги в зависимости от направления."""
        abs_w = abs(width)
        abs_h = abs(height)
        # rect всегда positive, top-left = min(sx, x)
        self._x = min(sx, sx + width)
        self._y = min(sy, sy + height)
        self._width = abs_w
        self._height = abs_h
        # Дуга рисуется в углу, соответствующем направлению перетаскивания
        if width >= 0 and height >= 0:
            self._start_angle = 0.0      # правый нижний угол rect
        elif width < 0 and height >= 0:
            self._start_angle = 90.0     # левый нижний угол rect
        elif width < 0 and height < 0:
            self._start_angle = 180.0    # левый верхний угол rect
        else:
            self._start_angle = 270.0    # правый верхний угол rect
        self._span_angle = 90.0

    def add_vertex(self, x: float, y: float) -> None:
        pass

    # ------------------------------------------------------------------
    # Свойства
    # ------------------------------------------------------------------

    @property
    def x(self) -> float:
        return self._x

    @property
    def y(self) -> float:
        return self._y

    @property
    def width(self) -> float:
        return self._width

    @property
    def height(self) -> float:
        return self._height

    @property
    def start_angle(self) -> float:
        return self._start_angle

    @start_angle.setter
    def start_angle(self, angle: float) -> None:
        self._start_angle = angle % 360.0

    @property
    def span_angle(self) -> float:
        return self._span_angle

    @span_angle.setter
    def span_angle(self, angle: float) -> None:
        self._span_angle = angle

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

            # rect всегда positive, x/y = top-left
            w = self._width
            h = self._height

            # Дуга рисуется в углу, соответствующем направлению перетаскивания
            start_16 = int(self._start_angle * 16)
            span_16 = -int(self._span_angle * 16)

            if w > 0.1 and h > 0.1:
                painter.drawArc(QRectF(self._x, self._y, w, h), start_16, span_16)
            else:
                painter.drawPoint(QPointF(self._x + w / 2, self._y + h / 2))

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
        self._x += dx
        self._y += dy

    def rotate(self, angle: float, center: Optional[QPointF] = None) -> None:
        if center is None:
            center = QPointF(self._x + self._width / 2, self._y + self._height / 2)
        self._rotation = (self._rotation + angle) % 360.0

    def scale(self, factor: float, center: Optional[QPointF] = None) -> None:
        if center is None:
            center = QPointF(self._x + self._width / 2, self._y + self._height / 2)
        self._width *= factor
        self._height *= factor
        if self._width < 0.1:
            self._width = 0.1
        if self._height < 0.1:
            self._height = 0.1
        if self._width < 0:
            self._x += self._width
            self._width = -self._width
        if self._height < 0:
            self._y += self._height
            self._height = -self._height

    def bounding_rect(self) -> QRectF:
        pad = max(self.pen_width / 2 + 5, 6)
        return self._safe_rect(
            self._x - pad,
            self._y - pad,
            self._width + pad * 2,
            self._height + pad * 2,
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
            self._x = mouse_pos.x()
            self._y = mouse_pos.y()
        elif handle == HandleType.TOP_RIGHT:
            self._y = mouse_pos.y()
            self._width = mouse_pos.x() - self._x
        elif handle == HandleType.BOTTOM_LEFT:
            self._x = mouse_pos.x()
            self._height = mouse_pos.y() - self._y
        elif handle == HandleType.BOTTOM_RIGHT:
            self._width = mouse_pos.x() - self._x
            self._height = mouse_pos.y() - self._y

    # ------------------------------------------------------------------
    # Сериализация
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update({
            "x": self._x,
            "y": self._y,
            "width": self._width,
            "height": self._height,
            "start_angle": self._start_angle,
            "span_angle": self._span_angle,
        })
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "ArcShape":
        obj = cls(
            x=data["x"],
            y=data["y"],
            width=data["width"],
            height=data["height"],
            start_angle=data.get("start_angle", 0.0),
            span_angle=data.get("span_angle", 90.0),
            pen_color=data["pen_color"],
            brush_color=data.get("brush_color"),
            pen_width=data.get("pen_width", 2.0),
        )
        obj._selected = data.get("selected", False)
        obj._rotation = data.get("rotation", 0.0)
        obj._start_x = data.get("start_x", data["x"])
        obj._start_y = data.get("start_y", data["y"])
        return obj
