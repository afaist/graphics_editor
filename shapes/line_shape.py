# shapes/line_shape.py
"""Фигуры: Отрезок, Прямая, Луч."""

from __future__ import annotations

import math

from PySide6.QtCore import QLineF, QPointF, QRectF
from PySide6.QtGui import QColor, QPainter, QPen

from .base_shape import BaseShape, HandleType, ShapeType

# Безопасный лимит координат для "бесконечных" линий.
SAFE_INFINITY = 10_000.0


class LineShape(BaseShape):
    """Отрезок, луч или прямая."""

    def __init__(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        shape_type: ShapeType = ShapeType.LINE,
        pen_color: tuple[int, int, int] = (0, 0, 0),
        pen_width: float = 2.0,
        selected: bool = False,
    ):
        # !!! Инициализируем _shape_type ДО вызова super().__init__() !!!
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
        # Защита: painter может быть невалидным при краше Qt
        if painter is None:
            return
        painter.save()
        try:
            # Валидация pen_width — NaN/inf вызывают segfault в QPen
            pw = self.pen_width
            if not isinstance(pw, (int, float)) or not math.isfinite(pw) or pw <= 0:
                pw = 2.0

            pen = QPen(self.pen_color, pw)
            painter.setPen(pen)

            x1, y1 = self._x1, self._y1
            x2, y2 = self._x2, self._y2

            # Защита от NaN
            if math.isnan(x1) or math.isnan(y1) or math.isnan(x2) or math.isnan(y2):
                return

            # Защита от infinity
            if (
                not math.isfinite(x1)
                or not math.isfinite(y1)
                or not math.isfinite(x2)
                or not math.isfinite(y2)
            ):
                return

            # Валидация: если точки совпадают или отрезок слишком мал
            dist = self.length()

            if self._shape_type == ShapeType.RAY:
                dx = x2 - x1
                dy = y2 - y1
                length_sq = dx * dx + dy * dy

                if length_sq > SAFE_INFINITY:
                    # Используем предвычисленный SAFE_INFINITY
                    # Нормализуем вектор, чтобы избежать переполнения при сильном зуме
                    length = math.sqrt(length_sq)
                    limit = SAFE_INFINITY / length
                    end_x = x1 + dx * limit
                    end_y = y1 + dy * limit
                    painter.drawLine(QPointF(x1, y1), QPointF(end_x, end_y))
                else:
                    painter.drawLine(QPointF(x1, y1), QPointF(x1 + 1, y1 + 1))

            elif self._shape_type == ShapeType.INFINITE_LINE:
                dx = x2 - x1
                dy = y2 - y1
                length_sq = dx * dx + dy * dy

                if length_sq > SAFE_INFINITY:
                    length = math.sqrt(length_sq)
                    limit = SAFE_INFINITY / length
                    start_x = x1 - dx * limit
                    start_y = y1 - dy * limit
                    end_x = x2 + dx * limit
                    end_y = y2 + dy * limit
                    painter.drawLine(QPointF(start_x, start_y), QPointF(end_x, end_y))
                else:
                    painter.drawLine(QPointF(x1, y1), QPointF(x1 + 1, y1 + 1))

            else:
                # Обычный отрезок (LINE)
                if dist < 0.2:
                    painter.drawPoint(QPointF(x1, y1))
                else:
                    painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

            # Концевые маркеры выделения
            if self._selected:
                pen.setColor(QColor(0, 120, 255))
                pen.setWidth(1)
                painter.setPen(pen)
                for px, py in [(x1, y1), (x2, y2)]:
                    painter.drawRect(int(px) - 5, int(py) - 5, 10, 10)
        except Exception:
            # В случае любой ошибки при отрисовке, не ломаем приложение
            pass
        finally:
            painter.restore()

    def contains_point(self, point: QPointF) -> bool:
        """Проверяет, находится ли точка близко к линии."""
        return self._dist_to_line(point.x(), point.y()) <= max(self.pen_width / 2 + 4, 5)

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
        elif self._shape_type == ShapeType.RAY and t < 0:
            return math.hypot(px - x1, py - y1)
        # Для INFINITE_LINE t может быть любым

        proj_x = x1 + t * dx
        proj_y = y1 + t * dy
        return math.hypot(px - proj_x, py - proj_y)

    def move(self, dx: float, dy: float) -> None:
        self._x1 += dx
        self._y1 += dy
        self._x2 += dx
        self._y2 += dy

    def rotate(self, angle: float, center: QPointF | None = None) -> None:
        if center is None:
            center = QPointF((self._x1 + self._x2) / 2, (self._y1 + self._y2) / 2)

        rx1, ry1 = self._rotate_point(self._x1, self._y1, center.x(), center.y(), angle)
        rx2, ry2 = self._rotate_point(self._x2, self._y2, center.x(), center.y(), angle)

        self._x1, self._y1 = rx1, ry1
        self._x2, self._y2 = rx2, ry2

    @staticmethod
    def _rotate_point(
        x: float, y: float, cx: float, cy: float, angle_deg: float
    ) -> tuple[float, float]:
        rad = math.radians(angle_deg)
        cos_a, sin_a = math.cos(rad), math.sin(rad)
        dx, dy = x - cx, y - cy
        return cx + dx * cos_a - dy * sin_a, cy + dx * sin_a + dy * cos_a

    def scale(self, factor: float, center: QPointF | None = None) -> None:
        if center is None:
            center = QPointF((self._x1 + self._x2) / 2, (self._y1 + self._y2) / 2)

        self._x1, self._y1 = self._scale_point(self._x1, self._y1, center.x(), center.y(), factor)
        self._x2, self._y2 = self._scale_point(self._x2, self._y2, center.x(), center.y(), factor)

    @staticmethod
    def _scale_point(
        x: float, y: float, cx: float, cy: float, factor: float
    ) -> tuple[float, float]:
        return cx + (x - cx) * factor, cy + (y - cy) * factor

    def bounding_rect(self) -> QRectF:
        # Защита от NaN / inf координат — возвращаем пустой rect
        coords = [self._x1, self._y1, self._x2, self._y2]
        if any(not math.isfinite(c) for c in coords):
            return QRectF()

        # Для бесконечных линий возвращаем ограниченный прямоугольник сцены
        if self._shape_type in (ShapeType.RAY, ShapeType.INFINITE_LINE):
            return QRectF(-SAFE_INFINITY, -SAFE_INFINITY, SAFE_INFINITY * 2, SAFE_INFINITY * 2)

        # Используем приватные поля из self
        x1, x2 = self._x1, self._x2
        y1, y2 = self._y1, self._y2

        x_min = min(x1, x2)
        x_max = max(x1, x2)
        y_min = min(y1, y2)
        y_max = max(y1, y2)

        # Защита от нулевых размеров
        if x_max - x_min < 0.01:
            x_min -= 1
            x_max += 1
        if y_max - y_min < 0.01:
            y_min -= 1
            y_max += 1

        pad = max(self.pen_width / 2 + 4, 5)
        return QRectF(x_min - pad, y_min - pad, x_max - x_min + pad * 2, y_max - y_min + pad * 2)

    def get_handles(self) -> list[QPointF]:
        return [QPointF(self._x1, self._y1), QPointF(self._x2, self._y2)]

    def get_handle_type(self, point: QPointF, tolerance: float = 5.0) -> HandleType:
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
        d.update(
            {
                "x1": self._x1,
                "y1": self._y1,
                "x2": self._x2,
                "y2": self._y2,
                "shape_type": self._shape_type.value,
            }
        )
        return d

    @classmethod
    def from_dict(cls, data: dict) -> LineShape:
        shape_type_val = data.get("shape_type", "line")
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
