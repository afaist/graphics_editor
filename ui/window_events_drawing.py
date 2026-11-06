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
        ToolTypeEnum.RHOMBUS,
        ToolTypeEnum.QUADRILATERAL_IRREGULAR,
    )
)

# Фигуры, требующие диалог параметров при завершении рисования
GEOMETRY_FINISH_TOOLS: frozenset[ToolTypeEnum] = frozenset(
    (
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
        from PySide6.QtWidgets import QDialog, QHBoxLayout, QLineEdit, QPushButton, QVBoxLayout

        mw = self._mw

        # Создаём диалог для ввода текста
        dialog = QDialog(mw)
        dialog.setWindowTitle("Ввод текста")
        dialog.setMinimumWidth(300)

        layout = QVBoxLayout(dialog)

        line_edit = QLineEdit()
        line_edit.setPlaceholderText("Введите текст...")
        line_edit.setMinimumHeight(40)
        layout.addWidget(line_edit)

        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Отмена")
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        ok_btn.clicked.connect(dialog.accept)
        cancel_btn.clicked.connect(dialog.reject)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            text = line_edit.text().strip()
            if text:
                shape.text = text
                mw.add_shape(shape)
            # Если текст пустой — отменяем создание

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
