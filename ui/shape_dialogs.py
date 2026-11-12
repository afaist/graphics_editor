"""Диалоги ввода параметров для новых геометрических фигур."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)


class ShapeParamDialog(QDialog):
    """Базовый диалог для ввода параметров фигуры."""

    def __init__(self, parent, title: str):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(320)

        # Непрозрачный фон — предотвращает прозрачность от стиля приложения
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.setStyleSheet(
            "QDialog { "
            "    background-color: #ffffff; "
            "} "
            "QGroupBox { "
            "    font-weight: bold; "
            "    border: 1px solid #ddd; "
            "    border-radius: 4px; "
            "    margin-top: 8px; "
            "    padding-top: 12px; "
            "} "
            "QGroupBox::title { "
            "    subcontrol-origin: margin; "
            "    left: 8px; "
            "} "
            "QLabel { "
            "    color: #000000; "
            "    font-size: 10pt; "
            "} "
            "QFormLayout QLabel { "
            "    color: #000000; "
            "    font-size: 10pt; "
            "} "
            "QComboBox, QDoubleSpinBox, QSpinBox { "
            "    background-color: #ffffff; "
            "    color: #000000; "
            "    border: 1px solid #999; "
            "    border-radius: 3px; "
            "    padding: 4px 8px; "
            "    font-size: 10pt; "
            "} "
            "QComboBox::drop-down { "
            "    border: none; "
            "} "
            "QComboBox::down-arrow { "
            "    image: none; "
            "    border: 2px solid #999; "
            "    border-radius: 2px; "
            "    min-width: 8px; "
            "    min-height: 8px; "
            "} "
            "QPushButton { "
            "    background-color: #ffffff; "
            "    color: #000000; "
            "    border: 1px solid #999; "
            "    border-radius: 3px; "
            "    padding: 6px 16px; "
            "    font-size: 10pt; "
            "    font-weight: bold; "
            "} "
            "QPushButton:hover { "
            "    background-color: #e0e0e0; "
            "} "
            "QPushButton:pressed { "
            "    background-color: #cccccc; "
            "}"
        )

        self._main_layout = QVBoxLayout(self)
        self._main_layout.setSpacing(12)

        self.params_layout = QFormLayout()
        self.params_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        self._main_layout.addLayout(self.params_layout)

        self._main_layout.addStretch()

        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Отмена")
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        self._main_layout.addLayout(btn_layout)

        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)

    def get_params(self) -> dict:
        """Возвращает параметры, введённые в диалоге. Переопределяется в подклассах."""
        return {}

    def _create_double_spin(
        self, label: str, min_val: float, max_val: float, default: float
    ) -> QDoubleSpinBox:
        """Создать QDoubleSpinBox и добавить в layout. Переопределяется при необходимости."""
        spin = QDoubleSpinBox()
        spin.setRange(min_val, max_val)
        spin.setValue(default)
        spin.setSingleStep(1)
        spin.setDecimals(1)
        self.params_layout.addRow(label, spin)
        return spin

    def _create_labeled_spin(
        self, label_text: str, min_val: float, max_val: float, default: float
    ):
        """Создать QDoubleSpinBox с QLabel и вернуть (spin, label)."""
        label = QLabel(label_text)
        spin = QDoubleSpinBox()
        spin.setRange(min_val, max_val)
        spin.setValue(default)
        spin.setSingleStep(1)
        spin.setDecimals(1)
        self.params_layout.addRow(label, spin)
        return spin, label

    def _add_hint(self, text: str) -> None:
        """Добавить подсказку в конец диалога."""
        hint = QLabel(text)
        hint.setStyleSheet("color: #666; font-size: 9pt;")
        self.layout().insertWidget(self.layout().count() - 1, hint)


class TriangleParamDialog(ShapeParamDialog):
    """Диалог ввода параметров треугольника."""

    def __init__(self, parent, triangle_type: str = "equilateral"):
        super().__init__(parent, "Параметры треугольника")

        self._type_combo = QComboBox()
        self._type_combo.addItems(
            ["Правильный", "Равнобедренный", "Прямоугольный", "Тупоугольный"]
        )

        type_values = ["equilateral", "isosceles", "right", "obtuse"]
        current_idx = type_values.index(triangle_type) if triangle_type in type_values else 0
        self._type_combo.setCurrentIndex(current_idx)

        self.params_layout.addRow("Тип:", self._type_combo)

        # Поля для каждого типа — сохраняем ссылки на лейблы для скрытия/показа
        self._side_a_spin, self._side_a_label = self._create_labeled_spin(
            "Сторона:", 10, 2000, 100
        )
        self._side_b_spin, self._side_b_label = self._create_labeled_spin(
            "Сторона (b):", 10, 2000, 100
        )
        self._height_spin, self._height_label = self._create_labeled_spin(
            "Высота:", 10, 2000, 86.6
        )
        self._angle_spin, self._angle_label = self._create_labeled_spin("Угол (°):", 1, 179, 60)

        # --- Группа: Построение из вершины ---
        sep1 = QLabel("───────────────────────────────")
        sep1.setStyleSheet("color: #999;")
        self.params_layout.addRow(sep1)

        # Выбор вершины
        self._vertex_combo = QComboBox()
        self._vertex_combo.addItems(["A", "B", "C"])
        self._vertex_combo.setCurrentIndex(0)
        self.params_layout.addRow("Из вершины:", self._vertex_combo)

        # Чекбоксы для дополнительных линий (по умолчанию НЕ выбраны)
        # Используем QHBoxLayout с отступом для видимости чекбоксов

        hlayout = QHBoxLayout()
        hlayout.setContentsMargins(30, 0, 0, 0)

        self._draw_height_cb = QCheckBox("Высота")
        self._draw_height_cb.setChecked(False)
        hlayout.addWidget(self._draw_height_cb)

        self._draw_median_cb = QCheckBox("Медиана")
        self._draw_median_cb.setChecked(False)
        hlayout.addWidget(self._draw_median_cb)

        self._draw_bisector_cb = QCheckBox("Биссектриса")
        self._draw_bisector_cb.setChecked(False)
        hlayout.addWidget(self._draw_bisector_cb)

        hlayout.addStretch()
        self.params_layout.addRow("", hlayout)

        # --- Группа: Окружности ---
        sep2 = QLabel("───────────────────────────────")
        sep2.setStyleSheet("color: #999;")
        self.params_layout.addRow(sep2)

        hlayout2 = QHBoxLayout()
        hlayout2.setContentsMargins(30, 0, 0, 0)

        self._circumscribed_cb = QCheckBox("Описанная окружность")
        self._circumscribed_cb.setChecked(False)
        hlayout2.addWidget(self._circumscribed_cb)

        self._inscribed_cb = QCheckBox("Вписанная окружность")
        self._inscribed_cb.setChecked(False)
        hlayout2.addWidget(self._inscribed_cb)

        hlayout2.addStretch()
        self.params_layout.addRow("", hlayout2)

        # --- Группа: Размеры углов ---
        sep3 = QLabel("───────────────────────────────")
        sep3.setStyleSheet("color: #999;")
        self.params_layout.addRow(sep3)

        hlayout3 = QHBoxLayout()
        hlayout3.setContentsMargins(30, 0, 0, 0)

        self._draw_angles_cb = QCheckBox("Выводить размер углов")
        self._draw_angles_cb.setChecked(False)
        hlayout3.addWidget(self._draw_angles_cb)

        hlayout3.addStretch()
        self.params_layout.addRow("", hlayout3)

        self._hint_label = QLabel("")
        self._hint_label.setStyleSheet("color: #666; font-size: 9pt;")
        self._update_hint("equilateral")

        self._type_combo.currentIndexChanged.connect(self._on_type_changed)

        # Добавить подсказку в layout
        self.layout().addWidget(self._hint_label)

        # Сначала показываем поля для equilateral
        self._update_fields("equilateral")
        self._on_type_changed(current_idx)

    def _update_fields(self, type_key: str):
        """Показать/скрыть поля в зависимости от типа."""
        if type_key == "equilateral":
            self._side_a_label.setVisible(True)
            self._side_a_spin.setVisible(True)
            self._side_b_label.setVisible(False)
            self._side_b_spin.setVisible(False)
            self._height_label.setVisible(False)
            self._height_spin.setVisible(False)
            self._angle_label.setVisible(False)
            self._angle_spin.setVisible(False)
        elif type_key == "isosceles":
            self._side_a_label.setVisible(True)
            self._side_a_spin.setVisible(True)
            self._side_b_label.setVisible(False)
            self._side_b_spin.setVisible(False)
            self._height_label.setVisible(True)
            self._height_spin.setVisible(True)
            self._angle_label.setVisible(False)
            self._angle_spin.setVisible(False)
        elif type_key == "right":
            self._side_a_label.setVisible(True)
            self._side_a_spin.setVisible(True)
            self._side_b_label.setVisible(True)
            self._side_b_spin.setVisible(True)
            self._height_label.setVisible(False)
            self._height_spin.setVisible(False)
            self._angle_label.setVisible(False)
            self._angle_spin.setVisible(False)
        elif type_key == "obtuse":
            self._side_a_label.setVisible(True)
            self._side_a_spin.setVisible(True)
            self._side_b_label.setVisible(True)
            self._side_b_spin.setVisible(True)
            self._height_label.setVisible(False)
            self._height_spin.setVisible(False)
            self._angle_label.setVisible(True)
            self._angle_spin.setVisible(True)

    def _update_hint(self, type_key: str):
        hints = {
            "equilateral": "Достаточна одна сторона — все углы 60°",
            "isosceles": "Основание (a) и высота из вершины",
            "right": "Катеты a и b (угол 90° между ними)",
            "obtuse": "Две стороны и угол между ними (> 90° — тупоугольный)",
        }
        self._hint_label.setText(hints.get(type_key, ""))

    def _on_type_changed(self, index: int):
        type_values = ["equilateral", "isosceles", "right", "obtuse"]
        type_key = type_values[index]

        # Обновляем подсказку и видимость полей
        self._update_hint(type_key)
        self._update_fields(type_key)

        # Обновляем тексты лейблов в зависимости от типа
        if type_key == "equilateral":
            self._side_a_label.setText("Сторона:")
        elif type_key == "isosceles":
            self._side_a_label.setText("Основание:")
            self._height_label.setText("Высота:")
        elif type_key == "right":
            self._side_a_label.setText("Катет (a):")
            self._side_b_label.setText("Катет (b):")
        elif type_key == "obtuse":
            self._side_a_label.setText("Сторона (a):")
            self._side_b_label.setText("Сторона (b):")

        # Обновляем диапазон и значение угла в зависимости от типа
        if type_key == "obtuse":
            self._angle_spin.setRange(91, 179)
            self._angle_spin.setValue(120)
        elif type_key == "right":
            self._angle_spin.setRange(1, 179)
            self._angle_spin.setValue(90)
        elif type_key == "equilateral" or type_key == "isosceles":
            self._angle_spin.setRange(1, 179)
            self._angle_spin.setValue(60)

    def get_params(self) -> dict:
        type_values = ["equilateral", "isosceles", "right", "obtuse"]
        triangle_type = type_values[self._type_combo.currentIndex()]

        return {
            "triangle_type": triangle_type,
            "side_a": self._side_a_spin.value(),
            "side_b": self._side_b_spin.value(),
            "height": self._height_spin.value(),
            "angle_deg": self._angle_spin.value(),
            "vertex_index": self._vertex_combo.currentIndex(),
            "draw_height": self._draw_height_cb.isChecked(),
            "draw_median": self._draw_median_cb.isChecked(),
            "draw_bisector": self._draw_bisector_cb.isChecked(),
            "draw_circumscribed": self._circumscribed_cb.isChecked(),
            "draw_inscribed": self._inscribed_cb.isChecked(),
            "draw_angles": self._draw_angles_cb.isChecked(),
        }


class ParallelogramParamDialog(ShapeParamDialog):
    """Диалог ввода параметров параллелограмма."""

    def __init__(self, parent):
        super().__init__(parent, "Параметры параллелограмма")

        self._side_a_spin = self._create_double_spin("Сторона (a):", 10, 2000, 150)
        self._side_b_spin = self._create_double_spin("Сторона (b):", 10, 2000, 100)
        self._angle_spin = self._create_double_spin("Угол при основании (°):", 1, 179, 60)

        # Дополнительные линии
        hlayout = QHBoxLayout()
        hlayout.setContentsMargins(30, 0, 0, 0)

        self._show_heights_cb = QCheckBox("Высота")
        self._show_heights_cb.setChecked(False)
        hlayout.addWidget(self._show_heights_cb)

        self._show_diagonals_cb = QCheckBox("Диагонали")
        self._show_diagonals_cb.setChecked(False)
        hlayout.addWidget(self._show_diagonals_cb)

        self._show_circumcircle_cb = QCheckBox("Описанная окружность")
        self._show_circumcircle_cb.setChecked(False)
        hlayout.addWidget(self._show_circumcircle_cb)

        hlayout.addStretch()
        self.params_layout.addRow("", hlayout)

        # Выбор вершины для высот
        self._height_vertex_combo = QComboBox()
        self._height_vertex_combo.addItem("Из всех вершин", -1)
        self._height_vertex_combo.addItem("Из вершины A", 0)
        self._height_vertex_combo.addItem("Из вершины B", 1)
        self._height_vertex_combo.addItem("Из вершины C", 2)
        self._height_vertex_combo.addItem("Из вершины D", 3)
        self._height_vertex_combo.setCurrentIndex(0)
        self.params_layout.addRow("Высоты из:", self._height_vertex_combo)

    def get_params(self) -> dict:
        return {
            "side_a": self._side_a_spin.value(),
            "side_b": self._side_b_spin.value(),
            "angle_deg": self._angle_spin.value(),
            "show_heights": self._show_heights_cb.isChecked(),
            "show_diagonals": self._show_diagonals_cb.isChecked(),
            "show_circumcircle": self._show_circumcircle_cb.isChecked(),
            "height_from_vertex": self._height_vertex_combo.currentData(),
        }


class TrapezoidParamDialog(ShapeParamDialog):
    """Диалог ввода параметров трапеции."""

    def __init__(self, parent, trapezoid_type: str = "scalene"):
        super().__init__(parent, "Параметры трапеции")

        # Фиксируем тип трапеции на основе выбранного инструмента
        self._trapezoid_type = trapezoid_type

        if self._trapezoid_type == "isosceles":
            # Равнобедренная: основания + угол
            self._base_a_spin, self._base_a_label = self._create_labeled_spin(
                "Основание (a):", 10, 2000, 200
            )
            self._base_b_spin, self._base_b_label = self._create_labeled_spin(
                "Основание (b):", 10, 2000, 100
            )
            self._angle_spin, self._angle_label = self._create_labeled_spin(
                "Угол при основании (°):", 1, 179, 60
            )
        else:
            # Произвольная: top_width, bottom_width, height, offset_left
            self._top_width_spin, self._top_width_label = self._create_labeled_spin(
                "Верхнее основание:", 10, 2000, 100
            )
            self._bottom_width_spin, self._bottom_width_label = self._create_labeled_spin(
                "Нижнее основание:", 10, 2000, 200
            )
            self._height_spin, self._height_label = self._create_labeled_spin(
                "Высота:", 10, 2000, 100
            )
            self._offset_left_spin, self._offset_left_label = self._create_labeled_spin(
                "Смещение (offset_left):", -1000, 1000, 0
            )

        # Чекбокс средней линии
        self._midline_checkbox = QCheckBox("Показать среднюю линию")
        self._midline_checkbox.setChecked(False)
        self.params_layout.addRow("", self._midline_checkbox)

        # Дополнительные линии
        hlayout2 = QHBoxLayout()
        hlayout2.setContentsMargins(30, 0, 0, 0)

        self._show_heights_cb = QCheckBox("Высота")
        self._show_heights_cb.setChecked(False)
        hlayout2.addWidget(self._show_heights_cb)

        self._show_diagonals_cb = QCheckBox("Диагонали")
        self._show_diagonals_cb.setChecked(False)
        hlayout2.addWidget(self._show_diagonals_cb)

        self._show_circumcircle_cb = QCheckBox("Описанная окружность")
        self._show_circumcircle_cb.setChecked(False)
        hlayout2.addWidget(self._show_circumcircle_cb)

        hlayout2.addStretch()
        self.params_layout.addRow("", hlayout2)

        # Выбор вершины для высот
        self._height_vertex_combo = QComboBox()
        self._height_vertex_combo.addItem("Из всех вершин", -1)
        self._height_vertex_combo.addItem("Из вершины A", 0)
        self._height_vertex_combo.addItem("Из вершины B", 1)
        self._height_vertex_combo.addItem("Из вершины C", 2)
        self._height_vertex_combo.addItem("Из вершины D", 3)
        self._height_vertex_combo.setCurrentIndex(0)
        self.params_layout.addRow("Высоты из:", self._height_vertex_combo)

    def get_params(self) -> dict:
        params = {
            "trapezoid_type": self._trapezoid_type,
            "show_midline": self._midline_checkbox.isChecked(),
            "show_heights": self._show_heights_cb.isChecked(),
            "show_diagonals": self._show_diagonals_cb.isChecked(),
            "show_circumcircle": self._show_circumcircle_cb.isChecked(),
            "height_from_vertex": self._height_vertex_combo.currentData(),
        }
        if self._trapezoid_type == "isosceles":
            params.update(
                {
                    "base_a": self._base_a_spin.value(),
                    "base_b": self._base_b_spin.value(),
                    "angle_deg": self._angle_spin.value(),
                }
            )
        else:
            params.update(
                {
                    "top_width": self._top_width_spin.value(),
                    "bottom_width": self._bottom_width_spin.value(),
                    "height": self._height_spin.value(),
                    "offset_left": self._offset_left_spin.value(),
                }
            )
        return params


class RectangleParamDialog(ShapeParamDialog):
    """Диалог ввода параметров прямоугольника."""

    def __init__(self, parent):
        super().__init__(parent, "Параметры прямоугольника")

        self._width_spin = self._create_double_spin("Ширина:", 10, 2000, 200)
        self._height_spin = self._create_double_spin("Высота:", 10, 2000, 150)

        hlayout = QHBoxLayout()
        hlayout.setContentsMargins(30, 0, 0, 0)

        self._show_diagonals_cb = QCheckBox("Диагонали")
        self._show_diagonals_cb.setChecked(False)
        hlayout.addWidget(self._show_diagonals_cb)

        self._show_circumcircle_cb = QCheckBox("Описанная окружность")
        self._show_circumcircle_cb.setChecked(False)
        hlayout.addWidget(self._show_circumcircle_cb)

        hlayout.addStretch()
        self.params_layout.addRow("", hlayout)

    def get_params(self) -> dict:
        return {
            "width": self._width_spin.value(),
            "height": self._height_spin.value(),
            "show_diagonals": self._show_diagonals_cb.isChecked(),
            "show_circumcircle": self._show_circumcircle_cb.isChecked(),
        }


class ArcParamDialog(ShapeParamDialog):
    """Диалог ввода параметров дуги."""

    def __init__(self, parent):
        super().__init__(parent, "Параметры дуги")

        self._radius_spin = self._create_double_spin("Радиус:", 10, 2000, 100)
        self._start_angle_spin = self._create_double_spin("Угол начала (°):", 0, 360, 0)
        self._end_angle_spin = self._create_double_spin("Угол окончания (°):", 0, 360, 180)

        # Подсказка
        self._add_hint("0° = 3 часа, углы по часовой стрелке")

    def get_params(self) -> dict:
        return {
            "radius": self._radius_spin.value(),
        }


class CircleParamDialog(ShapeParamDialog):
    """Диалог ввода параметров окружности."""

    def __init__(self, parent):
        super().__init__(parent, "Параметры окружности")

        self._radius_spin = self._create_double_spin("Радиус:", 10, 2000, 100)

        # Комбо-бокс для типа отображения радиуса/диаметра
        self._radius_type_combo = QComboBox()
        self._radius_type_combo.addItems(["Радиус", "Диаметр"])
        self.params_layout.addRow("Отображение:", self._radius_type_combo)

        # Комбо-бокс для типа касательной
        self._tangent_type_combo = QComboBox()
        self._tangent_type_combo.addItems(["Нет", "Одна касательная", "Две касательные из точки"])
        self.params_layout.addRow("Касательная:", self._tangent_type_combo)

        # Чекбокс для хорды
        self._show_chord_cb = QCheckBox("Показать хорду")
        self.params_layout.addRow("", self._show_chord_cb)

        # Подсказка
        self._add_hint(
            "Окружность с центром и дополнительными элементами.\n"
            "Касательная строится перпендикулярно радиусу в точке на окружности."
        )

    def get_params(self) -> dict:
        return {
            "radius": self._radius_spin.value(),
            "radius_type": self._radius_type_combo.currentIndex(),  # 0=radius, 1=diameter
            "tangent_type": self._tangent_type_combo.currentIndex(),  # 0=none, 1=single, 2=double
            "show_chord": self._show_chord_cb.isChecked(),
        }


class ParabolaParamDialog(ShapeParamDialog):
    """Диалог ввода параметров параболы."""

    def __init__(self, parent):
        super().__init__(parent, "Параметры параболы")

        self._focal_length_spin = self._create_double_spin("Фокальный параметр (p):", 10, 1000, 80)

        self._direction_combo = QComboBox()
        self._direction_combo.addItems(["Вверх ↑", "Вниз ↓", "Вправо →", "Влево ←"])
        self.params_layout.addRow("Направление:", self._direction_combo)

        # Подсказка
        self._add_hint("Парабола: y = a·(x-h)² + k, где a = 1/(4p)")

    def get_params(self) -> dict:
        direction_map = {0: "up", 1: "down", 2: "right", 3: "left"}
        return {
            "focal_length": self._focal_length_spin.value(),
            "direction": direction_map[self._direction_combo.currentIndex()],
        }


class HyperbolaParamDialog(ShapeParamDialog):
    """Диалог ввода параметров гиперболы."""

    def __init__(self, parent):
        super().__init__(parent, "Параметры гиперболы")

        self._semi_axis_a_spin = self._create_double_spin("Полуось (a):", 10, 1000, 80)
        self._semi_axis_b_spin = self._create_double_spin("Полуось (b):", 10, 1000, 60)

        self._direction_combo = QComboBox()
        self._direction_combo.addItems(["Горизонтальная ↔", "Вертикальная ↕"])
        self.params_layout.addRow("Направление:", self._direction_combo)

        # Подсказка
        self._add_hint("Гипербола: (x-h)²/a² - (y-k)²/b² = 1")

    def get_params(self) -> dict:
        direction_map = {0: "horizontal", 1: "vertical"}
        return {
            "semi_axis_a": self._semi_axis_a_spin.value(),
            "semi_axis_b": self._semi_axis_b_spin.value(),
            "direction": direction_map[self._direction_combo.currentIndex()],
        }


class AngleParamDialog(ShapeParamDialog):
    """Диалог ввода параметров угла."""

    def __init__(self, parent):
        super().__init__(parent, "Параметры угла")

        self._side_a_spin = self._create_double_spin("Сторона (a):", 10, 2000, 150)
        self._side_b_spin = self._create_double_spin("Сторона (b):", 10, 2000, 100)
        self._angle_spin = self._create_double_spin("Угол (°):", 0.1, 359.9, 90)

        # Подсказка
        self._add_hint("0° = 3 часа, углы отсчитываются против часовой стрелки")

    def get_params(self) -> dict:
        return {
            "side_a": self._side_a_spin.value(),
            "side_b": self._side_b_spin.value(),
            "angle_deg": self._angle_spin.value(),
        }


class AdjacentAngleParamDialog(ShapeParamDialog):
    """Диалог ввода параметров смежных углов."""

    def __init__(self, parent):
        super().__init__(parent, "Параметры смежных углов")

        self._side_a_spin = self._create_double_spin("Сторона (a):", 10, 2000, 150)
        self._side_b_spin = self._create_double_spin("Сторона (b):", 10, 2000, 100)
        self._side_c_spin = self._create_double_spin("Сторона (c):", 10, 2000, 150)
        self._angle_spin = self._create_double_spin("Угол (°):", 0.1, 179.9, 90)

        # Подсказка
        self._add_hint("Смежные углы: α + β = 180°, общая сторона между ними")

    def get_params(self) -> dict:
        return {
            "side_a": self._side_a_spin.value(),
            "side_b": self._side_b_spin.value(),
            "side_c": self._side_c_spin.value(),
            "angle_deg": self._angle_spin.value(),
        }


class VerticalAngleParamDialog(ShapeParamDialog):
    """Диалог ввода параметров вертикальных углов."""

    def __init__(self, parent):
        super().__init__(parent, "Параметры вертикальных углов")

        self._side_a_spin = self._create_double_spin("Сторона (a):", 10, 2000, 150)
        self._side_b_spin = self._create_double_spin("Сторона (b):", 10, 2000, 100)
        self._side_c_spin = self._create_double_spin("Сторона (c):", 10, 2000, 150)
        self._angle_spin = self._create_double_spin("Угол (°):", 0.1, 179.9, 90)

        # Подсказка
        self._hint_label = QLabel(
            "Вертикальные углы: α = γ, β = δ, образуются при пересечении двух прямых"
        )
        self._hint_label.setStyleSheet("color: #666; font-size: 9pt;")
        self.layout().insertWidget(self.layout().count() - 1, self._hint_label)

    def get_params(self) -> dict:
        return {
            "side_a": self._side_a_spin.value(),
            "side_b": self._side_b_spin.value(),
            "side_c": self._side_c_spin.value(),
            "angle_deg": self._angle_spin.value(),
        }


class TransversalAngleParamDialog(ShapeParamDialog):
    """Диалог ввода параметров угла трансверсали."""

    def __init__(self, parent):
        super().__init__(parent, "Параметры трансверсали")

        self._parallel_distance_spin = self._create_double_spin(
            "Расстояние между параллельными:", 10, 1000, 150
        )
        self._angle_spin = self._create_double_spin("Угол трансверсали (°):", 1, 179, 45)

        # Подсказка
        self._hint_label = QLabel(
            "Трансверсаль пересекает две параллельные прямые, образуя 8 углов"
        )
        self._hint_label.setStyleSheet("color: #666; font-size: 9pt;")
        self.layout().insertWidget(self.layout().count() - 1, self._hint_label)

    def get_params(self) -> dict:
        return {
            "side_a": 150,
            "side_b": 100,
            "angle_deg": self._angle_spin.value(),
            "parallel_distance": self._parallel_distance_spin.value(),
        }


class RegularPolygonParamDialog(ShapeParamDialog):
    """Диалог ввода параметров правильного многоугольника."""

    def __init__(self, parent, num_sides: int = 6):
        super().__init__(parent, "Параметры правильного многоугольника")

        self._num_sides_spin = self._create_double_spin("Количество сторон:", 3, 12, num_sides)
        self._radius_spin = self._create_double_spin("Радиус:", 10, 1000, 100)

        # Чекбокс вывода градусной меры углов
        self._show_angles_cb = QCheckBox("Выводить градусную меру углов")
        self._show_angles_cb.setChecked(False)
        self.params_layout.addRow("", self._show_angles_cb)

        # Чекбокс диагоналей (для квадрата)
        self._show_diagonals_cb = QCheckBox("Диагонали")
        self._show_diagonals_cb.setChecked(False)
        self.params_layout.addRow("", self._show_diagonals_cb)

        # Чекбокс описанной окружности (для квадрата)
        self._show_circumcircle_cb = QCheckBox("Описанная окружность")
        self._show_circumcircle_cb.setChecked(False)
        self.params_layout.addRow("", self._show_circumcircle_cb)

        # Подсказка
        self._add_hint("Правильный n-угольник: все стороны и углы равны")

    def get_params(self) -> dict:
        return {
            "num_sides": int(self._num_sides_spin.value()),
            "radius": self._radius_spin.value(),
            "show_angles": self._show_angles_cb.isChecked(),
            "show_diagonals": self._show_diagonals_cb.isChecked(),
            "show_circumcircle": self._show_circumcircle_cb.isChecked(),
        }


class PlatonicSolidParamDialog(ShapeParamDialog):
    """Диалог ввода параметров платонова тела."""

    def __init__(self, parent, solid_type: str = "tetrahedron"):
        super().__init__(parent, "Параметры платонова тела")

        self._solid_type = solid_type

        self._size_spin = self._create_double_spin("Размер:", 10, 500, 150)

        # Подсказки для каждого тела
        hints = {
            "tetrahedron": "Тетраэдр: 4 грани (треугольники), 4 вершины, 6 рёбер",
            "cube": "Куб: 6 граней (квадраты), 8 вершин, 12 рёбер",
            "octahedron": "Октаэдр: 8 граней (треугольники), 6 вершин, 12 рёбер",
            "dodecahedron": "Додекаэдр: 12 граней (пятиугольники), 20 вершин, 30 рёбер",
            "icosahedron": "Икосаэдр: 20 граней (треугольники), 12 вершин, 30 рёбер",
        }
        self._hint_label = QLabel(hints.get(solid_type, ""))
        self._hint_label.setStyleSheet("color: #666; font-size: 9pt;")
        self.layout().insertWidget(self.layout().count() - 1, self._hint_label)

    def get_params(self) -> dict:
        return {
            "solid_type": self._solid_type,
            "size": self._size_spin.value(),
        }


class Solid3DParamDialog(ShapeParamDialog):
    """Диалог ввода параметров 3D тела."""

    def __init__(self, parent, solid_type: str = "parallelepiped"):
        super().__init__(parent, "Параметры 3D тела")

        self._solid_type = solid_type

        self._size_spin = self._create_double_spin("Размер:", 10, 500, 150)

        # Подсказки для каждого тела
        hints = {
            "parallelepiped": "Прямоугольный параллелепипед: 6 граней (прямоугольники)",
            "sphere": "Сфера: круг с меридианами и штриховкой",
            "cylinder": "Цилиндр: два эллипса (основания) + боковые линии",
            "cone": "Конус: эллипс основания + вершина",
            "pyramid": "Пирамида: основание + вершина",
            "prism": "Призма: два многоугольника + боковые рёбра",
            "truncated_cone": "Усечённый конус: два эллипса разных размеров",
            "truncated_pyramid": "Усечённая пирамида: два квадрата разных размеров",
        }
        self._hint_label = QLabel(hints.get(solid_type, ""))
        self._hint_label.setStyleSheet("color: #666; font-size: 9pt;")
        self.layout().insertWidget(self.layout().count() - 1, self._hint_label)

    def get_params(self) -> dict:
        return {
            "solid_type": self._solid_type,
            "size": self._size_spin.value(),
        }


class SharyginParamDialog(ShapeParamDialog):
    """Диалог ввода параметров треугольника Шарыгина."""

    def __init__(self, parent):
        super().__init__(parent, "Параметры треугольника Шарыгина")

        self._size_spin = self._create_double_spin("Размер:", 50, 1000, 200)

        # Подсказка
        self._hint_label = QLabel(
            "Треугольник, образованный основаниями биссектрис исходного треугольника"
        )
        self._hint_label.setStyleSheet("color: #666; font-size: 9pt;")
        self.layout().insertWidget(self.layout().count() - 1, self._hint_label)

    def get_params(self) -> dict:
        return {
            "radius": self._radius_spin.value(),
        }


class FractalParamDialog(ShapeParamDialog):
    """Диалог ввода параметров фрактала."""

    # Параметры по умолчанию: (глубина, размер)
    _defaults: dict[str, tuple[int, float]] = {
        "koch": (4, 300.0),
        "sierpinski_triangle": (5, 300.0),
        "sierpinski_carpet": (4, 300.0),
        "pythagorean_tree": (7, 50.0),
    }

    def __init__(self, parent, fractal_type: str = "koch"):
        super().__init__(parent, "Параметры фрактала")
        self._fractal_type = fractal_type

        # Параметры по умолчанию зависят от типа фрактала
        default_depth, default_size = self._defaults.get(fractal_type, (4, 300.0))

        # Глубина рекурсии
        self._depth_spin = self._create_double_spin("Глубина:", 1, 12, default_depth)

        # Размер — для дерева Пифагора это сторона первого квадрата
        size_label = "Сторона квадрата:" if fractal_type == "pythagorean_tree" else "Размер:"
        self._size_spin = self._create_double_spin(size_label, 50, 2000, default_size)

        # Угол для дерева Пифагора
        self._angle_spin: QDoubleSpinBox | None = None
        if fractal_type == "pythagorean_tree":
            self._angle_spin = self._create_double_spin("Угол при основании (°):", 1, 89, 45)
            self._add_hint(
                "Дерево Пифагора — квадрат на основании + прямоугольный треугольник "
                "с углом при основании. 45° — классическое симметричное дерево."
            )

        if fractal_type == "mandelbrot":
            self._add_hint("Множество Мандельброта — zₙ₊₁ = zₙ² + c")
        elif fractal_type == "julia":
            self._add_hint("Множество Жюлиа — zₙ₊₁ = zₙ² + c (c фиксировано)")
        elif fractal_type == "sierpinski_triangle":
            self._add_hint(
                "Треугольник Серпинского — рекурсивное удаление центральных треугольников"
            )
        elif fractal_type == "koch":
            self._add_hint("Снежинка Коха — рекурсивное деление сторон на 4 части")

    def get_params(self) -> dict:
        params: dict = {
            "depth": int(self._depth_spin.value()),
            "size": self._size_spin.value(),
        }
        if self._angle_spin is not None:
            params["angle"] = self._angle_spin.value()
        return params


class MandelbrotParamDialog(ShapeParamDialog):
    """Диалог для множества Мандельброта."""

    def __init__(self, parent):
        super().__init__(parent, "Множество Мандельброта")

        self._size_spin = self._create_double_spin("Размер (px):", 200, 2000, 500)
        self._iter_spin = self._create_double_spin("Итерации:", 50, 1000, 256)

        self._add_hint("zₙ₊₁ = zₙ² + c, где z и c — комплексные числа")

    def get_params(self) -> dict:
        return {
            "size": int(self._size_spin.value()),
            "max_iter": int(self._iter_spin.value()),
        }


class JuliaParamDialog(ShapeParamDialog):
    """Диалог для множества Жюлиа."""

    def __init__(self, parent):
        super().__init__(parent, "Множество Жюлиа")

        self._size_spin = self._create_double_spin("Размер (px):", 200, 2000, 500)
        self._iter_spin = self._create_double_spin("Итерации:", 50, 1000, 256)
        self._c_real_spin = self._create_double_spin("c (вещ.):", -2.0, 2.0, -0.7)
        self._c_imag_spin = self._create_double_spin("c (мним.):", -2.0, 2.0, 0.27015)

        self._add_hint("zₙ₊₁ = zₙ² + c, c фиксировано для всего фрактала")

    def get_params(self) -> dict:
        return {
            "size": int(self._size_spin.value()),
            "max_iter": int(self._iter_spin.value()),
            "c_real": self._c_real_spin.value(),
            "c_imag": self._c_imag_spin.value(),
        }


def create_dialog_for_tool(tool_type) -> ShapeParamDialog | None:
    """Создаёт диалог для ввода параметров фигуры по типу инструмента.

    Args:
        tool_type: тип инструмента (ToolType)

    Returns:
        экземпляр ShapeParamDialog или None
    """
    from tools.tool_types import ToolType

    if tool_type == ToolType.CIRCLE:
        return CircleParamDialog(None)
    elif tool_type == ToolType.ARC:
        return ArcParamDialog(None)
    elif tool_type == ToolType.PARABOLA:
        return ParabolaParamDialog(None)
    elif tool_type == ToolType.HYPERBOLA:
        return HyperbolaParamDialog(None)
    elif tool_type == ToolType.RECTANGLE:
        return RectangleParamDialog(None)
    elif tool_type in (
        ToolType.TRIANGLE_EQUILATERAL,
        ToolType.TRIANGLE_ISOSCELES,
        ToolType.TRIANGLE_RIGHT,
        ToolType.TRIANGLE_OBTUSE,
    ):
        type_map = {
            ToolType.TRIANGLE_EQUILATERAL: "equilateral",
            ToolType.TRIANGLE_ISOSCELES: "isosceles",
            ToolType.TRIANGLE_RIGHT: "right",
            ToolType.TRIANGLE_OBTUSE: "obtuse",
        }
        return TriangleParamDialog(None, type_map[tool_type])
    elif tool_type == ToolType.TRIANGLE_CONGRUENT:
        return CongruentTrianglesParamDialog(None)
    elif tool_type == ToolType.TRIANGLE_SIMILAR:
        return SimilarTrianglesParamDialog(None)
    elif tool_type == ToolType.TRIANGLE_SHARYGIN:
        return SharyginParamDialog(None)
    elif tool_type == ToolType.PARALLELOGRAM:
        return ParallelogramParamDialog(None)
    elif tool_type in (ToolType.TRAPEZOID_ISOSCELES, ToolType.TRAPEZOID):
        return TrapezoidParamDialog(
            None, "isosceles" if tool_type == ToolType.TRAPEZOID_ISOSCELES else "scalene"
        )
    elif tool_type in (
        ToolType.ANGLE,
        ToolType.ANGLE_ADJACENT,
        ToolType.ANGLE_VERTICAL,
        ToolType.ANGLE_TRANSVERSAL,
    ):
        return AngleParamDialog(None)
    elif tool_type in (
        ToolType.REGULAR_TRIANGLE,
        ToolType.REGULAR_PENTAGON,
        ToolType.REGULAR_HEXAGON,
    ):
        return RegularPolygonParamDialog(None)
    elif tool_type == ToolType.SQUARE:
        return None
    elif tool_type in (
        ToolType.TETRAHEDRON,
        ToolType.CUBE,
        ToolType.OCTAHEDRON,
        ToolType.DODECAHEDRON,
        ToolType.ICOSAHEDRON,
    ):
        solid_map = {
            ToolType.TETRAHEDRON: "tetrahedron",
            ToolType.CUBE: "cube",
            ToolType.OCTAHEDRON: "octahedron",
            ToolType.DODECAHEDRON: "dodecahedron",
            ToolType.ICOSAHEDRON: "icosahedron",
        }
        return PlatonicSolidParamDialog(None, solid_map[tool_type])
    elif tool_type == ToolType.RHOMBUS:
        return RhombusParamDialog(None)
    elif tool_type == ToolType.QUADRILATERAL_IRREGULAR:
        return QuadrilateralParamDialog(None)
    elif tool_type == ToolType.CIRCUMSCRIBED_QUADRILATERAL:
        return CircumscribedQuadrilateralParamDialog(None)
    # Фракталы
    elif tool_type == ToolType.FRACTAL_KOCH:
        return FractalParamDialog(None, "koch")
    elif tool_type == ToolType.FRACTAL_SIERPINSKI_TRIANGLE:
        return FractalParamDialog(None, "sierpinski_triangle")
    elif tool_type == ToolType.FRACTAL_SIERPINSKI_CARPET:
        return FractalParamDialog(None, "sierpinski_carpet")
    elif tool_type == ToolType.FRACTAL_PYTHAGOREAN_TREE:
        return FractalParamDialog(None, "pythagorean_tree")
    elif tool_type == ToolType.FRACTAL_CANTOR_SET:
        return FractalParamDialog(None, "cantor_set")
    elif tool_type == ToolType.FRACTAL_MANDELBROT:
        return MandelbrotParamDialog(None)
    elif tool_type == ToolType.FRACTAL_JULIA:
        return JuliaParamDialog(None)
    elif tool_type == ToolType.FRACTAL_NEWTON:
        return FractalParamDialog(None, "newton")
    # 3D тела
    elif tool_type == ToolType.PARALLELEPIPED:
        return Solid3DParamDialog(None, "parallelepiped")
    elif tool_type == ToolType.SPHERE:
        return Solid3DParamDialog(None, "sphere")
    elif tool_type == ToolType.CYLINDER:
        return Solid3DParamDialog(None, "cylinder")
    elif tool_type == ToolType.CONE:
        return Solid3DParamDialog(None, "cone")
    elif tool_type == ToolType.PYRAMID:
        return Solid3DParamDialog(None, "pyramid")
    elif tool_type == ToolType.PRISM:
        return Solid3DParamDialog(None, "prism")
    elif tool_type == ToolType.TRUNCATED_CONE:
        return Solid3DParamDialog(None, "truncated_cone")
    elif tool_type == ToolType.TRUNCATED_PYRAMID:
        return Solid3DParamDialog(None, "truncated_pyramid")

    return None


# ====================================================================
# Диалоги для равных и подобных треугольников
# ====================================================================


class CongruentTrianglesParamDialog(ShapeParamDialog):
    """Диалог ввода параметров двух равных треугольников."""

    def __init__(self, parent):
        super().__init__(parent, "Параметры двух равных треугольников")

        self._side_a_spin, self._side_a_label = self._create_labeled_spin(
            "Сторона (a):", 10, 2000, 100
        )
        self._side_b_spin, self._side_b_label = self._create_labeled_spin(
            "Сторона (b):", 10, 2000, 100
        )
        self._angle_spin, self._angle_label = self._create_labeled_spin("Угол (°):", 1, 179, 30)

        btn_layout = QHBoxLayout()
        random_btn = QPushButton("Случайные")
        random_btn.clicked.connect(self._randomize)
        btn_layout.addWidget(random_btn)
        btn_layout.addStretch()
        self._main_layout.addLayout(btn_layout)

        self._hint_label = QLabel("Две стороны и угол между ними — треугольники равны")
        self._hint_label.setStyleSheet("color: #666; font-size: 9pt;")
        self.layout().addWidget(self._hint_label)

    def _randomize(self) -> None:
        import random

        self._side_a_spin.setValue(random.randint(50, 200))
        self._side_b_spin.setValue(random.randint(50, 200))
        self._angle_spin.setValue(30)

    def get_params(self) -> dict:
        return {
            "side_a": self._side_a_spin.value(),
            "side_b": self._side_b_spin.value(),
            "angle_deg": self._angle_spin.value(),
        }


class SimilarTrianglesParamDialog(ShapeParamDialog):
    """Диалог ввода параметров двух подобных треугольников."""

    def __init__(self, parent):
        super().__init__(parent, "Параметры двух подобных треугольников")

        self._side_a_spin, self._side_a_label = self._create_labeled_spin(
            "Сторона (a):", 10, 2000, 100
        )
        self._side_b_spin, self._side_b_label = self._create_labeled_spin(
            "Сторона (b):", 10, 2000, 100
        )
        self._angle_spin, self._angle_label = self._create_labeled_spin("Угол (°):", 1, 179, 30)
        self._ratio_spin, self._ratio_label = self._create_labeled_spin(
            "Коэффициент подобия (k):", 0.5, 10.0, 2.0
        )

        btn_layout = QHBoxLayout()
        random_btn = QPushButton("Случайные")
        random_btn.clicked.connect(self._randomize)
        btn_layout.addWidget(random_btn)
        btn_layout.addStretch()
        self._main_layout.addLayout(btn_layout)

        self._hint_label = QLabel(
            "Две стороны и угол между ними — второй треугольник подобен с коэф. k"
        )
        self._hint_label.setStyleSheet("color: #666; font-size: 9pt;")
        self.layout().addWidget(self._hint_label)

    def _randomize(self) -> None:
        import random

        self._side_a_spin.setValue(random.randint(50, 200))
        self._side_b_spin.setValue(random.randint(50, 200))
        self._angle_spin.setValue(30)

    def get_params(self) -> dict:
        return {
            "side_a": self._side_a_spin.value(),
            "side_b": self._side_b_spin.value(),
            "angle_deg": self._angle_spin.value(),
            "similarity_ratio": self._ratio_spin.value(),
        }


# ====================================================================
# Диалоги для четырёхугольников
# ====================================================================


class RhombusParamDialog(ShapeParamDialog):
    """Диалог ввода параметров ромба."""

    def __init__(self, parent):
        super().__init__(parent, "Параметры ромба")

        self._side_a_spin = self._create_double_spin("Полу-диагональ (dx):", 10, 2000, 100)
        self._side_b_spin = self._create_double_spin("Полу-диагональ (dy):", 10, 2000, 75)

        hlayout = QHBoxLayout()
        hlayout.setContentsMargins(30, 0, 0, 0)

        self._show_heights_cb = QCheckBox("Высота")
        self._show_heights_cb.setChecked(False)
        hlayout.addWidget(self._show_heights_cb)

        self._show_diagonals_cb = QCheckBox("Диагонали")
        self._show_diagonals_cb.setChecked(False)
        hlayout.addWidget(self._show_diagonals_cb)

        hlayout.addStretch()
        self.params_layout.addRow("", hlayout)

        self._height_vertex_combo = QComboBox()
        self._height_vertex_combo.addItem("Из всех вершин", -1)
        self._height_vertex_combo.addItem("Из вершины A", 0)
        self._height_vertex_combo.addItem("Из вершины B", 1)
        self._height_vertex_combo.addItem("Из вершины C", 2)
        self._height_vertex_combo.addItem("Из вершины D", 3)
        self._height_vertex_combo.setCurrentIndex(0)
        self.params_layout.addRow("Высоты из:", self._height_vertex_combo)

    def get_params(self) -> dict:
        return {
            "side_a": self._side_a_spin.value(),
            "side_b": self._side_b_spin.value(),
            "show_heights": self._show_heights_cb.isChecked(),
            "show_diagonals": self._show_diagonals_cb.isChecked(),
            "height_from_vertex": self._height_vertex_combo.currentData(),
        }


class QuadrilateralParamDialog(ShapeParamDialog):
    """Диалог ввода параметров неправильного четырёхугольника."""

    def __init__(self, parent):
        super().__init__(parent, "Параметры четырёхугольника")

        # 4 стороны
        self._side_a_spin = self._create_double_spin("Сторона a:", 10, 1000, 150)
        self._side_b_spin = self._create_double_spin("Сторона b:", 10, 1000, 120)
        self._side_c_spin = self._create_double_spin("Сторона c:", 10, 1000, 180)
        self._side_d_spin = self._create_double_spin("Сторона d:", 10, 1000, 130)
        self._angle_spin = self._create_double_spin("Угол (°):", 1, 179, 75)

        # Кнопка "Случайный"
        self._random_btn = QPushButton("Случайный")
        self._random_btn.clicked.connect(self._randomize)
        self._random_btn.setStyleSheet(
            "QPushButton { background-color: #e3f2fd; padding: 8px; font-weight: bold; }"
        )

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self._random_btn)
        btn_layout.addStretch()
        self.params_layout.addRow("", btn_layout)

        hlayout = QHBoxLayout()
        hlayout.setContentsMargins(30, 0, 0, 0)

        self._show_diagonals_cb = QCheckBox("Диагонали")
        self._show_diagonals_cb.setChecked(False)
        hlayout.addWidget(self._show_diagonals_cb)

        self._show_heights_cb = QCheckBox("Высота")
        self._show_heights_cb.setChecked(False)
        hlayout.addWidget(self._show_heights_cb)

        self._show_bisectors_cb = QCheckBox("Биссектрисы")
        self._show_bisectors_cb.setChecked(False)
        hlayout.addWidget(self._show_bisectors_cb)

        self._show_angles_cb = QCheckBox("Углы")
        self._show_angles_cb.setChecked(False)
        hlayout.addWidget(self._show_angles_cb)

        self._show_circumcircle_cb = QCheckBox("Описанная окружность")
        self._show_circumcircle_cb.setChecked(False)
        hlayout.addWidget(self._show_circumcircle_cb)

        hlayout.addStretch()
        self.params_layout.addRow("", hlayout)

        self._height_vertex_combo = QComboBox()
        self._height_vertex_combo.addItem("Из всех вершин", -1)
        self._height_vertex_combo.addItem("Из вершины A", 0)
        self._height_vertex_combo.addItem("Из вершины B", 1)
        self._height_vertex_combo.addItem("Из вершины C", 2)
        self._height_vertex_combo.addItem("Из вершины D", 3)
        self._height_vertex_combo.setCurrentIndex(0)
        self.params_layout.addRow("Высоты из:", self._height_vertex_combo)

    def _randomize(self) -> None:
        """Случайные параметры."""
        import random

        self._side_a_spin.setValue(random.randint(80, 300))
        self._side_b_spin.setValue(random.randint(80, 300))
        self._side_c_spin.setValue(random.randint(80, 300))
        self._side_d_spin.setValue(random.randint(80, 300))
        self._angle_spin.setValue(random.randint(20, 160))

    def get_params(self) -> dict:
        return {
            "side_a": self._side_a_spin.value(),
            "side_b": self._side_b_spin.value(),
            "side_c": self._side_c_spin.value(),
            "side_d": self._side_d_spin.value(),
            "angle_deg": self._angle_spin.value(),
            "show_heights": self._show_heights_cb.isChecked(),
            "show_diagonals": self._show_diagonals_cb.isChecked(),
            "show_bisectors": self._show_bisectors_cb.isChecked(),
            "show_angles": self._show_angles_cb.isChecked(),
            "show_circumcircle": self._show_circumcircle_cb.isChecked(),
            "height_from_vertex": self._height_vertex_combo.currentData(),
        }


class CircumscribedQuadrilateralParamDialog(ShapeParamDialog):
    """Диалог ввода параметров описанного четырёхугольника."""

    def __init__(self, parent):
        super().__init__(parent, "Параметры описанного четырёхугольника")

        self._radius_spin = self._create_double_spin("Радиус:", 10, 2000, 150)

        # Подсказка
        self._add_hint(
            "Четырёхугольник, вписанный в окружность.\nВершины A, B, C, D лежат на окружности."
        )

    def get_params(self) -> dict:
        return {
            "radius": self._radius_spin.value(),
        }
