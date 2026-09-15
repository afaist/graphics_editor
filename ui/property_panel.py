"""Panel свойств выделенной фигуры."""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSpinBox,
    QDoubleSpinBox,
    QPushButton,
    QFrame,
)


class ColorButton(QPushButton):
    """Кнопка-образец цвета."""

    color_changed = Signal(tuple)  # (r, g, b)

    def __init__(self, initial: tuple = (0, 0, 0), parent=None):
        super().__init__(parent)
        self._color = list(initial)
        self.setText("...")
        self._update_style()
        self.clicked.connect(self._pick_color)

    def _update_style(self):
        r, g, b = self._color
        self.setStyleSheet(
            f"QPushButton {{ "
            f"background-color: rgb({r},{g},{b}); "
            f"border: 1px solid #999; "
            f"border-radius: 3px; "
            f"min-width: 40px; min-height: 24px; "
            f"}}"
        )

    def _pick_color(self):
        from PySide6.QtWidgets import QColorDialog
        c = QColorDialog.getColor(QColor(*self._color), self, "Выбор цвета")
        if c.isValid():
            self._color = (c.red(), c.green(), c.blue())
            self._update_style()
            self.color_changed.emit(self._color)

    def get_color(self) -> tuple:
        return tuple(self._color)

    def set_color(self, c: tuple):
        self._color = list(c)
        self._update_style()


