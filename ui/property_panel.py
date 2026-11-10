"""Panel свойств выделенной фигуры."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from shapes.base_shape import SHAPE_NAMES_RU
from shapes.text_shape import TextShape
from tools.drawing_styles import LINE_STYLES
from ui.common_widgets import _ColorButton


class PropertyPanel(QWidget):
    """Панель свойств выделенной фигуры."""

    properties_changed = Signal(dict)

    def __init__(self, parent=None):
        """Инициализация панели свойств с пустым состоянием."""
        super().__init__(parent)
        self._selected_props: dict | None = None
        self._selected_shape_type: str | None = None
        self._mw = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(8)

        # Название фигуры
        self._shape_label = QLabel("Не выбрано")
        self._shape_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(self._shape_label)

        # Цвет контура
        lbl1 = QLabel("Цвет контура:")
        lbl1.setStyleSheet("font-weight: bold;")
        layout.addWidget(lbl1)

        h1 = QHBoxLayout()
        self.btn_pen_color = _ColorButton((0, 0, 0))
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
        self.btn_brush_color = _ColorButton((255, 255, 255))
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

        # Параметры шрифта текста (скрыты по умолчанию)
        lbl_font = QLabel("Параметры шрифта:")
        lbl_font.setStyleSheet("font-weight: bold;")
        self._lbl_font_params = lbl_font
        self._lbl_font_params.setVisible(False)
        layout.addWidget(self._lbl_font_params)

        # Семейство шрифта
        h_font_family = QHBoxLayout()
        lbl_font_family = QLabel("Шрифт:")
        lbl_font_family.setFixedWidth(60)
        self.combo_font_family = QComboBox()
        self.combo_font_family.setEditable(False)
        self.combo_font_family.setMinimumWidth(150)
        self.combo_font_family.setVisible(False)
        self.combo_font_family.currentIndexChanged.connect(self._on_font_family_changed)
        h_font_family.addWidget(lbl_font_family)
        h_font_family.addWidget(self.combo_font_family)
        h_font_family.addStretch()
        self._h_font_family = h_font_family
        layout.addLayout(self._h_font_family)

        # Размер шрифта
        h_font_size = QHBoxLayout()
        lbl_font_size = QLabel("Размер:")
        lbl_font_size.setFixedWidth(60)
        lbl_font_size.setVisible(False)
        self.spin_font_size = QSpinBox()
        self.spin_font_size.setRange(4, 200)
        self.spin_font_size.setValue(14)
        self.spin_font_size.setSingleStep(1)
        self.spin_font_size.setVisible(False)
        self.spin_font_size.valueChanged.connect(self._on_font_size_changed)
        h_font_size.addWidget(lbl_font_size)
        h_font_size.addWidget(self.spin_font_size)
        h_font_size.addStretch()
        self._h_font_size = h_font_size
        self._lbl_font_size = lbl_font_size
        layout.addLayout(self._h_font_size)

        # Жирный + Курсив
        h_font_style = QHBoxLayout()
        self.chk_font_bold = QCheckBox("Жирный")
        self.chk_font_bold.setVisible(False)
        self.chk_font_bold.toggled.connect(self._on_font_bold_toggled)
        h_font_style.addWidget(self.chk_font_bold)

        self.chk_font_italic = QCheckBox("Курсив")
        self.chk_font_italic.setVisible(False)
        self.chk_font_italic.toggled.connect(self._on_font_italic_toggled)
        h_font_style.addWidget(self.chk_font_italic)

        # Подчёркнутый + Зачёркнутый
        self.chk_font_underline = QCheckBox("Подчёрк.")
        self.chk_font_underline.setVisible(False)
        font_under = QFont("Segoe UI", 10)
        font_under.setUnderline(True)
        self.chk_font_underline.setFont(font_under)
        self.chk_font_underline.toggled.connect(self._on_font_underline_toggled)
        h_font_style.addWidget(self.chk_font_underline)

        self.chk_font_strikethrough = QCheckBox("Зачёркн.")
        self.chk_font_strikethrough.setVisible(False)
        font_strike = QFont("Segoe UI", 10)
        font_strike.setStrikeOut(True)
        self.chk_font_strikethrough.setFont(font_strike)
        self.chk_font_strikethrough.toggled.connect(self._on_font_strikethrough_toggled)
        h_font_style.addWidget(self.chk_font_strikethrough)
        h_font_style.addStretch()
        self._h_font_style = h_font_style
        layout.addLayout(self._h_font_style)

        # Скрыть поля параметров шрифта по умолчанию
        for i in range(self._h_font_family.count()):
            item = self._h_font_family.itemAt(i)
            if item is not None:
                w = item.widget()
                if w:
                    w.setVisible(False)
        self.spin_font_size.setVisible(False)
        self.chk_font_bold.setVisible(False)
        self.chk_font_italic.setVisible(False)
        self.chk_font_underline.setVisible(False)
        self.chk_font_strikethrough.setVisible(False)

        layout.addSpacing(12)

        # Параметры карандаша (скрыты по умолчанию)
        lbl_pencil = QLabel("Параметры карандаша:")
        lbl_pencil.setStyleSheet("font-weight: bold;")
        self._lbl_pencil = lbl_pencil
        self._lbl_pencil.setVisible(False)
        layout.addWidget(self._lbl_pencil)

        # Цвет карандаша + кнопка сброса
        h_pencil_color = QHBoxLayout()
        lbl_pencil_color = QLabel("Цвет:")
        lbl_pencil_color.setFixedWidth(40)
        self.btn_pencil_color = _ColorButton((0, 0, 0))
        self.btn_pencil_color.color_changed.connect(self._on_pencil_color_changed)
        self.btn_pencil_color.setVisible(False)
        h_pencil_color.addWidget(lbl_pencil_color)
        h_pencil_color.addWidget(self.btn_pencil_color)
        h_pencil_color.addStretch()

        self.btn_reset_pencil = QPushButton("Сбросить")
        self.btn_reset_pencil.setVisible(False)
        self.btn_reset_pencil.setFixedWidth(80)
        self.btn_reset_pencil.setStyleSheet(
            "QPushButton { "
            "background-color: #e0e0e0; "
            "border: 1px solid #999; "
            "border-radius: 4px; "
            "padding: 4px 8px; "
            "font-weight: bold; "
            "}"
            "QPushButton:disabled { "
            "color: #ccc; "
            "}"
        )
        self.btn_reset_pencil.clicked.connect(self._on_reset_pencil)
        h_pencil_color.addWidget(self.btn_reset_pencil)
        self._h_pencil_color = h_pencil_color
        layout.addLayout(self._h_pencil_color)

        # Толщина карандаша
        h_pencil_width = QHBoxLayout()
        lbl_pencil_width = QLabel("Толщина:")
        lbl_pencil_width.setFixedWidth(40)
        self.spin_pencil_width = QDoubleSpinBox()
        self.spin_pencil_width.setRange(0.5, 50.0)
        self.spin_pencil_width.setValue(2.0)
        self.spin_pencil_width.setSingleStep(0.5)
        self.spin_pencil_width.valueChanged.connect(self._on_pencil_width_changed)
        self.spin_pencil_width.setVisible(False)
        h_pencil_width.addWidget(lbl_pencil_width)
        h_pencil_width.addWidget(self.spin_pencil_width)
        h_pencil_width.addStretch()
        self._h_pencil_width = h_pencil_width
        layout.addLayout(self._h_pencil_width)

        # Тип линии
        h_pencil_style = QHBoxLayout()
        lbl_pencil_style = QLabel("Тип:")
        lbl_pencil_style.setFixedWidth(40)
        self.combo_pencil_style = QComboBox()
        self.combo_pencil_style.setVisible(False)
        for name, style in LINE_STYLES:
            self.combo_pencil_style.addItem(name, style)
        self.combo_pencil_style.currentIndexChanged.connect(self._on_pencil_style_changed)
        h_pencil_style.addWidget(lbl_pencil_style)
        h_pencil_style.addWidget(self.combo_pencil_style)
        h_pencil_style.addStretch()
        self._h_pencil_style = h_pencil_style
        layout.addLayout(self._h_pencil_style)

        # Скрыть поля параметров карандаша по умолчанию
        for i in range(self._h_pencil_color.count()):
            item = self._h_pencil_color.itemAt(i)
            if item is not None:
                w = item.widget()
                if w:
                    w.setVisible(False)
        for i in range(self._h_pencil_width.count()):
            item = self._h_pencil_width.itemAt(i)
            if item is not None:
                w = item.widget()
                if w:
                    w.setVisible(False)
        for i in range(self._h_pencil_style.count()):
            item = self._h_pencil_style.itemAt(i)
            if item is not None:
                w = item.widget()
                if w:
                    w.setVisible(False)

        layout.addSpacing(12)

        # Координаты и размеры (для прямоугольных фигур)
        lbl5 = QLabel("Позиция и размер:")
        lbl5.setStyleSheet("font-weight: bold;")
        self._lbl_coord_params = lbl5
        self._lbl_coord_params.setVisible(False)
        layout.addWidget(self._lbl_coord_params)

        # X
        h_x = QHBoxLayout()
        lbl_x = QLabel("X:")
        lbl_x.setFixedWidth(20)
        self.lbl_coord_x = lbl_x
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
        self.lbl_coord_y = lbl_y
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
        self.lbl_coord_w = lbl_w
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
        self.lbl_coord_h = lbl_h
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

        # Параметры формулы (скрыты по умолчанию)
        lbl_formula = QLabel("Параметры формулы:")
        lbl_formula.setStyleSheet("font-weight: bold;")
        self._lbl_formula_params = lbl_formula
        self._lbl_formula_params.setVisible(False)
        layout.addWidget(self._lbl_formula_params)

        # Стиль формулы (fontset)
        h_formula_style = QHBoxLayout()
        lbl_formula_style = QLabel("Стиль:")
        lbl_formula_style.setFixedWidth(60)
        self.combo_formula_style = QComboBox()
        self.combo_formula_style.setEditable(False)
        self.combo_formula_style.setMinimumWidth(150)
        self.combo_formula_style.setVisible(False)
        self.combo_formula_style.addItems(
            [
                "DejaVu Sans",
                "DejaVu Serif",
                "Computer Modern",
                "STIX",
                "STIX Sans",
            ]
        )
        self.combo_formula_style.setCurrentIndex(2)  # Computer Modern по умолчанию
        self.combo_formula_style.currentIndexChanged.connect(self._on_formula_style_changed)
        h_formula_style.addWidget(lbl_formula_style)
        h_formula_style.addWidget(self.combo_formula_style)
        h_formula_style.addStretch()
        self._h_formula_style = h_formula_style
        layout.addLayout(self._h_formula_style)

        # Размер формулы
        h_formula_size = QHBoxLayout()
        lbl_formula_size = QLabel("Размер:")
        lbl_formula_size.setFixedWidth(60)
        lbl_formula_size.setVisible(False)
        self._lbl_formula_size = lbl_formula_size
        self.spin_formula_size = QSpinBox()
        self.spin_formula_size.setRange(6, 200)
        self.spin_formula_size.setValue(16)
        self.spin_formula_size.setSingleStep(1)
        self.spin_formula_size.setSuffix(" px")
        self.spin_formula_size.setVisible(False)
        self.spin_formula_size.valueChanged.connect(self._on_formula_size_changed)
        h_formula_size.addWidget(lbl_formula_size)
        h_formula_size.addWidget(self.spin_formula_size)
        h_formula_size.addStretch()
        self._h_formula_size = h_formula_size
        layout.addLayout(self._h_formula_size)

        # Скрыть поля параметров формулы по умолчанию
        for i in range(self._h_formula_style.count()):
            item = self._h_formula_style.itemAt(i)
            if item is not None:
                w = item.widget()
                if w:
                    w.setVisible(False)
        self.spin_formula_size.setVisible(False)

        layout.addSpacing(12)

        # Параметры дуги (скрыты по умолчанию)
        lbl_arc = QLabel("Параметры дуги:")
        lbl_arc.setStyleSheet("font-weight: bold;")
        self._lbl_arc_params = lbl_arc
        self._lbl_arc_params.setVisible(False)
        layout.addWidget(self._lbl_arc_params)

        # Радиус
        h_r = QHBoxLayout()
        lbl_r = QLabel("R:")
        lbl_r.setFixedWidth(20)
        self.lbl_arc_radius = lbl_r
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
        self.lbl_arc_start = lbl_sa
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
        self.lbl_arc_end = lbl_ea
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
            item = self.h_side_a.itemAt(i)
            if item is not None:
                w = item.widget()
                if w:
                    w.setVisible(False)
        for i in range(self.h_side_b.count()):
            item = self.h_side_b.itemAt(i)
            if item is not None:
                w = item.widget()
                if w:
                    w.setVisible(False)
        for i in range(self.h_angle_deg.count()):
            item = self.h_angle_deg.itemAt(i)
            if item is not None:
                w = item.widget()
                if w:
                    w.setVisible(False)

        layout.addStretch()

    # ------------------------------------------------------------------
    # Обновление панели
    # ------------------------------------------------------------------

    def set_main_window(self, mw) -> None:
        """Устанавливает ссылку на MainWindow."""
        self._mw = mw

    def on_tool_changed(self, tool_type: str) -> None:
        """Обработчик смены инструмента — показать/скрыть панель карандаша и дуги."""
        if tool_type in (
            "pencil",
            "line",
            "ray",
            "infinite_line",
        ):
            self.set_pencil_controls_visible(True)
            self.sync_pencil_controls()
        else:
            self.set_pencil_controls_visible(False)
        if tool_type == "arc":
            self._enable_arc_fields(True)
        else:
            self._enable_arc_fields(False)

    def set_properties(self, props: dict | None) -> None:
        self._selected_props = props
        if props is None:
            self._shape_label.setText("Не выбрано")
            self.btn_pen_color.set_color((0, 0, 0))
            self.btn_pen_color.setEnabled(False)
            self.spin_pen_width.setEnabled(False)
            self.btn_brush_color.setEnabled(False)
            self.chk_no_brush.setEnabled(False)
            self.spin_rotation.setEnabled(False)
            self._enable_coordinate_fields(False)
            self._enable_arc_fields(False)
            self._enable_font_fields(False)
            return

        # Блокируем ВСЕ сигналы property panel на время заполнения
        self.blockSignals(True)

        try:
            # Устанавливаем название фигуры
            shape_type = props.get("_shape_type", "")
            self._selected_shape_type = shape_type
            shape_name = SHAPE_NAMES_RU.get(shape_type, shape_type.replace("_", " ").title())
            self._shape_label.setText(f"{shape_name}")

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
            self.spin_pen_width.setValue(pw)

            bc = props.get("brush_color")
            if bc:
                self.btn_brush_color.set_color(bc)
                self.chk_no_brush.setChecked(False)
            else:
                self.chk_no_brush.setChecked(True)

            rot = props.get("rotation", 0)
            self.spin_rotation.setValue(rot)

            geometry_shapes = (
                "rectangle",
                "ellipse",
                "triangle_equilateral",
                "triangle_isosceles",
                "triangle_right",
                "triangle_obtuse",
                "parallelogram",
                "trapezoid_isosceles",
                "trapezoid",
                "angle",
            )
            # Фигуры, для которых актуальны "Позиция и размер"
            coord_shapes = (
                "rectangle",
                "ellipse",
                "circle",
                "arc",
                "graph",
                "parabola",
                "hyperbola",
                "regular_triangle",
                "square",
                "regular_pentagon",
                "regular_hexagon",
                "trigonometric_circle",
                "trig_circle_full",
                "unit_circle",
                "circumscribed_quadrilateral",
            )
            if shape_type == "rectangle":
                # Для прямоугольника показываем координаты/размеры
                self._enable_coordinate_fields(True)
                self._enable_arc_fields(False)
                self._enable_angle_fields(False)
            elif shape_type == "arc":
                # Для дуги показываем координаты/размеры и параметры дуги
                self._enable_coordinate_fields(True)
                self._enable_arc_fields(True)
                self.spin_x.setValue(props.get("_x", 0))
                self.spin_y.setValue(props.get("_y", 0))
                self.spin_width.setValue(props.get("_width", 100))
                self.spin_height.setValue(props.get("_height", 100))
                self.spin_radius.setValue(props.get("_radius", 100))
                self.spin_start_angle.setValue(props.get("_start_angle", 0))
                self.spin_end_angle.setValue(props.get("_end_angle", 90))
            elif shape_type in coord_shapes:
                # Для фигур с координатами/размерами
                self._enable_coordinate_fields(True)
                self._enable_arc_fields(False)
                self.spin_x.setValue(props.get("_x", 0))
                self.spin_y.setValue(props.get("_y", 0))
                if shape_type == "circle" or shape_type == "circumscribed_quadrilateral":
                    # Для окружности и описанного четырёхугольника храним radius напрямую
                    radius = props.get("_radius", 50)
                    diameter = 2 * radius
                    self.spin_width.setValue(diameter)
                    self.spin_height.setValue(diameter)
                else:
                    self.spin_width.setValue(props.get("_width", 100))
                    self.spin_height.setValue(props.get("_height", 100))
            elif shape_type in geometry_shapes:
                # Для остальных геометрических фигур (треугольники, четырёхугольники, угол)
                self._enable_coordinate_fields(False)
                self._enable_arc_fields(False)
                if shape_type == "angle":
                    self._enable_angle_fields(True)
                    self.spin_side_a.setValue(props.get("_side_a", 150))
                    self.spin_side_b.setValue(props.get("_side_b", 100))
                    self.spin_angle_deg.setValue(props.get("_angle_deg", 90))
                else:
                    self._enable_angle_fields(False)
            elif shape_type == "text":
                # Для текста показываем параметры шрифта
                self._enable_font_fields(True)
                self._set_font_properties_from_dict(props)
            elif shape_type == "formula":
                # Для формулы показываем стиль и размер
                self._enable_formula_fields(True)
                fontset = props.get("fontset", "cm")
                # Маппинг fontset value → display name
                fontset_to_name = {
                    "dejavusans": "DejaVu Sans",
                    "dejavuserif": "DejaVu Serif",
                    "cm": "Computer Modern",
                    "stix": "STIX",
                    "stixsans": "STIX Sans",
                }
                display_name = fontset_to_name.get(fontset, "Computer Modern")
                idx = self.combo_formula_style.findText(display_name)
                if idx >= 0:
                    self.combo_formula_style.setCurrentIndex(idx)
                self.spin_formula_size.setValue(props.get("font_size", 16))
            else:
                self._enable_coordinate_fields(False)
                self._enable_arc_fields(False)
                self._enable_formula_fields(False)

            # Показываем параметры карандаша если инструмент карандаш/линии
            if self._mw is not None:
                from tools.tool_types import ToolType

                current_tool = self._mw._tool_manager.current_tool
                if current_tool in (
                    ToolType.PENCIL,
                    ToolType.LINE,
                    ToolType.RAY,
                    ToolType.INFINITE_LINE,
                ):
                    self.set_pencil_controls_visible(True)
                    self.sync_pencil_controls()
                else:
                    self.set_pencil_controls_visible(False)
        finally:
            # Разблокируем сигналы
            self.blockSignals(False)

    def _enable_coordinate_fields(self, enabled: bool) -> None:
        """Включить/отключить поля координат и размеров."""
        self._lbl_coord_params.setVisible(enabled)
        self.lbl_coord_x.setVisible(enabled)
        self.spin_x.setVisible(enabled)
        self.lbl_coord_y.setVisible(enabled)
        self.spin_y.setVisible(enabled)
        self.lbl_coord_w.setVisible(enabled)
        self.spin_width.setVisible(enabled)
        self.lbl_coord_h.setVisible(enabled)
        self.spin_height.setVisible(enabled)

    def _enable_arc_fields(self, enabled: bool) -> None:
        """Включить/отключить поля параметров дуги."""
        self._lbl_arc_params.setVisible(enabled)
        self.lbl_arc_radius.setVisible(enabled)
        self.lbl_arc_start.setVisible(enabled)
        self.lbl_arc_end.setVisible(enabled)
        self.spin_radius.setVisible(enabled)
        self.spin_start_angle.setVisible(enabled)
        self.spin_end_angle.setVisible(enabled)
        self.spin_radius.setEnabled(enabled)
        self.spin_start_angle.setEnabled(enabled)
        self.spin_end_angle.setEnabled(enabled)

    def _enable_angle_fields(self, enabled: bool) -> None:
        """Включить/отключить поля параметров угла."""
        self.lbl_angle_params.setVisible(enabled)
        # Layouts don't have setVisible, hide children widgets
        for i in range(self.h_side_a.count()):
            item = self.h_side_a.itemAt(i)
            if item is not None:
                w = item.widget()
                if w:
                    w.setVisible(enabled)
        for i in range(self.h_side_b.count()):
            item = self.h_side_b.itemAt(i)
            if item is not None:
                w = item.widget()
                if w:
                    w.setVisible(enabled)
        for i in range(self.h_angle_deg.count()):
            item = self.h_angle_deg.itemAt(i)
            if item is not None:
                w = item.widget()
                if w:
                    w.setVisible(enabled)
        self.spin_side_a.setEnabled(enabled)
        self.spin_side_b.setEnabled(enabled)
        self.spin_angle_deg.setEnabled(enabled)

    def _enable_font_fields(self, enabled: bool) -> None:
        """Включить/отключить поля параметров шрифта."""
        self._lbl_font_params.setVisible(enabled)
        for i in range(self._h_font_family.count()):
            item = self._h_font_family.itemAt(i)
            if item is not None:
                w = item.widget()
                if w:
                    w.setVisible(enabled)
        self._lbl_font_size.setVisible(enabled)
        self.spin_font_size.setVisible(enabled)
        self.chk_font_bold.setVisible(enabled)
        self.chk_font_italic.setVisible(enabled)
        self.chk_font_underline.setVisible(enabled)
        self.chk_font_strikethrough.setVisible(enabled)
        if enabled:
            self.combo_font_family.setEnabled(True)
            self.spin_font_size.setEnabled(True)
            self.chk_font_bold.setEnabled(True)
            self.chk_font_italic.setEnabled(True)
            self.chk_font_underline.setEnabled(True)
            self.chk_font_strikethrough.setEnabled(True)
        else:
            self.combo_font_family.setEnabled(False)
            self.spin_font_size.setEnabled(False)
            self.chk_font_bold.setEnabled(False)
            self.chk_font_italic.setEnabled(False)
            self.chk_font_underline.setEnabled(False)
            self.chk_font_strikethrough.setEnabled(False)

    def _enable_formula_fields(self, enabled: bool) -> None:
        """Включить/отключить поля параметров формулы."""
        self._lbl_formula_params.setVisible(enabled)
        self._lbl_formula_size.setVisible(enabled)
        for i in range(self._h_formula_style.count()):
            item = self._h_formula_style.itemAt(i)
            if item is not None:
                w = item.widget()
                if w:
                    w.setVisible(enabled)
        self.spin_formula_size.setVisible(enabled)
        if enabled:
            self.combo_formula_style.setEnabled(True)
            self.spin_formula_size.setEnabled(True)
        else:
            self.combo_formula_style.setEnabled(False)
            self.spin_formula_size.setEnabled(False)

    def _set_font_properties_from_dict(self, props: dict) -> None:
        """Установка свойств шрифта из словаря без генерации сигналов."""
        # Блокируем ВСЕ сигналы font widgets
        self.combo_font_family.blockSignals(True)
        self.spin_font_size.blockSignals(True)
        self.chk_font_bold.blockSignals(True)
        self.chk_font_italic.blockSignals(True)
        self.chk_font_underline.blockSignals(True)
        self.chk_font_strikethrough.blockSignals(True)

        try:
            self.combo_font_family.clear()
            TextShape.populate_available_fonts()
            for family in TextShape.AVAILABLE_FONTS:
                self.combo_font_family.addItem(family)
            font_family = props.get("font_family", TextShape.DEFAULT_FONT_FAMILY)
            idx = self.combo_font_family.findText(font_family)
            if idx >= 0:
                self.combo_font_family.setCurrentIndex(idx)
            self.spin_font_size.setValue(props.get("font_size", TextShape.DEFAULT_FONT_SIZE))
            fw = props.get("font_weight", 0)
            self.chk_font_bold.setChecked(fw == QFont.Weight.Bold)
            self.chk_font_italic.setChecked(props.get("italic", False))
            self.chk_font_underline.setChecked(props.get("underline", False))
            self.chk_font_strikethrough.setChecked(props.get("strikethrough", False))
        finally:
            # Разблокируем сигналы
            self.combo_font_family.blockSignals(False)
            self.spin_font_size.blockSignals(False)
            self.chk_font_bold.blockSignals(False)
            self.chk_font_italic.blockSignals(False)
            self.chk_font_underline.blockSignals(False)
            self.chk_font_strikethrough.blockSignals(False)

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
        self._enable_font_fields(False)
        self._enable_formula_fields(False)

        # Скрываем/показываем параметры карандаша в зависимости от активного инструмента
        if self._mw is not None:
            from tools.tool_types import ToolType

            current_tool = self._mw._tool_manager.current_tool
            if current_tool in (
                ToolType.PENCIL,
                ToolType.LINE,
                ToolType.RAY,
                ToolType.INFINITE_LINE,
            ):
                self.set_pencil_controls_visible(True)
                self.sync_pencil_controls()
            else:
                self.set_pencil_controls_visible(False)

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
            if (
                self._selected_shape_type == "circle"
                or self._selected_shape_type == "circumscribed_quadrilateral"
            ):
                # Для окружности и описанного четырёхугольника возвращаем radius напрямую из spinner (диаметр / 2)
                result["_radius"] = self.spin_width.value() / 2
            else:
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

        # Добавляем свойства шрифта текста, если выделен текст
        if self._selected_shape_type == "text" and self.combo_font_family.isEnabled():
            result["font_family"] = self.combo_font_family.currentText()
            result["font_size"] = self.spin_font_size.value()
            result["font_weight"] = (
                QFont.Weight.Bold if self.chk_font_bold.isChecked() else QFont.Weight.Normal
            )
            result["italic"] = self.chk_font_italic.isChecked()
            result["underline"] = self.chk_font_underline.isChecked()
            result["strikethrough"] = self.chk_font_strikethrough.isChecked()

        # Добавляем параметры формулы, если выделена формула
        if self._selected_shape_type == "formula" and self.combo_formula_style.isEnabled():
            display_name = self.combo_formula_style.currentText()
            name_to_fontset = {
                "DejaVu Sans": "dejavusans",
                "DejaVu Serif": "dejavuserif",
                "Computer Modern": "cm",
                "STIX": "stix",
                "STIX Sans": "stixsans",
            }
            result["fontset"] = name_to_fontset.get(display_name, "cm")
            result["font_size"] = self.spin_formula_size.value()

        return result

    def set_multiple_shapes(self, shapes) -> None:
        """Установка общих свойств для нескольких фигур."""
        if not shapes:
            self.clear()
            return

        # Скрываем параметры карандаша при выделении фигур
        self.set_pencil_controls_visible(False)

        # Собираем общие свойства для всех фигур
        common_props = {}

        # Проверяем, совпадают ли свойства у всех фигур
        first_props = shapes[0].get_properties()

        for prop_name in ["pen_color", "pen_width", "brush_color", "rotation"]:
            if all(
                shape.get_properties().get(prop_name) == first_props.get(prop_name)
                for shape in shapes
            ):
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
            new_val = self.spin_width.value()
            if (
                self._selected_shape_type == "circle"
                or self._selected_shape_type == "circumscribed_quadrilateral"
            ):
                # Для окружности и описанного четырёхугольника width = height = 2 * radius
                self._selected_props["_radius"] = new_val / 2
                self.spin_height.blockSignals(True)
                self.spin_height.setValue(new_val)
                self.spin_height.blockSignals(False)
            else:
                self._selected_props["_width"] = new_val
        elif sender is self.spin_height:
            new_val = self.spin_height.value()
            if (
                self._selected_shape_type == "circle"
                or self._selected_shape_type == "circumscribed_quadrilateral"
            ):
                # Для окружности и описанного четырёхугольника width = height = 2 * radius
                self._selected_props["_radius"] = new_val / 2
                self.spin_width.blockSignals(True)
                self.spin_width.setValue(new_val)
                self.spin_width.blockSignals(False)
            else:
                self._selected_props["_height"] = new_val
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

    # ------------------------------------------------------------------
    # Свойства шрифта текста
    # ------------------------------------------------------------------

    def _on_font_size_changed(self, value: int):
        """Обработчик изменения размера шрифта."""
        if self._selected_props is None:
            return
        self._selected_props["font_size"] = value
        self.properties_changed.emit(self._selected_props)

    def _on_font_bold_toggled(self, checked: bool):
        """Обработчик изменения жирности шрифта."""
        if self._selected_props is None:
            return
        self._selected_props["font_weight"] = QFont.Weight.Bold if checked else QFont.Weight.Normal
        self.properties_changed.emit(self._selected_props)

    def _on_font_italic_toggled(self, checked: bool):
        """Обработчик изменения курсива."""
        if self._selected_props is None:
            return
        self._selected_props["italic"] = checked
        self.properties_changed.emit(self._selected_props)

    def _on_font_underline_toggled(self, checked: bool):
        """Обработчик изменения подчёркивания."""
        if self._selected_props is None:
            return
        self._selected_props["underline"] = checked
        self.properties_changed.emit(self._selected_props)

    def _on_font_strikethrough_toggled(self, checked: bool):
        """Обработчик изменения зачёркивания."""
        if self._selected_props is None:
            return
        self._selected_props["strikethrough"] = checked
        self.properties_changed.emit(self._selected_props)

    def _on_font_family_changed(self, index: int):
        """Обработчик изменения семейства шрифта."""
        if self._selected_props is None:
            return
        family = self.combo_font_family.currentText()
        self._selected_props["font_family"] = family
        self.properties_changed.emit(self._selected_props)

    # ------------------------------------------------------------------
    # Параметры формулы
    # ------------------------------------------------------------------

    def _on_formula_style_changed(self, index: int):
        """Обработчик изменения стиля формулы (fontset)."""
        if self._selected_props is None:
            return
        display_name = self.combo_formula_style.currentText()
        # Маппинг display name → fontset value
        name_to_fontset = {
            "DejaVu Sans": "dejavusans",
            "DejaVu Serif": "dejavuserif",
            "Computer Modern": "cm",
            "STIX": "stix",
            "STIX Sans": "stixsans",
        }
        self._selected_props["fontset"] = name_to_fontset.get(display_name, "cm")
        self.properties_changed.emit(self._selected_props)

    def _on_formula_size_changed(self, value: int):
        """Обработчик изменения размера формулы."""
        if self._selected_props is None:
            return
        self._selected_props["font_size"] = value
        self.properties_changed.emit(self._selected_props)

    # ------------------------------------------------------------------
    # Параметры карандаша
    # ------------------------------------------------------------------

    def set_pencil_controls_visible(self, visible: bool) -> None:
        """Показать/скрыть элементы управления карандашом."""
        self._lbl_pencil.setVisible(visible)
        # Layouts don't have setVisible, hide children widgets
        for i in range(self._h_pencil_color.count()):
            item = self._h_pencil_color.itemAt(i)
            if item is not None:
                w = item.widget()
                if w:
                    w.setVisible(visible)
        for i in range(self._h_pencil_width.count()):
            item = self._h_pencil_width.itemAt(i)
            if item is not None:
                w = item.widget()
                if w:
                    w.setVisible(visible)
        for i in range(self._h_pencil_style.count()):
            item = self._h_pencil_style.itemAt(i)
            if item is not None:
                w = item.widget()
                if w:
                    w.setVisible(visible)

    def sync_pencil_controls(self) -> None:
        """Синхронизировать UI карандаша с текущими параметрами ToolManager."""
        if self._mw is None or self._mw._tool_manager is None:
            return
        tm = self._mw._tool_manager
        # Устанавливаем цвет
        self.btn_pencil_color.set_color(tm._pencil_color)
        # Устанавливаем толщину
        self.spin_pencil_width.setValue(tm._pencil_width)
        # Устанавливаем тип линии
        style_value = tm._pencil_style
        idx = self.combo_pencil_style.findData(style_value)
        if idx >= 0:
            self.combo_pencil_style.setCurrentIndex(idx)
        # Обновляем состояние кнопки сброса
        self._update_reset_pencil_button()

    def _update_reset_pencil_button(self) -> None:
        """Активировать кнопку сброса, если значения отличаются от настроек по умолчанию."""
        if self._mw is None or self._mw._tool_manager is None:
            self.btn_reset_pencil.setEnabled(False)
            return
        tm = self._mw._tool_manager
        settings = self._mw._settings
        differs = (
            tm._pencil_color != settings.default_pen_color
            or abs(tm._pencil_width - settings.default_pen_width) > 0.001
            or tm._pencil_style != 1  # SolidLine
        )
        self.btn_reset_pencil.setEnabled(differs)

    def set_pencil_style_options(self, styles: list[tuple[str, int]]) -> None:
        """Установить варианты типов линий для карандаша."""
        self.combo_pencil_style.clear()
        for name, style in styles:
            self.combo_pencil_style.addItem(name, style)

    def _on_pencil_color_changed(self, color: tuple):
        if self._mw is None:
            return
        self._mw._tool_manager._pencil_color = color
        self._update_reset_pencil_button()
        if self._mw._tool_manager._temp_shape is not None:
            self._mw._tool_manager._temp_shape.pen_color = color
            self._mw._event_manager._drawing.update_temp_shape()

    def _on_pencil_width_changed(self, value: float):
        if self._mw is None:
            return
        self._mw._tool_manager._pencil_width = value
        self._update_reset_pencil_button()
        if self._mw._tool_manager._temp_shape is not None:
            self._mw._tool_manager._temp_shape.pen_width = value
            self._mw._event_manager._drawing.update_temp_shape()

    def _on_pencil_style_changed(self, index: int):
        if self._mw is None:
            return
        style = self.combo_pencil_style.currentData()
        self._mw._tool_manager._pencil_style = int(style)
        self._update_reset_pencil_button()
        if self._mw._tool_manager._temp_shape is not None:
            self._mw._tool_manager._temp_shape._pen_style = self._mw._tool_manager._pencil_style
            self._mw._event_manager._drawing.update_temp_shape()

    def _on_reset_pencil(self) -> None:
        """Сбросить параметры карандаша к значениям по умолчанию из настроек."""
        if self._mw is None or self._mw._tool_manager is None:
            return
        tm = self._mw._tool_manager
        settings = self._mw._settings
        tm._pencil_color = settings.default_pen_color
        tm._pencil_width = settings.default_pen_width
        tm._pencil_style = 1  # Qt.PenStyle.SolidLine
        self.sync_pencil_controls()
        if tm._temp_shape is not None:
            tm._temp_shape.pen_color = settings.default_pen_color
            tm._temp_shape.pen_width = settings.default_pen_width
            tm._temp_shape._pen_style = 1
            self._mw._event_manager._drawing.update_temp_shape()
