"""Обработка рисования фигур: старт, продолжение, завершение, временные фигуры."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from PySide6.QtCore import QPointF

from shapes.base_shape import HandleType
from tools.tool_types import ToolType as ToolTypeEnum

if TYPE_CHECKING:
    from ui.scene_items import ShapeSceneItem

if TYPE_CHECKING:
    from shapes.text_shape import TextShape
    from ui.main_window import MainWindow

# Фигуры, которые не создают temp-shape, а сразу открывают диалог
GEOMETRY_DIALOG_TOOLS: frozenset[ToolTypeEnum] = frozenset(
    (
        ToolTypeEnum.CIRCLE,
        ToolTypeEnum.ARC,
        ToolTypeEnum.PARABOLA,
        ToolTypeEnum.HYPERBOLA,
        ToolTypeEnum.ANGLE,
        ToolTypeEnum.ANGLE_ADJACENT,
        ToolTypeEnum.ANGLE_VERTICAL,
        ToolTypeEnum.ANGLE_TRANSVERSAL,
        ToolTypeEnum.REGULAR_TRIANGLE,
        ToolTypeEnum.SQUARE,
        ToolTypeEnum.REGULAR_PENTAGON,
        ToolTypeEnum.REGULAR_HEXAGON,
        ToolTypeEnum.TRIANGLE_SHARYGIN,
        ToolTypeEnum.TETRAHEDRON,
        ToolTypeEnum.CUBE,
        ToolTypeEnum.OCTAHEDRON,
        ToolTypeEnum.DODECAHEDRON,
        ToolTypeEnum.ICOSAHEDRON,
        ToolTypeEnum.PARALLELEPIPED,
        ToolTypeEnum.SPHERE,
        ToolTypeEnum.CYLINDER,
        ToolTypeEnum.CONE,
        ToolTypeEnum.PYRAMID,
        ToolTypeEnum.PRISM,
        ToolTypeEnum.TRUNCATED_CONE,
        ToolTypeEnum.TRUNCATED_PYRAMID,
        ToolTypeEnum.RHOMBUS,
        ToolTypeEnum.QUADRILATERAL_IRREGULAR,
        ToolTypeEnum.CIRCUMSCRIBED_QUADRILATERAL,
        # Фракталы
        ToolTypeEnum.FRACTAL_KOCH,
        ToolTypeEnum.FRACTAL_SIERPINSKI_TRIANGLE,
        ToolTypeEnum.FRACTAL_SIERPINSKI_CARPET,
        ToolTypeEnum.FRACTAL_PYTHAGOREAN_TREE,
        ToolTypeEnum.FRACTAL_CANTOR_SET,
        ToolTypeEnum.FRACTAL_MANDELBROT,
        ToolTypeEnum.FRACTAL_JULIA,
        ToolTypeEnum.FRACTAL_NEWTON,
    )
)

# Фигуры, требующие диалог параметров при завершении рисования
GEOMETRY_FINISH_TOOLS: frozenset[ToolTypeEnum] = frozenset(
    (
        ToolTypeEnum.CIRCLE,
        ToolTypeEnum.RECTANGLE,
        ToolTypeEnum.TRIANGLE_EQUILATERAL,
        ToolTypeEnum.TRIANGLE_ISOSCELES,
        ToolTypeEnum.TRIANGLE_RIGHT,
        ToolTypeEnum.TRIANGLE_OBTUSE,
        ToolTypeEnum.TRIANGLE_CONGRUENT,
        ToolTypeEnum.TRIANGLE_SIMILAR,
        ToolTypeEnum.TRIANGLE_SHARYGIN,
        ToolTypeEnum.PARALLELOGRAM,
        ToolTypeEnum.TRAPEZOID_ISOSCELES,
        ToolTypeEnum.TRAPEZOID,
        ToolTypeEnum.RHOMBUS,
        ToolTypeEnum.QUADRILATERAL_IRREGULAR,
        ToolTypeEnum.CIRCUMSCRIBED_QUADRILATERAL,
        ToolTypeEnum.ARC,
        ToolTypeEnum.PARABOLA,
        ToolTypeEnum.HYPERBOLA,
        ToolTypeEnum.ANGLE,
        ToolTypeEnum.ANGLE_ADJACENT,
        ToolTypeEnum.ANGLE_VERTICAL,
        ToolTypeEnum.ANGLE_TRANSVERSAL,
        ToolTypeEnum.REGULAR_TRIANGLE,
        ToolTypeEnum.SQUARE,
        ToolTypeEnum.REGULAR_PENTAGON,
        ToolTypeEnum.REGULAR_HEXAGON,
        ToolTypeEnum.TETRAHEDRON,
        ToolTypeEnum.CUBE,
        ToolTypeEnum.OCTAHEDRON,
        ToolTypeEnum.DODECAHEDRON,
        ToolTypeEnum.ICOSAHEDRON,
        ToolTypeEnum.PARALLELEPIPED,
        ToolTypeEnum.SPHERE,
        ToolTypeEnum.CYLINDER,
        ToolTypeEnum.CONE,
        ToolTypeEnum.PYRAMID,
        ToolTypeEnum.PRISM,
        ToolTypeEnum.TRUNCATED_CONE,
        ToolTypeEnum.TRUNCATED_PYRAMID,
        # Фракталы
        ToolTypeEnum.FRACTAL_KOCH,
        ToolTypeEnum.FRACTAL_SIERPINSKI_TRIANGLE,
        ToolTypeEnum.FRACTAL_SIERPINSKI_CARPET,
        ToolTypeEnum.FRACTAL_PYTHAGOREAN_TREE,
        ToolTypeEnum.FRACTAL_CANTOR_SET,
        ToolTypeEnum.FRACTAL_MANDELBROT,
        ToolTypeEnum.FRACTAL_JULIA,
        ToolTypeEnum.FRACTAL_NEWTON,
    )
)

# Фигуры, завершающиеся через finish_current_shape
COMPOSED_FINISH_TOOLS: frozenset[ToolTypeEnum] = frozenset(
    (
        ToolTypeEnum.POLYGON,
        ToolTypeEnum.POLYLINE,
        ToolTypeEnum.QUADRILATERAL_IRREGULAR,
        ToolTypeEnum.FORMULA,
        ToolTypeEnum.GRAPH_LINEAR,
        ToolTypeEnum.GRAPH_QUADRATIC,
        ToolTypeEnum.GRAPH_SIN,
        ToolTypeEnum.GRAPH_COS,
        ToolTypeEnum.GRAPH_TAN,
        ToolTypeEnum.GRAPH_LOG,
        ToolTypeEnum.GRAPH_EXP,
        ToolTypeEnum.GRAPH_SQRT,
    )
)

# Фигуры, требующие диалог параметров (позиция = start_point)
START_POINT_DIALOG_TOOLS: frozenset[ToolTypeEnum] = frozenset(
    (
        ToolTypeEnum.CIRCLE,
        ToolTypeEnum.ARC,
        ToolTypeEnum.PARABOLA,
        ToolTypeEnum.HYPERBOLA,
        ToolTypeEnum.ANGLE,
        ToolTypeEnum.ANGLE_ADJACENT,
        ToolTypeEnum.ANGLE_VERTICAL,
        ToolTypeEnum.ANGLE_TRANSVERSAL,
        ToolTypeEnum.REGULAR_TRIANGLE,
        ToolTypeEnum.SQUARE,
        ToolTypeEnum.REGULAR_PENTAGON,
        ToolTypeEnum.REGULAR_HEXAGON,
        ToolTypeEnum.TRIANGLE_SHARYGIN,
        ToolTypeEnum.TETRAHEDRON,
        ToolTypeEnum.CUBE,
        ToolTypeEnum.OCTAHEDRON,
        ToolTypeEnum.DODECAHEDRON,
        ToolTypeEnum.ICOSAHEDRON,
        ToolTypeEnum.PARALLELEPIPED,
        ToolTypeEnum.SPHERE,
        ToolTypeEnum.CYLINDER,
        ToolTypeEnum.CONE,
        ToolTypeEnum.PYRAMID,
        ToolTypeEnum.PRISM,
        ToolTypeEnum.TRUNCATED_CONE,
        ToolTypeEnum.TRUNCATED_PYRAMID,
        ToolTypeEnum.CIRCUMSCRIBED_QUADRILATERAL,
        # Фракталы
        ToolTypeEnum.FRACTAL_KOCH,
        ToolTypeEnum.FRACTAL_SIERPINSKI_TRIANGLE,
        ToolTypeEnum.FRACTAL_SIERPINSKI_CARPET,
        ToolTypeEnum.FRACTAL_PYTHAGOREAN_TREE,
        ToolTypeEnum.FRACTAL_CANTOR_SET,
        ToolTypeEnum.FRACTAL_MANDELBROT,
        ToolTypeEnum.FRACTAL_JULIA,
        ToolTypeEnum.FRACTAL_NEWTON,
    )
)


class DrawingManager:
    """Управление рисованием фигур и временными объектами на сцене."""

    def __init__(self, main_window: MainWindow):
        self._mw = main_window

    # ------------------------------------------------------------------
    # Старт / продолжение рисования
    # ------------------------------------------------------------------

    def start_drawing(self, pos: QPointF, shift_pressed: bool):
        """Начало рисования новой фигуры."""
        mw = self._mw
        if mw._tool_manager.current_tool in GEOMETRY_DIALOG_TOOLS:
            mw._is_drawing = True
            mw._start_point = pos
            return

        mw._is_drawing = True
        # Удаляем старый temp item, чтобы не было дубликатов при каждом клике
        self.clear_temp_shape()
        mw._tool_manager.start_shape(pos, mw._settings)
        self.update_temp_shape()

    def continue_drawing(self, pos: QPointF, shift_pressed: bool):
        """Продолжение рисования фигуры."""
        mw = self._mw
        mw._tool_manager.update_shape(pos, shift_pressed)
        self.update_temp_shape()

    # ------------------------------------------------------------------
    # Завершение рисования
    # ------------------------------------------------------------------

    def finish_drawing(self, pos: QPointF, shift_pressed: bool):
        """Завершение рисования фигуры."""
        mw = self._mw
        from shapes.line_shape import LineShape
        from shapes.pencil_shape import PencilShape
        from shapes.point_shape import PointShape
        from shapes.polyline_shape import PolylineShape
        from shapes.text_shape import TextShape

        current_tool = mw._tool_manager.current_tool

        # Фигуры с параметрическим вводом — открываем диалог
        if current_tool in GEOMETRY_FINISH_TOOLS:
            # Для ARC, ANGLE и правильных фигур используем позицию нажатия
            if current_tool in START_POINT_DIALOG_TOOLS:
                dialog_pos = mw._start_point
                if dialog_pos is None:
                    mw._is_drawing = False
                    return
            else:
                dialog_pos = pos
            mw._event_manager._dialogs.show_shape_dialog(current_tool, dialog_pos)
            mw._is_drawing = False
            return

        shape = None

        if current_tool in COMPOSED_FINISH_TOOLS:
            shape = mw._tool_manager.finish_current_shape(mw._settings)
        else:
            shape = mw._tool_manager.finish_shape(pos)

        if shape is None:
            mw._is_drawing = False
            return

        if isinstance(shape, PointShape):
            mw.add_shape(shape)
            self.clear_temp_shape()
        elif isinstance(shape, TextShape):
            # Для текста — запрашиваем ввод текста
            self._finish_text_drawing(shape)
        else:
            br = shape.bounding_rect()
            w = br.width()
            h = br.height()

            if isinstance(shape, (LineShape, PolylineShape, PencilShape)):
                mw.add_shape(shape)
                self.clear_temp_shape()
            elif w > 1 or h > 1:
                mw.add_shape(shape)
                self.clear_temp_shape()

        mw._is_drawing = False

    # ------------------------------------------------------------------
    # Диалог для текста
    # ------------------------------------------------------------------

    def _finish_text_drawing(self, shape: TextShape):
        """Завершение рисования текстовой фигуры с вводом текста."""
        from PySide6.QtGui import QFont
        from PySide6.QtWidgets import (
            QCheckBox,
            QComboBox,
            QDialog,
            QHBoxLayout,
            QLabel,
            QLineEdit,
            QPushButton,
            QSpinBox,
            QVBoxLayout,
        )

        from shapes.text_shape import TextShape

        mw = self._mw

        # Заполняем список доступных шрифтов
        TextShape.populate_available_fonts()
        available_fonts = TextShape.AVAILABLE_FONTS

        # Создаём диалог для ввода текста
        dialog = QDialog(mw)
        dialog.setWindowTitle("Ввод текста")
        dialog.setMinimumWidth(450)
        dialog.setMinimumHeight(400)

        main_layout = QVBoxLayout(dialog)

        # --- Группа текста ---
        text_group = QVBoxLayout()
        lbl_text = QLabel("Текст:")
        lbl_text.setStyleSheet("font-weight: bold;")
        text_group.addWidget(lbl_text)

        line_edit = QLineEdit()
        line_edit.setPlaceholderText("Введите текст...")
        line_edit.setMinimumHeight(40)
        text_group.addWidget(line_edit)
        main_layout.addLayout(text_group)

        # --- Группа настроек шрифта ---
        font_group = QVBoxLayout()
        lbl_font = QLabel("Шрифт:")
        lbl_font.setStyleSheet("font-weight: bold;")
        font_group.addWidget(lbl_font)

        # Строка: семейство шрифта + размер
        font_row1 = QHBoxLayout()
        lbl_family = QLabel("Семейство:")
        font_combo = QComboBox()
        for family in available_fonts:
            # Предварительно применяем шрифт к элементу для предпросмотра
            item_font = QFont(family, 10)
            font_combo.setItemData(font_combo.count(), item_font)
            font_combo.addItem(family)
        font_combo.setCurrentText(TextShape.DEFAULT_FONT_FAMILY)
        font_row1.addWidget(lbl_family)
        font_row1.addWidget(font_combo)

        lbl_size = QLabel("Размер:")
        size_spin = QSpinBox()
        size_spin.setRange(4, 200)
        size_spin.setValue(TextShape.DEFAULT_FONT_SIZE)
        size_spin.setSingleStep(1)
        font_row1.addWidget(lbl_size)
        font_row1.addWidget(size_spin)
        font_row1.addStretch()
        font_group.addLayout(font_row1)

        # Строка: жирный + курсив
        font_row2 = QHBoxLayout()
        chk_bold = QCheckBox("Жирный")
        chk_bold.setStyleSheet("font-weight: bold;")
        font_row2.addWidget(chk_bold)

        chk_italic = QCheckBox("Курсив")
        chk_italic.setFont(QFont(font_combo.currentText(), 10, QFont.Weight.Normal, True))
        font_row2.addWidget(chk_italic)

        chk_underline = QCheckBox("Подчёркнутый")
        f_under = QFont(font_combo.currentText(), 10)
        f_under.setUnderline(True)
        chk_underline.setFont(f_under)
        font_row2.addWidget(chk_underline)

        chk_strikethrough = QCheckBox("Зачёркнутый")
        f_strike = QFont(font_combo.currentText(), 10)
        f_strike.setStrikeOut(True)
        chk_strikethrough.setFont(f_strike)
        font_row2.addWidget(chk_strikethrough)
        font_row2.addStretch()
        font_group.addLayout(font_row2)

        main_layout.addLayout(font_group)

        # --- Предпросмотр ---
        preview_label = QLabel("Предпросмотр:")
        preview_label.setStyleSheet("font-weight: bold;")
        main_layout.addWidget(preview_label)

        preview_text = QLabel("Пример текста: Аа Бб 123")
        preview_text.setStyleSheet(
            "QLabel { "
            "background-color: #f5f5f5; "
            "border: 1px solid #ccc; "
            "border-radius: 4px; "
            "padding: 10px; "
            "}"
        )
        preview_text.setMinimumHeight(50)
        main_layout.addWidget(preview_text)

        # --- Кнопки ---
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Отмена")
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        main_layout.addLayout(btn_layout)

        # --- Логика предпросмотра ---
        def update_preview():
            text = line_edit.text() if line_edit.text() else "Пример текста: Аа Бб 123"
            family = font_combo.currentText()
            size = size_spin.value()
            weight = QFont.Weight.Bold if chk_bold.isChecked() else QFont.Weight.Normal
            italic = chk_italic.isChecked()
            underline = chk_underline.isChecked()
            strikethrough = chk_strikethrough.isChecked()

            font = QFont(family, size)
            font.setWeight(weight)
            font.setItalic(italic)
            font.setUnderline(underline)
            font.setStrikeOut(strikethrough)
            preview_text.setFont(font)
            preview_text.setText(text)

        # Связываем события обновления предпросмотра
        line_edit.textChanged.connect(update_preview)
        font_combo.currentTextChanged.connect(update_preview)
        size_spin.valueChanged.connect(update_preview)
        chk_bold.toggled.connect(update_preview)
        chk_italic.toggled.connect(update_preview)
        chk_underline.toggled.connect(update_preview)
        chk_strikethrough.toggled.connect(update_preview)

        # Начальный предпросмотр
        update_preview()

        ok_btn.clicked.connect(dialog.accept)
        cancel_btn.clicked.connect(dialog.reject)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            text = line_edit.text().strip()
            if text:
                shape.text = text
                shape.font_family = font_combo.currentText()
                shape.font_size = size_spin.value()
                shape.font_weight = (
                    QFont.Weight.Bold if chk_bold.isChecked() else QFont.Weight.Normal
                )
                shape.italic = chk_italic.isChecked()
                shape.underline = chk_underline.isChecked()
                shape.strikethrough = chk_strikethrough.isChecked()
                mw.add_shape(shape)

        self.clear_temp_shape()

    # ------------------------------------------------------------------
    # Временные фигуры
    # ------------------------------------------------------------------

    def update_temp_shape(self):
        """Обновление временной фигуры на сцене."""
        mw = self._mw
        from ui.scene_items import ShapeSceneItem

        temp_shape = mw._tool_manager.temp_shape
        if temp_shape is None or mw._scene is None:
            return

        # Обновляем существующий элемент или создаём новый
        item = mw._temp_shape_item
        if item is not None and item.scene() == mw._scene:
            # Обновляем существующий элемент без удаления/добавления
            shape_item = cast("ShapeSceneItem", item)
            shape_item._shape = temp_shape
            shape_item.prepareGeometryChange()
            shape_item.update()
        else:
            # Создаём новый элемент
            if item is not None:
                try:
                    if mw._scene and item.scene() == mw._scene:
                        mw._scene.removeItem(item)
                except RuntimeError:
                    pass
            item = ShapeSceneItem(temp_shape)
            item.setZValue(1000)  # Поверх всех фигур
            mw._scene.addItem(item)
            mw._temp_shape_item = item

    def clear_temp_shape(self):
        """Очистка временной фигуры."""
        mw = self._mw
        if hasattr(mw, "_temp_shape_item") and mw._temp_shape_item is not None:
            try:
                if mw._scene and mw._temp_shape_item.scene() == mw._scene:
                    mw._scene.removeItem(mw._temp_shape_item)
            except RuntimeError:
                pass
            finally:
                mw._temp_shape_item = None

    # ------------------------------------------------------------------
    # Сброс состояния
    # ------------------------------------------------------------------

    def reset_drawing_state(self):
        """Сброс состояния рисования."""
        mw = self._mw
        mw._is_drawing = False
        mw._last_mouse_pos = None
        mw._selection_rect_start = None
        mw._selection_start_pos = None
        mw._is_dragging = False
        mw._is_selecting = False
        mw._is_moving = False
        mw._is_resizing = False
        mw._resize_shape = None
        mw._resize_handle_type = HandleType.NONE

        self.clear_temp_shape()
        mw._tool_manager.reset_current_shape()
