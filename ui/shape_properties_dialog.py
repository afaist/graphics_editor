"""Диалог отображения свойств геометрических фигур."""

from __future__ import annotations

import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QFrame,
    QGroupBox,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from shapes.base_shape import SHAPE_NAMES_RU
from shapes.shape_properties import get_properties


class _PropertyWidget(QWidget):
    """Виджет одного свойства."""

    def __init__(self, title: str, description: str, formula: str, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.setStyleSheet(
            "_PropertyWidget { "
            "    background-color: #f9f9f9; "
            "    border: 1px solid #e0e0e0; "
            "    border-radius: 6px; "
            "    padding: 8px; "
            "}"
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        # Заголовок
        lbl_title = QLabel(title)
        lbl_title.setFont(QFont("Sans Serif", 10, QFont.Weight.Bold))
        lbl_title.setStyleSheet("color: #333333;")
        layout.addWidget(lbl_title)

        # Описание
        lbl_desc = QLabel(description)
        lbl_desc.setWordWrap(True)
        lbl_desc.setFont(QFont("Sans Serif", 9))
        lbl_desc.setStyleSheet("color: #555555;")
        layout.addWidget(lbl_desc)

        # Формула (если есть)
        if formula:
            lbl_formula = QLabel(formula)
            lbl_formula.setWordWrap(True)
            lbl_formula.setFont(QFont("Courier New", 10, QFont.Weight.Bold))
            lbl_formula.setStyleSheet(
                "color: #0066cc; "
                "background-color: #ffffff; "
                "border: 1px solid #cccccc; "
                "border-radius: 4px; "
                "padding: 4px 8px; "
            )
            layout.addWidget(lbl_formula)

        layout.addStretch()


class _PropertySection(QWidget):
    """Секция свойств с заголовком."""

    def __init__(self, title: str, items: list, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        # Заголовок секции
        lbl_section = QLabel(title)
        lbl_section.setFont(QFont("Sans Serif", 11, QFont.Weight.Bold))
        lbl_section.setStyleSheet("color: #0066cc; padding: 4px 0px;")
        layout.addWidget(lbl_section)

        # Разделитель
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("color: #cccccc;")
        layout.addWidget(separator)

        # Элементы свойств
        for item in items:
            prop_widget = _PropertyWidget(
                title=item.title,
                description=item.description,
                formula=item.formula,
            )
            layout.addWidget(prop_widget)

        layout.addStretch()


class ShapePropertiesDialog(QDialog):
    """Диалог отображения свойств фигуры."""

    def __init__(self, shape, parent=None):
        super().__init__(parent)
        self._shape = shape
        self._shape_type = shape.shape_type.value if hasattr(shape, "shape_type") else "unknown"
        self.setWindowTitle("Свойства фигуры")
        self.setMinimumSize(400, 300)
        self.setMaximumSize(600, 800)

        # Непрозрачный фон
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.setStyleSheet("QDialog {     background-color: #ffffff; }")

        # Основной layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Контент
        self._content_widget = QWidget()
        content_layout = QVBoxLayout(self._content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        props = get_properties(self._shape_type)
        if props:
            # Заголовок
            shape_name = SHAPE_NAMES_RU.get(
                self._shape_type, self._shape_type.replace("_", " ").title()
            )
            lbl_title = QLabel(shape_name)
            lbl_title.setFont(QFont("Sans Serif", 14, QFont.Weight.Bold))
            lbl_title.setStyleSheet("color: #003366; padding: 12px;")
            content_layout.addWidget(lbl_title)

            # Разделитель
            separator = QFrame()
            separator.setFrameShape(QFrame.Shape.HLine)
            separator.setFrameShadow(QFrame.Shadow.Sunken)
            separator.setStyleSheet("color: #cccccc;")
            content_layout.addWidget(separator)

            # Группа со свойствами
            group = QGroupBox("Свойства")
            group.setFont(QFont("Sans Serif", 10, QFont.Weight.Bold))
            group.setStyleSheet(
                "QGroupBox { "
                "    background-color: #ffffff; "
                "    border: 1px solid #dddddd; "
                "    border-radius: 6px; "
                "    margin-top: 8px; "
                "    padding-top: 12px; "
                "} "
                "QGroupBox::title { "
                "    subcontrol-origin: margin; "
                "    left: 10px; "
                "    padding: 0 4px; "
                "}"
            )

            group_layout = QVBoxLayout(group)
            group_layout.setContentsMargins(12, 12, 12, 12)
            group_layout.setSpacing(8)

            # Создаём секцию для всех свойств
            section = _PropertySection("Основные свойства", props.properties)
            group_layout.addWidget(section)

            content_layout.addWidget(group)
        else:
            lbl_no_props = QLabel(f"Свойства для фигуры «{self._shape_type}» не найдены")
            lbl_no_props.setFont(QFont("Sans Serif", 10))
            lbl_no_props.setStyleSheet("color: #888888; padding: 20px;")
            lbl_no_props.setAlignment(Qt.AlignmentFlag.AlignCenter)
            content_layout.addWidget(lbl_no_props)

        content_layout.addStretch()

        # Кнопки
        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(6)

        btn_export = QPushButton("Экспорт", self)
        btn_export.setFont(QFont("Sans Serif", 10, QFont.Weight.Bold))
        btn_export.setMinimumHeight(36)
        btn_export.clicked.connect(self._on_export_clicked)
        btn_export.setStyleSheet(
            "QPushButton { "
            "    background-color: #28a745; "
            "    color: #ffffff; "
            "    border: none; "
            "    border-radius: 4px; "
            "    padding: 8px 24px; "
            "} "
            "QPushButton:hover { "
            "    background-color: #218838; "
            "} "
            "QPushButton:pressed { "
            "    background-color: #1e7e34; "
            "}"
        )
        btn_layout.addWidget(btn_export)

        btn_close = QPushButton("Закрыть", self)
        btn_close.setFont(QFont("Sans Serif", 10, QFont.Weight.Bold))
        btn_close.setMinimumHeight(36)
        btn_close.clicked.connect(self.accept)
        btn_close.setStyleSheet(
            "QPushButton { "
            "    background-color: #0066cc; "
            "    color: #ffffff; "
            "    border: none; "
            "    border-radius: 4px; "
            "    padding: 8px 24px; "
            "} "
            "QPushButton:hover { "
            "    background-color: #0055aa; "
            "} "
            "QPushButton:pressed { "
            "    background-color: #004488; "
            "}"
        )
        btn_layout.addWidget(btn_close)

        content_layout.addLayout(btn_layout)

        # Прокрутка для маленьких экранов
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setWidget(self._content_widget)

        main_layout.addWidget(scroll)

    # ------------------------------------------------------------------
    # Экспорт
    # ------------------------------------------------------------------

    def _on_export_clicked(self) -> None:
        """Экспорт свойств фигуры в Markdown."""
        from logging_config import get_logger

        self._logger = get_logger("shape_properties_dialog")
        mw = self.parent()
        if mw is None:
            QMessageBox.warning(self, "Ошибка", "Не удалось получить доступ к приложению.")
            return

        # Получаем manager из MainWindow
        manager = getattr(mw, "_manager", None)
        if manager is None:
            QMessageBox.warning(self, "Ошибка", "Не удалось получить менеджер фигур.")
            return

        # Получаем имя фигуры до открытия диалога
        shape_name = SHAPE_NAMES_RU.get(
            self._shape_type, self._shape_type.replace("_", " ").title()
        )
        props = get_properties(self._shape_type)

        # Диалог выбора файла
        default_name = shape_name.replace(" ", "_")
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Экспорт свойств фигуры",
            f"{default_name}.md",
            "Markdown (*.md);;Все файлы (*)",
            options=QFileDialog.Option.DontUseNativeDialog,
        )
        if not filepath:
            return

        if not filepath.lower().endswith(".md"):
            filepath += ".md"

        # Получаем ID фигуры для уникального имени PNG
        shape_id = self._shape.id if hasattr(self._shape, "id") else 0
        png_filename = f"{shape_name.replace(' ', '_')}_id{shape_id}.png"

        # Сохраняем PNG рядом с markdown-файлом
        md_dir = os.path.dirname(filepath) or "."
        png_path = os.path.join(md_dir, png_filename)

        # Экспортируем фигуру в PNG
        success = self._export_shape_to_png(manager, png_path)
        if not success:
            QMessageBox.warning(
                self,
                "Ошибка экспорта",
                "Не удалось экспортировать изображение фигуры.",
            )
            return

        # Генерируем markdown контент
        md_content = self._build_markdown(shape_name, props, png_filename)

        # Записываем markdown файл
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(md_content)

        QMessageBox.information(
            self,
            "Экспорт завершён",
            f"Свойства фигуры экспортированы в:\n{filepath}",
        )
        self._logger.info("Экспорт завершён: %s", filepath)

    def _export_shape_to_png(self, manager, filepath: str) -> bool:
        """Экспортирует выделенную фигуру в PNG."""
        try:
            from PySide6.QtCore import QRectF
            from PySide6.QtGui import QColor, QImage, QImageWriter, QPainter
            from PySide6.QtWidgets import QGraphicsScene

            from ui.scene_items import ShapeSceneItem

            scene = QGraphicsScene()
            scene.setBackgroundBrush(QColor(0xFFFFFF))

            # Добавляем выделенные фигуры
            for shape in manager.shapes:
                if shape.id in manager.selected_ids:
                    item = ShapeSceneItem(shape)
                    item.setZValue(0)
                    scene.addItem(item)

            rect = scene.itemsBoundingRect()

            # Обработка пустой сцены или пустого bounding rect
            if rect.isEmpty():
                return False

            # Добавляем отступ
            padding = 30
            rect.adjust(-padding, -padding, padding, padding)

            # Вычисляем размеры с пропорциями
            aspect = rect.width() / rect.height() if rect.height() > 0 else 1.0
            if aspect >= 1:
                img_width = 500
                img_height = max(int(500 / aspect), 50)
            else:
                img_height = 500
                img_width = max(int(500 * aspect), 50)

            img_width = max(img_width, 50)
            img_height = max(img_height, 50)

            image = QImage(img_width, img_height, QImage.Format.Format_ARGB32_Premultiplied)
            image.fill(QColor(0xFFFFFF))

            painter = QPainter(image)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            scene.render(painter, QRectF(0, 0, img_width, img_height), rect)
            painter.end()

            writer = QImageWriter(filepath)
            writer.setFormat(b"PNG")
            writer.setQuality(95)

            if not writer.write(image):
                raise OSError(f"Failed to save PNG: {writer.errorString()}")

            return True

        except Exception as e:
            self._logger.error("Ошибка экспорта PNG: %s", e)
            return False

    def _build_markdown(self, shape_name: str, props, png_filename: str) -> str:
        """Собирает markdown контент."""
        lines: list[str] = []

        # Заголовок первого уровня
        lines.append(f"# {shape_name}")
        lines.append("")

        # Изображение (относительный путь)
        lines.append(f"![{shape_name}]({png_filename})")
        lines.append("")

        # Свойства
        if props:
            lines.append("## Свойства")
            lines.append("")
            lines.append("| Параметр | Описание | Формула |")
            lines.append("| --- | --- | --- |")

            for item in props.properties:
                title = self._escape_md(item.title)
                description = self._escape_md(item.description)
                formula = self._escape_md(item.formula) if item.formula else ""
                lines.append(f"| {title} | {description} | {formula} |")

            lines.append("")
        else:
            lines.append("*Свойства для данной фигуры не описаны.*")
            lines.append("")

        return "\n".join(lines)

    @staticmethod
    def _escape_md(text: str) -> str:
        """Экранирует специальные символы Markdown."""
        return text.replace("|", "\\|")
