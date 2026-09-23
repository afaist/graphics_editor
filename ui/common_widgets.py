"""Общие UI-компоненты, используемые в нескольких модулях."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QColorDialog, QPushButton, QWidget


class _ColorButton(QPushButton):
    """Кнопка выбора цвета с превью."""

    color_changed = Signal(tuple)

    def __init__(
        self,
        initial: tuple[int, int, int] = (0, 0, 0),
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self._color: tuple[int, int, int] = initial
        self.setFixedHeight(30)
        self._update_style()
        self.clicked.connect(self._choose_color)

    def _update_style(self) -> None:
        r, g, b = self._color
        self.setStyleSheet(
            f"QPushButton {{ "
            f"background-color: rgb({r}, {g}, {b}); "
            f"border: 1px solid #999; "
            f"border-radius: 4px; "
            f"}}"
        )

    def _choose_color(self) -> None:
        dlg = QColorDialog(self)
        r, g, b = self._color
        dlg.setCurrentColor(QColor(r, g, b))
        if dlg.exec():
            color = dlg.currentColor()
            self._color = (color.red(), color.green(), color.blue())
            self._update_style()
            self.color_changed.emit(self._color)

    # Алиас для обратной совместимости с тестами
    _pick = _choose_color

    def set_color(self, color: tuple[int, int, int]) -> None:
        self._color = color
        self._update_style()

    def get_color(self) -> tuple[int, int, int]:
        return self._color
