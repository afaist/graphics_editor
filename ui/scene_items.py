# ui/scene_items.py
from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QGraphicsItem

from shapes.base_shape import BaseShape

if TYPE_CHECKING:
    pass


class ShapeSceneItem(QGraphicsItem):
    """QGraphicsItem-обёртка вокруг BaseShape для отображения в сцене.

    Теперь этот Item является основным источником данных для трансформаций,
    а Canvas будет использовать его методы для точного хит-теста.
    """

    def __init__(self, shape: BaseShape, parent=None):
        super().__init__(parent)
        self._shape = shape
        # Отключаем кэширование — важно для фигур с динамическим boundingRect (текст)
        self.setCacheMode(QGraphicsItem.CacheMode.NoCache)
        # Важно: ItemIsSelectable нужен, если мы хотим, чтобы Qt сам управлял подсветкой,
        # но в нашей архитектуре выделение управляет логическая фигура.
        # Мы отключаем флаги, так как логика кастомная, но позволяем принимать события.
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        self.setAcceptedMouseButtons(Qt.MouseButton.NoButton)

    def get_shape(self) -> BaseShape:
        """Публичный доступ к фигуре для Canvas и менеджеров."""
        return self._shape

    def boundingRect(self) -> QRectF:
        if self._shape is None:
            return QRectF()
        try:
            return self._shape.bounding_rect()
        except Exception:
            return QRectF()

    def paint(self, painter: QPainter, option, widget=None) -> None:
        # Защита: painter может быть невалидным
        if painter is None:
            return
        # Защита: shape может быть удалён
        if self._shape is None:
            return
        painter.save()
        try:
            self._shape.draw(painter)
        except Exception:
            pass
        finally:
            painter.restore()

    def itemChange(self, change, value):
        """Переопределяем itemChange для принудительной перерисовки."""
        if change == QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
            self.update()
        return super().itemChange(change, value)

    def shape(self):
        """Возвращает точную форму для хит-теста."""
        # Для оптимизации можно возвращать QPainterPath из фигуры, если он доступен
        # Сейчас возвращаем прямоугольник boundingRect для простоты
        return QGraphicsItem.shape(self)
