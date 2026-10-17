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
    QVBoxLayout,
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
        self.setMinimumWidth(500)
        self.setMinimumHeight(550)

        self._func_name = func_name
        self._params = params or {}
        self._preview_label: QLabel | None = None
        self._func_combo: QComboBox | None = None
        self._param_spinboxes: dict[str, QDoubleSpinBox] = {}
        self._debounce_timer: QTimer | None = None

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Настраивает интерфейс диалога."""
        main_layout = self._main_layout
        main_layout.setSpacing(10)

        # --- Выбор функции ---
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
        main_layout.addWidget(func_group)

        # --- Параметры ---
        param_group = QGroupBox("Параметры")
        param_layout = QFormLayout()
        param_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)

        self._update_param_fields()
        param_group.setLayout(param_layout)
        main_layout.addWidget(param_group)

        # --- Превью ---
        preview_group = QGroupBox("Превью графика")
        preview_layout = QVBoxLayout()

        self._preview_label = QLabel("Выберите функцию для превью")
        self._preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._preview_label.setFont(QFont("Segoe UI", 14))
        self._preview_label.setMinimumHeight(100)
        self._preview_label.setStyleSheet(
            "QLabel { background-color: #f5f5f5; border-radius: 4px; padding: 8px; }"
        )
        preview_layout.addWidget(self._preview_label)

        preview_group.setLayout(preview_layout)
        main_layout.addWidget(preview_group)

        # --- Быстрый выбор коэффициентов ---
        quick_group = QGroupBox("Быстрый выбор")
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
        main_layout.addWidget(quick_group)

        main_layout.addStretch()

    def _update_param_fields(self) -> None:
        """Обновляет поля ввода параметров для выбранной функции."""
        from shapes.graph_shape import GRAPH_FUNCTIONS

        # Удаляем старые поля
        for spin in self._param_spinboxes.values():
            spin.deleteLater()
        self._param_spinboxes.clear()

        func_key = self._func_combo.currentData()
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
            self.params_layout.addRow(label, spin)

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

        # Рендерим график
        try:
            import io
            import math

            import numpy as np
            from matplotlib.figure import Figure

            from shapes.graph_shape import GRAPH_FUNCTIONS

            dpi = 150
            fig = Figure(figsize=(4, 3), dpi=dpi)
            ax = fig.add_subplot(111)

            func_info = GRAPH_FUNCTIONS[func_key]  # type: ignore[index]
            fn = func_info["fn"]  # type: ignore[operator]

            x_vals = np.linspace(-10, 10, 500)
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
            ax.plot(x_vals, y_vals, color="black", linewidth=2)
            ax.set_xlim(-10, 10)
            ax.axhline(y=0, color="gray", linewidth=0.5, alpha=0.7)
            ax.axvline(x=0, color="gray", linewidth=0.5, alpha=0.7)
            ax.grid(True, alpha=0.3)

            buf = io.BytesIO()
            fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight", pad_inches=0.1)
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
        }

    def get_latex(self) -> str:
        """Возвращает данные графика (для совместимости с finish_graph)."""
        return ""
