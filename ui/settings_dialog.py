"""Диалог настроек приложения: параметры по умолчанию для новых фигур."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from ui.common_widgets import _ColorButton
from ui.theme_manager import ThemeManager, ThemeName


class SettingsDialog(QDialog):
    """Диалог настроек по умолчанию: цвет контура, заливка, толщина линии."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Настройки")
        self.setModal(True)
        self.resize(360, 480)

        # Текущие значения (копии)
        self._pen_color: tuple[int, int, int] = (0, 0, 0)
        self._brush_color: tuple[int, int, int] | None = None
        self._no_brush: bool = True
        self._pen_width: float = 2.0
        self._current_theme: str = "light"

        # Параметры графиков
        self._graph_width: int = 0
        self._graph_height: int = 0
        self._graph_font_size: int = 0
        self._graph_x_range: int = 0
        self._graph_x_steps: int = 0

        self._parent_mw = parent  # MainWindow для сохранения настроек
        self._build_ui()

    # ------------------------------------------------------------------
    # Инициализация значений
    # ------------------------------------------------------------------

    def set_defaults(
        self,
        pen_color: tuple[int, int, int],
        brush_color: tuple[int, int, int] | None,
        pen_width: float,
        theme: str = "light",
        graph_width: int = 300,
        graph_height: int = 200,
        graph_font_size: int = 8,
        graph_x_range: int = 10,
        graph_x_steps: int = 500,
    ) -> None:
        """Установить начальные значения из настроек приложения."""
        self._pen_color = tuple(pen_color)
        self._brush_color = brush_color
        self._no_brush = brush_color is None
        self._pen_width = pen_width
        self._current_theme = theme

        self._graph_width = graph_width
        self._graph_height = graph_height
        self._graph_font_size = graph_font_size
        self._graph_x_range = graph_x_range
        self._graph_x_steps = graph_x_steps

        # Обновляем виджеты
        self._btn_pen_color.set_color(self._pen_color)
        self._spin_pen_width.setValue(self._pen_width)
        self._chk_no_brush.setChecked(self._no_brush)
        self._btn_brush_color.setEnabled(not self._no_brush)
        if not self._no_brush and self._brush_color is not None:
            self._btn_brush_color.set_color(self._brush_color)

        # Обновляем параметры графиков
        self._spin_graph_width.setValue(self._graph_width)
        self._spin_graph_height.setValue(self._graph_height)
        self._spin_graph_font_size.setValue(self._graph_font_size)
        self._spin_graph_x_range.setValue(self._graph_x_range)
        self._spin_graph_x_steps.setValue(self._graph_x_steps)

        # Обновляем комбо-бокс темы
        if hasattr(self, "_theme_combo"):
            theme_names = list(ThemeManager.THEMES.keys())
            try:
                current_theme = ThemeName(self._current_theme)
                idx = theme_names.index(current_theme)
                self._theme_combo.setCurrentIndex(idx)
            except ValueError:
                pass

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # --- Цвет контура ---
        h_pen = QHBoxLayout()
        lbl_pen = QLabel("Цвет контура:")
        lbl_pen.setFixedWidth(120)
        lbl_pen.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        self._btn_pen_color = _ColorButton((0, 0, 0))
        self._btn_pen_color.color_changed.connect(self._on_pen_color_changed)

        h_pen.addWidget(lbl_pen)
        h_pen.addWidget(self._btn_pen_color)
        h_pen.addStretch()
        layout.addLayout(h_pen)

        # --- Толщина линии ---
        h_width = QHBoxLayout()
        lbl_width = QLabel("Толщина линии:")
        lbl_width.setFixedWidth(120)
        lbl_width.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        self._spin_pen_width = QDoubleSpinBox()
        self._spin_pen_width.setRange(0.5, 50.0)
        self._spin_pen_width.setSingleStep(0.5)
        self._spin_pen_width.setValue(2.0)

        h_width.addWidget(lbl_width)
        h_width.addWidget(self._spin_pen_width)
        h_width.addStretch()
        layout.addLayout(h_width)

        # --- Цвет заливки ---
        h_brush = QHBoxLayout()
        lbl_brush = QLabel("Цвет заливки:")
        lbl_brush.setFixedWidth(120)
        lbl_brush.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        self._btn_brush_color = _ColorButton((255, 255, 255))
        self._btn_brush_color.color_changed.connect(self._on_brush_color_changed)

        self._chk_no_brush = QCheckBox("Нет")
        self._chk_no_brush.setChecked(True)
        self._chk_no_brush.toggled.connect(self._on_no_brush_toggled)

        h_brush.addWidget(lbl_brush)
        h_brush.addWidget(self._btn_brush_color)
        h_brush.addWidget(self._chk_no_brush)
        h_brush.addStretch()
        layout.addLayout(h_brush)

        # --- Тема оформления ---
        h_theme = QHBoxLayout()
        lbl_theme = QLabel("Тема:")
        lbl_theme.setFixedWidth(120)
        lbl_theme.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        self._theme_combo = QComboBox()
        self._theme_combo.addItems(ThemeManager.THEMES.values())
        # Устанавливаем текущую тему
        theme_names = list(ThemeManager.THEMES.keys())
        current_idx = (
            theme_names.index(ThemeName(self._current_theme))
            if self._current_theme in [t.value for t in theme_names]
            else 0
        )
        self._theme_combo.setCurrentIndex(current_idx)

        h_theme.addWidget(lbl_theme)
        h_theme.addWidget(self._theme_combo)
        h_theme.addStretch()
        layout.addLayout(h_theme)

        # --- Параметры графиков ---
        lbl_graph = QLabel("Параметры графиков:")
        lbl_graph.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        layout.addWidget(lbl_graph)

        # Ширина
        h_gw = QHBoxLayout()
        lbl_gw = QLabel("Ширина:")
        lbl_gw.setFixedWidth(120)
        lbl_gw.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self._spin_graph_width = QSpinBox()
        self._spin_graph_width.setRange(100, 1200)
        self._spin_graph_width.setSuffix(" px")
        h_gw.addWidget(lbl_gw)
        h_gw.addWidget(self._spin_graph_width)
        h_gw.addStretch()
        layout.addLayout(h_gw)

        # Высота
        h_gh = QHBoxLayout()
        lbl_gh = QLabel("Высота:")
        lbl_gh.setFixedWidth(120)
        lbl_gh.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self._spin_graph_height = QSpinBox()
        self._spin_graph_height.setRange(100, 800)
        self._spin_graph_height.setSuffix(" px")
        h_gh.addWidget(lbl_gh)
        h_gh.addWidget(self._spin_graph_height)
        h_gh.addStretch()
        layout.addLayout(h_gh)

        # Размер шрифта
        h_gfs = QHBoxLayout()
        lbl_gfs = QLabel("Размер шрифта:")
        lbl_gfs.setFixedWidth(120)
        lbl_gfs.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self._spin_graph_font_size = QSpinBox()
        self._spin_graph_font_size.setRange(6, 48)
        self._spin_graph_font_size.setSuffix(" px")
        h_gfs.addWidget(lbl_gfs)
        h_gfs.addWidget(self._spin_graph_font_size)
        h_gfs.addStretch()
        layout.addLayout(h_gfs)

        # Диапазон X
        h_gxr = QHBoxLayout()
        lbl_gxr = QLabel("Диапазон X:")
        lbl_gxr.setFixedWidth(120)
        lbl_gxr.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self._spin_graph_x_range = QSpinBox()
        self._spin_graph_x_range.setRange(1, 100)
        self._spin_graph_x_range.setSuffix(" (от -N до N)")
        h_gxr.addWidget(lbl_gxr)
        h_gxr.addWidget(self._spin_graph_x_range)
        h_gxr.addStretch()
        layout.addLayout(h_gxr)

        # Точность
        h_gxs = QHBoxLayout()
        lbl_gxs = QLabel("Точность:")
        lbl_gxs.setFixedWidth(120)
        lbl_gxs.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self._spin_graph_x_steps = QSpinBox()
        self._spin_graph_x_steps.setRange(50, 5000)
        self._spin_graph_x_steps.setSuffix(" точек")
        h_gxs.addWidget(lbl_gxs)
        h_gxs.addWidget(self._spin_graph_x_steps)
        h_gxs.addStretch()
        layout.addLayout(h_gxs)

        # Кнопки
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_reset = QPushButton("Сброс")
        btn_reset.clicked.connect(self._on_reset)
        btn_layout.addWidget(btn_reset)
        btn_ok = QPushButton("OK")
        btn_ok.clicked.connect(self._on_ok)
        btn_cancel = QPushButton("Отмена")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

    def _on_reset(self) -> None:
        """Сбросить настройки к значениям по умолчанию."""
        self._pen_color = (0, 0, 0)
        self._brush_color = None
        self._no_brush = True
        self._pen_width = 2.0

        self._graph_width = 450
        self._graph_height = 300
        self._graph_font_size = 10
        self._graph_x_range = 10
        self._graph_x_steps = 500

        self._btn_pen_color.set_color(self._pen_color)
        self._spin_pen_width.setValue(self._pen_width)
        self._chk_no_brush.setChecked(True)
        self._btn_brush_color.setEnabled(False)

        self._spin_graph_width.setValue(self._graph_width)
        self._spin_graph_height.setValue(self._graph_height)
        self._spin_graph_font_size.setValue(self._graph_font_size)
        self._spin_graph_x_range.setValue(self._graph_x_range)
        self._spin_graph_x_steps.setValue(self._graph_x_steps)

    # ------------------------------------------------------------------
    # Слоты
    # ------------------------------------------------------------------

    def _on_pen_color_changed(self, color: tuple[int, int, int]) -> None:
        self._pen_color = color

    def _on_brush_color_changed(self, color: tuple[int, int, int]) -> None:
        self._brush_color = color

    def _on_no_brush_toggled(self, checked: bool) -> None:
        self._btn_brush_color.setEnabled(not checked)
        if checked:
            self._brush_color = None

    def _on_ok(self) -> None:
        """Применить и сохранить настройки."""
        mw = self._parent_mw
        if mw is None:
            self.accept()
            return

        settings = mw._settings
        settings.default_pen_color = self._pen_color
        settings.default_pen_width = self._spin_pen_width.value()
        settings.default_brush_color = (
            None if self._chk_no_brush.isChecked() else self._brush_color
        )

        # Сохраняем тему
        theme_names = list(ThemeManager.THEMES.keys())
        theme_idx = self._theme_combo.currentIndex()
        if 0 <= theme_idx < len(theme_names):
            theme = theme_names[theme_idx]
            settings.theme = theme.value
            # Применяем тему сразу
            mw.apply_theme(theme)

        # Сохраняем параметры графиков
        settings.graph_default_width = self._spin_graph_width.value()
        settings.graph_default_height = self._spin_graph_height.value()
        settings.graph_default_font_size = self._spin_graph_font_size.value()
        settings.graph_default_x_range = self._spin_graph_x_range.value()
        settings.graph_default_x_steps = self._spin_graph_x_steps.value()

        # Сохраняем в файл
        try:
            settings.save()
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox

            QMessageBox.warning(self, "Предупреждение", f"Не удалось сохранить настройки: {e}")

        self.accept()


# ------------------------------------------------------------------
# Вспомогательный виджет — кнопка-образец цвета
# ------------------------------------------------------------------
# _ColorButton импортируется из ui.common_widgets
