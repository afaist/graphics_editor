"""Фигура: Точка."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QPainter, QPen

from .base_shape import BaseShape, HandleType, ShapeType


class PointShape(BaseShape):
    """Точка на холсте."""

    def __init__(
        self,
        x: float,
        y: float,
        radius: float = 2.0,
        pen_color: tuple[int, int, int] = (0, 0, 0),
        brush_color: tuple[int, int, int] | None = (255, 255, 255),
        pen_width: float = 2.0,
        selected: bool = False,
    ):
        super().__init__(pen_color, pen_width, brush_color, selected)
        self._x = x
        self._y = y
        self.radius = radius  # используем сеттер для валидации

    def _get_shape_type(self) -> ShapeType:
        return ShapeType.POINT

    def set_end_point(self, x: float, y: float) -> None:
        pass  # Точка не имеет конечной точки

    def set_size(self, width: float, height: float) -> None:
        pass  # Точка не имеет размера

    def add_vertex(self, x: float, y: float) -> None:
        pass  # Точка не имеет вершин

    # ------------------------------------------------------------------
    # Свойства
    # ------------------------------------------------------------------

    @property
    def x(self) -> float:
        return self._x

    @x.setter
    def x(self, value: float) -> None:
        self._x = value

    @property
    def y(self) -> float:
        return self._y

    @y.setter
    def y(self, value: float) -> None:
        self._y = value

    @property
    def radius(self) -> float:
        return self._radius

    @radius.setter
    def radius(self, r: float) -> None:
        if r < 1.0:
            raise ValueError("Radius must be at least 1.0")
        self._radius = r

    # ------------------------------------------------------------------
    # Abstract methods implementation
    # ------------------------------------------------------------------

    def draw(self, painter: QPainter) -> None:
        """Отрисовать точку на QPainter."""
        painter.save()
        try:
            # Настройка пера и кисти
            pen = QPen(self.pen_color, self.pen_width)
            painter.setPen(pen)

            if self.brush_color is not None:
                painter.setBrush(QBrush(self.brush_color))
            else:
                painter.setBrush(Qt.BrushStyle.NoBrush)

            # Применяем поворот вокруг точки (для точки поворот визуального эффекта не даёт, но для согласованности)
            if abs(self._rotation) > 0.01:
                painter.translate(self._x, self._y)
                painter.rotate(self._rotation)
                painter.translate(-self._x, -self._y)

            # Отрисовка точки (маленький эллипс)
            painter.drawEllipse(QPointF(self._x, self._y), self._radius, self._radius)

            # Если точка выделена, рисуем рамку выделения
            if self._selected:
                selection_pen = QPen(QColor(0, 120, 255), 1)
                painter.setPen(selection_pen)
                painter.setBrush(Qt.BrushStyle.NoBrush)

                r = self._radius + 4
                painter.drawRect(QRectF(self._x - r, self._y - r, r * 2, r * 2))
        finally:
            painter.restore()

    def contains_point(self, point: QPointF) -> bool:
        """Проверить, принадлежит ли точка фигуре."""
        dx = point.x() - self._x
        dy = point.y() - self._y
        distance_squared = dx * dx + dy * dy
        tolerance_radius = self._radius + 4  # допуск для удобства клика
        return distance_squared <= tolerance_radius * tolerance_radius

    def move(self, dx: float, dy: float) -> None:
        """Переместить точку на (dx, dy)."""
        self._x += dx
        self._y += dy

    def rotate(self, angle: float, center: QPointF | None = None) -> None:
        """Повернуть точку на angle градусов."""
        # Для точки вращение не меняет её положение
        self._rotation = (self._rotation + angle) % 360.0

    def scale(self, factor: float, center: QPointF | None = None) -> None:
        """Масштабировать точку."""
        if factor <= 0:
            raise ValueError("Scale factor must be positive")
        self._radius *= factor
        self._radius = max(1.0, self._radius)

    def bounding_rect(self) -> QRectF:
        """Вернуть bounding box фигуры."""
        r = self._radius + 4  # добавляем допуск для выделения
        return self._safe_rect(self._x - r, self._y - r, r * 2, r * 2)

    def get_handles(self) -> list[QPointF]:
        """Вернуть список маркеров преобразования."""
        return [QPointF(self._x, self._y)]

    def get_handle_type(self, point: QPointF, tolerance: float = 5.0) -> HandleType:
        """Определить тип маркера под указанной точкой."""
        dx = point.x() - self._x
        dy = point.y() - self._y
        distance_squared = dx * dx + dy * dy
        max_distance = (tolerance + self._radius) ** 2

        if distance_squared <= max_distance:
            return HandleType.MOVE
        return HandleType.NONE

    def apply_handle_transform(
        self, handle: HandleType, point: QPointF, mouse_pos: QPointF
    ) -> None:
        """Применить преобразование через маркер."""
        if handle == HandleType.MOVE:
            self._x = mouse_pos.x()
            self._y = mouse_pos.y()

    # ------------------------------------------------------------------
    # Сериализация
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Сериализовать фигуру в словарь."""
        d = super().to_dict()
        d.update({"x": self._x, "y": self._y, "radius": self._radius})
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PointShape:
        """Десериализовать точку из словаря."""
        obj = cls(
            x=data["x"],
            y=data["y"],
            radius=data.get("radius", 2.0),
            pen_color=data["pen_color"],
            brush_color=data.get("brush_color"),
            pen_width=data.get("pen_width", 2.0),
            selected=data.get("selected", False),
        )
        # Устанавливаем дополнительные свойства
        obj._rotation = data.get("rotation", 0.0)
        obj.id = data["id"]
        obj.group_id = data.get("group_id")
        return obj
