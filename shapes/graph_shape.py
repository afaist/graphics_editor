"""Фигура: График математической функции."""

from __future__ import annotations

import io
import math
from typing import Any

from PySide6.QtCore import QPointF, QRectF
from PySide6.QtGui import QColor, QImage, QPainter, QPen, Qt

from .base_shape import BaseShape, HandleType, ShapeType

# Доступные функции и их описания
GRAPH_FUNCTIONS: dict[str, dict[str, Any]] = {
    "linear": {"name": "Линейная", "fn": lambda x, a, b: a * x + b, "params": ["a", "b"]},
    "quadratic": {
        "name": "Квадратичная",
        "fn": lambda x, a, b, c: a * x * x + b * x + c,
        "params": ["a", "b", "c"],
    },
    "sin": {"name": "Синус", "fn": lambda x, a, b: a * math.sin(b * x), "params": ["a", "b"]},
    "cos": {"name": "Косинус", "fn": lambda x, a, b: a * math.cos(b * x), "params": ["a", "b"]},
    "tan": {"name": "Тангенс", "fn": lambda x, a, b: a * math.tan(b * x), "params": ["a", "b"]},
    "log": {
        "name": "Логарифм",
        "fn": lambda x, a, b: a * math.log(b * x) if b * x > 0 else float("nan"),
        "params": ["a", "b"],
    },
    "exp": {"name": "Экспонента", "fn": lambda x, a, b: a * math.exp(b * x), "params": ["a", "b"]},
    "sqrt": {
        "name": "Корень",
        "fn": lambda x, a, b: a * math.sqrt(b * x) if b * x >= 0 else float("nan"),
        "params": ["a", "b"],
    },
}


