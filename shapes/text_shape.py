"""Фигура: Текст."""

from __future__ import annotations

from typing import List, Optional, Tuple, Dict, Any

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPen, QFont

from .base_shape import BaseShape, HandleType, ShapeType


class TextShape(BaseShape):
    """Текстовая надпись на холсте."""

    DEFAULT_FONT_SIZE = 14

    def __init__(
        self,
        x: float,
        y: float,
        text: str = "",
        font_size: int = DEFAULT_FONT_SIZE,
        pen_color: Tuple[int, int, int] = (0, 0, 0),
        pen_width: float = 2.0,
        selected: bool = False,
    ):
        super().__init__(pen_color, pen_width, None, selected)
        self._x = x
        self._y = y
        self._text = text
        self._font_size = max(4, min(200, font_size))

    def _get_shape_type(self) -> ShapeType:
        return ShapeType.TEXT

    def set_end_point(self, x: float, y: float) -> None:
        pass

    def set_size(self, width: float, height: float) -> None:
        pass

    def add_vertex(self, x: float, y: float) -> None:
        pass

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
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, value: str) -> None:
        self._text = value

    @property
    def font_size(self) -> int:
        return self._font_size

    @font_size.setter
    def font_size(self, value: int) -> None:
        if value < 4:
            value = 4
        if value > 200:
            value = 200
        self._font_size = value

    # ------------------------------------------------------------------
    # Абстрактные методы
    # ------------------------------------------------------------------

    def draw(self, painter: QPainter) -> None:
        painter.save()
        try:
            pen = QPen(self.pen_color, self.pen_width)
            painter.setPen(pen)

            font = QFont("Segoe UI", self._font_size)
            painter.setFont(font)

            if self._text:
                # Рисуем текст с выравниванием по левому краю и базовой линии
                painter.drawText(
                    QPointF(self._x, self._y),
                    self._text,
                )

            if self._selected:
                pen.setColor(QColor(0, 120, 255))
                pen.setWidth(1)
                painter.setPen(pen)
                br = self.bounding_rect()
                if br.width() > 0 and br.height() > 0:
                    painter.drawRect(br)
        finally:
            painter.restore()

    def contains_point(self, point: QPointF) -> bool:
        if not self._text:
            return False
        br = self.bounding_rect()
        return br.contains(point)

    def move(self, dx: float, dy: float) -> None:
        self._x += dx
        self._y += dy

    def rotate(self, angle: float, center: Optional[QPointF] = None) -> None:
        # Текст не поддерживаем вращение в этой версии
        pass

    def scale(self, factor: float, center: Optional[QPointF] = None) -> None:
        if factor > 0:
            self._font_size = max(4, int(self._font_size * factor))

    def bounding_rect(self) -> QRectF:
        if not self._text:
            return self._safe_rect(
                self._x - 5,
                self._y - self._font_size,
                10,
                self._font_size + 5,
            )
        # Приблизительная оценка размера текста
        approx_width = len(self._text) * self._font_size * 0.6
        return self._safe_rect(
            self._x - 2,
            self._y - self._font_size - 2,
            max(approx_width, 10),
            self._font_size + 6,
        )

    def get_handles(self) -> List[QPointF]:
        if not self._text:
            return []
        br = self.bounding_rect()
        return [
            QPointF(br.left(), br.top()),
            QPointF(br.right(), br.top()),
            QPointF(br.left(), br.bottom()),
            QPointF(br.right(), br.bottom()),
        ]

    def get_handle_type(self, point: QPointF, tolerance: float = 5.0) -> HandleType:
        import math
        handles = self.get_handles()
        for i, h in enumerate(handles):
            dx = point.x() - h.x()
            dy = point.y() - h.y()
            if math.sqrt(dx * dx + dy * dy) <= tolerance:
                return HandleType(i + 2)
        return HandleType.NONE

    def apply_handle_transform(
        self, handle: HandleType, point: QPointF, mouse_pos: QPointF
    ) -> None:
        if handle == HandleType.TOP_LEFT:
            self._x = mouse_pos.x()
            self._y = mouse_pos.y()
        elif handle == HandleType.BOTTOM_RIGHT:
            self._font_size = max(4, int(mouse_pos.x() - self._x) // 6)

    # ------------------------------------------------------------------
    # Сериализация
    # ------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d.update({
            "x": self._x,
            "y": self._y,
            "text": self._text,
            "font_size": self._font_size,
        })
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TextShape":
        obj = cls(
            x=data["x"],
            y=data["y"],
            text=data.get("text", ""),
            font_size=data.get("font_size", cls.DEFAULT_FONT_SIZE),
            pen_color=data["pen_color"],
            pen_width=data.get("pen_width", 2.0),
            selected=data.get("selected", False),
        )
        obj._rotation = data.get("rotation", 0.0)
        return obj
