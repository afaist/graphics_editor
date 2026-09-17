"""Диалоги справки: «Быстрые клавиши» и «О программе»."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog,
    QGroupBox,
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class ShortcutsDialog(QDialog):
    """Диалог «Быстрые клавиши»."""

    SHORTCUTS = [
        # Файл
        ("Создать новый проект", "Ctrl + N"),
        ("Открыть проект", "Ctrl + O"),
        ("Сохранить проект", "Ctrl + S"),
        ("Сохранить как...", "Ctrl + Shift + S"),
        ("Экспорт в PNG...", "Ctrl + Shift + P"),
        ("Экспорт в SVG...", "Ctrl + Shift + G"),
        ("Выход", "Ctrl + Q"),
        # Правка
        ("Отменить", "Ctrl + Z"),
        ("Повторить", "Ctrl + Y / Ctrl + Shift + Z"),
        ("Вырезать", "Ctrl + X"),
        ("Копировать", "Ctrl + C"),
        ("Вставить", "Ctrl + V"),
        ("Удалить", "Delete"),
        ("Выделить всё", "Ctrl + A"),
        ("Снять выделение / отменить рисование", "Escape"),
        # Вид
        ("Приблизить", "Ctrl + = / Ctrl + +"),
        ("Отдалить", "Ctrl + -"),
        ("Сбросить масштаб", "Ctrl + 0"),
        # Инструменты
        ("Выделение", "V"),
        ("Точка", "P"),
        ("Отрезок", "L"),
        ("Луч", "R"),
        ("Прямая", "I"),
        ("Прямоугольник", "Q"),
        ("Эллипс", "E"),
        ("Дуга", "A"),
        ("Многоугольник", "G"),
        ("Ломаная", "Y"),
        ("Текст", "T"),
        ("Треугольник", "8"),
        ("Параллелограмм", "9"),
        ("Равнобедр. трапеция", "0"),
        ("Произв. трапеция", "U"),
        ("Угол", "J"),
    ]

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Быстрые клавиши")
        self.setModal(True)
        self.resize(520, 500)
        self._build_ui()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        group = QGroupBox("Горячие клавиши")
        grid = QTableWidget(self)
        grid.setColumnCount(2)
        grid.setHorizontalHeaderLabels(("Действие", "Клавиша"))
        header = grid.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        grid.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        grid.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        grid.verticalHeader().setVisible(False)
        grid.setRowCount(len(self.SHORTCUTS))

        for row, (action, key) in enumerate(self.SHORTCUTS):
            item_action = QTableWidgetItem(action)
            item_action.setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
            item_key = QTableWidgetItem(key)
            item_key.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignHCenter)
            grid.setItem(row, 0, item_action)
            grid.setItem(row, 1, item_key)

        group.setLayout(QVBoxLayout())
        group.layout().addWidget(grid)  # type: ignore[union-attr]
        layout.addWidget(group)


class AboutDialog(QDialog):
    """Диалог «О программе»."""

    PROGRAM_NAME = "Графический редактор"
    VERSION = "1.0"
    DESCRIPTION = (
        "Векторный графический редактор для создания и редактирования "
        "геометрических фигур.\n\n"
        "Возможности:\n"
        "  • 15+ типов фигур (отрезки, многоугольники, дуги, текст и др.)\n"
        "  • Undo / Redo с полной историей действий\n"
        "  • Автосохранение проектов\n"
        "  • Экспорт в PNG и SVG\n"
        "  • Сетка и привязка к ней\n"
        "  • Панель свойств и истории фигур\n"
    )

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("О программе")
        self.setModal(True)
        self._build_ui()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        # Заголовок
        title = QLabel(self.PROGRAM_NAME)
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Версия
        version = QLabel(f"Версия {self.VERSION}")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version.setStyleSheet("color: #888;")
        layout.addWidget(version)

        layout.addSpacing(12)

        # Описание
        desc = QLabel(self.DESCRIPTION)
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc)

        layout.addSpacing(12)

        # Технология
        tech = QLabel("Стек: Python 3, PySide6 (Qt 6)")
        tech.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tech.setStyleSheet("color: #888; font-size: 9pt;")
        layout.addWidget(tech)
