"""Диалоги ввода параметров для новых геометрических фигур."""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QDoubleValidator
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QSpinBox,
    QDoubleSpinBox,
    QPushButton,
    QGroupBox,
    QFormLayout,
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


class TriangleParamDialog(ShapeParamDialog):
    """Диалог ввода параметров треугольника."""

    def __init__(self, parent, triangle_type: str = "equilateral"):
        super().__init__(parent, "Параметры треугольника")
        
        self._type_combo = QComboBox()
        self._type_combo.addItems(["Равносторонний", "Равнобедренный", "Прямоугольный", "Тупоугольный"])
        
        type_values = ["equilateral", "isosceles", "right", "obtuse"]
        current_idx = type_values.index(triangle_type) if triangle_type in type_values else 0
        self._type_combo.setCurrentIndex(current_idx)
        
        self.params_layout.addRow("Тип:", self._type_combo)
        
        # Поля для каждого типа
        self._side_a_spin = self._create_double_spin("Сторона (a):", 10, 2000, 100)
        
        self._side_b_spin = self._create_double_spin("Сторона (b):", 10, 2000, 100)
        
        self._height_spin = self._create_double_spin("Высота:", 10, 2000, 86.6)
        
        self._angle_spin = self._create_double_spin("Угол (°):", 1, 179, 60)
        
        # Подсказки
        hints = {
            "equilateral": "Достаточна одна сторона — все углы 60°",
            "isosceles": "Основание (a) и высота из вершины",
            "right": "Катеты a и b (угол 90° между ними)",
            "obtuse": "Две стороны и угол между ними (> 90° — тупоугольный)",
        }
        self._hint_label = QLabel("")
        self._hint_label.setStyleSheet("color: #666; font-size: 9pt;")
        self._update_hint("equilateral")
        
        self._type_combo.currentIndexChanged.connect(self._on_type_changed)
        
        # Добавить подсказку в layout
        self.layout().addWidget(self._hint_label)
        
        # Сначала показываем поля для equilateral
        self._update_fields("equilateral")
        self._on_type_changed(current_idx)

    def _create_double_spin(self, label: str, min_val: float, max_val: float, default: float) -> QDoubleSpinBox:
        spin = QDoubleSpinBox()
        spin.setRange(min_val, max_val)
        spin.setValue(default)
        spin.setSingleStep(1)
        spin.setDecimals(1)
        self.params_layout.addRow(label, spin)
        return spin

    def _update_fields(self, type_key: str):
        """Показать/скрыть поля в зависимости от типа."""
        for widget in self.params_layout.children():
            if hasattr(widget, "widget") and widget.widget(0):
                label = widget.widget(0)
                if hasattr(label, "text"):
                    text = label.text()
                    if type_key == "equilateral":
                        widget.widget(0).setText("Сторона:")
                        widget.widget(1).setPlaceholderText("Все стороны равны")
                    elif type_key == "isosceles":
                        widget.widget(0).setText("Основание:")
                        widget.widget(1).setPlaceholderText("Длина основания")
                    elif type_key == "right":
                        if "Сторона (b)" in text or "Катет (b)" in text:
                            widget.widget(0).setText("Катет (b):")
                        elif "Сторона (a)" in text or "Катет (a)" in text:
                            widget.widget(0).setText("Катет (a):")
                    elif type_key == "obtuse":
                        if "Сторона (b)" in text:
                            widget.widget(0).setText("Сторона (b):")
                        elif "Сторона (a)" in text:
                            widget.widget(0).setText("Сторона (a):")

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
        
        # Показываем все поля всегда, но подсказки меняем
        self._update_hint(type_key)

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

    def _create_double_spin(self, label: str, min_val: float, max_val: float, default: float) -> QDoubleSpinBox:
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
        
        self._type_combo = QComboBox()
        self._type_combo.addItems(["Равнобедренная", "Произвольная"])
        
        type_values = ["isosceles", "scalene"]
        current_idx = 0 if trapezoid_type == "isosceles" else 1
        self._type_combo.setCurrentIndex(current_idx)
        
        self.params_layout.addRow("Тип:", self._type_combo)
        
        # Создаём поля с сохранением ссылок на лейблы
        self._base_a_spin, self._base_a_label = self._create_labeled_spin("Основание (a):", 10, 2000, 200)
        self._base_b_spin, self._base_b_label = self._create_labeled_spin("Основание (b):", 10, 2000, 100)
        self._height_spin, self._height_label = self._create_labeled_spin("Высота:", 10, 2000, 100)
        self._offset_spin, self._offset_label = self._create_labeled_spin("Смещение:", -500, 500, 0)
        self._angle_spin, self._angle_label = self._create_labeled_spin("Угол при основании (°):", 1, 179, 60)
        
        self._type_combo.currentIndexChanged.connect(self._on_type_changed)
        self._on_type_changed(current_idx)

    def _create_labeled_spin(self, label_text: str, min_val: float, max_val: float, default: float):
        """Создать QDoubleSpinBox с QLabel и вернуть (spin, label)."""
        label = QLabel(label_text)
        spin = QDoubleSpinBox()
        spin.setRange(min_val, max_val)
        spin.setValue(default)
        spin.setSingleStep(1)
        spin.setDecimals(1)
        self.params_layout.addRow(label, spin)
        return spin, label

    def _on_type_changed(self, index: int):
        type_values = ["isosceles", "scalene"]
        type_key = type_values[index]
        
        # Для равнобедренной — показываем основания и угол
        # Для произвольной — показываем основания, высоту и смещение
        if type_key == "isosceles":
            self._base_a_label.setVisible(True)
            self._base_a_spin.setVisible(True)
            self._base_b_label.setVisible(True)
            self._base_b_spin.setVisible(True)
            self._angle_label.setVisible(True)
            self._angle_spin.setVisible(True)
            self._height_label.setVisible(False)
            self._height_spin.setVisible(False)
            self._offset_label.setVisible(False)
            self._offset_spin.setVisible(False)
        else:
            self._base_a_label.setVisible(True)
            self._base_a_spin.setVisible(True)
            self._base_b_label.setVisible(True)
            self._base_b_spin.setVisible(True)
            self._height_label.setVisible(True)
            self._height_spin.setVisible(True)
            self._offset_label.setVisible(True)
            self._offset_spin.setVisible(True)
            self._angle_label.setVisible(False)
            self._angle_spin.setVisible(False)

    def get_params(self) -> dict:
        type_values = ["isosceles", "scalene"]
        trapezoid_type = type_values[self._type_combo.currentIndex()]
        
        params = {
            "trapezoid_type": trapezoid_type,
            "base_a": self._base_a_spin.value(),
            "base_b": self._base_b_spin.value(),
        }
        
        if trapezoid_type == "isosceles":
            params["angle_deg"] = self._angle_spin.value()
        else:
            params["height"] = self._height_spin.value()
            params["offset"] = self._offset_spin.value()
        
        return params


def create_dialog_for_tool(tool_type) -> Optional[ShapeParamDialog]:
    """Создать диалог для указанного типа инструмента."""
    from tools.tool_manager import ToolType
    
    if tool_type == ToolType.TRIANGLE_EQUILATERAL:
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
    
    return None
