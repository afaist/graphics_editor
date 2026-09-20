"""Фигура: Прямоугольник (и квадрат)."""

from __future__ import annotations

import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPen

from .base_shape import BaseShape, HandleType, ShapeType


class RectangleShape(BaseShape):
    """Прямоугольник, заданный левой верхней точкой и размерами.

    Вершины хранятся в clockwise-порядке, начиная с левого нижнего угла:
    A (левый нижний), B (правый нижний), C (правый верхний), D (левый верхний).
    """

    def __init__(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        pen_color: tuple[int, int, int] = (0, 0, 0),
        pen_width: float = 2.0,
        brush_color: tuple[int, int, int] | None = None,
        selected: bool = False,
    ):
        super().__init__(pen_color, pen_width, brush_color, selected)
        self._x = x
        self._y = y
        self._width = width
        self._height = height
        self._rotation = 0.0  # Инициализируем вращение

        # Вершины в clockwise-порядке, начиная с левого нижнего угла
        self._vertices: list[QPointF] = []
        self._labels: list[str] = ["A", "B", "C", "D"]
        self._rebuild_vertices()

    def set_end_point(self, x: float, y: float) -> None:
        pass  # Прямоугольник не использует set_end_point

    def set_size(self, width: float, height: float) -> None:
        self._width = width
        self._height = height
        self._rebuild_vertices()

    def add_vertex(self, x: float, y: float) -> None:
        pass  # Прямоугольник не имеет вершин для добавления

    def _get_shape_type(self) -> ShapeType:
        return ShapeType.RECTANGLE

    # ------------------------------------------------------------------
    # Перестройка вершин
    # ------------------------------------------------------------------

    def _rebuild_vertices(self) -> None:
        """Пересчитать вершины из x, y, width, height.

        Порядок — по часовой стрелке, начиная с левого нижнего угла:
        A (левый нижний) → D (левый верхний) → C (правый верхний) → B (правый нижний).
        """
        w = abs(self._width)
        h = abs(self._height)
        x = self._x if self._width >= 0 else self._x + self._width
        y = self._y if self._height >= 0 else self._y + self._height

        # Clockwise от левого нижнего угла (Qt: Y вниз)
        self._vertices = [
            QPointF(x, y + h),  # A — левый нижний
            QPointF(x, y),  # D — левый верхний
            QPointF(x + w, y),  # C — правый верхний
            QPointF(x + w, y + h),  # B — правый нижний
        ]

    @property
    def vertices(self) -> list[QPointF]:
        return self._vertices

    @property
    def labels(self) -> list[str]:
        return self._labels

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
        try:
            pen = QPen(self.pen_color, self.pen_width)
            painter.setPen(pen)
            if self.brush_color:
                painter.setBrush(QBrush(self.brush_color))
            else:
                painter.setBrush(Qt.BrushStyle.NoBrush)

            # Применяем поворот вокруг центра фигуры
            if abs(self._rotation) > 0.01:
                cx = self._x + self._width / 2
                cy = self._y + self._height / 2
                painter.translate(cx, cy)
                painter.rotate(self._rotation)
                painter.translate(-cx, -cy)

            # Защита от краша при нулевых/отрицательных размерах
            w = abs(self._width)
            h = abs(self._height)
            x = self._x if self._width >= 0 else self._x + self._width
            y = self._y if self._height >= 0 else self._y + self._height

            if w > 0.1 and h > 0.1:
                painter.drawRect(QRectF(x, y, w, h))
            else:
                painter.drawPoint(QPointF(x + w / 2, y + h / 2))

            # Маркеры вершин
            pen.setColor(QColor(80, 80, 80))
            pen.setWidth(1)
            painter.setPen(pen)
            painter.setBrush(QBrush(QColor(255, 255, 255)))
            for v in self._vertices:
                painter.drawEllipse(v, 3, 3)

            # Подпись вершин
            self._draw_vertex_labels(painter)

            if self._selected:
                pen.setColor(QColor(0, 120, 255))
                pen.setWidth(1)
                painter.setPen(pen)
                painter.setBrush(Qt.BrushStyle.NoBrush)
                for hx, hy in self._handle_positions():
                    painter.drawRect(int(hx) - 4, int(hy) - 4, 8, 8)
        finally:
            painter.restore()

    def _draw_vertex_labels(self, painter: QPainter) -> None:
        """Отрисовать подписи вершин (A, B, C, D)."""
        if not self._vertices:
            return

        cx = sum(v.x() for v in self._vertices) / 4
        cy = sum(v.y() for v in self._vertices) / 4

        font = QFont()
        font.setFamily("Arial")
        font.setPointSizeF(9)
        painter.setFont(font)
        painter.setPen(QColor(50, 50, 50))

        offset = 16

        for i, v in enumerate(self._vertices):
            dx = v.x() - cx
            dy = v.y() - cy
            dist = math.sqrt(dx * dx + dy * dy)
            if dist < 0.01:
                continue
            dx /= dist
            dy /= dist

            label_x = v.x() + dx * offset
            label_y = v.y() + dy * offset

            text_rect = QRectF(label_x - 10, label_y - 10, 20, 20)
            painter.drawText(
                text_rect,
                Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter,
                self._labels[i],
            )

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
        self._rebuild_vertices()

    def rotate(self, angle: float, center: QPointF | None = None) -> None:
        if center is None:
            center = QPointF(self._x + self._width / 2, self._y + self._height / 2)
        self._rotation = (self._rotation + angle) % 360.0

    def scale(self, factor: float, center: QPointF | None = None) -> None:
        if center is None:
            center = QPointF(self._x + self._width / 2, self._y + self._height / 2)
        self._width *= factor
        self._height *= factor

        # Защита от отрицательных размеров
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

        self._rebuild_vertices()

    def bounding_rect(self) -> QRectF:
        pad = max(self.pen_width / 2 + 5, 6)
        if abs(self._rotation) < 0.1:
            return self._safe_rect(
                self._x - pad,
                self._y - pad,
                self._width + pad * 2,
                self._height + pad * 2,
            )
        return self._safe_rect(
            self._x - pad,
            self._y - pad,
            abs(self._width) + pad * 2,
            abs(self._height) + pad * 2,
        )

    def _handle_positions(self) -> list[tuple[float, float]]:
        return [(v.x(), v.y()) for v in self._vertices]

    def get_handles(self) -> list[QPointF]:
        return list(self._vertices)

    def get_handle_type(self, point: QPointF, tolerance: float = 5.0) -> HandleType:
        for i, v in enumerate(self._vertices):
            dx = point.x() - v.x()
            dy = point.y() - v.y()
            distance = math.sqrt(dx * dx + dy * dy)
            if distance <= tolerance:
                # Вершины в clockwise-порядке: A=BL, D=TL, C=TR, B=BR
                handle_map = [
                    HandleType.BOTTOM_LEFT,  # 0 -> A (левый нижний)
                    HandleType.TOP_LEFT,  # 1 -> D (левый верхний)
                    HandleType.TOP_RIGHT,  # 2 -> C (правый верхний)
                    HandleType.BOTTOM_RIGHT,  # 3 -> B (правый нижний)
                ]
                return handle_map[i]
        return HandleType.NONE

    def apply_handle_transform(
        self, handle: HandleType, point: QPointF, mouse_pos: QPointF
    ) -> None:
        # Маппинг HandleType -> индекс вершины
        handle_to_vertex = {
            HandleType.BOTTOM_LEFT: 0,  # A
            HandleType.TOP_LEFT: 1,  # D
            HandleType.TOP_RIGHT: 2,  # C
            HandleType.BOTTOM_RIGHT: 3,  # B
        }
        idx = handle_to_vertex.get(handle)
        if idx is not None and 0 <= idx < len(self._vertices):
            self._vertices[idx].setX(mouse_pos.x())
            self._vertices[idx].setY(mouse_pos.y())

    def _recalc_from_vertices(self) -> None:
        """Пересчитать x, y, width, height из вершин."""
        if len(self._vertices) < 4:
            return
        xs = [v.x() for v in self._vertices]
        ys = [v.y() for v in self._vertices]
        self._x = min(xs)
        self._y = min(ys)
        self._width = max(xs) - min(xs)
        self._height = max(ys) - min(ys)

    # ------------------------------------------------------------------
    # Свойства для панели
    # ------------------------------------------------------------------

    def get_properties(self) -> dict:
        d = super().get_properties()
        d["_x"] = self._x
        d["_y"] = self._y
        d["_width"] = self._width
        d["_height"] = self._height
        d["_rotation"] = self._rotation
        return d

    def apply_properties(self, properties: dict) -> None:
        super().apply_properties(properties)

        if properties is None:
            return

        if "_x" in properties:
            self._x = properties["_x"]
        if "_y" in properties:
            self._y = properties["_y"]
        if "_width" in properties:
            self._width = properties["_width"]
        if "_height" in properties:
            self._height = properties["_height"]
        if "_rotation" in properties:
            self._rotation = properties["_rotation"]

        self._rebuild_vertices()

    # ------------------------------------------------------------------
    # Сериализация
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        d = super().to_dict()
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
    def from_dict(cls, data: dict) -> RectangleShape:
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
