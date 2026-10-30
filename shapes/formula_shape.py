"""Фигура: Математическая формула (LaTeX)."""

from __future__ import annotations

import math
from typing import Any

from PySide6.QtCore import QPointF, QRectF
from PySide6.QtGui import QColor, QImage, QPainter, QPen

from logging_config import get_logger

from .base_shape import BaseShape, HandleType, ShapeType

logger = get_logger("formula_shape")


def _get_default_fontset() -> str:
    """Определяет доступный mathtext fontset по умолчанию."""
    try:
        import matplotlib

        # Проверяем, был ли уже установлен fontset в main.py
        current = matplotlib.rcParams.get("mathtext.fontset", "cm")
        if current in ("dejavusans", "dejavuserif"):
            return current
    except Exception:
        pass
    return "cm"


class FormulaShape(BaseShape):
    """Математическая формула, отрисованная из LaTeX-строки через matplotlib."""

    DEFAULT_FONT_SIZE = 16
    # Масштаб рендеринга (DPI multiplier) — выше = лучше качество
    RENDER_SCALE = 2

    def __init__(
        self,
        x: float,
        y: float,
        latex_text: str = "",
        font_size: int = DEFAULT_FONT_SIZE,
        fontset: str | None = None,
        pen_color: tuple[int, int, int] = (0, 0, 0),
        pen_width: float = 2.0,
        selected: bool = False,
    ):
        if fontset is None:
            fontset = _get_default_fontset()
        super().__init__(pen_color, pen_width, None, selected)
        self._x = x
        self._y = y
        self._latex = latex_text
        self._font_size = max(4, min(200, font_size))
        self._fontset = fontset
        # Кэш рендернутого изображения
        self._rendered_image: QImage | None = None
        self._render_dirty: bool = True
        self._rendered_size: tuple[int, int] = (0, 0)

    def _get_shape_type(self) -> ShapeType:
        return ShapeType.FORMULA

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
    def latex(self) -> str:
        return self._latex

    @latex.setter
    def latex(self, value: str) -> None:
        if self._latex != value:
            self._latex = value
            self._render_dirty = True

    @property
    def font_size(self) -> int:
        return self._font_size

    @font_size.setter
    def font_size(self, value: int) -> None:
        if value < 4:
            value = 4
        if value > 200:
            value = 200
        if self._font_size != value:
            self._font_size = value
            self._render_dirty = True

    @property
    def fontset(self) -> str:
        return self._fontset

    @fontset.setter
    def fontset(self, value: str) -> None:
        if self._fontset != value:
            self._fontset = value
            self._render_dirty = True

    # ------------------------------------------------------------------
    # Рендеринг LaTeX
    # ------------------------------------------------------------------

    def _render_latex(self) -> None:
        """Рендерит LaTeX-строку в QImage через matplotlib.mathtext."""
        if not self._latex.strip():
            self._rendered_image = None
            self._rendered_size = (0, 0)
            self._render_dirty = False
            return

        try:
            import matplotlib
            from matplotlib.mathtext import MathTextParser

            # Масштабируем DPI пропорционально font_size
            scale = self._font_size / 10.0
            dpi = int(100 * self.RENDER_SCALE * scale)

            # Временно переключаем mathtext fontset
            rc = matplotlib.rcParams
            old_fontset = rc["mathtext.fontset"]
            rc["mathtext.fontset"] = self._fontset

            parser = MathTextParser("agg")
            parsed = parser.parse(f"${self._latex}$", dpi=dpi)
            arr = parsed.image

            import numpy as np

            arr = np.array(arr)
            if arr.ndim == 2:
                h, w = arr.shape
                rgba = np.zeros((h, w, 4), dtype=np.uint8)
                rgba[:, :, 0] = 0
                rgba[:, :, 1] = 0
                rgba[:, :, 2] = 0
                rgba[:, :, 3] = arr
            else:
                rgba = arr
            h, w = rgba.shape[:2]
            stride = w * 4
            qimage = QImage(rgba.tobytes(), w, h, stride, QImage.Format.Format_RGBA8888)
            self._rendered_image = qimage.copy()
            self._rendered_size = (w, h)

            rc["mathtext.fontset"] = old_fontset

        except ImportError:
            logger.debug("matplotlib не доступен, формула не рендерится")
            self._rendered_image = None
            self._rendered_size = (0, 0)
        except Exception:
            logger.warning("Ошибка рендеринга формулы: %s", self._latex[:50], exc_info=True)
            self._rendered_image = None
            self._rendered_size = (0, 0)
        finally:
            self._render_dirty = False

    # ------------------------------------------------------------------
    # Абстрактные методы
    # ------------------------------------------------------------------

    def draw(self, painter: QPainter) -> None:
        painter.save()
        try:
            pen = QPen(self.pen_color, self.pen_width)
            painter.setPen(pen)

            # Рендерим если нужно
            if self._render_dirty:
                self._render_latex()

            if self._rendered_image is not None and not self._rendered_image.isNull():
                painter.drawImage(QPointF(self._x, self._y), self._rendered_image)

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
        br = self.bounding_rect()
        return br.contains(point)

    def move(self, dx: float, dy: float) -> None:
        self._x += dx
        self._y += dy

    def rotate(self, angle: float, center: QPointF | None = None) -> None:
        # Формулы не поддерживаем вращение в этой версии
        pass

    def scale(self, factor: float, center: QPointF | None = None) -> None:
        if factor > 0:
            self._font_size = max(4, int(self._font_size * factor))
            self._render_dirty = True

    def bounding_rect(self) -> QRectF:
        if self._rendered_image is not None and not self._rendered_image.isNull():
            w = self._rendered_image.width()
            h = self._rendered_image.height()
            return self._safe_rect(
                self._x - 2,
                self._y - 2,
                max(w, 10),
                h + 6,
            )
        return self._safe_rect(
            self._x - 2,
            self._y - self._font_size - 2,
            100,
            self._font_size + 6,
        )

    def _handle_positions(self) -> list[tuple[float, float]]:
        br = self.bounding_rect()
        return [
            (br.left(), br.top()),
            (br.right(), br.top()),
            (br.left(), br.bottom()),
            (br.right(), br.bottom()),
        ]

    def get_handle_type(self, point: QPointF, tolerance: float = 5.0) -> HandleType:
        handles = self.get_handles()
        for i, h in enumerate(handles):
            dx = point.x() - h.x()
            dy = point.y() - h.y()
            if math.sqrt(dx * dx + dy * dy) <= tolerance:
                return HandleType(i + 2)
        return HandleType.NONE

    def apply_handle_transform(
        self,
        handle: HandleType,
        point: QPointF,
        mouse_pos: QPointF,
        shift_pressed: bool = False,
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
                "latex": self._latex,
                "font_size": self._font_size,
                "fontset": self._fontset,
            }
        )
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FormulaShape:
        obj = cls(
            x=data["x"],
            y=data["y"],
            latex_text=data.get("latex", ""),
            font_size=data.get("font_size", cls.DEFAULT_FONT_SIZE),
            fontset=data.get("fontset", _get_default_fontset()),
            pen_color=data["pen_color"],
            pen_width=data.get("pen_width", 2.0),
            selected=data.get("selected", False),
        )
        obj._rotation = data.get("rotation", 0.0)
        # При загрузке — принудительный перерендер
        obj._render_dirty = True
        return obj
