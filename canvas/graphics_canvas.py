# canvas/graphics_canvas.py
"""GraphicsCanvas — холст на основе QGraphicsView."""

from __future__ import annotations

from typing import Optional, Union

from PySide6.QtCore import QRect, Qt, QRectF, QPointF, Signal, QPoint
from PySide6.QtGui import QPainter, QPen, QColor, QPixmap, QWheelEvent, QMouseEvent
from PySide6.QtSvg import QSvgGenerator
from PySide6.QtWidgets import (
    QGraphicsView,
    QGraphicsScene,
)

from manager.shape_manager import ShapeManager
from settings.settings import Settings

class GraphicsCanvas(QGraphicsView):
    """Холст с сеткой, масштабированием и панорамированием."""

    # Сигналы
    mouse_position_changed = Signal(float, float)
    zoom_changed = Signal(float)

    # Новые сигналы для обработки мыши
    mouse_pressed = Signal(object)  # MouseEvent
    mouse_moved = Signal(object)    # MouseEvent
    mouse_released = Signal(object) # MouseEvent

    def __init__(
        self,
        scene: QGraphicsScene,
        manager: ShapeManager,
        settings: Settings,
        parent=None,
    ):
        super().__init__(parent)
        self.setScene(scene)
        self._manager = manager
        self._settings = settings

        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        # По умолчанию — без перетаскивания; переключается через set_drag_mode
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setBackgroundBrush(QColor(settings.canvas_background))

        self._zoom: float = 1.0

    # ------------------------------------------------------------------
    # Масштабирование
    # ------------------------------------------------------------------

    def zoom_in(self) -> None:
        self._apply_zoom(1.2)

    def zoom_out(self) -> None:
        self._apply_zoom(1 / 1.2)

    def reset_zoom(self) -> None:
        """Сбросить масштаб к 1.0 и перерисовать."""
        self._zoom = 1.0
        self.resetTransform()
        self.zoom_changed.emit(self._zoom)

    def _apply_zoom(self, factor: float) -> None:
        new_zoom = self._zoom * factor
        if 0.05 <= new_zoom <= 50.0:
            self._zoom = new_zoom
            self.scale(factor, factor)
            self.zoom_changed.emit(self._zoom)

    def get_zoom(self) -> float:
        return self._zoom

    # ------------------------------------------------------------------
    # Переключение режима перетаскивания (DragMode)
    # ------------------------------------------------------------------

    def set_drag_mode(self, mode: QGraphicsView.DragMode) -> None:
        """Переключить режим перетаскивания холста."""
        self.setDragMode(mode)

    # ------------------------------------------------------------------
    # Mouse events
    # ------------------------------------------------------------------

    def mousePressEvent(self, event: QMouseEvent):
        super().mousePressEvent(event)
        self.mouse_pressed.emit(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        super().mouseMoveEvent(event)
        self.mouse_moved.emit(event)

        # Используем event.pos() напрямую — он возвращает QPoint, совместимый с mapToScene
        pos = self.mapToScene(event.pos())
        self.mouse_position_changed.emit(pos.x(), pos.y())

    def mouseReleaseEvent(self, event: QMouseEvent):
        super().mouseReleaseEvent(event)
        self.mouse_released.emit(event)

    def wheelEvent(self, event: QWheelEvent):
        if event.angleDelta().y() > 0:
            self.zoom_in()
        else:
            self.zoom_out()

    # ------------------------------------------------------------------
    # Координаты из скены в мировые
    # ------------------------------------------------------------------

    def scene_point(self, event_pos: Union[QPoint, QPointF]) -> QPointF:
        """Возвращает координаты точки на сцене.

        Args:
            event_pos: QPoint или QPointF — позиция в координатах виджета

        Returns:
            QPointF — позиция в координатах сцены
        """
        if not self.scene():
            raise RuntimeError("Сцена не инициализирована")

        if isinstance(event_pos, QPoint):
            return self.mapToScene(event_pos)

        # Преобразуем QPointF в QPoint с округлением координат
        qpoint = QPoint(round(event_pos.x()), round(event_pos.y()))
        return self.mapToScene(qpoint)

    # ------------------------------------------------------------------
    # Привязка к сетке
    # ------------------------------------------------------------------


    def snap_to_grid(self, x: float, y: float) -> tuple:
        if not self._settings.snap_to_grid:
            return (x, y)
        sp = self._settings.grid_spacing
        sx = round(x / sp) * sp
        sy = round(y / sp) * sp
        return (sx, sy)

    # ------------------------------------------------------------------
    # Отрисовка сетки (в QGraphicsScene)
    # ------------------------------------------------------------------

    def drawBackground(self, painter: QPainter, rect: Union[QRectF, QRect]) -> None:
        # Случай 1: Сетка не видна -> рисуем только фон
        if not self._settings.grid_visible:
            super().drawBackground(painter, rect)
            return

        # Случай 2: Сетка видна -> сначала рисуем фон, потом сетку
        painter.save()

        # 1. Рисуем фон (цвет)
        super().drawBackground(painter, rect)

        # 2. Рисуем сетку
        rect_f = QRectF(rect) if not isinstance(rect, QRectF) else rect

        minor_color = QColor(self._settings.grid_color_minor)
        major_color = QColor(self._settings.grid_color_major)
        minor_sp = self._settings.grid_minor_spacing
        major_sp = self._settings.grid_spacing

        left = int(rect_f.left())
        top = int(rect_f.top())

        # минорная сетка
        pen_minor = QPen(minor_color, 0.5)
        painter.setPen(pen_minor)
        x = (left // minor_sp) * minor_sp
        while x < rect_f.right():
            painter.drawLine(int(x), int(rect_f.top()), int(x), int(rect_f.bottom()))
            x += minor_sp
        y = (top // minor_sp) * minor_sp
        while y < rect_f.bottom():
            painter.drawLine(int(rect_f.left()), int(y), int(rect_f.right()), int(y))
            y += minor_sp

        # мажорная сетка
        pen_major = QPen(major_color, 1.0)
        painter.setPen(pen_major)
        x = (left // major_sp) * major_sp
        while x < rect_f.right():
            painter.drawLine(int(x), int(rect_f.top()), int(x), int(rect_f.bottom()))
            x += major_sp
        y = (top // major_sp) * major_sp
        while y < rect_f.bottom():
            painter.drawLine(int(rect_f.left()), int(y), int(rect_f.right()), int(y))
            y += major_sp

        painter.restore()

    # ------------------------------------------------------------------
    # Экспорт
    # ------------------------------------------------------------------

    def export_to_png(self, file_path: str) -> None:
        """Экспорт сцены в PNG файл."""
        if not self.scene():
            raise Exception("Сцена не инициализирована")

        rect = self.sceneRect()
        if rect.isEmpty():
            pixmap = QPixmap(1, 1)
        else:
            # Создаём pixmap с размерами сцены
            pixmap = QPixmap(int(rect.width()), int(rect.height()))
            pixmap.fill(QColor(self._settings.canvas_background))  # Заливка фоном

            # Рендерим сцену в pixmap
            painter = QPainter(pixmap)
            self.scene().render(painter, QRectF(0, 0, rect.width(), rect.height()), rect)
            painter.end()

        # Сохраняем в файл
        if not pixmap.save(file_path):
            raise IOError(f"Не удалось сохранить PNG файл: {file_path}")

    def export_to_svg(self, file_path: str) -> None:
        """Экспорт сцены в SVG файл."""
        if not self.scene():
            raise Exception("Сцена не инициализирована")

        rect = self.sceneRect()
        if rect.isEmpty():
            raise Exception("Сцена пуста")

        generator = QSvgGenerator()
        generator.setFileName(file_path)
        generator.setSize(rect.size().toSize())
        generator.setViewBox(rect)
        generator.setTitle("Графический редактор")
        generator.setDescription("Экспорт из графического редактора")

        # Рендерим сцену в SVG
        painter = QPainter(generator)
        self.scene().render(painter, QRectF(0, 0, rect.width(), rect.height()), rect)
        painter.end()

# Конец файла