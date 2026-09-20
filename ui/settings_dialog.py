"""Диалог настроек приложения: параметры по умолчанию для новых фигур."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QDialog,
    QDoubleSpinBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class SettingsDialog(QDialog):
    """Диалог настроек по умолчанию: цвет контура, заливка, толщина линии."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Настройки")
        self.setModal(True)
        self.resize(360, 240)

        # Текущие значения (копии)
        self._pen_color: tuple[int, int, int] = (0, 0, 0)
        self._brush_color: tuple[int, int, int] | None = None
        self._no_brush: bool = True
        self._pen_width: float = 2.0

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
    ) -> None:
        """Установить начальные значения из настроек приложения."""
        self._pen_color = tuple(pen_color)
        self._brush_color = brush_color
        self._no_brush = brush_color is None
        self._pen_width = pen_width

        # Обновляем виджеты
        self._btn_pen_color.set_color(self._pen_color)
        self._spin_pen_width.setValue(self._pen_width)
        self._chk_no_brush.setChecked(self._no_brush)
        self._btn_brush_color.setEnabled(not self._no_brush)
        if not self._no_brush and self._brush_color is not None:
            self._btn_brush_color.set_color(self._brush_color)

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

        self._btn_pen_color.set_color(self._pen_color)
        self._spin_pen_width.setValue(self._pen_width)
        self._chk_no_brush.setChecked(True)
        self._btn_brush_color.setEnabled(False)

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


class _ColorButton(QPushButton):
    """Компактная кнопка-образец цвета."""

    color_changed = Signal(tuple)  # (r, g, b)

    def __init__(self, initial: tuple = (0, 0, 0), parent: QWidget | None = None):
        super().__init__(parent)
        self._color: list[int] = list(initial)
        self.setText("...")
        self.setFixedWidth(80)
        self._update_style()
        self.clicked.connect(self._pick)

    def _update_style(self) -> None:
        r, g, b = self._color
        self.setStyleSheet(
            f"QPushButton {{ background-color: rgb({r},{g},{b}); "
            f"border: 1px solid #999; border-radius: 3px; min-height: 24px; }}"
        )

    def _pick(self) -> None:
        c = QColorDialog.getColor(QColor(*self._color), self, "Выбор цвета")
        if c.isValid():
            self._color = (c.red(), c.green(), c.blue())
            self._update_style()
            self.color_changed.emit(self._color)

    def get_color(self) -> tuple[int, int, int]:
        return tuple(self._color)

    def set_color(self, c: tuple[int, int, int]) -> None:
        self._color = list(c)
        self._update_style()
