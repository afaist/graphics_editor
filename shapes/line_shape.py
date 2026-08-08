"""Фигуры: Отрезок, Прямая, Луч."""

from __future__ import annotations

import math
from typing import List, Optional, Tuple

from PySide6.QtCore import QLineF, QPointF, QRectF
from PySide6.QtGui import QColor, QPainter, QPen

from .base_shape import BaseShape, HandleType, ShapeType


# Константа для "бесконечности" (достаточно большое число для масштаба экрана)
INFINITY = 1000000000.0


class LineShape(BaseShape):
    """Отрезок, луч или прямая."""

    def __init__(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        shape_type: ShapeType = ShapeType.LINE,
        pen_color: Tuple[int, int, int] = (0, 0, 0),
        pen_width: float = 2.0,
        selected: bool = False,
    ):
        # !!! Инициализируем _shape_type ДО вызова super().__init__() !!!
        # Иначе base_shape.__init__ вызовет self._get_shape_type(), который
        # попытается обратиться к несуществующему self._shape_type
        self._shape_type = shape_type
        self._x1 = x1
        self._y1 = y1
        self._x2 = x2
        self._y2 = y2
        
        super().__init__(pen_color, pen_width, None, selected)
        
    def set_end_point(self, x: float, y: float) -> None:
        """Обновляет вторую точку. Для линий/лучей это меняет направление."""
        self._x2 = x
        self._y2 = y

    def set_size(self, width: float, height: float) -> None:
        pass

    def add_vertex(self, x: float, y: float) -> None:
        pass
        
    def _get_shape_type(self) -> ShapeType:
        return self._shape_type

    # ------------------------------------------------------------------
    # Свойства
    # ------------------------------------------------------------------

    @property
    def x1(self) -> float:
        return self._x1

    @property
    def y1(self) -> float:
        return self._y1

    @property
    def x2(self) -> float:
        return self._x2

    @property
    def y2(self) -> float:
        return self._y2

    def length(self) -> float:
        dx = self._x2 - self._x1
        dy = self._y2 - self._y1
        return math.sqrt(dx * dx + dy * dy)

    # ------------------------------------------------------------------
    # Abstract methods
    # ------------------------------------------------------------------

    def draw(self, painter: QPainter) -> None:
        painter.save()
        pen = QPen(self.pen_color, self.pen_width)
        painter.setPen(pen)

        if self._shape_type == ShapeType.RAY:
            # Луч: начинается в (x1, y1), проходит через (x2, y2)
            # Вычисляем вектор направления
            dx = self._x2 - self._x1
            dy = self._y2 - self._y1
            
            # Если точки совпадают, рисуем точку или короткий отрезок
            length_sq = dx*dx + dy*dy
            if length_sq < 1e-6:
                 painter.drawLine(QPointF(self._x1, self._y1), QPointF(self._x1 + 10, self._y1 + 10))
            else:
                # Продлеваем линию далеко за пределы сцены
                end_x = self._x1 + dx * INFINITY
                end_y = self._y1 + dy * INFINITY
                painter.drawLine(QPointF(self._x1, self._y1), QPointF(end_x, end_y))

        elif self._shape_type == ShapeType.INFINITE_LINE:
            # Прямая: проходит через (x1, y1) и (x2, y2) в обе стороны
            dx = self._x2 - self._x1
            dy = self._y2 - self._y1
            
            length_sq = dx*dx + dy*dy
            if length_sq < 1e-6:
                # Если точки совпадают, прямую нарисовать невозможно, рисуем точку
                painter.drawLine(QPointF(self._x1, self._y1), QPointF(self._x1 + 10, self._y1 + 10))
            else:
                # Линия начинается за точкой 1 в обратном направлении и заканчивается за точкой 2
                start_x = self._x1 - dx * INFINITY
                start_y = self._y1 - dy * INFINITY
                end_x = self._x2 + dx * INFINITY
                end_y = self._y2 + dy * INFINITY
                painter.drawLine(QPointF(start_x, start_y), QPointF(end_x, end_y))
        
        else:
            # Обычный отрезок (LINE)
            painter.drawLine(QPointF(self._x1, self._y1), QPointF(self._x2, self._y2))

        # Концевые маркеры выделения
        if self._selected:
            pen.setColor(QColor(0, 120, 255))
            pen.setWidth(1)
            painter.setPen(pen)
            for px, py in [(self._x1, self._y1), (self._x2, self._y2)]:
                painter.drawRect(int(px) - 5, int(py) - 5, 10, 10)

        painter.restore()

    def contains_point(self, point: QPointF) -> bool:
        """Проверяет, находится ли точка близко к линии."""
        return (
            self._dist_to_line(point.x(), point.y())
            <= max(self.pen_width / 2 + 4, 5)
        )

    def _dist_to_line(self, px: float, py: float) -> float:
        """Расстояние от точки до бесконечной прямой (или луча/отрезка)."""
        x1, y1, x2, y2 = self._x1, self._y1, self._x2, self._y2
        dx, dy = x2 - x1, y2 - y1
        length_sq = dx * dx + dy * dy
        
        if length_sq < 1e-6:
            return math.hypot(px - x1, py - y1)

        t = ((px - x1) * dx + (py - y1) * dy) / length_sq

        # Логика различается для LINE, RAY, INFINITE_LINE
        if self._shape_type == ShapeType.LINE:
            # Для отрезка: проецируем на отрезок [0, 1]
            t = max(0.0, min(1.0, t))
        elif self._shape_type == ShapeType.RAY:
            # Для луча: проецируем на [0, +inf)
            # Если t < 0, значит точка "за" началом луча. 
            # Ближайшая точка - это начало луча.
            if t < 0:
                return math.hypot(px - x1, py - y1)
        # Для INFINITE_LINE t может быть любым, проецируем на всю линию

        proj_x = x1 + t * dx
        proj_y = y1 + t * dy
        return math.hypot(px - proj_x, py - proj_y)

    def move(self, dx: float, dy: float) -> None:
        self._x1 += dx
        self._y1 += dy
        self._x2 += dx
        self._y2 += dy

    def rotate(self, angle: float, center: Optional[QPointF] = None) -> None:
        if center is None:
            center = QPointF((self._x1 + self._x2) / 2, (self._y1 + self._y2) / 2)
        
        # Вращаем обе точки вокруг центра
        rx1, ry1 = self._rotate_point(self._x1, self._y1, center.x(), center.y(), angle)
        rx2, ry2 = self._rotate_point(self._x2, self._y2, center.x(), center.y(), angle)
        
        self._x1, self._y1 = rx1, ry1
        self._x2, self._y2 = rx2, ry2

    @staticmethod
    def _rotate_point(
        x: float, y: float, cx: float, cy: float, angle_deg: float
    ) -> Tuple[float, float]:
        rad = math.radians(angle_deg)
        cos_a, sin_a = math.cos(rad), math.sin(rad)
        dx, dy = x - cx, y - cy
        return cx + dx * cos_a - dy * sin_a, cy + dx * sin_a + dy * cos_a

    def scale(self, factor: float, center: Optional[QPointF] = None) -> None:
        # Для линий масштабирование относительно центра может искажать бесконечные линии,
        # но для простоты масштабируем относительно центра фигуры или заданного центра
        if center is None:
            # Для бесконечных линий центр не имеет смысла для масштаба, но используем x1 для простоты
            # или середну x1 и x2.
            center = QPointF((self._x1 + self._x2) / 2, (self._y1 + self._y2) / 2)
            
        self._x1, self._y1 = self._scale_point(self._x1, self._y1, center.x(), center.y(), factor)
        self._x2, self._y2 = self._scale_point(self._x2, self._y2, center.x(), center.y(), factor)

    @staticmethod
    def _scale_point(
        x: float, y: float, cx: float, cy: float, factor: float
    ) -> Tuple[float, float]:
        return cx + (x - cx) * factor, cy + (y - cy) * factor

    def bounding_rect(self) -> QRectF:
        """Возвращает ограничивающий прямоугольник."""
        # Для бесконечных линий bounding_rect должен быть бесконечно большим, 
        # чтобы включал всю сцену или очень большую область.
        if self._shape_type in (ShapeType.RAY, ShapeType.INFINITE_LINE):
            # Возвращаем очень большой прямоугольник
            return QRectF(-INFINITY, -INFINITY, INFINITY * 2, INFINITY * 2)
        
        x_min = min(self._x1, self._x2)
        x_max = max(self._x1, self._x2)
        y_min = min(self._y1, self._y2)
        y_max = max(self._y1, self._y2)
        pad = max(self.pen_width / 2 + 4, 5)
        return QRectF(x_min - pad, y_min - pad, x_max - x_min + pad * 2, y_max - y_min + pad * 2)

    def get_handles(self) -> List[QPointF]:
        return [QPointF(self._x1, self._y1), QPointF(self._x2, self._y2)]

    def get_handle_type(
        self, point: QPointF, tolerance: float = 5.0
    ) -> HandleType:
        d1 = QLineF(point, QPointF(self._x1, self._y1)).length()
        d2 = QLineF(point, QPointF(self._x2, self._y2)).length()

        if d1 <= tolerance:
            return HandleType.TOP_LEFT
        if d2 <= tolerance:
            return HandleType.BOTTOM_RIGHT
        return HandleType.NONE

    def apply_handle_transform(
        self, handle: HandleType, point: QPointF, mouse_pos: QPointF
    ) -> None:
        if handle == HandleType.TOP_LEFT:
            self._x1 = mouse_pos.x()
            self._y1 = mouse_pos.y()
        elif handle == HandleType.BOTTOM_RIGHT:
            self._x2 = mouse_pos.x()
            self._y2 = mouse_pos.y()

    # ------------------------------------------------------------------
    # Сериализация
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update({
            "x1": self._x1, 
            "y1": self._y1, 
            "x2": self._x2, 
            "y2": self._y2,
            "shape_type": self._shape_type.value
        })
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "LineShape":
        shape_type_val = data.get("shape_type", "line")
        # Преобразуем строковое значение обратно в Enum, если нужно, или используйте функцию-карту
        # Здесь предполагаем, что ShapeType уже импортирован и доступен
        from .base_shape import ShapeType
        shape_type = ShapeType(shape_type_val)

        obj = cls(
            x1=data["x1"],
            y1=data["y1"],
            x2=data["x2"],
            y2=data["y2"],
            shape_type=shape_type,
            pen_color=data["pen_color"],
            pen_width=data.get("pen_width", 2.0),
        )
        obj._selected = data.get("selected", False)
        obj._rotation = data.get("rotation", 0.0)
        return obj