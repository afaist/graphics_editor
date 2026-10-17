"""Диалог выбора математической функции для построения графика."""

from __future__ import annotations

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from ui.shape_dialogs import ShapeParamDialog

# Параметры по умолчанию для каждой функции
DEFAULT_PARAMS = {
    "linear": {"a": 1.0, "b": 0.0},
    "quadratic": {"a": 1.0, "b": 0.0, "c": 0.0},
    "sin": {"a": 1.0, "b": 1.0},
    "cos": {"a": 1.0, "b": 1.0},
    "tan": {"a": 1.0, "b": 1.0},
    "log": {"a": 1.0, "b": 1.0},
    "exp": {"a": 1.0, "b": 1.0},
    "sqrt": {"a": 1.0, "b": 1.0},
}


class GraphEditorDialog(ShapeParamDialog):
    """Диалог выбора функции и параметров для построения графика."""

    def __init__(self, parent=None, func_name: str = "linear", params: dict | None = None):
        super().__init__(parent, "Построение графика")
        self.setMinimumWidth(520)
        self.setMinimumHeight(620)

        self._func_name = func_name
        self._params = params or {}
        self._preview_label: QLabel | None = None
        self._func_combo: QComboBox | None = None
        self._param_spinboxes: dict[str, QDoubleSpinBox] = {}
        self._width_spin: QSpinBox | None = None
        self._height_spin: QSpinBox | None = None
        self._font_size_spin: QSpinBox | None = None
        self._pen_width_spin: QDoubleSpinBox | None = None
        self._x_range_spin: QSpinBox | None = None
        self._x_steps_spin: QSpinBox | None = None
        self._debounce_timer: QTimer | None = None

        self._setup_ui()
        self._apply_theme()
        # Инициализируем поля параметров после создания combo
        self._update_param_fields()
        # Обновляем превью после полной инициализации
        self._schedule_preview_update()

    def _apply_theme(self) -> None:
        """Применяет стили на основе палитры системы (светлая/тёмная тема)."""
        palette = self.palette()
        bg = palette.color(self.window().backgroundRole()).name()
        fg = palette.color(self.window().foregroundRole()).name()
        light_bg = palette.color(self.window().backgroundRole()).lighter(115).name()
        border = palette.color(self.window().backgroundRole()).darker(120).name()

        self.setStyleSheet(
            f"QDialog {{ background-color: {bg}; }}"
            f"QGroupBox {{ "
            f"    font-weight: bold; "
            f"    border: 1px solid {border}; "
            f"    border-radius: 4px; "
            f"    margin-top: 8px; "
            f"    padding-top: 12px; "
            f"    background-color: {bg}; "
            f"}}"
            f"QGroupBox::title {{ "
            f"    subcontrol-origin: margin; "
            f"    left: 8px; "
            f"}}"
            f"QLabel {{ color: {fg}; }}"
            f"QFormLayout QLabel {{ color: {fg}; }}"
            f"QComboBox, QDoubleSpinBox, QSpinBox {{ "
            f"    background-color: {light_bg}; "
            f"    color: {fg}; "
            f"    border: 1px solid {border}; "
            f"    border-radius: 3px; "
            f"    padding: 4px 8px; "
            f"}}"
            f"QComboBox::drop-down {{ border: none; }}"
            f"QComboBox::down-arrow {{ "
            f"    image: none; "
            f"    border: 2px solid {border}; "
            f"    border-radius: 2px; "
            f"    min-width: 8px; "
            f"    min-height: 8px; "
            f"}}"
            f"QPushButton {{ "
            f"    background-color: {light_bg}; "
            f"    color: {fg}; "
            f"    border: 1px solid {border}; "
            f"    border-radius: 3px; "
            f"    padding: 6px 16px; "
            f"    font-weight: bold; "
            f"}}"
            f"QPushButton:hover {{ background-color: {palette.color(self.window().backgroundRole()).lighter(125).name()}; }}"
            f"QPushButton:pressed {{ background-color: {palette.color(self.window().backgroundRole()).darker(110).name()}; }}"
            f"QScrollArea {{ border: none; background-color: transparent; }}"
            f"QLabel {{ background-color: transparent; }}"
        )

    def _setup_ui(self) -> None:
        """Настраивает интерфейс диалога."""
        main_layout = self._main_layout

        # --- Scroll-область с формами ---
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        scroll_content = QWidget()
        self._scroll_layout = QVBoxLayout(scroll_content)
        self._scroll_layout.setSpacing(12)
        self._scroll_layout.setContentsMargins(12, 12, 12, 12)

        scroll.setWidget(scroll_content)

        # --- 1. Тип функции ---
        func_group = QGroupBox("Тип функции")
        func_layout = QVBoxLayout()
        self._func_combo = QComboBox()
        from shapes.graph_shape import GRAPH_FUNCTIONS

        for key, info in GRAPH_FUNCTIONS.items():
            self._func_combo.addItem(info["name"], key)

        self._func_combo.setCurrentText(GRAPH_FUNCTIONS[self._func_name]["name"])
        self._func_combo.setFont(QFont("Segoe UI", 10))
        self._func_combo.currentIndexChanged.connect(self._on_function_changed)
        func_layout.addWidget(self._func_combo)
        func_group.setLayout(func_layout)
        self._scroll_layout.addWidget(func_group)

        # --- 2. Параметры функции ---
        param_group = QGroupBox("Параметры функции")
        self._param_form = QFormLayout()
        self._param_form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        param_group.setLayout(self._param_form)
        self._scroll_layout.addWidget(param_group)

        # --- 3. Параметры отображения ---
        display_group = QGroupBox("Параметры отображения")
        display_layout = QFormLayout()
        display_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)

        self._font_size_spin = QSpinBox()
        self._font_size_spin.setRange(6, 48)
        self._font_size_spin.setValue(12)
        self._font_size_spin.setSuffix(" px")
        self._font_size_spin.setFont(QFont("Segoe UI", 9))
        self._font_size_spin.valueChanged.connect(self._schedule_preview_update)
        display_layout.addRow("Размер шрифта:", self._font_size_spin)

        self._pen_width_spin = QDoubleSpinBox()
        self._pen_width_spin.setRange(0.5, 10.0)
        self._pen_width_spin.setDecimals(1)
        self._pen_width_spin.setValue(2.0)
        self._pen_width_spin.setSingleStep(0.5)
        self._pen_width_spin.setSuffix(" px")
        self._pen_width_spin.setFont(QFont("Segoe UI", 9))
        self._pen_width_spin.valueChanged.connect(self._schedule_preview_update)
        display_layout.addRow("Толщина пера:", self._pen_width_spin)

        self._x_range_spin = QSpinBox()
        self._x_range_spin.setRange(1, 100)
        self._x_range_spin.setValue(10)
        self._x_range_spin.setSuffix(" (диапазон X от -N до N)")
        self._x_range_spin.setFont(QFont("Segoe UI", 9))
        self._x_range_spin.valueChanged.connect(self._schedule_preview_update)
        display_layout.addRow("Диапазон X:", self._x_range_spin)

        self._x_steps_spin = QSpinBox()
        self._x_steps_spin.setRange(50, 5000)
        self._x_steps_spin.setValue(500)
        self._x_steps_spin.setSuffix(" точек")
        self._x_steps_spin.setFont(QFont("Segoe UI", 9))
        self._x_steps_spin.valueChanged.connect(self._schedule_preview_update)
        display_layout.addRow("Точность:", self._x_steps_spin)

        display_group.setLayout(display_layout)
        self._scroll_layout.addWidget(display_group)

        # --- 4. Размер графика ---
        size_group = QGroupBox("Размер графика на холсте")
        size_layout = QFormLayout()
        size_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)

        self._width_spin = QSpinBox()
        self._width_spin.setRange(100, 1200)
        self._width_spin.setValue(300)
        self._width_spin.setSuffix(" px")
        self._width_spin.setFont(QFont("Segoe UI", 9))
        self._width_spin.valueChanged.connect(self._schedule_preview_update)
        size_layout.addRow("Ширина:", self._width_spin)

        self._height_spin = QSpinBox()
        self._height_spin.setRange(100, 800)
        self._height_spin.setValue(200)
        self._height_spin.setSuffix(" px")
        self._height_spin.setFont(QFont("Segoe UI", 9))
        self._height_spin.valueChanged.connect(self._schedule_preview_update)
        size_layout.addRow("Высота:", self._height_spin)

        size_group.setLayout(size_layout)
        self._scroll_layout.addWidget(size_group)

        # --- 5. Быстрый выбор ---
        quick_group = QGroupBox("Быстрый выбор коэффициентов")
        quick_layout = QVBoxLayout()
        quick_items = [
            ("a = 1", "linear", {"a": 1}),
            ("a = -1", "linear", {"a": -1}),
            ("a = 2", "linear", {"a": 2}),
            ("b = 1", "linear", {"b": 1}),
            ("b = -1", "linear", {"b": -1}),
            ("a = 0.5", "linear", {"a": 0.5}),
        ]
        btn_layout = QHBoxLayout()
        for label, func, param in quick_items:
            btn = QPushButton(label)
            btn.setFixedSize(80, 28)
            btn.setFont(QFont("Segoe UI", 8))
            btn.clicked.connect(lambda checked, p=param: self._apply_quick_param(p))
            btn_layout.addWidget(btn)
        quick_layout.addLayout(btn_layout)
        quick_group.setLayout(quick_layout)
        self._scroll_layout.addWidget(quick_group)

        self._scroll_layout.addStretch()
        main_layout.addWidget(scroll)

        # --- 6. Превью (между scroll и кнопками OK/Отмена) ---
        preview_group = QGroupBox("Превью графика")
        preview_layout = QVBoxLayout()

        self._preview_label = QLabel("Загрузка...")
        self._preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._preview_label.setFont(QFont("Segoe UI", 14))
        self._preview_label.setMinimumHeight(150)
        preview_layout.addWidget(self._preview_label)

        preview_group.setLayout(preview_layout)
        main_layout.addWidget(preview_group)

    def _update_param_fields(self) -> None:
        """Обновляет поля ввода параметров для выбранной функции."""
        from shapes.graph_shape import GRAPH_FUNCTIONS

        # Очищаем форму
        while self._param_form.rowCount() > 0:
            self._param_form.removeRow(0)

        self._param_spinboxes.clear()

        func_key = self._func_combo.currentData()
        if not func_key:
            return

        func_info = GRAPH_FUNCTIONS.get(func_key, {})
        params = func_info.get("params", [])
        defaults = DEFAULT_PARAMS.get(func_key, {})

        for param_name in params:
            spin = QDoubleSpinBox()
            spin.setRange(-100, 100)
            spin.setDecimals(3)
            spin.setValue(self._params.get(param_name, defaults.get(param_name, 1.0)))
            spin.setSingleStep(0.1)
            spin.setFont(QFont("Segoe UI", 9))
            spin.valueChanged.connect(self._schedule_preview_update)
            self._param_spinboxes[param_name] = spin

            label = QLabel(f"Параметр {param_name}:")
            self._param_form.addRow(label, spin)

    def _on_function_changed(self, index: int) -> None:
        """Вызывается при смене типа функции."""
        self._update_param_fields()
        self._schedule_preview_update()

    def _apply_quick_param(self, param: dict[str, float]) -> None:
        """Применяет быстрый выбор параметра."""
        for key, value in param.items():
            if key in self._param_spinboxes:
                self._param_spinboxes[key].setValue(value)
        self._schedule_preview_update()

    def _schedule_preview_update(self) -> None:
        """Запускает обновление превью с debounce."""
        if self._debounce_timer is None:
            self._debounce_timer = QTimer(self)
            self._debounce_timer.setSingleShot(True)
            self._debounce_timer.setInterval(200)
            self._debounce_timer.timeout.connect(self._update_preview)
        self._debounce_timer.start()

    def _update_preview(self) -> None:
        """Обновляет превью графика."""
        if self._preview_label is None:
            return

        func_key = self._func_combo.currentData()
        if not func_key:
            return

        # Собираем параметры
        params = {}
        for name, spin in self._param_spinboxes.items():
            params[name] = spin.value()

        pen_width = self._pen_width_spin.value() if self._pen_width_spin else 2.0
        x_range = self._x_range_spin.value() if self._x_range_spin else 10
        x_steps = self._x_steps_spin.value() if self._x_steps_spin else 500

        # Рендерим график
        try:
            import io
            import math

            import numpy as np
            from matplotlib.figure import Figure

            from shapes.graph_shape import GRAPH_FUNCTIONS

            dpi = 150
            fig = Figure(figsize=(6, 4), dpi=dpi, constrained_layout=True)
            ax = fig.add_subplot(111)

            func_info = GRAPH_FUNCTIONS[func_key]  # type: ignore[index]
            fn = func_info["fn"]  # type: ignore[operator]

            x_vals = np.linspace(-x_range, x_range, x_steps)
            y_vals = []

            for x in x_vals:
                try:
                    args = [params.get(p, 1.0) for p in func_info["params"]]
                    y = fn(x, *args)
                    if math.isfinite(y):
                        y_vals.append(y)
                    else:
                        y_vals.append(float("nan"))
                except (ValueError, OverflowError):
                    y_vals.append(float("nan"))

            y_vals = np.array(y_vals)
            ax.plot(x_vals, y_vals, color="black", linewidth=pen_width)
            ax.set_xlim(-x_range, x_range)
            ax.axhline(y=0, color="gray", linewidth=0.5, alpha=0.7)
            ax.axvline(x=0, color="gray", linewidth=0.5, alpha=0.7)
            ax.grid(True, alpha=0.3)

            # Авто-масштабирование Y
            y_min = np.nanmin(y_vals)
            y_max = np.nanmax(y_vals)
            if np.isfinite(y_min) and np.isfinite(y_max) and y_max - y_min > 0:
                y_pad = (y_max - y_min) * 0.1
                ax.set_ylim(y_min - y_pad, y_max + y_pad)
            else:
                ax.set_ylim(-1, 1)

            # Заголовок
            func_info = GRAPH_FUNCTIONS[func_key]  # type: ignore[index]
            ax.set_title(func_info["name"], fontsize=10, fontweight="bold")
            ax.tick_params(labelsize=8)

            buf = io.BytesIO()
            fig.savefig(buf, format="png", dpi=dpi)
            buf.seek(0)
            fig.clf()

            from PIL import Image

            img = Image.open(buf)

            # Конвертируем PIL Image в base64 для QLabel
            buf2 = io.BytesIO()
            img.save(buf2, format="PNG")
            buf2.seek(0)
            import base64

            img_b64 = base64.b64encode(buf2.read()).decode()
            html = f'<img src="data:image/png;base64,{img_b64}" />'
            self._preview_label.setText(html)
            self._preview_label.setStyleSheet(
                "QLabel { background-color: white; border-radius: 4px; padding: 4px; }"
            )

        except ImportError:
            self._preview_label.setText("matplotlib не установлен")
            self._preview_label.setStyleSheet(
                "QLabel { background-color: #fff8e1; border-radius: 4px; padding: 8px; color: #f57c00; }"
            )
        except Exception:
            self._preview_label.setText("Ошибка рендеринга")
            self._preview_label.setStyleSheet(
                "QLabel { background-color: #fff3f3; border-radius: 4px; padding: 8px; color: #c00; }"
            )

    def get_params(self) -> dict:
        """Возвращает параметры из диалога."""
        params = {}
        for name, spin in self._param_spinboxes.items():
            params[name] = spin.value()

        return {
            "func_name": self._func_combo.currentData(),
            "params": params,
            "width": self._width_spin.value(),
            "height": self._height_spin.value(),
            "font_size": self._font_size_spin.value(),
            "pen_width": self._pen_width_spin.value(),
            "x_range": self._x_range_spin.value(),
            "x_steps": self._x_steps_spin.value(),
        }

    def get_latex(self) -> str:
        """Возвращает данные графика (для совместимости с finish_graph)."""
        return ""
