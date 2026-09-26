"""Базовый класс Shape — родитель для всех геометрических фигур."""

from __future__ import annotations

import copy
import math
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any

from PySide6.QtCore import QPointF, QRectF
from PySide6.QtGui import QColor, QPainter


class ShapeType(Enum):
    """Типы фигур."""

    POINT = "point"
    LINE = "line"
    RAY = "ray"
    INFINITE_LINE = "infinite_line"
    RECTANGLE = "rectangle"
    ELLIPSE = "ellipse"
    POLYGON = "polygon"
    POLYLINE = "polyline"
    ARC = "arc"
    TEXT = "text"
    TRIANGLE_EQUILATERAL = "triangle_equilateral"
    TRIANGLE_ISOSCELES = "triangle_isosceles"
    TRIANGLE_RIGHT = "triangle_right"
    TRIANGLE_OBTUSE = "triangle_obtuse"
    PARALLELOGRAM = "parallelogram"
    TRAPEZOID_ISOSCELES = "trapezoid_isosceles"
    TRAPEZOID = "trapezoid"
    ANGLE = "angle"


class HandleType(Enum):
    """Типы маркеров преобразования."""

    NONE = 0
    MOVE = 1
    TOP_LEFT = 2
    TOP_RIGHT = 3
    BOTTOM_LEFT = 4
    BOTTOM_RIGHT = 5
    TOP_CENTER = 6
    BOTTOM_CENTER = 7
    LEFT_CENTER = 8
    RIGHT_CENTER = 9
    ROTATION = 10


