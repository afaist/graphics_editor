"""Фигура: Прямоугольник (и квадрат)."""

from __future__ import annotations

import math

from PySide6.QtCore import QPointF, QRectF
from PySide6.QtGui import QPainter

from tools.quadrilateral_tools import (
    draw_angles as _draw_angles,
)
from tools.quadrilateral_tools import (
    draw_bisectors as _draw_bisectors,
)

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
        show_diagonals: bool = False,
        show_circumcircle: bool = False,
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

        # Дополнительные линии
        self._show_heights = False
        self._show_diagonals = show_diagonals
        self._show_bisectors = False
        self._show_angles = False
        self._show_circumcircle = show_circumcircle
        self._height_from_vertex = -1

    def _get_shape_type(self) -> ShapeType:
        """Возвращает тип фигуры — RECTANGLE."""
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

    @property
    def show_heights(self) -> bool:
        return self._show_heights

    @show_heights.setter
    def show_heights(self, value: bool) -> None:
        self._show_heights = value

    @property
    def show_diagonals(self) -> bool:
        return self._show_diagonals

    @show_diagonals.setter
    def show_diagonals(self, value: bool) -> None:
        self._show_diagonals = value

    @property
    def show_bisectors(self) -> bool:
        return self._show_bisectors

    @show_bisectors.setter
    def show_bisectors(self, value: bool) -> None:
        self._show_bisectors = value

    @property
    def show_angles(self) -> bool:
        return self._show_angles

    @show_angles.setter
    def show_angles(self, value: bool) -> None:
        self._show_angles = value

    @property
    def show_circumcircle(self) -> bool:
        return self._show_circumcircle

    @show_circumcircle.setter
    def show_circumcircle(self, value: bool) -> None:
        self._show_circumcircle = value

    @property
    def height_from_vertex(self) -> int:
        return self._height_from_vertex

    @height_from_vertex.setter
    def height_from_vertex(self, value: int) -> None:
        self._height_from_vertex = value

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

    def _rotation_center(self) -> tuple[float, float]:
        """Возвращает центр поворота — середина прямоугольника."""
        cx = self._x + self._width / 2
        cy = self._y + self._height / 2
        return (cx, cy)

    def _draw_shape_content(self, painter: QPainter) -> None:
        """Рисует прямоугольник и дополнительные элементы."""
        # Защита от краша при нулевых/отрицательных размерах
        w = abs(self._width)
        h = abs(self._height)
        x = self._x if self._width >= 0 else self._x + self._width
        y = self._y if self._height >= 0 else self._y + self._height

        if w > 0.1 and h > 0.1:
            painter.drawRect(QRectF(x, y, w, h))
        else:
            painter.drawPoint(QPointF(x + w / 2, y + h / 2))

        # Вершины, подписи, selection — через _draw_common
        self._draw_common(painter, self._rotation_center())

        # Диагонали
        if self._show_diagonals and len(self._vertices) == 4:
            self._draw_diagonals(painter)

        # Описанная окружность
        if self._show_circumcircle and len(self._vertices) == 4:
            self.draw_circumcircle(painter)

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
        pad = self._compute_bounding_padding(self.pen_width)
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
        self, handle: HandleType, point: QPointF, mouse_pos: QPointF, shift_pressed: bool = False
    ) -> None:
        """Применить трансформацию через маркер для прямоугольника."""
        dx = mouse_pos.x() - point.x()
        dy = mouse_pos.y() - point.y()

        self._x, self._y, self._width, self._height = self._apply_rect_handle(
            handle, dx, dy, self._x, self._y, self._width, self._height, shift_pressed
        )

        # Перестраиваем все вершины из новых x/y/width/height
        self._rebuild_vertices()

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
    # Дополнительные элементы четырёхугольника
    # ------------------------------------------------------------------

    def is_cyclic(self) -> bool:
        return True  # прямоугольник всегда вписываемый

    def draw_diagonals(self, painter: QPainter) -> None:
        self._draw_diagonals(painter)

    def draw_heights(self, painter: QPainter, vertex_index: int | None = None) -> None:
        self._draw_heights(painter, vertex_index)

    def draw_bisectors(self, painter: QPainter, vertex_indices: list[int] | None = None) -> None:
        _draw_bisectors(painter, self, vertex_indices)

    def draw_angles(self, painter: QPainter) -> None:
        _draw_angles(painter, self)

    # ------------------------------------------------------------------
    # Позиция для undo
    # ------------------------------------------------------------------

    def get_position_data(self) -> dict:
        return {
            "x": self._x,
            "y": self._y,
            "width": self._width,
            "height": self._height,
        }

    def restore_position_data(self, data: dict) -> None:
        self._x = data["x"]
        self._y = data["y"]
        self._width = data["width"]
        self._height = data["height"]
        self._rebuild_vertices()

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
        d["show_diagonals"] = self._show_diagonals
        d["show_circumcircle"] = self._show_circumcircle
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
        if "show_diagonals" in properties:
            self._show_diagonals = properties["show_diagonals"]
        if "show_circumcircle" in properties:
            self._show_circumcircle = properties["show_circumcircle"]

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
                "show_diagonals": self._show_diagonals,
                "show_circumcircle": self._show_circumcircle,
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
            show_diagonals=data.get("show_diagonals", False),
            show_circumcircle=data.get("show_circumcircle", False),
        )
        obj._selected = data.get("selected", False)
        obj._rotation = data.get("rotation", 0.0)
        return obj
