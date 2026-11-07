"""Фигура: Текст."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import QPointF, QRectF
from PySide6.QtGui import QFont, QFontDatabase, QPainter

from .base_shape import BaseShape, HandleType, ShapeType


class TextShape(BaseShape):
    """Текстовая надпись на холсте."""

    DEFAULT_FONT_SIZE = 14
    DEFAULT_FONT_FAMILY = "Segoe UI"

    # Доступные шрифты (по умолчанию — базовый набор)
    AVAILABLE_FONTS: list[str] = [
        "Segoe UI",
        "Arial",
        "Times New Roman",
        "Courier New",
        "Verdana",
        "Georgia",
        "Trebuchet MS",
        "Comic Sans MS",
        "Impact",
        "Lucida Console",
        "Tahoma",
        "Helvetica",
        "DejaVu Sans",
        "Ubuntu",
        "Liberation Sans",
        "MS Sans Serif",
    ]
    _fonts_populated: bool = False

    def __init__(
        self,
        x: float,
        y: float,
        text: str = "",
        font_size: int = DEFAULT_FONT_SIZE,
        font_family: str = DEFAULT_FONT_FAMILY,
        pen_color: tuple[int, int, int] = (0, 0, 0),
        pen_width: float = 2.0,
        selected: bool = False,
        font_weight: int = QFont.Weight.Normal,
        italic: bool = False,
        underline: bool = False,
        strikethrough: bool = False,
    ):
        super().__init__(pen_color, pen_width, None, selected)
        self._x = x
        self._y = y
        self._text = text
        self._font_size = max(4, min(200, font_size))
        self._font_family = font_family
        self._font_weight = font_weight
        self._italic = italic
        self._underline = underline
        self._strikethrough = strikethrough

    def _get_shape_type(self) -> ShapeType:
        """Возвращает тип фигуры — TEXT."""
        return ShapeType.TEXT

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

    @property
    def font_family(self) -> str:
        return self._font_family

    @font_family.setter
    def font_family(self, value: str) -> None:
        self._font_family = value

    @property
    def font_weight(self) -> int:
        return self._font_weight

    @font_weight.setter
    def font_weight(self, value: int) -> None:
        self._font_weight = value

    @property
    def italic(self) -> bool:
        return self._italic

    @italic.setter
    def italic(self, value: bool) -> None:
        self._italic = value

    @property
    def underline(self) -> bool:
        return self._underline

    @underline.setter
    def underline(self, value: bool) -> None:
        self._underline = value

    @property
    def strikethrough(self) -> bool:
        return self._strikethrough

    @strikethrough.setter
    def strikethrough(self, value: bool) -> None:
        self._strikethrough = value

    # ------------------------------------------------------------------
    # Вспомогательные методы
    # ------------------------------------------------------------------

    @classmethod
    def populate_available_fonts(cls) -> None:
        """Заполняет список доступных шрифтов из системы (если ещё не заполнен)."""
        if cls._fonts_populated:
            return
        try:
            db = QFontDatabase()
            for family in db.families():
                cls.AVAILABLE_FONTS.append(family)
        except Exception:
            pass
        cls._fonts_populated = True
        # Обеспечиваем наличие шрифта по умолчанию
        if cls.DEFAULT_FONT_FAMILY not in cls.AVAILABLE_FONTS:
            cls.AVAILABLE_FONTS.insert(0, cls.DEFAULT_FONT_FAMILY)

    def get_qfont(self) -> QFont:
        """Создаёт QFont на основе текущих свойств."""
        font = QFont(self._font_family, self._font_size)
        font.setWeight(QFont.Weight(self._font_weight))
        font.setItalic(self._italic)
        font.setUnderline(self._underline)
        font.setStrikeOut(self._strikethrough)
        return font

    # ------------------------------------------------------------------
    # Абстрактные методы
    # ------------------------------------------------------------------

    def _rotation_center(self) -> tuple[float, float] | None:
        """Возвращает центр поворота — центр bounding rect текста."""
        if not self._text:
            return None
        br = self.bounding_rect()
        cx = br.left() + br.width() / 2
        cy = br.top() + br.height() / 2
        return (cx, cy)

    def _draw_shape_content(self, painter: QPainter) -> None:
        """Рисует текст."""
        font = self.get_qfont()
        painter.setFont(font)

        if self._text:
            # Рисуем текст с выравниванием по левому краю и базовой линии
            painter.drawText(
                QPointF(self._x, self._y),
                self._text,
            )

    def contains_point(self, point: QPointF) -> bool:
        if not self._text:
            return False
        br = self.bounding_rect()
        return br.contains(point)

    def move(self, dx: float, dy: float) -> None:
        self._x += dx
        self._y += dy

    def rotate(self, angle: float, center: QPointF | None = None) -> None:
        # Текст не поддерживаем вращение в этой версии
        pass

    def scale(self, factor: float, center: QPointF | None = None) -> None:
        if factor > 0:
            self._font_size = max(4, int(self._font_size * factor))

    def _get_font_props(self) -> dict[str, Any]:
        """Возвращает словарь свойств шрифта."""
        return {
            "font_family": self._font_family,
            "font_weight": self._font_weight,
            "italic": self._italic,
            "underline": self._underline,
            "strikethrough": self._strikethrough,
        }

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

    def _handle_positions(self) -> list[tuple[float, float]]:
        if not self._text:
            return []
        br = self.bounding_rect()
        return [
            (br.left(), br.top()),
            (br.right(), br.top()),
            (br.left(), br.bottom()),
            (br.right(), br.bottom()),
        ]

    def get_handles(self) -> list[QPointF]:
        if not self._text:
            return []
        return [QPointF(hx, hy) for hx, hy in self._handle_positions()]

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
        self, handle: HandleType, point: QPointF, mouse_pos: QPointF, shift_pressed: bool = False
    ) -> None:
        if handle == HandleType.TOP_LEFT:
            self._x = mouse_pos.x()
            self._y = mouse_pos.y()
        elif handle == HandleType.BOTTOM_RIGHT:
            self._font_size = max(4, int(mouse_pos.x() - self._x) // 6)

    # ------------------------------------------------------------------
    # Позиция для undo
    # ------------------------------------------------------------------

    def get_position_data(self) -> dict[str, Any]:
        return {"x": self._x, "y": self._y}

    def restore_position_data(self, data: dict[str, Any]) -> None:
        self._x = data["x"]
        self._y = data["y"]

    # ------------------------------------------------------------------
    # Сериализация
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        d = super().to_dict()
        d.update(
            {
                "x": self._x,
                "y": self._y,
                "text": self._text,
                "font_size": self._font_size,
                "font_family": self._font_family,
                "font_weight": self._font_weight,
                "italic": self._italic,
                "underline": self._underline,
                "strikethrough": self._strikethrough,
            }
        )
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TextShape:
        obj = cls(
            x=data["x"],
            y=data["y"],
            text=data.get("text", ""),
            font_size=data.get("font_size", cls.DEFAULT_FONT_SIZE),
            font_family=data.get("font_family", cls.DEFAULT_FONT_FAMILY),
            pen_color=data["pen_color"],
            pen_width=data.get("pen_width", 2.0),
            selected=data.get("selected", False),
            font_weight=data.get("font_weight", QFont.Weight.Normal),
            italic=data.get("italic", False),
            underline=data.get("underline", False),
            strikethrough=data.get("strikethrough", False),
        )
        obj._rotation = data.get("rotation", 0.0)
        return obj
