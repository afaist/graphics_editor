"""Диалоги ввода параметров для новых геометрических фигур."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
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

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        self.params_layout = QFormLayout()
        self.params_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        layout.addLayout(self.params_layout)

        layout.addStretch()

        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Отмена")
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)

    def get_params(self) -> dict:
        """Возвращает параметры, введённые в диалоге. Переопределяется в подклассах."""
        return {}


class TriangleParamDialog(ShapeParamDialog):
    """Диалог ввода параметров треугольника."""

    def __init__(self, parent, triangle_type: str = "equilateral"):
        super().__init__(parent, "Параметры треугольника")

        self._type_combo = QComboBox()
        self._type_combo.addItems(
            ["Равносторонний", "Равнобедренный", "Прямоугольный", "Тупоугольный"]
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

        self._hint_label = QLabel("")
        self._hint_label.setStyleSheet("color: #666; font-size: 9pt;")
        self._update_hint("equilateral")

        self._type_combo.currentIndexChanged.connect(self._on_type_changed)

        # Добавить подсказку в layout
        self.layout().addWidget(self._hint_label)

        # Сначала показываем поля для equilateral
        self._update_fields("equilateral")
        self._on_type_changed(current_idx)

    def _create_double_spin(
        self, label: str, min_val: float, max_val: float, default: float
    ) -> QDoubleSpinBox:
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
        }


class ParallelogramParamDialog(ShapeParamDialog):
    """Диалог ввода параметров параллелограмма."""

    def __init__(self, parent):
        super().__init__(parent, "Параметры параллелограмма")

        self._side_a_spin = self._create_double_spin("Сторона (a):", 10, 2000, 150)
        self._side_b_spin = self._create_double_spin("Сторона (b):", 10, 2000, 100)
        self._angle_spin = self._create_double_spin("Угол при основании (°):", 1, 179, 60)

    def _create_double_spin(
        self, label: str, min_val: float, max_val: float, default: float
    ) -> QDoubleSpinBox:
        spin = QDoubleSpinBox()
        spin.setRange(min_val, max_val)
        spin.setValue(default)
        spin.setSingleStep(1)
        spin.setDecimals(1)
        self.params_layout.addRow(label, spin)
        return spin

    def get_params(self) -> dict:
        return {
            "side_a": self._side_a_spin.value(),
            "side_b": self._side_b_spin.value(),
            "angle_deg": self._angle_spin.value(),
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

    def get_params(self) -> dict:
        if self._trapezoid_type == "isosceles":
            return {
                "trapezoid_type": self._trapezoid_type,
                "base_a": self._base_a_spin.value(),
                "base_b": self._base_b_spin.value(),
                "angle_deg": self._angle_spin.value(),
            }
        else:
            return {
                "trapezoid_type": self._trapezoid_type,
                "top_width": self._top_width_spin.value(),
                "bottom_width": self._bottom_width_spin.value(),
                "height": self._height_spin.value(),
                "offset_left": self._offset_left_spin.value(),
            }


class RectangleParamDialog(ShapeParamDialog):
    """Диалог ввода параметров прямоугольника."""

    def __init__(self, parent):
        super().__init__(parent, "Параметры прямоугольника")

        self._width_spin = self._create_double_spin("Ширина:", 10, 2000, 200)
        self._height_spin = self._create_double_spin("Высота:", 10, 2000, 150)

    def _create_double_spin(
        self, label: str, min_val: float, max_val: float, default: float
    ) -> QDoubleSpinBox:
        spin = QDoubleSpinBox()
        spin.setRange(min_val, max_val)
        spin.setValue(default)
        spin.setSingleStep(1)
        spin.setDecimals(1)
        self.params_layout.addRow(label, spin)
        return spin

    def get_params(self) -> dict:
        return {
            "width": self._width_spin.value(),
            "height": self._height_spin.value(),
        }


class ArcParamDialog(ShapeParamDialog):
    """Диалог ввода параметров дуги."""

    def __init__(self, parent):
        super().__init__(parent, "Параметры дуги")

        self._radius_spin = self._create_double_spin("Радиус:", 10, 2000, 100)
        self._start_angle_spin = self._create_double_spin("Угол начала (°):", 0, 360, 0)
        self._end_angle_spin = self._create_double_spin("Угол окончания (°):", 0, 360, 180)

        # Подсказка
        self._hint_label = QLabel("0° = 3 часа, углы по часовой стрелке")
        self._hint_label.setStyleSheet("color: #666; font-size: 9pt;")
        self.layout().insertWidget(self.layout().count() - 1, self._hint_label)

    def _create_double_spin(
        self, label: str, min_val: float, max_val: float, default: float
    ) -> QDoubleSpinBox:
        spin = QDoubleSpinBox()
        spin.setRange(min_val, max_val)
        spin.setValue(default)
        spin.setSingleStep(1)
        spin.setDecimals(1)
        self.params_layout.addRow(label, spin)
        return spin

    def get_params(self) -> dict:
        return {
            "radius": self._radius_spin.value(),
            "start_angle": self._start_angle_spin.value(),
            "end_angle": self._end_angle_spin.value(),
        }


class AngleParamDialog(ShapeParamDialog):
    """Диалог ввода параметров угла."""

    def __init__(self, parent):
        super().__init__(parent, "Параметры угла")

        self._side_a_spin = self._create_double_spin("Сторона (a):", 10, 2000, 150)
        self._side_b_spin = self._create_double_spin("Сторона (b):", 10, 2000, 100)
        self._angle_spin = self._create_double_spin("Угол (°):", 0.1, 359.9, 90)

        # Подсказка
        self._hint_label = QLabel("0° = 3 часа, углы отсчитываются против часовой стрелки")
        self._hint_label.setStyleSheet("color: #666; font-size: 9pt;")
        self.layout().insertWidget(self.layout().count() - 1, self._hint_label)

    def _create_double_spin(
        self, label: str, min_val: float, max_val: float, default: float
    ) -> QDoubleSpinBox:
        spin = QDoubleSpinBox()
        spin.setRange(min_val, max_val)
        spin.setValue(default)
        spin.setSingleStep(1)
        spin.setDecimals(1)
        self.params_layout.addRow(label, spin)
        return spin

    def get_params(self) -> dict:
        return {
            "side_a": self._side_a_spin.value(),
            "side_b": self._side_b_spin.value(),
            "angle_deg": self._angle_spin.value(),
        }


def create_dialog_for_tool(tool_type) -> ShapeParamDialog | None:
    """Создать диалог для указанного типа инструмента."""
    from tools.tool_manager import ToolType

    if tool_type == ToolType.RECTANGLE:
        return RectangleParamDialog(None)
    elif tool_type == ToolType.TRIANGLE_EQUILATERAL:
        return TriangleParamDialog(None, "equilateral")
    elif tool_type == ToolType.TRIANGLE_ISOSCELES:
        return TriangleParamDialog(None, "isosceles")
    elif tool_type == ToolType.TRIANGLE_RIGHT:
        return TriangleParamDialog(None, "right")
    elif tool_type == ToolType.TRIANGLE_OBTUSE:
        return TriangleParamDialog(None, "obtuse")
    elif tool_type == ToolType.PARALLELOGRAM:
        return ParallelogramParamDialog(None)
    elif tool_type == ToolType.TRAPEZOID_ISOSCELES:
        return TrapezoidParamDialog(None, "isosceles")
    elif tool_type == ToolType.TRAPEZOID:
        return TrapezoidParamDialog(None, "scalene")
    elif tool_type == ToolType.ARC:
        return ArcParamDialog(None)
    elif tool_type == ToolType.ANGLE:
        return AngleParamDialog(None)

    return None
