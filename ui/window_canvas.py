"""Модуль настройки сцены и холста для MainWindow."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QColor, QPen, QPainter
from PySide6.QtWidgets import QGraphicsScene

if TYPE_CHECKING:
    from ui.scene_items import ShapeSceneItem


class CanvasManager:
    """Управление графической сценой, холстом и отрисовкой сетки."""

    def __init__(self, main_window):
        """
        Args:
            main_window: ссылка на MainWindow (для доступа к self._scene,
                         self._settings, self._manager и т.д.)
        """
        self._mw = main_window

    # ------------------------------------------------------------------
    # Инициализация сцены и холста
    # ------------------------------------------------------------------

    def setup_scene(self):
        """Настройка графической сцены и холста."""
        mw = self._mw
        mw._scene = QGraphicsScene(mw)
        mw._scene.setBackgroundBrush(QColor(mw._settings.canvas_background))

        from canvas.graphics_canvas import GraphicsCanvas

        mw._canvas = GraphicsCanvas(mw._scene, mw._manager, mw._settings, mw)

    # ------------------------------------------------------------------
    # Отрисовка сетки
    # ------------------------------------------------------------------

    def draw_grid(self, painter: QPainter, rect: QRectF) -> None:
        """Отрисовка сетки на холсте."""
        if not self._mw._settings.grid_visible:
            return

        painter.save()
        from PySide6.QtGui import QColor, QPen

        minor_color = QColor(self._mw._settings.grid_color_minor)
        major_color = QColor(self._mw._settings.grid_color_major)
        minor_sp = self._mw._settings.grid_minor_spacing
        major_sp = self._mw._settings.grid_spacing

        left = int(rect.left())
        top = int(rect.top())

        # Отрисовка мелких линий
        pen_minor = QPen(minor_color, 0.5)
        painter.setPen(pen_minor)
        self._draw_grid_lines(painter, left, top, rect, minor_sp)

        # Отрисовка крупных линий
        pen_major = QPen(major_color, 1.0)
        painter.setPen(pen_major)
        self._draw_grid_lines(painter, left, top, rect, major_sp)

        painter.restore()

    def _draw_grid_lines(
        self, painter: QPainter, left: int, top: int, rect: QRectF, spacing: int
    ) -> None:
        """Вспомогательный метод для отрисовки линий сетки."""
        # Вертикальные линии
        x = (left // spacing) * spacing
        while x < rect.right():
            painter.drawLine(int(x), int(rect.top()), int(x), int(rect.bottom()))
            x += spacing

        # Горизонтальные линии
        y = (top // spacing) * spacing
        while y < rect.bottom():
            painter.drawLine(int(rect.left()), int(y), int(rect.right()), int(y))
            y += spacing

    # ------------------------------------------------------------------
    # Синхронизация сцены
    # ------------------------------------------------------------------

    def sync_scene_with_manager(self):
        """Синхронизировать items сцены с фигурами менеджера.

        Использует shape.id как ключ для сопоставления ShapeSceneItem <-> BaseShape.
        """
        scene = self._mw._scene
        if scene is None:
            return

        from ui.scene_items import ShapeSceneItem

        # 1. Собираем map: shape_id -> ShapeSceneItem
        shape_id_to_item: dict[int, ShapeSceneItem] = {}
        for item in scene.items():
            if isinstance(item, ShapeSceneItem) and item.zValue() == 0:
                shape = item._shape if hasattr(item, '_shape') else None
                if shape is not None:
                    shape_id_to_item[shape.id] = item

        # 2. Проходим по фигурам менеджера (manager.shapes — это list значений)
        manager_shapes_list = self._mw._manager.shapes  # List[BaseShape]
        shape_ids_in_manager = {s.id for s in manager_shapes_list}
        shape_ids_in_scene = set(shape_id_to_item.keys())

        # 3. Items для обновления (есть и в manager, и в scene)
        common_ids = shape_ids_in_manager & shape_ids_in_scene
        for sid in common_ids:
            item = shape_id_to_item[sid]
            item.update()

        # 4. Items для создания (есть в manager, нет в scene)
        new_ids = shape_ids_in_manager - shape_ids_in_scene
        for sid in new_ids:
            # Находим shape по id
            shape = None
            for s in manager_shapes_list:
                if s.id == sid:
                    shape = s
                    break
            if shape is None:
                continue
            item = ShapeSceneItem(shape)
            item.setZValue(0)
            scene.addItem(item)

        # 5. Items для удаления (есть в scene, нет в manager)
        removed_ids = shape_ids_in_scene - shape_ids_in_manager
        for sid in removed_ids:
            item = shape_id_to_item[sid]
            scene.removeItem(item)

    # ------------------------------------------------------------------
    # Обновление холста
    # ------------------------------------------------------------------

    def refresh_canvas(self):
        """Принудительное обновление холста."""
        if self._mw._canvas:
            self._mw._canvas.update()
