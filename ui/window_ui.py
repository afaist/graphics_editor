"""Модуль построения UI: меню, тулбары, статусбар, доки."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QCheckBox,
    QDockWidget,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from ui.main_window import MainWindow


class UIManager:
    """Управление пользовательским интерфейсом MainWindow."""

    # Подсказки для инструментов
    TOOL_TIPS = {
        "select": "Выделение фигур (Shift — мульти)",
        "move": "Перемещение фигур",
        "point": "Создание точки на холсте",
        "line": "Создание отрезка двумя кликами",
        "ray": "Создание луча (начало + направление)",
        "infinite_line": "Создание бесконечной прямой",
        "rectangle": "Создание прямоугольника (через диалог)",
        "ellipse": "Создание эллипса протягиванием",
        "arc": "Создание дуги эллипса протягиванием",
        "polygon": "Создание многоугольника (клик — вершина, Enter — завершить)",
        "polyline": "Создание ломаной (клик — вершина, Enter — завершить)",
        "text": "Создание текстовой надписи (клик — позиция, Enter — завершить)",
        "triangle_equilateral": "Равносторонний треугольник (ввод стороны через диалог)",
        "triangle_isosceles": "Равнобедренный треугольник (ввод основания и высоты)",
        "triangle_right": "Прямоугольный треугольник (ввод катетов)",
        "triangle_obtuse": "Тупоугольный треугольник (ввод двух сторон и угла)",
        "parallelogram": "Параллелограмм (ввод сторон и угла)",
        "trapezoid_isosceles": "Равнобедренная трапеция (ввод оснований и угла)",
        "trapezoid": "Произвольная трапеция (ввод оснований, высоты, смещения)",
        "angle": "Угол (ввод сторон и угла через диалог)",
    }

    def __init__(self, main_window: MainWindow):
        self._mw = main_window

    # ------------------------------------------------------------------
    # Основная настройка UI
    # ------------------------------------------------------------------

    def setup_ui(self):
        """Настройка пользовательского интерфейса."""
        mw = self._mw
        from PySide6.QtWidgets import QSplitter

        central = QWidget()
        mw.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Левая панель инструментов
        left_panel = self.create_toolbar_panel()
        splitter.addWidget(left_panel)

        # Холст
        if mw._canvas is not None:
            splitter.addWidget(mw._canvas)

        # Правая панель свойств
        self.create_property_panel(splitter)

        # Правый док: Фигуры + История
        self.create_right_dock_panel(splitter)

        splitter.setStretchFactor(1, 1)  # Холст растягивается
        main_layout.addWidget(splitter)

        self.create_menu()
        self.create_statusbar()

    # ------------------------------------------------------------------
    # Панель свойств
    # ------------------------------------------------------------------

    def create_property_panel(self, splitter):
        """Создание панели свойств."""
        mw = self._mw
        from ui.property_panel import PropertyPanel

        mw._property_panel = PropertyPanel()
        right_dock = QDockWidget("Свойства", mw)
        right_dock.setWidget(mw._property_panel)
        right_dock.setFixedWidth(mw.DOCK_WIDTH)
        splitter.addWidget(right_dock)

    # ------------------------------------------------------------------
    # Панель инструментов
    # ------------------------------------------------------------------

    # ===================================================================
    # Правый док: Фигуры + История (вкладки)
    # ===================================================================

    def create_right_dock_panel(self, splitter):
        """Создание правого дока с вкладками: Фигуры | История."""
        mw = self._mw

        # Создаём HistoryPanel
        from ui.history_panel import HistoryPanel

        mw._history_panel = HistoryPanel()

        # Создаём QTabWidget
        tab_widget = QTabWidget()
        tab_widget.addTab(mw._history_panel, "Фигуры")
        # Пустая вкладка-заглушка — QUndoView будет создан в setup_undo_redo()
        empty = QWidget()
        tab_widget.addTab(empty, "История действий")

        # Оборачиваем в QDockWidget
        right_dock = QDockWidget("История действий", mw)
        right_dock.setWidget(tab_widget)
        right_dock.setFixedWidth(mw.DOCK_WIDTH)
        splitter.addWidget(right_dock)

    def create_toolbar_panel(self):
        """Создание панели инструментов."""

        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(4)

        # Группы инструментов
        layout.addWidget(self.create_tools_group())
        layout.addWidget(self.create_operations_group())
        layout.addWidget(self.create_view_group())

        layout.addStretch()
        return panel

    def create_tools_group(self):
        """Группа инструментов рисования."""
        mw = self._mw
        from tools.tool_types import ToolType

        group = QGroupBox("Инструменты")
        layout = QVBoxLayout()
        group.setLayout(layout)

        tools = [
            ("Выделение", "V", ToolType.SELECT),
            ("Перемещение", "M", ToolType.MOVE),
            ("Точка", "P", ToolType.POINT),
            ("Отрезок", "L", ToolType.LINE),
            ("Луч", "R", ToolType.RAY),
            ("Прямая", "I", ToolType.INFINITE_LINE),
            ("Прямоугольник", "Q", ToolType.RECTANGLE),
            ("Эллипс", "E", ToolType.ELLIPSE),
            ("Дуга", "A", ToolType.ARC),
            ("Многоугольник", "G", ToolType.POLYGON),
            ("Ломаная", "Y", ToolType.POLYLINE),
            ("Текст", "T", ToolType.TEXT),
            ("Треугольник", "8", ToolType.TRIANGLE_EQUILATERAL),
            ("Параллелограмм", "9", ToolType.PARALLELOGRAM),
            ("Равнобедр. трапеция", "0", ToolType.TRAPEZOID_ISOSCELES),
            ("Произв. трапеция", "U", ToolType.TRAPEZOID),
            ("Угол", "J", ToolType.ANGLE),
        ]

        for name, shortcut, tool_type in tools:
            btn = self.add_tool_button(layout, name, shortcut, tool_type)
            setattr(mw, f"_btn_{tool_type.value.lower()}", btn)

        layout.addStretch()
        return group

    COLOR_PALETTE = [
        ("Чёрный", (0, 0, 0)),
        ("Белый", (255, 255, 255)),
        ("Красный", (255, 0, 0)),
        ("Зелёный", (0, 128, 0)),
        ("Синий", (0, 0, 255)),
        ("Жёлтый", (255, 255, 0)),
        ("Оранжевый", (255, 165, 0)),
        ("Фиолетовый", (128, 0, 128)),
        ("Коричневый", (139, 69, 19)),
        ("Серый", (128, 128, 128)),
    ]

    def create_operations_group(self):
        """Группа операций с фигурами."""
        mw = self._mw
        group = QGroupBox("Операции")
        layout = QVBoxLayout()
        group.setLayout(layout)

        # Операции
        operations = [
            ("Удалить", mw._delete_selected),
            ("Копировать", mw._copy_selected),
            ("Вставить", mw._paste_clipboard),
        ]

        for name, callback in operations:
            self.add_button(layout, name, callback)

        return group

    def create_view_group(self):
        """Группа настроек вида."""
        mw = self._mw
        group = QGroupBox("Вид")
        layout = QVBoxLayout()
        group.setLayout(layout)

        view_actions = [
            ("Приблизить", mw._canvas.zoom_in if mw._canvas else None),
            ("Отдалить", mw._canvas.zoom_out if mw._canvas else None),
            ("Сбросить масштаб", mw._canvas.reset_zoom if mw._canvas else None),
        ]

        for name, callback in view_actions:
            self.add_button(layout, name, callback)

        return group

    # ------------------------------------------------------------------
    # Вспомогательные методы создания виджетов
    # ------------------------------------------------------------------

    def add_tool_button(self, layout, name: str, shortcut: str, tool_type) -> QPushButton:
        """Создание кнопки инструмента с автоматической настройкой."""
        mw = self._mw
        btn = QPushButton(f"{name} ({shortcut})")
        btn.setCheckable(True)
        btn.setObjectName(str(tool_type.value))
        btn.setToolTip(f"{name} — {shortcut}\n{self.TOOL_TIPS.get(tool_type.value, '')}")
        btn.clicked.connect(lambda checked, t=tool_type: mw._set_tool(t))
        layout.addWidget(btn)
        return btn

    def add_button(self, layout, name: str, callback) -> QPushButton:
        """Создание обычной кнопки."""
        btn = QPushButton(name)
        if callback:
            btn.clicked.connect(callback)
        btn.setToolTip(name)
        layout.addWidget(btn)
        return btn

    def add_checkbox(self, layout, name: str, checked: bool, callback) -> QCheckBox:
        """Создание чекбокса."""
        cb = QCheckBox(name)
        cb.setChecked(checked)
        cb.stateChanged.connect(callback)
        layout.addWidget(cb)
        return cb

    # ------------------------------------------------------------------
    # Меню
    # ------------------------------------------------------------------

    def create_menu(self):
        """Создание главного меню."""
        mw = self._mw
        menubar = mw.menuBar()

        # Файл
        file_menu = menubar.addMenu("Файл")
        file_actions = [
            ("Новый", "", mw._new_project),
            ("Открыть...", "", mw._open_project),
            ("Сохранить", "", mw._save_project),
            ("Сохранить как...", "", mw._save_project_as),
            None,  # Сепаратор
            ("Экспорт в PNG...", "", mw._export_png),
            ("Экспорт в SVG...", "", mw._export_svg),
            None,  # Сепаратор
            ("Выход", "", mw.close),
        ]
        self.add_menu_actions(file_menu, file_actions)

        # Правка
        edit_menu = menubar.addMenu("Правка")
        edit_actions = [
            ("Отменить", "", mw._undo),
            ("Повторить", "", mw._redo),
            None,
            ("Вырезать", "", mw._cut_selected),
            ("Копировать", "", mw._copy_selected),
            ("Вставить", "", mw._paste_clipboard),
            None,
            ("Удалить", "", mw._delete_selected),
            ("Выделить всё", "", mw._manager.select_all),
        ]
        self.add_menu_actions(edit_menu, edit_actions)

        # Вид
        view_menu = menubar.addMenu("Вид")
        if mw._canvas is not None:
            view_actions = [
                ("Приблизить", "", mw._canvas.zoom_in),
                ("Отдалить", "", mw._canvas.zoom_out),
                ("Сбросить масштаб", "", mw._canvas.reset_zoom),
                None,
                ("Обновить", None, mw._refresh_canvas),
                None,
                ("Сетка", None, mw._toggle_grid),
                ("Привязка к сетке", None, mw._toggle_snap),
            ]
            self.add_menu_actions(view_menu, view_actions)

        # Настройки
        settings_menu = menubar.addMenu("Настройки")
        settings_actions = [
            ("Параметры по умолчанию...", None, mw._show_settings),
        ]
        self.add_menu_actions(settings_menu, settings_actions)

        # Помощь
        help_menu = menubar.addMenu("Помощь")
        help_actions = [
            ("Быстрые клавиши", None, mw._show_shortcuts),
            ("Проверить обновления", None, mw._check_for_updates),
            ("О программе", None, mw._show_about),
        ]
        self.add_menu_actions(help_menu, help_actions)

    def add_menu_actions(self, menu, actions: list) -> None:
        """Вспомогательный метод для добавления действий в меню."""
        mw = self._mw
        for action_data in actions:
            if action_data is None:  # Сепаратор
                menu.addSeparator()
                continue

            name, shortcut, callback = action_data
            action = QAction(name, mw)
            if shortcut:
                action.setShortcut(shortcut)
            action.triggered.connect(callback)
            menu.addAction(action)

            # Для чекбоксов в меню
            if name == "Сетка":
                action.setCheckable(True)
                action.setChecked(mw._settings.grid_visible)
                action.toggled.connect(mw._toggle_grid)
            elif name == "Привязка к сетке":
                action.setCheckable(True)
                action.setChecked(mw._settings.snap_to_grid)
                action.toggled.connect(mw._toggle_snap)

    # ------------------------------------------------------------------
    # Статусбар
    # ------------------------------------------------------------------

    def create_statusbar(self):
        """Создание статусбара."""
        mw = self._mw
        mw._status = mw.statusBar()
        mw._status_label = QLabel("Готово")
        mw._coords_label = QLabel("X: 0  Y: 0")
        mw._zoom_label = QLabel("Масштаб: 100%")
        mw._tool_label = QLabel("Инструмент: Выделение")

        # Подсказка по использованию
        mw._hint_label = QLabel(
            "Shift — привязка к углам | Ctrl+колёiko — масштаб | ПКМ — контекстное меню"
        )
        mw._hint_label.setStyleSheet("color: #888; font-size: 9pt;")

        mw._status.addPermanentWidget(mw._hint_label)
        mw._status.addPermanentWidget(mw._tool_label)
        mw._status.addPermanentWidget(mw._coords_label)
        mw._status.addPermanentWidget(mw._zoom_label)
        mw._status.addWidget(mw._status_label)
