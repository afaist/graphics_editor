"""Панель истории фигур — список всех фигур с возможностью удаления."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from shapes.base_shape import BaseShape


class HistoryPanel(QWidget):
    """Панель истории фигур — список всех фигур с возможностью удаления."""

    shape_selected = Signal(int)  # ID фигуры
    shape_deleted = Signal(int)  # ID удалённой фигуры

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(4)

        lbl = QLabel("Фигуры:")
        lbl.setStyleSheet("font-weight: bold;")
        layout.addWidget(lbl)

        self._list = QListWidget()
        self._list.itemClicked.connect(self._on_item_clicked)
        self._list.itemDoubleClicked.connect(self._on_item_double_clicked)
        # Контекстное меню: «Удалить»
        self._list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._list.customContextMenuRequested.connect(self._show_context_menu)
        layout.addWidget(self._list)

        # Кнопка «Удалить выбранную»
        btn_layout = QHBoxLayout()
        self._btn_delete = QPushButton("Удалить")
        self._btn_delete.clicked.connect(self._on_delete_selected)
        btn_layout.addWidget(self._btn_delete)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

    def update_shapes(self, shapes=None):
        """Обновить список фигур. Аргумент shapes необязателен — берётся из менеджера если не передан."""
        # Блокируем сигналы списка для предотвращения лишних событий
        self._list.blockSignals(True)

        try:
            if shapes is None:
                if not hasattr(self, "_mw") or self._mw is None:
                    return
                shapes = self._mw._manager.shapes

            # Очищаем список перед заполнением
            self._list.clear()

            # Добавляем фигуры в обратном порядке (новые сверху)
            for shape in reversed(shapes):
                item = self._create_shape_item(shape)
                self._list.addItem(item)

            # Восстановить выделение если нужно
            if self._list.count() > 0:
                self._list.setCurrentRow(0)
        finally:
            self._list.blockSignals(False)

    # Карта названий фигур на русском
    _SHAPE_NAMES_RU = {
        "point": "Точка",
        "line": "Отрезок",
        "ray": "Луч",
        "infinite_line": "Прямая",
        "rectangle": "Прямоугольник",
        "ellipse": "Эллипс",
        "polygon": "Многоугольник",
        "polyline": "Ломаная",
        "arc": "Дуга",
        "text": "Текст",
        "triangle_equilateral": "Треугольник",
        "triangle_isosceles": "Треугольник",
        "triangle_right": "Треугольник",
        "triangle_obtuse": "Треугольник",
        "parallelogram": "Параллелограмм",
        "trapezoid_isosceles": "Трапеция",
        "trapezoid": "Трапеция",
        "angle": "Угол",
    }

    def _create_shape_item(self, shape: BaseShape) -> QListWidgetItem:
        """Создать элемент списка для фигуры."""
        type_name = self._SHAPE_NAMES_RU.get(
            shape.shape_type.value, shape.shape_type.value.replace("_", " ").title()
        )
        pen_color: tuple[int, int, int] | None = None
        pc = shape.pen_color
        if isinstance(pc, QColor):
            pen_color = (pc.red(), pc.green(), pc.blue())
        elif isinstance(pc, tuple):
            pen_color = pc

        # Формируем текст: "[Цвет] Тип #ID"
        if pen_color is not None:
            color_label = f"[{pen_color[0]:02x}{pen_color[1]:02x}{pen_color[2]:02x}]"
        else:
            color_label = "[000000]"
        text = f"{color_label} {type_name} #{shape.id}"

        item = QListWidgetItem(text)
        item.setData(Qt.ItemDataRole.UserRole, shape.id)

        # Цветной квадратик
        if pen_color is not None:
            r, g, b = pen_color
            item.setForeground(QColor(r, g, b))

        return item

    def _on_item_clicked(self, item: QListWidgetItem):
        """Выделение фигуры при клике на строку."""
        shape_id = item.data(Qt.ItemDataRole.UserRole)
        if shape_id is not None:
            self.shape_selected.emit(shape_id)

    def _on_item_double_clicked(self, item: QListWidgetItem):
        """Двойной клик — можно добавить зум к фигуре."""
        pass

    def _show_context_menu(self, pos):
        """Контекстное меню: Удалить."""
        item = self._list.currentItem()
        if item is None:
            return

        menu = QMenu(self)
        delete_action = menu.addAction("Удалить")

        action = menu.exec(self._list.mapToGlobal(pos))
        if action == delete_action:
            shape_id = item.data(Qt.ItemDataRole.UserRole)
            if shape_id is not None:
                self._delete_shape(shape_id)

    def _on_delete_selected(self):
        """Удаление выбранной фигуры."""
        item = self._list.currentItem()
        if item is None:
            return
        shape_id = item.data(Qt.ItemDataRole.UserRole)
        if shape_id is not None:
            self._delete_shape(shape_id)

    def set_main_window(self, mw):
        """Устанавливает ссылку на MainWindow для удаления фигур."""
        self._mw = mw

    def _delete_shape(self, shape_id: int):
        """Удалить фигуру по ID через ShapeManager.delete_shape_by_id."""
        if not hasattr(self, "_mw") or self._mw is None:
            return
        manager = self._mw._manager
        if manager.has_shape(shape_id):
            manager.delete_shape_by_id(shape_id)
            self.shape_deleted.emit(shape_id)
