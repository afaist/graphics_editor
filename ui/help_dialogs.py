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

from app_version import __version__


class ShortcutsDialog(QDialog):
    """Диалог «Быстрые клавиши»."""

    SHORTCUTS = [
        # Файл
        ("Создать новый проект", "Ctrl + N"),
        ("Открыть проект", "Ctrl + O"),
        ("Сохранить проект", "Ctrl + S"),
        ("Сохранить как...", "Ctrl + Shift + S"),
        ("Экспорт в PNG", "Ctrl + Shift + P"),
        ("Экспорт в SVG", "Ctrl + Shift + G"),
        ("Выход", "Ctrl + Q"),
        # Правка
        ("Отменить", "Ctrl + Z"),
        ("Повторить", "Ctrl + Y"),
        ("Вырезать", "Ctrl + X"),
        ("Копировать", "Ctrl + C"),
        ("Вставить", "Ctrl + V"),
        ("Дублировать", "Ctrl + D"),
        ("Удалить", "Delete"),
        ("Выделить всё", "Ctrl + A"),
        ("Снять выделение / отменить рисование", "Escape"),
        # Вид (масштаб)
        ("Приблизить", "Ctrl + = / Ctrl + +"),
        ("Отдалить", "Ctrl + -"),
        ("Сбросить масштаб", "Ctrl + 0"),
        # Инструменты — Выделение
        ("Выделение и перемещение", "V"),
        ("Перемещение без рисования", "M"),
        # Инструменты — Линии
        ("Отрезок", "L"),
        ("Луч", "R"),
        ("Прямая", "I"),
        # Инструменты — Фигуры
        ("Прямоугольник", "Q"),
        ("Параллелограмм", "9"),
        # Инструменты — Кривые
        ("Эллипс", "E"),
        ("Окружность", "Cc"),
        ("Дуга", "A"),
        ("Парабола", "Pp"),
        ("Гипербола", "Hh"),
        # Инструменты — Многоугольники
        ("Контур", "G"),
        ("Ломаная", "Y"),
        ("Правильный треугольник", "1"),
        ("Квадрат", "Qa"),
        ("Пятиугольник", ""),
        ("Шестиугольник", "6"),
        # Инструменты — Треугольники
        ("Правильный треугольник", "Ctrl+1"),
        ("Равнобедренный треугольник", "Ctrl+2"),
        ("Прямоугольный треугольник", "Ctrl+3"),
        ("Тупоугольный треугольник", "Ctrl+4"),
        ("Два равных треугольника", "Ctrl+5"),
        ("Два подобных треугольника", "Ctrl+6"),
        ("Треугольник Шарыгина", ""),
        # Инструменты — Трапеции
        ("Равнобедренная трапеция", "0"),
        ("Произвольная трапеция", "Ql"),
        # Инструменты — Углы
        ("Обычный угол", "Ctrl+J"),
        ("Смежные углы", "Ctrl+K"),
        ("Вертикальные углы", "Ctrl+X"),
        ("Угол трансверсали", "Ctrl+W"),
        # Инструменты — Текст и математика
        ("Текст", "T"),
        ("Формула (LaTeX)", "F"),
        # Инструменты — Графики
        ("График линейной", "1"),
        ("График квадратичной", "2"),
        ("График синуса", "3"),
        ("График косинуса", "4"),
        ("График тангенса", "5"),
        ("График логарифма", "6"),
        ("График экспоненты", "7"),
        ("График корня", "8"),
        # Инструменты — Платоновы тела
        ("Тетраэдр", "A"),
        ("Куб", "S"),
        ("Октаэдр", "D"),
        ("Додекаэдр", "F"),
        ("Икосаэдр", "G"),
        # Рисование с привязкой
        ("Привязка углов при рисовании (Shift)", "Shift"),
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
            item_key = QTableWidgetItem(key if key else "—")
            item_key.setTextAlignment(
                Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignHCenter
            )
            grid.setItem(row, 0, item_action)
            grid.setItem(row, 1, item_key)

        group.setLayout(QVBoxLayout())
        group.layout().addWidget(grid)  # type: ignore[union-attr]
        layout.addWidget(group)


class AboutDialog(QDialog):
    """Диалог «О программе»."""

    PROGRAM_NAME = "Графический редактор"
    VERSION = __version__
    DESCRIPTION = (
        "Векторный графический редактор для создания и редактирования "
        "геометрических фигур.\n\n"
        "Возможности:\n"
        "  • 30+ типов фигур (отрезки, многоугольники, кривые, текст и др.)\n"
        "  • Кривые: эллипс, окружность, дуга, парабола, гипербола\n"
        "  • Правильные многоугольники с выводом градусной меры углов\n"
        "  • Математические формулы (LaTeX-рендеринг, 5 стилей шрифта)\n"
        "  • Графики функций (линейная, квадратичная, тригонометрия и др.)\n"
        "  • Поворот фигур через панель свойств\n"
        "  • Выделение и трансформация (8 ручек для эллипса, 4 вершины для полигонов)\n"
        "  • Ресайз с пропорциями (Shift)\n"
        "  • Разные курсоры для разных ручек\n"
        "  • Платоновы тела (тетраэдр, куб, октаэдр, додекаэдр, икосаэдр)\n"
        "  • Треугольники (равносторонний, равнобедренный, прямоугольный,\n"
        "    тупоугольный, Шарыгина) с построением медиан, биссектрис, высот\n"
        "  • Два равных и два подобных треугольника\n"
        "  • Углы (обычный, смежные, вертикальные, трансверсаль)\n"
        "  • Undo / Redo с полной историей действий\n"
        "  • Группировка и разгруппировка фигур\n"
        "  • Z-Order: перемещение на передний/задний план\n"
        "  • Буфер обмена: копирование, вырезание, вставка, дублирование\n"
        "  • Автосохранение проектов\n"
        "  • Экспорт в PNG и SVG\n"
        "  • Настраиваемая двухуровневая сетка с привязкой\n"
        "  • Масштабирование (5%–5000%) и панорамирование\n"
        "  • Панель свойств и истории фигур\n"
        "  • Настройки по умолчанию (шрифт, размеры, цвета)\n"
        "  • Автоматическая проверка обновлений через GitHub API\n"
        "  • 903 unit-теста (pytest)\n"
        "\n"
        "\nАвтор проекта и разработчик — @afaist."
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

        layout.addSpacing(12)

        # GigaCode
        gigacode = QLabel(
            'Разработано с использованием <a href="https://gigacode.ai">GigaCode</a>'
        )
        gigacode.setAlignment(Qt.AlignmentFlag.AlignCenter)
        gigacode.setOpenExternalLinks(True)
        gigacode.setStyleSheet("color: #888; font-size: 9pt;")
        layout.addWidget(gigacode)
