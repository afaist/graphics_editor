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
    QMenu,
    QPushButton,
    QScrollArea,
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
        "regular_triangle": "Правильный треугольник (ввод радиуса через диалог)",
        "square": "Квадрат (ввод радиуса через диалог)",
        "regular_pentagon": "Правильный пятиугольник (ввод радиуса через диалог)",
        "regular_hexagon": "Правильный шестиугольник (ввод радиуса через диалог)",
        "tetrahedron": "Тетраэдр — 4 грани",
        "cube": "Куб — 6 граней",
        "octahedron": "Октаэдр — 8 граней",
        "dodecahedron": "Додекаэдр — 12 граней",
        "icosahedron": "Икосаэдр — 20 граней",
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
        right_dock = QDockWidget("Свойства фигуры", mw)
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
        mw._history_panel.setStyleSheet("background-color: #FFFFFF;")

        # Создаём QTabWidget
        tab_widget = QTabWidget()
        tab_widget.addTab(mw._history_panel, "Фигуры")
        # Пустая вкладка-заглушка — QUndoView будет создан в setup_undo_redo()
        empty = QWidget()
        empty.setStyleSheet("background-color: #FFFFFF;")
        tab_widget.addTab(empty, "История действий")

        # Оборачиваем в QDockWidget
        right_dock = QDockWidget("История действий", mw)
        right_dock.setWidget(tab_widget)
        right_dock.setFixedWidth(mw.DOCK_WIDTH)
        splitter.addWidget(right_dock)

        # Сохраняем ссылку на tab_widget для обновления при смене темы
        mw._tab_widget = tab_widget

    def create_toolbar_panel(self):
        """Создание панели инструментов."""

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(4)

        # Группы инструментов
        layout.addWidget(self.create_tools_group())
        layout.addWidget(self.create_operations_group())
        layout.addWidget(self.create_view_group())

        layout.addStretch()
        scroll.setWidget(panel)
        return scroll

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
            ("Текст", "T", ToolType.TEXT),
            ("Точка", "P", ToolType.POINT),
            ("Карандаш", "C", ToolType.PENCIL),
            ("Прямоугольник", "Q", ToolType.RECTANGLE),
            ("Эллипс", "E", ToolType.ELLIPSE),
            ("Дуга", "A", ToolType.ARC),
            ("Параллелограмм", "9", ToolType.PARALLELOGRAM),
            ("Многоугольник", "G", ToolType.POLYGON),
            ("Формула", "F", ToolType.FORMULA),
        ]

        for name, shortcut, tool_type in tools:
            btn = self.add_tool_button(layout, name, shortcut, tool_type)
            setattr(mw, f"_btn_{tool_type.value.lower()}", btn)

        # Кнопка "Линии" с подменю
        self._create_lines_button(layout, mw)

        # Кнопка "Углы" с подменю
        self._create_angles_button(layout, mw)

        # Кнопка "Треугольники" с подменю
        self._create_triangles_button(layout, mw)

        # Кнопка "Трапеция" с подменю
        self._create_trapezoid_button(layout, mw)

        # Кнопка "Графики" с подменю
        self._create_graphs_button(layout, mw)

        # Кнопка "Правильные многоугольники" с подменю
        self._create_regular_polygons_button(layout, mw)

        # Кнопка "Платоновы тела" с подменю
        self._create_platonic_solids_button(layout, mw)

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

    def _create_lines_button(self, layout, mw):
        """Создание кнопки 'Линии' с подменю."""
        from tools.tool_types import ToolType

        btn = QPushButton("Линии")
        btn.setCheckable(True)
        btn.setObjectName("lines")
        btn.setToolTip("Линии: Отрезок/Луч/Прямая")

        def _make_set_tool(tool_type):
            def handler():
                mw._set_tool(tool_type)
                btn.setChecked(True)

            return handler

        menu = QMenu(btn)
        menu.addAction("Отрезок", _make_set_tool(ToolType.LINE)).setShortcut("L")
        menu.addAction("Луч", _make_set_tool(ToolType.RAY)).setShortcut("R")
        menu.addAction("Прямая", _make_set_tool(ToolType.INFINITE_LINE)).setShortcut("I")

        btn.setMenu(menu)
        layout.addWidget(btn)
        mw._btn_lines = btn

    def _create_angles_button(self, layout, mw):
        """Создание кнопки "Углы" с подменю для выбора типа угла."""
        from tools.tool_types import ToolType

        btn = QPushButton("Углы")
        btn.setCheckable(True)
        btn.setObjectName("angle")
        btn.setToolTip("Угол — J\nСмежные углы — K\nВертикальные углы — X\nТрансверсаль — W")

        # Создаём подменю
        menu = QMenu(btn)
        menu.addAction("Обычный угол", lambda: mw._set_tool(ToolType.ANGLE)).setShortcut("J")
        menu.addAction("Смежные углы", lambda: mw._set_tool(ToolType.ANGLE_ADJACENT)).setShortcut(
            "K"
        )
        menu.addAction(
            "Вертикальные углы", lambda: mw._set_tool(ToolType.ANGLE_VERTICAL)
        ).setShortcut("X")
        menu.addAction(
            "Трансверсаль", lambda: mw._set_tool(ToolType.ANGLE_TRANSVERSAL)
        ).setShortcut("W")

        btn.setMenu(menu)
        layout.addWidget(btn)
        mw._btn_angle = btn

    def _create_triangles_button(self, layout, mw):
        """Создание кнопки 'Треугольники' с подменю для выбора типа треугольника."""
        from tools.tool_types import ToolType

        btn = QPushButton("Треугольники")
        btn.setCheckable(True)
        btn.setObjectName("triangle")
        btn.setToolTip(
            "Треугольники — 1/2/3/4\nРавносторонний — 1\nРавнобедренный — 2\nПрямоугольный — 3\nТупоугольный — 4\nШарыгина — 5"
        )

        # Создаём подменю
        menu = QMenu(btn)
        menu.addAction(
            "Равносторонний", lambda: mw._set_tool(ToolType.TRIANGLE_EQUILATERAL)
        ).setShortcut("1")
        menu.addAction(
            "Равнобедренный", lambda: mw._set_tool(ToolType.TRIANGLE_ISOSCELES)
        ).setShortcut("2")
        menu.addAction("Прямоугольный", lambda: mw._set_tool(ToolType.TRIANGLE_RIGHT)).setShortcut(
            "3"
        )
        menu.addAction("Тупоугольный", lambda: mw._set_tool(ToolType.TRIANGLE_OBTUSE)).setShortcut(
            "4"
        )
        menu.addAction(
            "Треугольник Шарыгина", lambda: mw._set_tool(ToolType.TRIANGLE_SHARYGIN)
        ).setShortcut("")

        btn.setMenu(menu)
        layout.addWidget(btn)
        mw._btn_triangle = btn

    def _create_trapezoid_button(self, layout, mw):
        """Создание кнопки 'Трапеция' с подменю для выбора типа трапеции."""
        from tools.tool_types import ToolType

        btn = QPushButton("Трапеции")
        btn.setCheckable(True)
        btn.setObjectName("trapezoid")
        btn.setToolTip("Трапеции — 0/У\nРавнобедр. трапеция — 0\nПроизв. трапеция — У")

        # Создаём подменю
        menu = QMenu(btn)
        menu.addAction(
            "Равнобедр. трапеция", lambda: mw._set_tool(ToolType.TRAPEZOID_ISOSCELES)
        ).setShortcut("0")
        menu.addAction(
            "Произвольная трапеция", lambda: mw._set_tool(ToolType.TRAPEZOID)
        ).setShortcut("U")

        btn.setMenu(menu)
        layout.addWidget(btn)
        mw._btn_trapezoid = btn

    def _create_graphs_button(self, layout, mw):
        """Создание кнопки 'Графики' с подменю для выбора типа функции."""
        from tools.tool_types import ToolType

        btn = QPushButton("Графики")
        btn.setCheckable(True)
        btn.setObjectName("graph")
        btn.setToolTip(
            "Графики — G\nЛинейная — 1\nКвадратичная — 2\nСинус — 3\nКосинус — 4\nТангенс — 5\nЛогарифм — 6\nЭкспонента — 7\nКорень — 8"
        )

        menu = QMenu(btn)
        menu.addAction("Линейная", lambda: mw._set_tool(ToolType.GRAPH_LINEAR)).setShortcut("1")
        menu.addAction("Квадратичная", lambda: mw._set_tool(ToolType.GRAPH_QUADRATIC)).setShortcut(
            "2"
        )
        menu.addAction("Синус", lambda: mw._set_tool(ToolType.GRAPH_SIN)).setShortcut("3")
        menu.addAction("Косинус", lambda: mw._set_tool(ToolType.GRAPH_COS)).setShortcut("4")
        menu.addAction("Тангенс", lambda: mw._set_tool(ToolType.GRAPH_TAN)).setShortcut("5")
        menu.addAction("Логарифм", lambda: mw._set_tool(ToolType.GRAPH_LOG)).setShortcut("6")
        menu.addAction("Экспонента", lambda: mw._set_tool(ToolType.GRAPH_EXP)).setShortcut("7")
        menu.addAction("Корень", lambda: mw._set_tool(ToolType.GRAPH_SQRT)).setShortcut("8")

        btn.setMenu(menu)
        layout.addWidget(btn)
        mw._btn_graph = btn

    def _create_regular_polygons_button(self, layout, mw):
        """Создание кнопки 'Правильные многоугольники' с подменю."""
        from tools.tool_types import ToolType

        btn = QPushButton("Многоугольники")
        btn.setCheckable(True)
        btn.setObjectName("regular_polygons")
        btn.setToolTip("Правильные многоугольники — 5/6\nТреугольник — 5\nШестиугольник — 6")

        def _make_set_tool(tool_type):
            def handler():
                mw._set_tool(tool_type)
                btn.setChecked(True)

            return handler

        menu = QMenu(btn)
        menu.addAction("Треугольник", _make_set_tool(ToolType.REGULAR_TRIANGLE)).setShortcut("5")
        menu.addAction("Квадрат", _make_set_tool(ToolType.SQUARE)).setShortcut("")
        menu.addAction("Пятиугольник", _make_set_tool(ToolType.REGULAR_PENTAGON)).setShortcut("")
        menu.addAction("Шестиугольник", _make_set_tool(ToolType.REGULAR_HEXAGON)).setShortcut("6")

        btn.setMenu(menu)
        layout.addWidget(btn)
        mw._btn_regular_polygons = btn

    def _create_platonic_solids_button(self, layout, mw):
        """Создание кнопки 'Платоновы тела' с подменю."""
        from tools.tool_types import ToolType

        btn = QPushButton("Платоновы тела")
        btn.setCheckable(True)
        btn.setObjectName("platonic_solids")
        btn.setToolTip("Платоновы тела — А/S/D/F/G")

        def _make_set_tool(tool_type):
            def handler():
                mw._set_tool(tool_type)
                btn.setChecked(True)

            return handler

        menu = QMenu(btn)
        menu.addAction("Тетраэдр", _make_set_tool(ToolType.TETRAHEDRON)).setShortcut("A")
        menu.addAction("Куб", _make_set_tool(ToolType.CUBE)).setShortcut("S")
        menu.addAction("Октаэдр", _make_set_tool(ToolType.OCTAHEDRON)).setShortcut("D")
        menu.addAction("Додекаэдр", _make_set_tool(ToolType.DODECAHEDRON)).setShortcut("F")
        menu.addAction("Икосаэдр", _make_set_tool(ToolType.ICOSAHEDRON)).setShortcut("G")

        btn.setMenu(menu)
        layout.addWidget(btn)
        mw._btn_platonic_solids = btn

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
