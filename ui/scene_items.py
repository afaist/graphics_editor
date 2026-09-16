# ui/scene_items.py
"""Модуль сценных объектов — QGraphicsItem-обёртки для фигур."""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Optional

from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtGui import QPainter, QPaintEvent, QPainterPath
from PySide6.QtCore import QPointF, QRectF, Qt

from shapes.base_shape import BaseShape, HandleType

if TYPE_CHECKING:
    from ui.main_window import MainWindow


class ShapeSceneItem(QGraphicsItem):
    """QGraphicsItem-обёртка вокруг BaseShape для отображения в сцене.

    Теперь этот Item является основным источником данных для трансформаций,
    а Canvas будет использовать его методы для точного хит-теста.

    Обработка мыши делегирована этому классу — он определяет маркеры,
    обрабатывает выделение, перетаскивание и изменение размера.
    """

    HANDLE_TOLERANCE = 8.0  # пиксели — допуск при попадании в маркер

    __slots__ = (
        "_callbacks",
    )

    def __init__(self, shape: BaseShape, parent=None):
        super().__init__(parent)
        self._shape = shape
        # Отключаем кэширование — важно для фигур с динамическим boundingRect (текст)
        self.setCacheMode(QGraphicsItem.CacheMode.NoCache)
        # Включаем флаги для взаимодействия с мышью
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        self.setAcceptedMouseButtons(
            Qt.MouseButton.LeftButton | Qt.MouseButton.RightButton
        )
        # Состояние перетаскивания
        self._dragging = False
        self._drag_start_pos: Optional[QRectF] = None
        self._active_handle: HandleType = HandleType.NONE
        self._handle_start_pos: Optional[QPointF] = None
        # Callback-based signal replacement — PySide6 Signal descriptor
        # doesn't work reliably on QGraphicsItem subclasses
        self._callbacks: dict[str, list[Callable]] = {
            "shape_selected": [],
            "shape_drag_started": [],
            "shape_dragging": [],
            "shape_drag_finished": [],
            "shape_resized": [],
        }

    # ------------------------------------------------------------------
    # Callback-базированные "сигналы" (замена PySide6 Signal для QGraphicsItem)
    # ------------------------------------------------------------------

    def on(self, event: str, callback: Callable) -> None:
        """Подписаться на событие."""
        if event in self._callbacks:
            self._callbacks[event].append(callback)

    def _emit(self, event: str, *args) -> None:
        """Вызвать все подписчики события."""
        for cb in self._callbacks.get(event, []):
            try:
                cb(*args)
            except Exception:
                pass

    # ------------------------------------------------------------------
    # Публичные методы
    # ------------------------------------------------------------------

    def get_shape(self) -> BaseShape:
        """Публичный доступ к фигуре для Canvas и менеджеров."""
        return self._shape

    # ------------------------------------------------------------------
    # Базовые QGraphicsItem методы
    # ------------------------------------------------------------------

    def boundingRect(self) -> QRectF:
        """Возвращает ограничивающий прямоугольник фигуры."""
        if self._shape is None:
            return QRectF()
        try:
            return self._shape.bounding_rect()
        except Exception:
            return QRectF()

    def paint(self, painter: QPainter, option, widget=None) -> None:
        """Отрисовка фигуры."""
        if painter is None:
            return
        if self._shape is None:
            return
        painter.save()
        try:
            self._shape.draw(painter)
        except Exception:
            pass
        finally:
            painter.restore()

        # Отрисовка маркеров преобразования при выделении
        if self.isSelected() and self._shape is not None:
            self._draw_handles(painter)

    def itemChange(self, change, value):
        """Реагируем на изменения состояния QGraphicsItem."""
        if change == QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
            self.update()
        return super().itemChange(change, value)

    def shape(self) -> QPainterPath:
        """Возвращает точную форму для хит-теста."""
        if self._shape is None:
            return QGraphicsItem.shape(self)
        try:
            # Пытаемся получить QPainterPath из фигуры
            path = self._shape.to_painter_path() if hasattr(self._shape, "to_painter_path") else None
            if path is not None:
                return path
        except Exception:
            pass
        # Fallback: bounding rect
        return QGraphicsItem.shape(self)

    # ------------------------------------------------------------------
    # Отрисовка маркеров
    # ------------------------------------------------------------------

    def _draw_handles(self, painter: QPainter) -> None:
        """Отрисовка маркеров преобразования вокруг выделенной фигуры."""
        from PySide6.QtGui import QPen, QBrush
        from PySide6.QtCore import QRectF

        painter.save()
        try:
            handles = self._shape.get_handles()
            pen = QPen(Qt.GlobalColor.black, 1.5)
            brush = QBrush(Qt.GlobalColor.white)
            handle_size = 6.0

            for handle_pos in handles:
                rect = QRectF(
                    handle_pos.x() - handle_size / 2,
                    handle_pos.y() - handle_size / 2,
                    handle_size,
                    handle_size,
                )
                painter.setPen(pen)
                painter.setBrush(brush)
                painter.drawRect(rect)
        except Exception:
            pass
        finally:
            painter.restore()

    # ------------------------------------------------------------------
    # Поиск маркера под курсором
    # ------------------------------------------------------------------

    def hit_test_handle(self, scene_pos: QPointF) -> HandleType:
        """Определяет, находится ли точка рядом с маркером преобразования."""
        if self._shape is None:
            return HandleType.NONE
        try:
            return self._shape.get_handle_type(scene_pos, self.HANDLE_TOLERANCE)
        except Exception:
            return HandleType.NONE

    # ------------------------------------------------------------------
    # Обработка мыши
    # ------------------------------------------------------------------

    def mousePressEvent(self, event):
        """Обработка нажатия левой кнопки мыши.

        Определяет, попал ли пользователь в маркер преобразования,
        или в тело фигуры для перетаскивания/выделения.
        """
        if event.button() != Qt.MouseButton.LeftButton:
            event.ignore()
            return

        scene_pos = self.mapToScene(event.pos())
        handle_type = self.hit_test_handle(scene_pos)

        if handle_type != HandleType.NONE:
            # Попадание в маркер — начинаем изменение размера
            self._active_handle = handle_type
            self._handle_start_pos = scene_pos
            self._dragging = True
            self._drag_start_pos = self.boundingRect()
            event.accept()
            return

        # Попадание в фигуру — выделяем или перетаскиваем
        if self._shape is not None:
            if self._shape.selected:
                # Уже выделена — начинаем перетаскивание
                self._dragging = True
                self._drag_start_pos = self.boundingRect()
                self._emit("shape_drag_started", self, event)
                event.accept()
            else:
                # Не выделена — сигнализируем о выделении
                self._emit("shape_selected", self, event)
                event.accept()
        else:
            event.ignore()

    def mouseMoveEvent(self, event):
        """Обработка движения мыши при зажатой кнопке.

        Перемещает фигуру или изменяет размер через маркеры.
        """
        if not self._dragging or self._shape is None:
            return

        scene_pos = self.mapToScene(event.pos())

        if self._active_handle != HandleType.NONE:
            # Изменение размера через маркер
            try:
                self._shape.apply_handle_transform(
                    self._active_handle,
                    self._handle_start_pos or scene_pos,
                    scene_pos,
                )
                self.update()
                self._emit("shape_resized", self)
            except Exception:
                pass
            event.accept()
        else:
            # Перетаскивание фигуры
            if self._drag_start_pos is not None:
                dx = scene_pos.x() - self._drag_start_pos.center().x()
                dy = scene_pos.y() - self._drag_start_pos.center().y()
                # Примечание: реальное перемещение обрабатывается через сигнал
                # shape_dragging, чтобы учесть перемещение всех выделенных фигур
            self._emit("shape_dragging", self, event)
            event.accept()

    def mouseReleaseEvent(self, event):
        """Обработка отпускания кнопки мыши."""
        if event.button() != Qt.MouseButton.LeftButton:
            event.ignore()
            return

        if self._dragging:
            self._dragging = False
            self._active_handle = HandleType.NONE
            self._drag_start_pos = None
            self._handle_start_pos = None
            self._emit("shape_drag_finished", self)
            event.accept()
        else:
            event.ignore()