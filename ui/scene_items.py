# ui/scene_items.py
from __future__ import annotations

from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtGui import QPainter, QPaintEvent
from PySide6.QtCore import QRectF, Qt

from shapes.base_shape import BaseShape


class ShapeSceneItem(QGraphicsItem):
    """QGraphicsItem-обёртка вокруг BaseShape для отображения в сцене."""

    def __init__(self, shape: BaseShape, parent=None):
        super().__init__(parent)
        self._shape = shape
        # Устанавливаем флаг, что мы принимаем события мыши, если нужно,
        # но для рисования достаточно paint.
        # Важно: ItemIsSelectable и ItemIsMovable управляются на уровне логических фигур или здесь, если нужно.
        # Сейчас вы отключаете их здесь, что ок, если логика обрабатывается в Canvas.
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        self.setAcceptedMouseButtons(Qt.MouseButton.NoButton)

    def boundingRect(self) -> QRectF:
        if self._shape is None:
            return QRectF()
        try:
            return self._shape.bounding_rect()
        except Exception:
            return QRectF()

    def paint(self, painter: QPainter, option, widget=None) -> None:
        if self._shape is None:
            return
        painter.save()
        try:
            self._shape.draw(painter)
        except Exception:
            # Если отрисовка фигуры упала, не ломаем всю сцену
            pass
        finally:
            painter.restore()

    def shape(self):
        """Возвращает точную форму для хит-теста."""
        # Для строк/отрезков хит-тест по boundingRect может быть неточным,
        # но для простоты пока оставим так.
        # Для улучшения можно вернуть QPainterPath, но это сложнее.
        return QGraphicsItem.shape(self)

    def mousePressEvent(self, event):
        pass

    def mouseMoveEvent(self, event):
        pass

    def mouseReleaseEvent(self, event):
        pass