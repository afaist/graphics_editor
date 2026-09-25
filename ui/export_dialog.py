"""Диалог выбора области и формата экспорта."""

from __future__ import annotations

from enum import Enum

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QLabel,
    QVBoxLayout,
    QWidget,
)


class ExportRegion(Enum):
    """Регион экспорта."""

    ALL_SHAPES = "all_shapes"
    SELECTED = "selected"
    VIEWPORT = "viewport"


class ExportFormat(Enum):
    """Формат экспорта."""

    PNG = "png"
    SVG = "svg"


class ExportDialog(QDialog):
    """Диалог выбора области и формата экспорта."""

    def __init__(
        self,
        has_selection: bool = False,
        fmt: ExportFormat = ExportFormat.PNG,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._selected = has_selection
        self._format = fmt
        self._build_ui()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Описание
        fmt_name = "PNG" if self._format == ExportFormat.PNG else "SVG"
        info = QLabel(f"Выберите область для экспорта в {fmt_name}:")
        layout.addWidget(info)

        # Комбобокс с вариантами региона
        self._combo = QComboBox()
        self._combo.addItem("Все фигуры на полотне", ExportRegion.ALL_SHAPES)

        if self._selected:
            self._combo.addItem("Выделенные фигуры", ExportRegion.SELECTED)
        else:
            self._combo.addItem("Выделенные фигуры (нет выделения)", ExportRegion.SELECTED)

        self._combo.addItem("Видимая область (viewport)", ExportRegion.VIEWPORT)
        layout.addWidget(self._combo)

        # Кнопки
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_ok)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    # ------------------------------------------------------------------
    # Обработчики
    # ------------------------------------------------------------------

    def _on_ok(self) -> None:
        """Выбрать файл и вернуть регион."""
        region = self._combo.currentData()  # type: ignore[union-attr]
        assert region is not None

        if self._format == ExportFormat.PNG:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Экспорт в PNG",
                "",
                "PNG-изображение (*.png)",
            )
        else:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Экспорт в SVG",
                "",
                "SVG-изображение (*.svg)",
            )

        if file_path:
            self._export_region = region
            self._file_path = file_path
            self.accept()
        else:
            self.reject()

    # ------------------------------------------------------------------
    # API
    # ------------------------------------------------------------------

    @property
    def export_region(self) -> ExportRegion:
        """Выбранный регион экспорта."""
        return self._combo.currentData()  # type: ignore[return-value]

    @property
    def file_path(self) -> str:
        """Выбранный путь для сохранения."""
        return getattr(self, "_file_path", "")
