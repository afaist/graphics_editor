"""ShapeSceneItem — обёртка фигуры для QGraphicsScene."""

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
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        self.setAcceptedMouseButtons(Qt.MouseButton.NoButton)  # не обрабатываем мышь — это делает canvas

    def boundingRect(self) -> QRectF:
        return self._shape.bounding_rect()

    def paint(self, painter: QPainter, option, widget=None) -> None:
        painter.save()
        self._shape.draw(painter)
        painter.restore()

    def shape(self):
        """Возвращает точную форму для хит-теста."""
        # упрощённо — используем bounding rect
        return QGraphicsItem.shape(self)

    def mousePressEvent(self, event):
        # не обрабатываем — мышь обрабатывается в MainWindow
        pass

    def mouseMoveEvent(self, event):
        pass

    def mouseReleaseEvent(self, event):
        pass

   