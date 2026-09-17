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

        layout.addSpacing(12)

        # Параметры дуги (скрыты по умолчанию)
        lbl_arc = QLabel("Параметры дуги:")
        lbl_arc.setStyleSheet("font-weight: bold;")
        layout.addWidget(lbl_arc)

        # Радиус
        h_r = QHBoxLayout()
        lbl_r = QLabel("R:")
        lbl_r.setFixedWidth(20)
        self.spin_radius = QDoubleSpinBox()
        self.spin_radius.setRange(0.1, 10000)
        self.spin_radius.setDecimals(1)
        self.spin_radius.setValue(100)
        self.spin_radius.setSingleStep(1)
        self.spin_radius.valueChanged.connect(self._on_arc_params_changed)
        h_r.addWidget(lbl_r)
        h_r.addWidget(self.spin_radius)
        h_r.addStretch()
        layout.addLayout(h_r)

        # Угол начала
        h_sa = QHBoxLayout()
        lbl_sa = QLabel("Начало:")
        lbl_sa.setFixedWidth(50)
        self.spin_start_angle = QDoubleSpinBox()
        self.spin_start_angle.setRange(0, 360)
        self.spin_start_angle.setDecimals(1)
        self.spin_start_angle.setValue(0)
        self.spin_start_angle.setSingleStep(1)
        self.spin_start_angle.setSuffix("°")
        self.spin_start_angle.valueChanged.connect(self._on_arc_params_changed)
        h_sa.addWidget(lbl_sa)
        h_sa.addWidget(self.spin_start_angle)
        h_sa.addStretch()
        layout.addLayout(h_sa)

        # Угол окончания
        h_ea = QHBoxLayout()
        lbl_ea = QLabel("Окончание:")
        lbl_ea.setFixedWidth(60)
        self.spin_end_angle = QDoubleSpinBox()
        self.spin_end_angle.setRange(0, 360)
        self.spin_end_angle.setDecimals(1)
        self.spin_end_angle.setValue(90)
        self.spin_end_angle.setSingleStep(1)
        self.spin_end_angle.setSuffix("°")
        self.spin_end_angle.valueChanged.connect(self._on_arc_params_changed)
        h_ea.addWidget(lbl_ea)
        h_ea.addWidget(self.spin_end_angle)
        h_ea.addStretch()
        layout.addLayout(h_ea)

        layout.addSpacing(12)

        # Параметры угла (скрыты по умолчанию)
        lbl_angle = QLabel("Параметры угла:")
        lbl_angle.setStyleSheet("font-weight: bold;")
        layout.addWidget(lbl_angle)
        self.lbl_angle_params = lbl_angle
        self.lbl_angle_params.setVisible(False)

        # Сторона a
        h_a = QHBoxLayout()
        lbl_a = QLabel("a:")
        lbl_a.setFixedWidth(20)
        self.spin_side_a = QDoubleSpinBox()
        self.spin_side_a.setRange(0.1, 10000)
        self.spin_side_a.setDecimals(1)
        self.spin_side_a.setValue(150)
        self.spin_side_a.setSingleStep(1)
        self.spin_side_a.valueChanged.connect(self._on_angle_params_changed)
        h_a.addWidget(lbl_a)
        h_a.addWidget(self.spin_side_a)
        h_a.addStretch()
        self.h_side_a = h_a
        layout.addLayout(h_a)

        # Сторона b
        h_b = QHBoxLayout()
        lbl_b = QLabel("b:")
        lbl_b.setFixedWidth(20)
        self.spin_side_b = QDoubleSpinBox()
        self.spin_side_b.setRange(0.1, 10000)
        self.spin_side_b.setDecimals(1)
        self.spin_side_b.setValue(100)
        self.spin_side_b.setSingleStep(1)
        self.spin_side_b.valueChanged.connect(self._on_angle_params_changed)
        h_b.addWidget(lbl_b)
        h_b.addWidget(self.spin_side_b)
        h_b.addStretch()
        self.h_side_b = h_b
        layout.addLayout(h_b)

        # Угол
        h_ang = QHBoxLayout()
        lbl_ang = QLabel("Угол:")
        lbl_ang.setFixedWidth(35)
        self.spin_angle_deg = QDoubleSpinBox()
        self.spin_angle_deg.setRange(0.1, 359.9)
        self.spin_angle_deg.setDecimals(1)
        self.spin_angle_deg.setValue(90)
        self.spin_angle_deg.setSingleStep(1)
        self.spin_angle_deg.setSuffix("°")
        self.spin_angle_deg.valueChanged.connect(self._on_angle_params_changed)
        h_ang.addWidget(lbl_ang)
        h_ang.addWidget(self.spin_angle_deg)
        h_ang.addStretch()
        self.h_angle_deg = h_ang
        layout.addLayout(h_ang)

        # Скрыть поля параметров угла по умолчанию
        self.lbl_angle_params.setVisible(False)
        for i in range(self.h_side_a.count()):
            w = self.h_side_a.itemAt(i).widget()
            if w:
                w.setVisible(False)
        for i in range(self.h_side_b.count()):
            w = self.h_side_b.itemAt(i).widget()
            if w:
                w.setVisible(False)
        for i in range(self.h_angle_deg.count()):
            w = self.h_angle_deg.itemAt(i).widget()
            if w:
                w.setVisible(False)

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
            self._enable_coordinate_fields(False)
            self._enable_arc_fields(False)
            return

        self.btn_pen_color.setEnabled(False)
        self.spin_pen_width.setEnabled(False)
        self.btn_brush_color.setEnabled(False)
        self.chk_no_brush.setEnabled(False)
        self.spin_rotation.setEnabled(False)
        # Отключаем поля координат/размеров и дуги
        self._enable_coordinate_fields(False)
        self._enable_arc_fields(False)
        self._enable_angle_fields(False)

        self.btn_pen_color.setEnabled(True)
        self.spin_pen_width.setEnabled(True)
        self.btn_brush_color.setEnabled(True)
        self.chk_no_brush.setEnabled(True)
        self.spin_rotation.setEnabled(True)

        pen = props.get("pen_color", (0, 0, 0))
        self.btn_pen_color.set_color(pen)

        pw = props.get("pen_width", 2.0)
        self.spin_pen_width.blockSignals(True)
        self.spin_pen_width.setValue(pw)
        self.spin_pen_width.blockSignals(False)

        bc = props.get("brush_color")
        if bc:
            self.btn_brush_color.set_color(bc)
            self.chk_no_brush.setChecked(False)
        else:
            self.chk_no_brush.setChecked(True)

        rot = props.get("rotation", 0)
        self.spin_rotation.blockSignals(True)
        self.spin_rotation.setValue(rot)
        self.spin_rotation.blockSignals(False)

        # Определяем тип фигуры и показываем поля координат/размеров
        shape_type = props.get("_shape_type", "")
        self._selected_shape_type = shape_type

        geometry_shapes = (
            "rectangle", "ellipse",
            "triangle_equilateral", "triangle_isosceles",
            "triangle_right", "triangle_obtuse",
            "parallelogram", "trapezoid_isosceles", "trapezoid",
            "angle",
        )
        if shape_type == "arc":
            # Для дуги показываем координаты/размеры и параметры дуги
            self._enable_coordinate_fields(True)
            self._enable_arc_fields(True)
            self.spin_x.blockSignals(True)
            self.spin_x.setValue(props.get("_x", 0))
            self.spin_x.blockSignals(False)
            self.spin_y.blockSignals(True)
            self.spin_y.setValue(props.get("_y", 0))
            self.spin_y.blockSignals(False)
            self.spin_width.blockSignals(True)
            self.spin_width.setValue(props.get("_width", 100))
            self.spin_width.blockSignals(False)
            self.spin_height.blockSignals(True)
            self.spin_height.setValue(props.get("_height", 100))
            self.spin_height.blockSignals(False)
            self.spin_radius.blockSignals(True)
            self.spin_radius.setValue(props.get("_radius", 100))
            self.spin_radius.blockSignals(False)
            self.spin_start_angle.blockSignals(True)
            self.spin_start_angle.setValue(props.get("_start_angle", 0))
            self.spin_start_angle.blockSignals(False)
            self.spin_end_angle.blockSignals(True)
            self.spin_end_angle.setValue(props.get("_end_angle", 90))
            self.spin_end_angle.blockSignals(False)
        elif shape_type in geometry_shapes:
            self._enable_coordinate_fields(True)
            self._enable_arc_fields(False)
            self.spin_x.blockSignals(True)
            self.spin_x.setValue(props.get("_x", 0))
            self.spin_x.blockSignals(False)
            self.spin_y.blockSignals(True)
            self.spin_y.setValue(props.get("_y", 0))
            self.spin_y.blockSignals(False)
            self.spin_width.blockSignals(True)
            self.spin_width.setValue(props.get("_width", 100))
            self.spin_width.blockSignals(False)
            self.spin_height.blockSignals(True)
            self.spin_height.setValue(props.get("_height", 100))
            self.spin_height.blockSignals(False)
            if shape_type == "angle":
                self._enable_angle_fields(True)
                self.spin_side_a.blockSignals(True)
                self.spin_side_a.setValue(props.get("_side_a", 150))
                self.spin_side_a.blockSignals(False)
                self.spin_side_b.blockSignals(True)
                self.spin_side_b.setValue(props.get("_side_b", 100))
                self.spin_side_b.blockSignals(False)
                self.spin_angle_deg.blockSignals(True)
                self.spin_angle_deg.setValue(props.get("_angle_deg", 90))
                self.spin_angle_deg.blockSignals(False)
            else:
                self._enable_angle_fields(False)
        else:
            self._enable_coordinate_fields(False)
            self._enable_arc_fields(False)

    def _enable_coordinate_fields(self, enabled: bool) -> None:
        """Включить/отключить поля координат и размеров."""
        self.spin_x.setEnabled(enabled)
        self.spin_y.setEnabled(enabled)
        self.spin_width.setEnabled(enabled)
        self.spin_height.setEnabled(enabled)

    def _enable_arc_fields(self, enabled: bool) -> None:
        """Включить/отключить поля параметров дуги."""
        self.spin_radius.setEnabled(enabled)
        self.spin_start_angle.setEnabled(enabled)
        self.spin_end_angle.setEnabled(enabled)

    def _enable_angle_fields(self, enabled: bool) -> None:
        """Включить/отключить поля параметров угла."""
        self.lbl_angle_params.setVisible(enabled)
        # Layouts don't have setVisible, hide children widgets
        for i in range(self.h_side_a.count()):
            w = self.h_side_a.itemAt(i).widget()
            if w:
                w.setVisible(enabled)
        for i in range(self.h_side_b.count()):
            w = self.h_side_b.itemAt(i).widget()
            if w:
                w.setVisible(enabled)
        for i in range(self.h_angle_deg.count()):
            w = self.h_angle_deg.itemAt(i).widget()
            if w:
                w.setVisible(enabled)
        self.spin_side_a.setEnabled(enabled)
        self.spin_side_b.setEnabled(enabled)
        self.spin_angle_deg.setEnabled(enabled)

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
        self._enable_arc_fields(False)
        self._enable_angle_fields(False)

        # Дополнительно сбрасываем значения элементов (опционально)
        self.spin_pen_width.blockSignals(True)
        self.spin_pen_width.setValue(2.0)
        self.spin_pen_width.blockSignals(False)
        self.btn_brush_color.set_color((255, 255, 255))
        self.chk_no_brush.setChecked(True)
        self.spin_rotation.blockSignals(True)
        self.spin_rotation.setValue(0)
        self.spin_rotation.blockSignals(False)
        self.spin_x.blockSignals(True)
        self.spin_x.setValue(0)
        self.spin_x.blockSignals(False)
        self.spin_y.blockSignals(True)
        self.spin_y.setValue(0)
        self.spin_y.blockSignals(False)
        self.spin_width.blockSignals(True)
        self.spin_width.setValue(100)
        self.spin_width.blockSignals(False)
        self.spin_height.blockSignals(True)
        self.spin_height.setValue(100)
        self.spin_height.blockSignals(False)
        self.spin_radius.blockSignals(True)
        self.spin_radius.setValue(100)
        self.spin_radius.blockSignals(False)
        self.spin_start_angle.blockSignals(True)
        self.spin_start_angle.setValue(0)
        self.spin_start_angle.blockSignals(False)
        self.spin_end_angle.blockSignals(True)
        self.spin_end_angle.setValue(90)
        self.spin_end_angle.blockSignals(False)

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

        # Добавляем параметры дуги, если они видны
        if self.spin_radius.isEnabled():
            result["_radius"] = self.spin_radius.value()
            result["_start_angle"] = self.spin_start_angle.value()
            result["_end_angle"] = self.spin_end_angle.value()

        # Добавляем параметры угла, если они видны
        if self.spin_side_a.isEnabled():
            result["_side_a"] = self.spin_side_a.value()
            result["_side_b"] = self.spin_side_b.value()
            result["_angle_deg"] = self.spin_angle_deg.value()

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

    def _on_arc_params_changed(self, value: float):
        """Обработчик изменения параметров дуги."""
        if self._selected_props is None:
            return
        sender = self.sender()
        if sender is self.spin_radius:
            self._selected_props["_radius"] = self.spin_radius.value()
        elif sender is self.spin_start_angle:
            self._selected_props["_start_angle"] = self.spin_start_angle.value()
        elif sender is self.spin_end_angle:
            self._selected_props["_end_angle"] = self.spin_end_angle.value()
        self.properties_changed.emit(self._selected_props)

    def _on_angle_params_changed(self, value: float):
        """Обработчик изменения параметров угла."""
        if self._selected_props is None:
            return
        sender = self.sender()
        if sender is self.spin_side_a:
            self._selected_props["_side_a"] = self.spin_side_a.value()
        elif sender is self.spin_side_b:
            self._selected_props["_side_b"] = self.spin_side_b.value()
        elif sender is self.spin_angle_deg:
            self._selected_props["_angle_deg"] = self.spin_angle_deg.value()
        self.properties_changed.emit(self._selected_props)