class PropertyPanel(QWidget):
    """Панель свойств выделенной фигуры."""

    properties_changed = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._selected_props: Optional[dict] = None
        self._selected_shape_type: Optional[str] = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(8)

        # Цвет контура
        lbl1 = QLabel("Цвет контура:")
        lbl1.setStyleSheet("font-weight: bold;")
        layout.addWidget(lbl1)

        h1 = QHBoxLayout()
        self.btn_pen_color = ColorButton((0, 0, 0))
        self.btn_pen_color.color_changed.connect(self._on_pen_color_changed)
        h1.addWidget(self.btn_pen_color)
        h1.addStretch()
        layout.addLayout(h1)

        # Толщина линии
        lbl2 = QLabel("Толщина линии:")
        lbl2.setStyleSheet("font-weight: bold;")
        layout.addWidget(lbl2)

        self.spin_pen_width = QDoubleSpinBox()
        self.spin_pen_width.setRange(0.5, 50.0)
        self.spin_pen_width.setValue(2.0)
        self.spin_pen_width.setSingleStep(0.5)
        self.spin_pen_width.valueChanged.connect(self._on_pen_width_changed)
        layout.addWidget(self.spin_pen_width)

        # Цвет заливки
        lbl3 = QLabel("Цвет заливки:")
        lbl3.setStyleSheet("font-weight: bold;")
        layout.addWidget(lbl3)

        h3 = QHBoxLayout()
        self.btn_brush_color = ColorButton((255, 255, 255))
        self.btn_brush_color.color_changed.connect(self._on_brush_color_changed)
        h3.addWidget(self.btn_brush_color)

        self.chk_no_brush = QPushButton("Нет")
        self.chk_no_brush.setCheckable(True)
        self.chk_no_brush.setChecked(True)
        self.chk_no_brush.toggled.connect(self._on_no_brush_toggled)
        h3.addWidget(self.chk_no_brush)
        h3.addStretch()
        layout.addLayout(h3)

        # Поворот
        lbl4 = QLabel("Поворот (°):")
        lbl4.setStyleSheet("font-weight: bold;")
        layout.addWidget(lbl4)

        self.spin_rotation = QDoubleSpinBox()
        self.spin_rotation.setRange(0, 360)
        self.spin_rotation.setValue(0)
        self.spin_rotation.setSingleStep(1)
        self.spin_rotation.valueChanged.connect(self._on_rotation_changed)
        layout.addWidget(self.spin_rotation)

        layout.addSpacing(12)

        # Координаты и размеры (для прямоугольных фигур)
        lbl5 = QLabel("Позиция и размер:")
        lbl5.setStyleSheet("font-weight: bold;")
        layout.addWidget(lbl5)

        # X
        h_x = QHBoxLayout()
        lbl_x = QLabel("X:")
        lbl_x.setFixedWidth(20)
        self.spin_x = QDoubleSpinBox()
        self.spin_x.setRange(-10000, 10000)
        self.spin_x.setDecimals(1)
        self.spin_x.setValue(0)
        self.spin_x.setSingleStep(1)
        self.spin_x.valueChanged.connect(self._on_position_changed)
        h_x.addWidget(lbl_x)
        h_x.addWidget(self.spin_x)
        h_x.addStretch()
        layout.addLayout(h_x)

        # Y
        h_y = QHBoxLayout()
        lbl_y = QLabel("Y:")
        lbl_y.setFixedWidth(20)
        self.spin_y = QDoubleSpinBox()
        self.spin_y.setRange(-10000, 10000)
        self.spin_y.setDecimals(1)
        self.spin_y.setValue(0)
        self.spin_y.setSingleStep(1)
        self.spin_y.valueChanged.connect(self._on_position_changed)
        h_y.addWidget(lbl_y)
        h_y.addWidget(self.spin_y)
        h_y.addStretch()
        layout.addLayout(h_y)

        # Width
        h_w = QHBoxLayout()
        lbl_w = QLabel("Ш:")
        lbl_w.setFixedWidth(20)
        self.spin_width = QDoubleSpinBox()
        self.spin_width.setRange(0.1, 10000)
        self.spin_width.setDecimals(1)
        self.spin_width.setValue(100)
        self.spin_width.setSingleStep(1)
        self.spin_width.valueChanged.connect(self._on_size_changed)
        h_w.addWidget(lbl_w)
        h_w.addWidget(self.spin_width)
        h_w.addStretch()
        layout.addLayout(h_w)

        # Height
        h_h = QHBoxLayout()
        lbl_h = QLabel("В:")
        lbl_h.setFixedWidth(20)
        self.spin_height = QDoubleSpinBox()
        self.spin_height.setRange(0.1, 10000)
        self.spin_height.setDecimals(1)
        self.spin_height.setValue(100)
        self.spin_height.setSingleStep(1)
        self.spin_height.valueChanged.connect(self._on_size_changed)
        h_h.addWidget(lbl_h)
        h_h.addWidget(self.spin_height)
        h_h.addStretch()
        layout.addLayout(h_h)

        layout.addStretch()

    # ------------------------------------------------------------------
    # Обновление панели
    # ------------------------------------------------------------------

    def set_properties(self, props: Optional[dict]) -> None:
        self._selected_props = props
        if props is None:
            self.btn_pen_color.set_color((0, 0, 0))
            self.btn_pen_color.setEnabled(False)
            self.spin_pen_width.setEnabled(False)
            self.btn_brush_color.setEnabled(False)
            self.chk_no_brush.setEnabled(False)
            self.spin_rotation.setEnabled(False)
            # Отключаем поля координат/размеров
            self._enable_coordinate_fields(False)
            return

        self.btn_pen_color.setEnabled(True)
        self.spin_pen_width.setEnabled(True)
        self.btn_brush_color.setEnabled(True)
        self.chk_no_brush.setEnabled(True)
        self.spin_rotation.setEnabled(True)

        pen = props.get("pen_color", (0, 0, 0))
        self.btn_pen_color.set_color(pen)

        pw = props.get("pen_width", 2.0)
        self.spin_pen_width.setValue(pw)

        bc = props.get("brush_color")
        if bc:
            self.btn_brush_color.set_color(bc)
            self.chk_no_brush.setChecked(False)
        else:
            self.chk_no_brush.setChecked(True)

        rot = props.get("rotation", 0)
        self.spin_rotation.setValue(rot)

        # Определяем тип фигуры и показываем поля координат/размеров
        shape_type = props.get("_shape_type", "")
        self._selected_shape_type = shape_type

        geometry_shapes = (
            "rectangle", "ellipse",
            "triangle_equilateral", "triangle_isosceles",
            "triangle_right", "triangle_obtuse",
            "parallelogram", "trapezoid_isosceles", "trapezoid",
        )
        if shape_type in geometry_shapes:
            self._enable_coordinate_fields(True)
            self.spin_x.setValue(props.get("_x", 0))
            self.spin_y.setValue(props.get("_y", 0))
            self.spin_width.setValue(props.get("_width", 100))
            self.spin_height.setValue(props.get("_height", 100))
        else:
            self._enable_coordinate_fields(False)

    def _enable_coordinate_fields(self, enabled: bool) -> None:
        """Включить/отключить поля координат и размеров."""
        self.spin_x.setEnabled(enabled)
        self.spin_y.setEnabled(enabled)
        self.spin_width.setEnabled(enabled)
        self.spin_height.setEnabled(enabled)

    def clear(self) -> None:
        """Очистка панели свойств — сброс всех элементов к состоянию «нет выделения»."""
        # Сбрасываем внутренние данные
        self._selected_props = None
        self._selected_shape_type = None

        # Обновляем интерфейс: отключаем все элементы управления
        self.btn_pen_color.set_color((0, 0, 0))
        self.btn_pen_color.setEnabled(False)
        self.spin_pen_width.setEnabled(False)
        self.btn_brush_color.setEnabled(False)
        self.chk_no_brush.setEnabled(False)
        self.spin_rotation.setEnabled(False)
        self._enable_coordinate_fields(False)

        # Дополнительно сбрасываем значения элементов (опционально)
        self.spin_pen_width.setValue(2.0)
        self.btn_brush_color.set_color((255, 255, 255))
        self.chk_no_brush.setChecked(True)
        self.spin_rotation.setValue(0)
        self.spin_x.setValue(0)
        self.spin_y.setValue(0)
        self.spin_width.setValue(100)
        self.spin_height.setValue(100)

    def get_updated_properties(self) -> dict:
        """Возвращает текущие значения свойств из виджетов панели."""
        brush_color = None
        if not self.chk_no_brush.isChecked():
            brush_color = self.btn_brush_color.get_color()

        result = {
            "pen_color": self.btn_pen_color.get_color(),
            "pen_width": self.spin_pen_width.value(),
            "brush_color": brush_color,
            "rotation": self.spin_rotation.value(),
        }

        # Добавляем координаты и размеры, если они видны
        if self.spin_x.isEnabled():
            result["_x"] = self.spin_x.value()
            result["_y"] = self.spin_y.value()
            result["_width"] = self.spin_width.value()
            result["_height"] = self.spin_height.value()

        return result

    def set_multiple_shapes(self, shapes) -> None:
        """Установка общих свойств для нескольких фигур."""
        if not shapes:
            self.clear()
            return

        # Собираем общие свойства для всех фигур
        common_props = {}

        # Проверяем, совпадают ли свойства у всех фигур
        first_props = shapes[0].get_properties()

        for prop_name in ['pen_color', 'pen_width', 'brush_color', 'rotation']:
            if all(shape.get_properties().get(prop_name) == first_props.get(prop_name)
                for shape in shapes):
                common_props[prop_name] = first_props[prop_name]

        self.set_properties(common_props)


    # ------------------------------------------------------------------
    # Слоты
    # ------------------------------------------------------------------

    def _on_pen_color_changed(self, color: tuple):
        if self._selected_props is None:
            return
        self._selected_props["pen_color"] = color
        self.properties_changed.emit(self._selected_props)

    def _on_pen_width_changed(self, value: float):
        if self._selected_props is None:
            return
        self._selected_props["pen_width"] = value
        self.properties_changed.emit(self._selected_props)

    def _on_brush_color_changed(self, color: tuple):
        if self._selected_props is None:
            return
        self._selected_props["brush_color"] = color
        self.chk_no_brush.setChecked(False)
        self.properties_changed.emit(self._selected_props)

    def _on_no_brush_toggled(self, checked: bool):
        if self._selected_props is None:
            return
        if checked:
            self._selected_props["brush_color"] = None
            self.btn_brush_color.setEnabled(False)
        else:
            self.btn_brush_color.setEnabled(True)
        self.properties_changed.emit(self._selected_props)

    def _on_rotation_changed(self, value: float):
        if self._selected_props is None:
            return
        self._selected_props["rotation"] = value
        self.properties_changed.emit(self._selected_props)

    def _on_position_changed(self, value: float):
        """Обработчик изменения координат X или Y."""
        if self._selected_props is None:
            return
        # Определяем, какое поле изменилось
        sender = self.sender()
        if sender is self.spin_x:
            self._selected_props["_x"] = self.spin_x.value()
        elif sender is self.spin_y:
            self._selected_props["_y"] = self.spin_y.value()
        self.properties_changed.emit(self._selected_props)

    def _on_size_changed(self, value: float):
        """Обработчик изменения ширины или высоты."""
        if self._selected_props is None:
            return
        sender = self.sender()
        if sender is self.spin_width:
            self._selected_props["_width"] = self.spin_width.value()
        elif sender is self.spin_height:
            self._selected_props["_height"] = self.spin_height.value()
        self.properties_changed.emit(self._selected_props)