class BaseShape(ABC):
    """Абстрактный базовый класс для всех геометрических фигур."""

    def __init__(
        self,
        pen_color: tuple[int, int, int] = (0, 0, 0),
        pen_width: float = 2.0,
        brush_color: tuple[int, int, int] | None = None,
        selected: bool = False,
    ):
        # ID будет назначен менеджером фигур
        self.id: int = -1
        self.shape_type: ShapeType = self._get_shape_type()

        # Валидация входных данных
        if not math.isfinite(pen_width) or pen_width < 0.5:
            raise ValueError("Pen width must be a finite number >= 0.5")

        self._pen_color = QColor(*self._validate_color(pen_color))
        self._pen_width = pen_width
        self._brush_color = (
            QColor(*self._validate_color(brush_color)) if brush_color is not None else None
        )
        self._selected = selected
        self._rotation: float = 0.0  # угол поворота в градусах
        self._group_id: int | None = None

    @staticmethod
    def _validate_color(color: tuple[int, int, int]) -> tuple[int, int, int]:
        """Валидация цвета: проверка диапазона и типа."""
        if len(color) != 3:
            raise ValueError("Color must be a tuple of 3 integers")
        if not all(isinstance(c, int) and 0 <= c <= 255 for c in color):
            raise ValueError("Color components must be integers in range 0–255")
        return color

    @abstractmethod
    def _get_shape_type(self) -> ShapeType:
        pass

    # ------------------------------------------------------------------
    # Свойства
    # ------------------------------------------------------------------

    @property
    def pen_color(self) -> QColor:
        return self._pen_color

    @pen_color.setter
    def pen_color(self, color: tuple[int, int, int]) -> None:
        self._pen_color = QColor(*self._validate_color(color))

    @property
    def pen_width(self) -> float:
        return self._pen_width

    @pen_width.setter
    def pen_width(self, w: float) -> None:
        if w < 0.5:
            raise ValueError("Pen width must be at least 0.5")
        self._pen_width = w

    @property
    def brush_color(self) -> QColor | None:
        return self._brush_color

    @brush_color.setter
    def brush_color(self, color: tuple[int, int, int] | None) -> None:
        if color is None:
            self._brush_color = None
        else:
            self._brush_color = QColor(*self._validate_color(color))

    @property
    def selected(self) -> bool:
        return self._selected

    @selected.setter
    def selected(self, value: bool) -> None:
        self._selected = value

    @property
    def rotation(self) -> float:
        return self._rotation

    @rotation.setter
    def rotation(self, angle: float) -> None:
        self._rotation = angle % 360.0

    @property
    def group_id(self) -> int | None:
        return self._group_id

    @group_id.setter
    def group_id(self, gid: int | None) -> None:
        self._group_id = gid

    # ------------------------------------------------------------------
    # Абстрактные методы (должны реализовать потомки)
    # ------------------------------------------------------------------

    @abstractmethod
    def set_end_point(self, x: float, y: float) -> None:
        pass

    @abstractmethod
    def set_size(self, width: float, height: float) -> None:
        pass

    @abstractmethod
    def add_vertex(self, x: float, y: float) -> None:
        pass

    @abstractmethod
    def draw(self, painter: QPainter) -> None:
        """Отрисовать фигуру на QPainter."""
        pass

    @abstractmethod
    def contains_point(self, point: QPointF) -> bool:
        """Проверить, принадлежит ли точка фигуре."""
        pass

    @abstractmethod
    def move(self, dx: float, dy: float) -> None:
        """Переместить фигуру на (dx, dy)."""
        pass

    @abstractmethod
    def rotate(self, angle: float, center: QPointF | None = None) -> None:
        """Повернуть фигуру на angle градусов."""
        pass

    @abstractmethod
    def scale(self, factor: float, center: QPointF | None = None) -> None:
        """Масштабировать фигуру."""
        pass

    @abstractmethod
    def bounding_rect(self) -> QRectF:
        """Вернуть bounding box фигуры."""
        pass

    @abstractmethod
    def get_handles(self) -> list[QPointF]:
        """Вернуть список маркеров преобразования."""
        pass

    @abstractmethod
    def get_handle_type(self, point: QPointF, tolerance: float = 5.0) -> HandleType:
        """Определить тип маркера под указанной точкой."""
        pass

    @abstractmethod
    def apply_handle_transform(
        self, handle: HandleType, point: QPointF, mouse_pos: QPointF, shift_pressed: bool = False
    ) -> None:
        """Применить преобразование через маркер."""
        pass

    def set_arc_params(self, sx: float, sy: float, width: float, height: float) -> None:
        """Задать параметры дуги (переопределяется в ArcShape)."""
        pass

    # ------------------------------------------------------------------
    # Методы для записи/восстановления позиции (используются в undo)
    # ------------------------------------------------------------------

    def get_position_data(self) -> dict[str, Any]:
        """Вернуть словарь с координатами фигуры для записи в undo-стек.

        Переопределяется в потомках. Возвращает пустой словарь по умолчанию.
        """
        return {}

    def restore_position_data(self, data: dict[str, Any]) -> None:
        """Восстановить координаты фигуры из словаря, записанного get_position_data().

        Переопределяется в потомках. Ничего не делает по умолчанию.
        """
        pass

    # ------------------------------------------------------------------
    # Сервисные методы
    # ------------------------------------------------------------------

    def copy(self) -> BaseShape:
        """Создать глубокую копию фигуры с новым ID."""
        new_shape = copy.deepcopy(self)
        new_shape.id = -1  # ID будет назначен менеджером
        return new_shape

    def offset(self, dx: float, dy: float) -> None:
        """Переместить фигуру на (dx, dy). Универсальный метод для всех типов фигур."""
        self.move(dx, dy)

    def to_dict(self) -> dict[str, Any]:
        """Сериализовать фигуру в словарь."""
        return {
            "id": self.id,
            "type": self.shape_type.value,
            "pen_color": (
                self._pen_color.red(),
                self._pen_color.green(),
                self._pen_color.blue(),
            ),
            "pen_width": self._pen_width,
            "brush_color": (
                (
                    self._brush_color.red(),
                    self._brush_color.green(),
                    self._brush_color.blue(),
                )
                if self._brush_color is not None
                else None
            ),
            "rotation": self._rotation,
            "group_id": self._group_id,
            "selected": self._selected,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BaseShape:
        """Десериализовать фигуру из словаря. Реализуется в потомках."""
        shape = cls(
            pen_color=data["pen_color"],
            pen_width=data["pen_width"],
            brush_color=data.get("brush_color"),
            selected=data.get("selected", False),
        )
        shape.id = data["id"]
        shape._rotation = data.get("rotation", 0.0)
        shape._group_id = data.get("group_id")
        return shape

    @staticmethod
    def _safe_rect(x: float, y: float, w: float, h: float) -> QRectF:
        """Создать QRectF, проверяя координаты на NaN/inf.

        Возвращает пустой QRectF(), если любые координаты невалидны.
        Это предотвращает segfault Qt при рендеринге.
        """
        if not all(math.isfinite(v) for v in (x, y, w, h)):
            return QRectF()
        return QRectF(x, y, w, h)

    def intersects(self, other: BaseShape) -> bool:
        """Проверить пересечение с другой фигурой (упрощённо через bounding box)."""
        return self.bounding_rect().intersects(other.bounding_rect())

    def get_properties(self) -> dict[str, Any]:
        """Вернуть свойства фигуры в виде словаря для панели свойств."""
        brush_color = None
        if self._brush_color is not None:
            brush_color = (
                self._brush_color.red(),
                self._brush_color.green(),
                self._brush_color.blue(),
            )
        return {
            "pen_color": (
                self._pen_color.red(),
                self._pen_color.green(),
                self._pen_color.blue(),
            ),
            "pen_width": self._pen_width,
            "brush_color": brush_color,
            "rotation": self._rotation,
        }

    def apply_properties(self, properties: dict[str, Any]) -> None:
        """Применить свойства, полученные из панели свойств."""
        if properties is None:
            return

        # Применяем цвет контура
        if "pen_color" in properties:
            pen_color = properties["pen_color"]
            # Конвертируем кортеж обратно в QColor через валидатор
            if isinstance(pen_color, tuple) and len(pen_color) == 3:
                self.pen_color = pen_color
            elif isinstance(pen_color, QColor):
                self.pen_color = (pen_color.red(), pen_color.green(), pen_color.blue())

        # Применяем толщину контура
        if "pen_width" in properties:
            self.pen_width = properties["pen_width"]

        # Применяем цвет заливки
        if "brush_color" in properties:
            brush_color = properties["brush_color"]
            if brush_color is None:
                self.brush_color = None
            elif isinstance(brush_color, tuple) and len(brush_color) == 3:
                self.brush_color = brush_color
            elif isinstance(brush_color, QColor):
                self.brush_color = (
                    brush_color.red(),
                    brush_color.green(),
                    brush_color.blue(),
                )

        # Применяем поворот
        if "rotation" in properties:
            self.rotation = properties["rotation"]


# ====================================================================
# Названия фигур на русском
# ====================================================================

SHAPE_NAMES_RU: dict[str, str] = {
    "point": "Точка",
    "line": "Отрезок",
    "ray": "Луч",
    "infinite_line": "Прямая",
    "rectangle": "Прямоугольник",
    "ellipse": "Эллипс",
    "polygon": "Многоугольник",
    "polyline": "Ломаная",
    "arc": "Дуга",
    "text": "Текст",
    "triangle_equilateral": "Равносторонний треугольник",
    "triangle_isosceles": "Равнобедренный треугольник",
    "triangle_right": "Прямоугольный треугольник",
    "triangle_obtuse": "Тупоугольный треугольник",
    "parallelogram": "Параллелограмм",
    "trapezoid_isosceles": "Равнобедренная трапеция",
    "trapezoid": "Трапеция",
    "angle": "Угол",
}
