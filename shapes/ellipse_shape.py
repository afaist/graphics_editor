"""Фигура: Эллипс (и окружность)."""

from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPen

from .base_shape import BaseShape, HandleType, ShapeType


class EllipseShape(BaseShape):
    """Эллипс, заданный bounding rect."""

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

    def set_end_point(self, x: float, y: float) -> None:
        pass  # Эллипс не использует set_end_point

    def set_size(self, width: float, height: float) -> None:
        self._width = width
        self._height = height

    def add_vertex(self, x: float, y: float) -> None:
        pass  # Эллипс не имеет вершин для добавления

    def _get_shape_type(self) -> ShapeType:
        return ShapeType.ELLIPSE

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
    def radius_x(self) -> float:
        return abs(self._width) / 2

    @property
    def radius_y(self) -> float:
        return abs(self._height) / 2

    # ------------------------------------------------------------------
    # Abstract methods
    # ------------------------------------------------------------------

    def draw(self, painter: QPainter) -> None:
        painter.save()
        try:
            pen = QPen(self.pen_color, self.pen_width)
            painter.setPen(pen)
            if self.brush_color:
                painter.setBrush(self.brush_color)

            # Применяем поворот вокруг центра фигуры
            if abs(self._rotation) > 0.01:
                cx = self._x + self._width / 2
                cy = self._y + self._height / 2
                painter.translate(cx, cy)
                painter.rotate(self._rotation)
                painter.translate(-cx, -cy)

            # Фикс: Qt может крашиться на очень маленьких или пустых эллипсах
            if self._width > 0.1 and self._height > 0.1:
                painter.drawEllipse(QRectF(self._x, self._y, self._width, self._height))
            else:
                # Рисуем точку, если эллипс "схлопнулся"
                painter.drawPoint(QPointF(self._x + self._width / 2, self._y + self._height / 2))

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
        cx = self._x + self._width / 2
        cy = self._y + self._height / 2
        rx = abs(self._width) / 2
        ry = abs(self._height) / 2
        if rx < 0.001 or ry < 0.001:
            return False
        dx = (point.x() - cx) / rx
        dy = (point.y() - cy) / ry
        return dx * dx + dy * dy <= 1.0

    def move(self, dx: float, dy: float) -> None:
        self._x += dx
        self._y += dy

    def rotate(self, angle: float, center: QPointF | None = None) -> None:
        self._rotation = (self._rotation + angle) % 360.0

    def scale(self, factor: float, center: QPointF | None = None) -> None:
        if center is None:
            center = QPointF(self._x + self._width / 2, self._y + self._height / 2)
        self._width *= factor
        self._height *= factor

        # Защита от отрицательных или слишком малых размеров
        if self._width < 0.1:
            self._width = 0.1
        if self._height < 0.1:
            self._height = 0.1

        # Если размеры стали отрицательными, инвертируем координаты и размер
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
            abs(self._width) + pad * 2,
            abs(self._height) + pad * 2,
        )

    def _handle_positions(self) -> list[tuple[float, float]]:
        """Возвращает позиции всех маркеров преобразования."""
        cx = self._x + self._width / 2  # центр по X
        cy = self._y + self._height / 2  # центр по Y

        # Угловые маркеры
        top_left = (self._x, self._y)
        top_right = (self._x + self._width, self._y)
        bottom_left = (self._x, self._y + self._height)
        bottom_right = (self._x + self._width, self._y + self._height)

        # Центральные маркеры по сторонам
        top_center = (cx, self._y)
        bottom_center = (cx, self._y + self._height)
        left_center = (self._x, cy)
        right_center = (self._x + self._width, cy)

        return [
            top_left,
            top_right,
            bottom_left,
            bottom_right,
            top_center,
            bottom_center,
            left_center,
            right_center,
        ]

    def get_handles(self) -> list[QPointF]:
        return [QPointF(hx, hy) for hx, hy in self._handle_positions()]

    def get_handle_type(self, point: QPointF, tolerance: float = 5.0) -> HandleType:
        """
        Определяет тип маркера преобразования по координатам точки.

        Args:
            point: координаты точки клика
            tolerance: допуск в пикселях для определения попадания в маркер
        Returns:
            HandleType: тип маркера или NONE, если точка вне маркеров
        """
        handle_positions = self._handle_positions()
        handle_types = [
            HandleType.TOP_LEFT,
            HandleType.TOP_RIGHT,
            HandleType.BOTTOM_LEFT,
            HandleType.BOTTOM_RIGHT,
            HandleType.TOP_CENTER,
            HandleType.BOTTOM_CENTER,
            HandleType.LEFT_CENTER,
            HandleType.RIGHT_CENTER,
        ]

        px, py = point.x(), point.y()

        for pos, handle_type in zip(handle_positions, handle_types):
            hx, hy = pos
            # Вычисляем расстояние вручную
            distance = ((px - hx) ** 2 + (py - hy) ** 2) ** 0.5

            if distance <= tolerance:
                return handle_type

        return HandleType.NONE

    def apply_handle_transform(
        self, handle: HandleType, point: QPointF, mouse_pos: QPointF
    ) -> None:
        if handle == HandleType.LEFT_CENTER or handle == HandleType.RIGHT_CENTER:
            self._width = mouse_pos.x() - self._x
        elif handle == HandleType.TOP_CENTER or handle == HandleType.BOTTOM_CENTER:
            self._height = mouse_pos.y() - self._y

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
            }
        )
        return d

    @classmethod
    def from_dict(cls, data: dict) -> EllipseShape:
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
