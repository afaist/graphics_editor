"""Диалог отображения свойств геометрических фигур."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QGroupBox,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from shapes.shape_properties import get_properties


class _PropertyWidget(QWidget):
    """Виджет одного свойства."""

    def __init__(self, title: str, description: str, formula: str, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.setStyleSheet(
            "_PropertyWidget { "
            "    background-color: #f9f9f9; "
            "    border: 1px solid #e0e0e0; "
            "    border-radius: 6px; "
            "    padding: 8px; "
            "}"
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        # Заголовок
        lbl_title = QLabel(title)
        lbl_title.setFont(QFont("Sans Serif", 10, QFont.Weight.Bold))
        lbl_title.setStyleSheet("color: #333333;")
        layout.addWidget(lbl_title)

        # Описание
        lbl_desc = QLabel(description)
        lbl_desc.setWordWrap(True)
        lbl_desc.setFont(QFont("Sans Serif", 9))
        lbl_desc.setStyleSheet("color: #555555;")
        layout.addWidget(lbl_desc)

        # Формула (если есть)
        if formula:
            lbl_formula = QLabel(formula)
            lbl_formula.setWordWrap(True)
            lbl_formula.setFont(QFont("Courier New", 10, QFont.Weight.Bold))
            lbl_formula.setStyleSheet(
                "color: #0066cc; "
                "background-color: #ffffff; "
                "border: 1px solid #cccccc; "
                "border-radius: 4px; "
                "padding: 4px 8px; "
            )
            layout.addWidget(lbl_formula)

        layout.addStretch()


class _PropertySection(QWidget):
    """Секция свойств с заголовком."""

    def __init__(self, title: str, items: list, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        # Заголовок секции
        lbl_section = QLabel(title)
        lbl_section.setFont(QFont("Sans Serif", 11, QFont.Weight.Bold))
        lbl_section.setStyleSheet("color: #0066cc; padding: 4px 0px;")
        layout.addWidget(lbl_section)

        # Разделитель
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("color: #cccccc;")
        layout.addWidget(separator)

        # Элементы свойств
        for item in items:
            prop_widget = _PropertyWidget(
                title=item.title,
                description=item.description,
                formula=item.formula,
            )
            layout.addWidget(prop_widget)

        layout.addStretch()


class ShapePropertiesDialog(QDialog):
    """Диалог отображения свойств фигуры."""

    def __init__(self, shape_type: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Свойства фигуры")
        self.setMinimumSize(400, 300)
        self.setMaximumSize(600, 800)

        # Непрозрачный фон
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.setStyleSheet("QDialog {     background-color: #ffffff; }")

        # Основной layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Контент
        self._content_widget = QWidget()
        content_layout = QVBoxLayout(self._content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        props = get_properties(shape_type)
        if props:
            # Заголовок
            lbl_title = QLabel(props.name)
            lbl_title.setFont(QFont("Sans Serif", 14, QFont.Weight.Bold))
            lbl_title.setStyleSheet("color: #003366; padding: 12px;")
            content_layout.addWidget(lbl_title)

            # Разделитель
            separator = QFrame()
            separator.setFrameShape(QFrame.Shape.HLine)
            separator.setFrameShadow(QFrame.Shadow.Sunken)
            separator.setStyleSheet("color: #cccccc;")
            content_layout.addWidget(separator)

            # Группа со свойствами
            group = QGroupBox("Свойства")
            group.setFont(QFont("Sans Serif", 10, QFont.Weight.Bold))
            group.setStyleSheet(
                "QGroupBox { "
                "    background-color: #ffffff; "
                "    border: 1px solid #dddddd; "
                "    border-radius: 6px; "
                "    margin-top: 8px; "
                "    padding-top: 12px; "
                "} "
                "QGroupBox::title { "
                "    subcontrol-origin: margin; "
                "    left: 10px; "
                "    padding: 0 4px; "
                "}"
            )

            group_layout = QVBoxLayout(group)
            group_layout.setContentsMargins(12, 12, 12, 12)
            group_layout.setSpacing(8)

            # Создаём секцию для всех свойств
            section = _PropertySection("Основные свойства", props.properties)
            group_layout.addWidget(section)

            content_layout.addWidget(group)
        else:
            lbl_no_props = QLabel(f"Свойства для фигуры «{shape_type}» не найдены")
            lbl_no_props.setFont(QFont("Sans Serif", 10))
            lbl_no_props.setStyleSheet("color: #888888; padding: 20px;")
            lbl_no_props.setAlignment(Qt.AlignmentFlag.AlignCenter)
            content_layout.addWidget(lbl_no_props)

        content_layout.addStretch()

        # Кнопка закрытия
        btn_close = QPushButton("Закрыть", self)
        btn_close.setFont(QFont("Sans Serif", 10, QFont.Weight.Bold))
        btn_close.setMinimumHeight(36)
        btn_close.clicked.connect(self.accept)
        btn_close.setStyleSheet(
            "QPushButton { "
            "    background-color: #0066cc; "
            "    color: #ffffff; "
            "    border: none; "
            "    border-radius: 4px; "
            "    padding: 8px 24px; "
            "} "
            "QPushButton:hover { "
            "    background-color: #0055aa; "
            "} "
            "QPushButton:pressed { "
            "    background-color: #004488; "
            "}"
        )
        content_layout.addWidget(btn_close)

        # Прокрутка для маленьких экранов
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setWidget(self._content_widget)

        main_layout.addWidget(scroll)
