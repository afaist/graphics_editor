"""Фигура: Гипербола."""

from __future__ import annotations

import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QPainter, QPen

from .base_shape import BaseShape, HandleType, ShapeType


class HyperbolaShape(BaseShape):
    """Гипербола, заданная центром, полуосью a, полуосью b и направлением.

    Уравнение:
    - direction='horizontal': (x-h)²/a² - (y-k)²/b² = 1
    - direction='vertical':   (y-k)²/a² - (x-h)²/b² = 1
    """

    VALID_DIRECTIONS = ("horizontal", "vertical")

    def __init__(
        self,
        cx: float,
        cy: float,
        semi_axis_a: float,
        semi_axis_b: float,
        direction: str = "horizontal",
        pen_color: tuple[int, int, int] = (0, 0, 0),
        pen_width: float = 2.0,
        brush_color: tuple[int, int, int] | None = None,
        selected: bool = False,
    ):
        super().__init__(pen_color, pen_width, brush_color, selected)
        if direction not in self.VALID_DIRECTIONS:
            raise ValueError(f"direction must be one of {self.VALID_DIRECTIONS}")
        self._cx = cx
        self._cy = cy
        self._semi_axis_a = semi_axis_a
        self._semi_axis_b = semi_axis_b
        self._direction = direction

    def set_size(self, width: float, height: float) -> None:
        self._semi_axis_a = max(width / 4, 10)
        self._semi_axis_b = max(height / 4, 10)

    def _get_shape_type(self) -> ShapeType:
        return ShapeType.HYPERBOLA

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
    def semi_axis_a(self) -> float:
        return self._semi_axis_a

    @semi_axis_a.setter
    def semi_axis_a(self, value: float) -> None:
        if value > 0.1:
            self._semi_axis_a = value

    @property
    def semi_axis_b(self) -> float:
        return self._semi_axis_b

    @semi_axis_b.setter
    def semi_axis_b(self, value: float) -> None:
        if value > 0.1:
            self._semi_axis_b = value

    @property
    def direction(self) -> str:
        return self._direction

    # ------------------------------------------------------------------
    # Вычисление точек
    # ------------------------------------------------------------------

    def _compute_points(self, num_samples: int = 300) -> list[list[tuple[float, float]]]:
        """Вычисляет точки двух ветвей гиперболы."""
        h, k = self._cx, self._cy
        a = self._semi_axis_a
        b = self._semi_axis_b

        branches: list[list[tuple[float, float]]] = [[], []]

        if self._direction == "horizontal":
            # (x-h)²/a² - (y-k)²/b² = 1
            # x = h ± a*sqrt(1 + (y-k)²/b²)
            # Решаем относительно y: y = k ± b*sqrt((x-h)²/a² - 1)
            # Domain: |x-h| >= a
            extent = max(a * 5, 200)
            # Правая ветвь (x >= h + a)
            right_points: list[tuple[float, float]] = []
            left_points: list[tuple[float, float]] = []
            dx = extent / num_samples
            x = h + a  # начало с вершины
            while x <= h + extent:
                val = ((x - h) ** 2) / (a**2) - 1
                if val >= 0:
                    dy = b * math.sqrt(val)
                    right_points.append((x, k - dy))
                    right_points.append((x, k + dy))
                x += dx
            # Сортируем правую ветвь по y
            right_points.sort(key=lambda p: p[1])
            # Левая ветвь (x <= h - a)
            x = h - a
            while x >= h - extent:
                val = ((x - h) ** 2) / (a**2) - 1
                if val >= 0:
                    dy = b * math.sqrt(val)
                    left_points.append((x, k - dy))
                    left_points.append((x, k + dy))
                x -= dx
            left_points.sort(key=lambda p: p[1])
            branches = [right_points, left_points]

        else:
            # (y-k)²/a² - (x-h)²/b² = 1
            extent = max(a * 5, 200)
            # Верхняя ветвь (y >= k + a)
            upper_points: list[tuple[float, float]] = []
            lower_points: list[tuple[float, float]] = []
            dy = extent / num_samples
            y = k + a
            while y <= k + extent:
                val = ((y - k) ** 2) / (a**2) - 1
                if val >= 0:
                    dx = b * math.sqrt(val)
                    upper_points.append((h - dx, y))
                    upper_points.append((h + dx, y))
                y += dy
            upper_points.sort(key=lambda p: p[0])
            # Нижняя ветвь (y <= k - a)
            y = k - a
            while y >= k - extent:
                val = ((y - k) ** 2) / (a**2) - 1
                if val >= 0:
                    dx = b * math.sqrt(val)
                    lower_points.append((h - dx, y))
                    lower_points.append((h + dx, y))
                y -= dy
            lower_points.sort(key=lambda p: p[0])
            branches = [upper_points, lower_points]

        return branches

    def _bounding_rect_from_points(
        self, branches: list[list[tuple[float, float]]], pad: float
    ) -> QRectF:
        all_points = []
        for branch in branches:
            all_points.extend(branch)
        if not all_points:
            r = max(self._semi_axis_a * 4, 50)
            return self._safe_rect(
                self._cx - r - pad,
                self._cy - r - pad,
                2 * r + 2 * pad,
                2 * r + 2 * pad,
            )
        xs = [p[0] for p in all_points]
        ys = [p[1] for p in all_points]
        return self._safe_rect(
            min(xs) - pad,
            min(ys) - pad,
            max(xs) - min(xs) + 2 * pad,
            max(ys) - min(ys) + 2 * pad,
        )

    # ------------------------------------------------------------------
    # Abstract methods
    # ------------------------------------------------------------------

    def draw(self, painter: QPainter) -> None:
        painter.save()
        try:
            pen = QPen(self.pen_color, self.pen_width)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)

            branches = self._compute_points()
            painter.setBrush(Qt.BrushStyle.NoBrush)

            for branch in branches:
                if len(branch) < 2:
                    continue
                qt_points = [QPointF(x, y) for x, y in branch]
                painter.drawPolyline(qt_points)

            # Рисуем вершины
            painter.setBrush(QBrush(self.pen_color))
            if self._direction == "horizontal":
                painter.drawEllipse(QPointF(self._cx - self._semi_axis_a, self._cy), 3, 3)
                painter.drawEllipse(QPointF(self._cx + self._semi_axis_a, self._cy), 3, 3)
            else:
                painter.drawEllipse(QPointF(self._cx, self._cy - self._semi_axis_a), 3, 3)
                painter.drawEllipse(QPointF(self._cx, self._cy + self._semi_axis_a), 3, 3)

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
        return self.bounding_rect().contains(point)

    def move(self, dx: float, dy: float) -> None:
        self._cx += dx
        self._cy += dy

    def scale(self, factor: float, center: QPointF | None = None) -> None:
        if center is None:
            center = QPointF(self._cx, self._cy)
        self._cx = center.x() + (self._cx - center.x()) * factor
        self._cy = center.y() + (self._cy - center.y()) * factor
        self._semi_axis_a *= factor
        self._semi_axis_b *= factor
        if self._semi_axis_a < 0.1:
            self._semi_axis_a = 0.1
        if self._semi_axis_b < 0.1:
            self._semi_axis_b = 0.1

    def bounding_rect(self) -> QRectF:
        pad = self._compute_bounding_padding(self.pen_width)
        branches = self._compute_points()
        return self._bounding_rect_from_points(branches, pad)

    # ------------------------------------------------------------------
    # Маркеры (handles)
    # ------------------------------------------------------------------

    def _handle_positions(self) -> list[tuple[float, float]]:
        if self._direction == "horizontal":
            return [
                (self._cx, self._cy),  # центр
                (self._cx - self._semi_axis_a, self._cy),  # левая вершина
                (self._cx + self._semi_axis_a, self._cy),  # правая вершина
            ]
        else:
            return [
                (self._cx, self._cy),  # центр
                (self._cx, self._cy - self._semi_axis_a),  # верхняя вершина
                (self._cx, self._cy + self._semi_axis_a),  # нижняя вершина
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
            # Правая/нижняя вершина — изменение a
            if self._direction == "horizontal":
                self._semi_axis_a = abs(mouse_pos.x() - self._cx)
            else:
                self._semi_axis_a = abs(mouse_pos.y() - self._cy)
            if self._semi_axis_a < 0.1:
                self._semi_axis_a = 0.1
        elif handle == HandleType.TOP_CENTER:
            # Верхняя/левая вершина — изменение a
            if self._direction == "horizontal":
                self._semi_axis_a = abs(self._cx - mouse_pos.x())
            else:
                self._semi_axis_a = abs(self._cy - mouse_pos.y())
            if self._semi_axis_a < 0.1:
                self._semi_axis_a = 0.1

    # ------------------------------------------------------------------
    # Позиция для undo
    # ------------------------------------------------------------------

    def get_position_data(self) -> dict:
        return {
            "cx": self._cx,
            "cy": self._cy,
            "semi_axis_a": self._semi_axis_a,
            "semi_axis_b": self._semi_axis_b,
            "direction": self._direction,
        }

    def restore_position_data(self, data: dict) -> None:
        self._cx = data["cx"]
        self._cy = data["cy"]
        self._semi_axis_a = data["semi_axis_a"]
        self._semi_axis_b = data["semi_axis_b"]
        self._direction = data["direction"]

    # ------------------------------------------------------------------
    # Сериализация
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update(
            {
                "cx": self._cx,
                "cy": self._cy,
                "semi_axis_a": self._semi_axis_a,
                "semi_axis_b": self._semi_axis_b,
                "direction": self._direction,
            }
        )
        return d

    @classmethod
    def from_dict(cls, data: dict) -> HyperbolaShape:
        obj = cls(
            cx=data["cx"],
            cy=data["cy"],
            semi_axis_a=data["semi_axis_a"],
            semi_axis_b=data["semi_axis_b"],
            direction=data.get("direction", "horizontal"),
            pen_color=data["pen_color"],
            brush_color=data.get("brush_color"),
            pen_width=data.get("pen_width", 2.0),
        )
        obj._selected = data.get("selected", False)
        obj._rotation = data.get("rotation", 0.0)
        return obj
