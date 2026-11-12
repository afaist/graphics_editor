"""Модуль построения UI: меню, тулбары, статусбар, доки."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QCheckBox,
    QDockWidget,
    QFrame,
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
        "circle": "Создание окружности протягиванием",
        "arc": "Создание дуги эллипса протягиванием",
        "parabola": "Создание параболы (ввод параметров через диалог)",
        "hyperbola": "Создание гиперболы (ввод параметров через диалог)",
        "polygon": "Создание многоугольника (клик — вершина, Enter — завершить)",
        "polyline": "Создание ломаной (клик — вершина, Enter — завершить)",
        "text": "Создание текстовой надписи (клик — позиция, Enter — завершить)",
        "triangle_equilateral": "Правильный треугольник (ввод стороны через диалог)",
        "triangle_isosceles": "Равнобедренный треугольник (ввод основания и высоты)",
        "triangle_right": "Прямоугольный треугольник (ввод катетов)",
        "triangle_obtuse": "Тупоугольный треугольник (ввод двух сторон и угла)",
        "parallelogram": "Параллелограмм (ввод сторон и угла)",
        "trapezoid_isosceles": "Равнобедренная трапеция (ввод оснований и угла)",
        "trapezoid": "Произвольная трапеция (ввод оснований, высоты, смещения)",
        "angle": "Угол (ввод сторон и угла через диалог)",
        "regular_pentagon": "Правильный пятиугольник (ввод радиуса через диалог)",
        "regular_hexagon": "Правильный шестиугольник (ввод радиуса через диалог)",
        "tetrahedron": "Тетраэдр — 4 грани",
        "cube": "Куб — 6 граней",
        "octahedron": "Октаэдр — 8 граней",
        "dodecahedron": "Додекаэдр — 12 граней",
        "icosahedron": "Икосаэдр — 20 граней",
        "parallelepiped": "Параллелепипед — 3D тело",
        "sphere": "Сфера — 3D тело",
        "cylinder": "Цилиндр — 3D тело",
        "cone": "Конус — 3D тело",
        "pyramid": "Пирамида — 3D тело",
        "prism": "Призма — 3D тело",
        "truncated_cone": "Усечённый конус — 3D тело",
        "truncated_pyramid": "Усечённая пирамида — 3D тело",
        "trigonometric_circle": "Тригонометрическая окружность — справочная диаграмма",
        "unit_circle": "Единичная окружность — интерактивная с подвижным радиусом",
        "trig_circle_full": "Тригонометрическая окружность с осями tg и ctg",
        "rhombus": "Ромб (ввод полу-диагоналей через диалог)",
        "quadrilateral_irregular": "Неправильный четырёхугольник (клик — вершина, 4 клика — завершить)",
        "circumscribed_quadrilateral": "Описанный четырёхугольник (клик — позиция, диалог — радиус)",
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
        mw._property_panel.set_main_window(mw)
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
        scroll.setFrameShape(QFrame.Shape.NoFrame)
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
            ("Карандаш", "C", ToolType.PENCIL),
            ("Точка", "P", ToolType.POINT),
            ("Контур", "G", ToolType.POLYGON),
            ("Текст", "T", ToolType.TEXT),
            ("Формула", "F", ToolType.FORMULA),
        ]

        for name, shortcut, tool_type in tools:
            btn = self.add_tool_button(layout, name, shortcut, tool_type)
            setattr(mw, f"_btn_{tool_type.value.lower()}", btn)

        # Кнопка "Линии" с подменю
        self._create_lines_button(layout, mw)

        # Кнопка "Кривые" с подменю
        self._create_curves_button(layout, mw)

        # Кнопка "Углы" с подменю
        self._create_angles_button(layout, mw)

        # Кнопка "Треугольники" с подменю
        self._create_triangles_button(layout, mw)

        # Кнопка "Четырёхугольники" с подменю
        self._create_quadrilaterals_button(layout, mw)

        # Кнопка "Правильные многоугольники" с подменю
        self._create_regular_polygons_button(layout, mw)

        # Кнопка "Платоновы тела" с подменю
        self._create_platonic_solids_button(layout, mw)

        # Кнопка "3D тела" с подменю
        self._create_solids_3d_button(layout, mw)

        # Кнопка "Графики" с подменю
        self._create_graphs_button(layout, mw)

        # Кнопка "Тригонометрия" с подменю
        self._create_trigonometry_button(layout, mw)

        # Кнопка "Фракталы" с подменю
        self._create_fractals_button(layout, mw)

        layout.addStretch()
        return group

    def create_operations_group(self):
        """Группа операций с фигурами."""
        mw = self._mw
        from tools.tool_types import ToolType

        group = QGroupBox("Операции")
        layout = QVBoxLayout()
        group.setLayout(layout)

        # Инструменты выделения и перемещения
        select_btn = self.add_tool_button(layout, "Выделение", "V", ToolType.SELECT)
        setattr(mw, "_btn_select", select_btn)

        move_btn = self.add_tool_button(layout, "Перемещение", "M", ToolType.MOVE)
        setattr(mw, "_btn_move", move_btn)

        layout.addSpacing(8)

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
        btn.setToolTip("Линии: Отрезок/Луч/Прямая\nРисуются карандашом (цвет, стиль, толщина)")

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

    def _create_curves_button(self, layout, mw):
        """Создание кнопки 'Кривые' с подменю."""
        from tools.tool_types import ToolType

        btn = QPushButton("Кривые")
        btn.setCheckable(True)
        btn.setObjectName("curves")
        btn.setToolTip(
            "Кривые — Cc\nЭллипс — E\nОкружность — Cc\nДуга — A\nПарабола — Pp\nГипербола — Hh"
        )

        def _make_set_tool(tool_type):
            def handler():
                mw._set_tool(tool_type)
                btn.setChecked(True)

            return handler

        menu = QMenu(btn)
        menu.addAction("Эллипс", _make_set_tool(ToolType.ELLIPSE)).setShortcut("E")
        menu.addAction("Окружность", _make_set_tool(ToolType.CIRCLE)).setShortcut("Cc")
        menu.addAction("Дуга", _make_set_tool(ToolType.ARC)).setShortcut("A")
        menu.addAction("Парабола", _make_set_tool(ToolType.PARABOLA)).setShortcut("Pp")
        menu.addAction("Гипербола", _make_set_tool(ToolType.HYPERBOLA)).setShortcut("Hh")

        btn.setMenu(menu)
        layout.addWidget(btn)
        mw._btn_curves = btn

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
            "Треугольники — 1/2/3/4\nПравильный — 1\nРавнобедренный — 2\nПрямоугольный — 3\nТупоугольный — 4\nРавных — 5\nПодобных — 6\nШарыгина — 7"
        )

        # Создаём подменю
        menu = QMenu(btn)
        menu.addAction(
            "Правильный", lambda: mw._set_tool(ToolType.TRIANGLE_EQUILATERAL)
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
            "Два равных треугольника", lambda: mw._set_tool(ToolType.TRIANGLE_CONGRUENT)
        ).setShortcut("")
        menu.addAction(
            "Два подобных треугольника", lambda: mw._set_tool(ToolType.TRIANGLE_SIMILAR)
        ).setShortcut("")
        menu.addAction(
            "Треугольник Шарыгина", lambda: mw._set_tool(ToolType.TRIANGLE_SHARYGIN)
        ).setShortcut("")

        btn.setMenu(menu)
        layout.addWidget(btn)
        mw._btn_triangle = btn

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

        btn = QPushButton("Правильные фиг.")
        btn.setCheckable(True)
        btn.setObjectName("regular_polygons")
        btn.setToolTip(
            "Правильные многоугольники:\nПятиугольник\nШестиугольник\nМожно выбрать любое количество сторон"
        )

        def _make_set_tool(tool_type):
            def handler():
                mw._set_tool(tool_type)
                btn.setChecked(True)

            return handler

        menu = QMenu(btn)
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

    def _create_solids_3d_button(self, layout, mw):
        """Создание кнопки '3D тела' с подменю."""
        from tools.tool_types import ToolType

        btn = QPushButton("3D тела")
        btn.setCheckable(True)
        btn.setObjectName("solids_3d")
        btn.setToolTip("3D тела — параллелепипед, сфера, цилиндр, конус, пирамида, призма")

        def _make_set_tool(tool_type):
            def handler():
                mw._set_tool(tool_type)
                btn.setChecked(True)

            return handler

        menu = QMenu(btn)
        menu.addAction("Куб", _make_set_tool(ToolType.CUBE))
        menu.addAction("Параллелепипед", _make_set_tool(ToolType.PARALLELEPIPED))
        menu.addAction("Сфера", _make_set_tool(ToolType.SPHERE))
        menu.addAction("Цилиндр", _make_set_tool(ToolType.CYLINDER))
        menu.addAction("Конус", _make_set_tool(ToolType.CONE))
        menu.addAction("Пирамида", _make_set_tool(ToolType.PYRAMID))
        menu.addAction("Призма", _make_set_tool(ToolType.PRISM))
        menu.addAction("Усечённый конус", _make_set_tool(ToolType.TRUNCATED_CONE))
        menu.addAction("Усечённая пирамида", _make_set_tool(ToolType.TRUNCATED_PYRAMID))

        btn.setMenu(menu)
        layout.addWidget(btn)
        mw._btn_solids_3d = btn

    def _create_trigonometry_button(self, layout, mw):
        """Создание кнопки 'Тригонометрия' с подменю."""
        from tools.tool_types import ToolType

        btn = QPushButton("Тригонометрия")
        btn.setCheckable(True)
        btn.setObjectName("trigonometry")
        btn.setToolTip(
            "Тригонометрия — Rr\nТригонометрич. окружность — R\nЕдиничная окружность — Rr"
        )

        def _make_set_tool(tool_type):
            def handler():
                mw._set_tool(tool_type)
                btn.setChecked(True)

            return handler

        menu = QMenu(btn)
        menu.addAction(
            "Тригонометрическая окружность",
            _make_set_tool(ToolType.TRIGONOMETRIC_CIRCLE),
        ).setShortcut("R")
        menu.addAction(
            "Тригонометрическая с осями tg/ctg",
            _make_set_tool(ToolType.TRIG_CIRCLE_FULL),
        ).setShortcut("Rt")
        menu.addAction("Единичная окружность", _make_set_tool(ToolType.UNIT_CIRCLE)).setShortcut(
            "Rr"
        )

        btn.setMenu(menu)
        layout.addWidget(btn)
        mw._btn_trigonometry = btn

    def _create_fractals_button(self, layout, mw):
        """Создание кнопки 'Фракталы' с подменю."""
        from tools.tool_types import ToolType

        btn = QPushButton("Фракталы")
        btn.setCheckable(True)
        btn.setObjectName("fractals")
        btn.setToolTip("Фракталы — геометрические, алгебраические, случайные")

        def _make_set_tool(tool_type):
            def handler():
                mw._set_tool(tool_type)
                btn.setChecked(True)

            return handler

        # Создаём подменю
        menu = QMenu(btn)

        # Геометрические фракталы
        geo_menu = menu.addMenu("Геометрические фракталы")
        geo_menu.addAction("Снежинка Коха", _make_set_tool(ToolType.FRACTAL_KOCH))
        geo_menu.addAction(
            "Треугольник Серпинского", _make_set_tool(ToolType.FRACTAL_SIERPINSKI_TRIANGLE)
        )
        geo_menu.addAction("Ковёр Серпинского", _make_set_tool(ToolType.FRACTAL_SIERPINSKI_CARPET))
        geo_menu.addAction("Дерево Пифагора", _make_set_tool(ToolType.FRACTAL_PYTHAGOREAN_TREE))
        geo_menu.addAction("Множество Кантора", _make_set_tool(ToolType.FRACTAL_CANTOR_SET))

        # Алгебраические фракталы
        alg_menu = menu.addMenu("Алгебраические фракталы")
        alg_menu.addAction("Множество Мандельброта", _make_set_tool(ToolType.FRACTAL_MANDELBROT))
        alg_menu.addAction("Множество Жюлиа", _make_set_tool(ToolType.FRACTAL_JULIA))
        alg_menu.addAction("Бассейны Ньютона", _make_set_tool(ToolType.FRACTAL_NEWTON))

        # Случайные фракталы (заглушка)
        rand_menu = menu.addMenu("Случайные фракталы")
        rand_menu.addAction("Броуновское дерево (скоро...)").setEnabled(False)

        btn.setMenu(menu)
        layout.addWidget(btn)
        mw._btn_fractals = btn

    def _create_quadrilaterals_button(self, layout, mw):
        """Создание кнопки 'Четырёхугольники' с подменю."""
        from tools.tool_types import ToolType

        btn = QPushButton("Четырёхугольники")
        btn.setCheckable(True)
        btn.setObjectName("quadrilaterals")
        btn.setToolTip(
            "Четырёхугольники\n"
            "Прямоугольник — Qq\n"
            "Квадрат — Qa\n"
            "Ромб — Rb\n"
            "Параллелограмм — 9\n"
            "Трапеция разносторонняя — U\n"
            "Трапеция равнобедренная — 0\n"
            "Неправильный четырёхугольник — Ql\n"
            "Описанный четырёхугольник — Qo"
        )

        def _make_set_tool(tool_type):
            def handler():
                mw._set_tool(tool_type)
                btn.setChecked(True)

            return handler

        menu = QMenu(btn)
        menu.addAction("Прямоугольник", _make_set_tool(ToolType.RECTANGLE)).setShortcut("Qq")
        menu.addAction("Квадрат", _make_set_tool(ToolType.SQUARE)).setShortcut("Qa")
        menu.addAction("Ромб", _make_set_tool(ToolType.RHOMBUS)).setShortcut("Rb")
        menu.addAction("Параллелограмм", _make_set_tool(ToolType.PARALLELOGRAM)).setShortcut("9")
        menu.addAction("Трапеция разносторонняя", _make_set_tool(ToolType.TRAPEZOID)).setShortcut(
            "U"
        )
        menu.addAction(
            "Трапеция равнобедренная", _make_set_tool(ToolType.TRAPEZOID_ISOSCELES)
        ).setShortcut("0")
        menu.addAction(
            "Неправильный четырёхугольник",
            _make_set_tool(ToolType.QUADRILATERAL_IRREGULAR),
        ).setShortcut("Ql")
        menu.addAction(
            "Описанный четырёхугольник",
            _make_set_tool(ToolType.CIRCUMSCRIBED_QUADRILATERAL),
        ).setShortcut("Qo")

        btn.setMenu(menu)
        layout.addWidget(btn)
        mw._btn_quadrilaterals = btn

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