class GraphShape(BaseShape):
    """Фигура - график математической функции."""

    DEFAULT_FONT_SIZE = 12
    DEFAULT_PEN_WIDTH = 2
    X_RANGE = 10
    X_STEPS = 500
    RENDER_SCALE = 2
    DEFAULT_WIDTH = 300
    DEFAULT_HEIGHT = 200

    def __init__(
        self,
        x: float,
        y: float,
        func_name: str = "linear",
        params: dict[str, float] | None = None,
        pen_color: tuple[int, int, int] = (0, 0, 0),
        pen_width: float = 2.0,
        selected: bool = False,
        width: float = 300,
        height: float = 200,
    ):
        super().__init__(pen_color, pen_width, None, selected)
        self._x = x
        self._y = y
        self._func_name = func_name
        self._params = params or {}
        self._width = width
        self._height = height
        self._rendered_image: QImage | None = None
        self._render_dirty = True
        self._rendered_size: tuple[int, int] = (0, 0)

        self._pen = QPen()
        self._set_pen(pen_color, pen_width)

    def _get_shape_type(self) -> ShapeType:
        return ShapeType.GRAPH

    def set_end_point(self, x: float, y: float) -> None:
        pass

    def set_size(self, width: float, height: float) -> None:
        pass

    def add_vertex(self, x: float, y: float) -> None:
        pass

    def _set_pen(self, color: QColor | tuple[int, int, int], width: float) -> None:
        if isinstance(color, QColor):
            self._pen.setColor(color)
        else:
            self._pen.setColor(QColor(color[0], color[1], color[2]))
        self._pen.setWidthF(width)
        self._pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        self._pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)

    @property
    def func_name(self) -> str:
        return self._func_name

    @func_name.setter
    def func_name(self, value: str) -> None:
        if self._func_name != value:
            self._func_name = value
            self._render_dirty = True

    @property
    def params(self) -> dict[str, float]:
        return dict(self._params)

    @params.setter
    def params(self, value: dict[str, float]) -> None:
        if self._params != value:
            self._params = value
            self._render_dirty = True

    @property
    def width(self) -> float:
        return self._width

    @width.setter
    def width(self, value: float) -> None:
        if self._width != value:
            self._width = value
            self._render_dirty = True

    @property
    def height(self) -> float:
        return self._height

    @height.setter
    def height(self, value: float) -> None:
        if self._height != value:
            self._height = value
            self._render_dirty = True

    def draw(self, painter: QPainter) -> None:
        """Рисует график на холсте."""
        if self._render_dirty:
            self._render_graph()

        if self._rendered_image and not self._rendered_image.isNull():
            painter.drawImage(QPointF(self._x, self._y), self._rendered_image)

    def _render_graph(self) -> None:
        """Рендерит график в QImage через matplotlib."""
        self._rendered_image = None
        self._rendered_size = (0, 0)

        try:
            import numpy as np
            from matplotlib.figure import Figure

            func_info = GRAPH_FUNCTIONS.get(self._func_name)
            if not func_info:
                return

            dpi = 100 * self.RENDER_SCALE
            # Вычисляем размер фигуры в дюймах из пикселей и DPI
            fig_width = self._width / dpi
            fig_height = self._height / dpi
            fig = Figure(figsize=(fig_width, fig_height), dpi=dpi)
            ax = fig.add_subplot(111)

            ax.set_xlim(-self.X_RANGE, self.X_RANGE)
            ax.axhline(y=0, color="gray", linewidth=0.5, alpha=0.7)
            ax.axvline(x=0, color="gray", linewidth=0.5, alpha=0.7)
            ax.grid(True, alpha=0.3)
            ax.set_aspect("equal")

            fn = func_info["fn"]
            params = self._params

            x_vals = np.linspace(-self.X_RANGE, self.X_RANGE, self.X_STEPS)
            y_vals = []

            for x in x_vals:
                try:
                    args = [params.get(p, 1.0) for p in func_info["params"]]
                    y = fn(x, *args)
                    if math.isfinite(y):
                        y_vals.append(y)
                    else:
                        y_vals.append(float("nan"))
                except (ValueError, OverflowError):
                    y_vals.append(float("nan"))

            y_vals = np.array(y_vals)

            ax.plot(
                x_vals, y_vals, color="black", linewidth=self._pen.widthF(), solid_capstyle="round"
            )

            buf = io.BytesIO()
            fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight", pad_inches=0.1)
            buf.seek(0)
            self._rendered_image = QImage.fromData(buf.read())
            if self._rendered_image is not None:
                self._rendered_size = (
                    self._rendered_image.width(),
                    self._rendered_image.height(),
                )
            else:
                self._rendered_size = (0, 0)
            fig.clf()

        except ImportError:
            pass

    def bounding_rect(self) -> QRectF:
        """Возвращает прямоугольник фигуры."""
        if self._rendered_image and not self._rendered_image.isNull():
            return QRectF(self._x, self._y, self._width, self._height)
        return QRectF(self._x, self._y, self._width, self._height)

    def contains_point(self, point: QPointF) -> bool:
        """Проверяет, содержится ли точка внутри фигуры."""
        br = self.bounding_rect()
        return br.contains(point)

    def move(self, dx: float, dy: float) -> None:
        """Перемещает фигуру."""
        self._x += dx
        self._y += dy
        self._render_dirty = True

    def get_handles(self) -> list[HandleType]:
        """Возвращает список маркеров преобразования."""
        return [
            HandleType.MOVE,
            HandleType.TOP_LEFT,
            HandleType.TOP_RIGHT,
            HandleType.BOTTOM_LEFT,
            HandleType.BOTTOM_RIGHT,
        ]

    def get_handle_type(self, point: QPointF, tolerance: float = 5.0) -> HandleType:
        """Определяет тип маркера по точке."""
        br = self.bounding_rect()
        margin = 8

        if br.contains(point):
            cx = br.center().x()
            cy = br.center().y()
            is_left = point.x() < cx - margin
            is_right = point.x() > cx + margin
            is_top = point.y() < cy - margin
            is_bottom = point.y() > cy + margin

            if is_top and is_left:
                return HandleType.TOP_LEFT
            elif is_top and is_right:
                return HandleType.TOP_RIGHT
            elif is_bottom and is_left:
                return HandleType.BOTTOM_LEFT
            elif is_bottom and is_right:
                return HandleType.BOTTOM_RIGHT
            else:
                return HandleType.MOVE

        return HandleType.NONE

    def apply_handle_transform(
        self,
        handle: HandleType,
        point: QPointF,
        mouse_pos: QPointF,
        shift_pressed: bool = False,
    ) -> None:
        """Применяет преобразование к маркеру (только перемещение)."""
        if handle == HandleType.MOVE:
            self.move(point.x() - self._x, point.y() - self._y)

    def rotate(self, angle: float, center: QPointF | None = None) -> None:
        """Графики не поддерживают вращение."""
        pass

    def scale(self, factor: float, center: QPointF | None = None) -> None:
        """Графики не поддерживают масштабирование."""
        pass

    def to_dict(self) -> dict[str, Any]:
        """Сериализует фигуру в словарь."""
        return {
            "type": "graph",
            "x": self._x,
            "y": self._y,
            "width": self._width,
            "height": self._height,
            "func_name": self._func_name,
            "params": self._params,
            "pen_color": self._color_to_tuple(self._pen.color()),
            "pen_width": self._pen.widthF(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GraphShape:
        """Создаёт фигуру из словаря."""
        return cls(
            x=data["x"],
            y=data["y"],
            func_name=data.get("func_name", "linear"),
            params=data.get("params", {}),
            pen_color=tuple(data.get("pen_color", [0, 0, 0])),
            pen_width=data.get("pen_width", 2),
            width=data.get("width", cls.DEFAULT_WIDTH),
            height=data.get("height", cls.DEFAULT_HEIGHT),
        )

    @staticmethod
    def _color_to_tuple(color: QColor) -> tuple[int, int, int]:
        """Конвертирует QColor в кортеж RGB."""
        return (color.red(), color.green(), color.blue())
