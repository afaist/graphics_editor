# canvas/graphics_canvas.py
"""GraphicsCanvas — холст на основе QGraphicsView."""

from __future__ import annotations

from PySide6.QtCore import QPoint, QPointF, QRect, QRectF, Qt, Signal
from PySide6.QtGui import QColor, QContextMenuEvent, QMouseEvent, QPainter, QPen, QWheelEvent
from PySide6.QtSvg import QSvgGenerator
from PySide6.QtWidgets import (
    QGraphicsScene,
    QGraphicsView,
    QMenu,
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
    mouse_moved = Signal(object)  # MouseEvent
    mouse_released = Signal(object)  # MouseEvent

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
        self.viewport().update()
        self.zoom_changed.emit(self._zoom)

    def _apply_zoom(self, factor: float) -> None:
        new_zoom = self._zoom * factor
        if 0.05 <= new_zoom <= 50.0:
            self._zoom = new_zoom
            self.scale(factor, factor)
            self.viewport().update()
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
        # Проверка модификатора Ctrl для масштабирования
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            if event.angleDelta().y() > 0:
                self.zoom_in()
            else:
                self.zoom_out()
            # Предотвращаем прокрутку скроллбара при зуме
            event.accept()
        else:
            # Передаем событие базовому классу для стандартной прокрутки/панорамирования
            super().wheelEvent(event)

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        """Контекстное меню по ПКМ на холсте."""
        if not self._manager:
            return

        menu = QMenu(self)

        # Действия зависят от выделения
        has_selection = len(self._manager.selected_shapes) > 0

        copy_action = menu.addAction("Копировать")
        copy_action.setEnabled(has_selection)
        copy_action.setShortcut("Ctrl+C")

        paste_action = menu.addAction("Вставить")
        paste_action.setEnabled(bool(self._manager.clipboard_shapes))

        cut_action = menu.addAction("Вырезать")
        cut_action.setEnabled(has_selection)
        cut_action.setShortcut("Ctrl+X")

        menu.addSeparator()

        delete_action = menu.addAction("Удалить")
        delete_action.setEnabled(has_selection)
        delete_action.setShortcut("Delete")

        duplicate_action = menu.addAction("Дублировать")
        duplicate_action.setEnabled(has_selection)
        duplicate_action.setShortcut("Ctrl+D")

        menu.addSeparator()

        front_action = menu.addAction("На передний план")
        front_action.setEnabled(has_selection)

        back_action = menu.addAction("На задний план")
        back_action.setEnabled(has_selection)

        action = menu.exec(event.globalPos())
        if action is None:
            return

        # Выполняем выбранное действие
        if action == copy_action:
            self._manager.copy_selected()
        elif action == paste_action:
            self._manager.paste_from_clipboard()
        elif action == cut_action:
            self._manager.cut_selected()
        elif action == delete_action:
            self._manager.delete_selected_undo()
        elif action == duplicate_action:
            self._duplicate_selected()
        elif action == front_action:
            self._manager.bring_to_front()
        elif action == back_action:
            self._manager.send_to_back()

    def _duplicate_selected(self) -> None:
        """Дублировать выделенные фигуры."""
        from manager.undo_commands import DuplicateShapesCommand

        if not self._manager.selected_shapes:
            return
        cmd = DuplicateShapesCommand(self._manager, list(self._manager.selected_shapes))
        self._manager.undo_stack.push(cmd)

    # ------------------------------------------------------------------
    # Координаты из сцены в мировые
    # ------------------------------------------------------------------

    def scene_point(self, event_pos: QPoint | QPointF) -> QPointF:
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

    def drawBackground(self, painter: QPainter, rect: QRectF | QRect) -> None:
        # Случай 1: Сетка не видна -> рисуем только фон
        if not self._settings.grid_visible:
            super().drawBackground(painter, rect)
            return

        # Случай 2: Сетка видна -> рисуем фон и сетку напрямую
        painter.save()

        # 1. Рисуем фон (цвет)
        super().drawBackground(painter, rect)

        # 2. Рисуем сетку напрямую
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

    def viewport_rect(self) -> QRectF:
        """Вернуть видимую область сцены (viewport)."""
        if not self.scene():
            return QRectF()
        # Координаты viewport в экранных пикселях → переводим в координаты сцены
        vp_rect = self.viewport().rect()
        scene_rect = self.mapToScene(vp_rect).boundingRect()
        return scene_rect

    def export_to_png(self, file_path: str) -> None:
        """Экспорт сцены в PNG файл.

        Делегирует FileManager.export_png() — более надёжный подход:
        создаёт временную сцену, рендерит через QPainter + QImageWriter.
        """
        from fileio.file_manager import FileManager

        success = FileManager.export_png(self._manager, file_path)
        if not success:
            raise OSError(f"Не удалось сохранить PNG файл: {file_path}")

    def export_to_svg(
        self,
        file_path: str,
        region: str = "all_shapes",
        selected_ids: set[int] | None = None,
        viewport_rect: QRectF | None = None,
    ) -> None:
        """Экспорт сцены в SVG файл.

        Args:
            file_path: путь для сохранения
            region: "all_shapes" | "selected" | "viewport"
            selected_ids: ID выделенных фигур (для region="selected")
            viewport_rect: прямоугольник viewport (для region="viewport")
        """
        if not self.scene():
            raise Exception("Сцена не инициализирована")

        # Создаём временную сцену с нужными фигурами
        from PySide6.QtGui import QColor, QPainter

        from ui.scene_items import ShapeSceneItem

        temp_scene = QGraphicsScene()
        temp_scene.setBackgroundBrush(QColor(0xFFFFFF))

        if region == "selected" and selected_ids:
            for shape in self._manager.shapes:
                if shape.id in selected_ids:
                    item = ShapeSceneItem(shape)
                    item.setZValue(0)
                    temp_scene.addItem(item)
        else:
            for shape in self._manager.shapes:
                item = ShapeSceneItem(shape)
                item.setZValue(0)
                temp_scene.addItem(item)

        # Определяем область рендеринга
        if region == "viewport" and viewport_rect is not None:
            rect = viewport_rect
        else:
            rect = temp_scene.itemsBoundingRect()

        if rect.isEmpty():
            raise Exception("Сцена пуста")

        # Добавляем отступ (padding) — учитываем подписи вершин (~16px) + размер шрифта
        padding = 30
        rect.adjust(-padding, -padding, padding, padding)

        # Viewbox всегда начинается с (0, 0) — SVG не поддерживает отрицательные координаты в viewbox
        viewbox = QRectF(0, 0, rect.width(), rect.height())

        generator = QSvgGenerator()
        generator.setFileName(file_path)
        generator.setSize(viewbox.size().toSize())
        generator.setViewBox(viewbox)
        generator.setTitle("Графический редактор")
        generator.setDescription("Экспорт из графического редактора")

        # Рендерим: содержимое из rect масштабируется в viewbox
        painter = QPainter(generator)
        temp_scene.render(painter, viewbox, rect)
        painter.end()


# Конец файла
