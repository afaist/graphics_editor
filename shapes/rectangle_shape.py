"""Фигура: Прямоугольник (и квадрат)."""


from __future__ import annotations

import math
from typing import List, Optional, Tuple

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QPainter, QPen

from .base_shape import BaseShape, HandleType, ShapeType

class RectangleShape(BaseShape):
    """Прямоугольник, заданный левой верхней точкой и размерами."""

    def __init__(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
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
        self._rotation = 0.0  # Инициализируем вращение

    def set_end_point(self, x: float, y: float) -> None:
        pass  # Прямоугольник не использует set_end_point

    def set_size(self, width: float, height: float) -> None:
        self._width = width
        self._height = height

    def add_vertex(self, x: float, y: float) -> None:
        pass  # Прямоугольник не имеет вершин для добавления

    def _get_shape_type(self) -> ShapeType:
        return ShapeType.RECTANGLE

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
    def right(self) -> float:
        return self._x + self._width

    @property
    def bottom(self) -> float:
        return self._y + self._height

    # ------------------------------------------------------------------
    # Abstract methods
    # ------------------------------------------------------------------

    def draw(self, painter: QPainter) -> None:
        painter.save()
        pen = QPen(self.pen_color, self.pen_width)
        painter.setPen(pen)
        if self.brush_color:
            painter.setBrush(QBrush(self.brush_color))
        else:
            painter.setBrush(Qt.BrushStyle.NoBrush)

        # Отрисовка прямоугольника
        painter.drawRect(
            QRectF(self._x, self._y, self._width, self._height)
        )

        if self._selected:
            pen.setColor(QColor(0, 120, 255))
            pen.setWidth(1)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            for hx, hy in self._handle_positions():
                painter.drawRect(int(hx) - 4, int(hy) - 4, 8, 8)

        painter.restore()

    def contains_point(self, point: QPointF) -> bool:
        rect = QRectF(self._x, self._y, self._width, self._height)
        # Учитываем поворот
        if abs(self._rotation) < 0.01:
            return rect.contains(point)
        # Упрощённо — проверка по bounding rect
        return self.bounding_rect().contains(point)

    def move(self, dx: float, dy: float) -> None:
        self._x += dx
        self._y += dy

    def rotate(self, angle: float, center: Optional[QPointF] = None) -> None:
        if center is None:
            center = QPointF(
                self._x + self._width / 2, self._y + self._height / 2
            )
        self._rotation = (self._rotation + angle) % 360.0

    def scale(self, factor: float, center: Optional[QPointF] = None) -> None:
        if center is None:
            center = QPointF(
                self._x + self._width / 2, self._y + self._height / 2
            )
        self._width *= factor
        self._height *= factor
        if self._width < 1:
            self._width = 1
        if self._height < 1:
            self._height = 1

    def bounding_rect(self) -> QRectF:
        pad = max(self.pen_width / 2 + 5, 6)
        if abs(self._rotation) < 0.01:
            return QRectF(
                self._x - pad,
                self._y - pad,
                self._width + pad * 2,
                self._height + pad * 2,
            )
        return QRectF(
            self._x - pad,
            self._y - pad,
            abs(self._width) + pad * 2,
            abs(self._height) + pad * 2,
        )

    def _handle_positions(self) -> List[Tuple[float, float]]:
        x, y, w, h = self._x, self._y, self._width, self._height
        return [
            (x, y),  # TL
            (x + w, y),  # TR
            (x, y + h),  # BL
            (x + w, y + h),  # BR
        ]

    def get_handles(self) -> List[QPointF]:
        return [QPointF(hx, hy) for hx, hy in self._handle_positions()]

    def get_handle_type(
        self, point: QPointF, tolerance: float = 5.0
    ) -> HandleType:
        for i, (hx, hy) in enumerate(self._handle_positions()):
            # Вычисляем расстояние вручную вместо distanceTo
            dx = point.x() - hx
            dy = point.y() - hy
            distance = math.sqrt(dx * dx + dy * dy)
            if distance <= tolerance:
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
        d = super(RectangleShape, self).to_dict()
        d.update(
            {
                "x": self._x,
                "y": self._y,
                "width": self._width,
                "height": self._height,
                "rotation": self._rotation,
            }
        )
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "RectangleShape":
        obj = cls(
            x=data["x"],
            y=data["y"],
            width=data["width"],
            height=data["height"],
            pen_color=data["pen_color"],
            brush_color=data.get("brush_color"),
            pen_width=data.get("pen_width", 2.0),
        )
        obj._selected = data.get("selected", False)
        obj._rotation = data.get("rotation", 0.0)
        return obj
