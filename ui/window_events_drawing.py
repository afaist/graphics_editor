"""Обработка рисования фигур: старт, продолжение, завершение, временные фигуры."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QPointF

from shapes.base_shape import HandleType
from tools.tool_types import ToolType as ToolTypeEnum

if TYPE_CHECKING:
    from shapes.text_shape import TextShape
    from ui.main_window import MainWindow


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
        if mw._tool_manager.current_tool in (ToolTypeEnum.ARC, ToolTypeEnum.ANGLE):
            mw._is_drawing = True
            mw._start_point = pos
            return
        mw._is_drawing = True
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
        from shapes.point_shape import PointShape
        from shapes.polyline_shape import PolylineShape
        from shapes.text_shape import TextShape
        from tools.tool_types import ToolType

        current_tool = mw._tool_manager.current_tool

        # Новые фигуры с параметрическим вводом
        geometry_tools = (
            ToolType.RECTANGLE,
            ToolType.TRIANGLE_EQUILATERAL,
            ToolType.TRIANGLE_ISOSCELES,
            ToolType.TRIANGLE_RIGHT,
            ToolType.TRIANGLE_OBTUSE,
            ToolType.PARALLELOGRAM,
            ToolType.TRAPEZOID_ISOSCELES,
            ToolType.TRAPEZOID,
            ToolType.ARC,
            ToolType.ANGLE,
        )

        if current_tool in geometry_tools:
            # Для ARC и ANGLE используем позицию нажатия, а не отпускания
            if current_tool in (ToolTypeEnum.ARC, ToolTypeEnum.ANGLE):
                dialog_pos = mw._start_point
                if dialog_pos is None:
                    mw._is_drawing = False
                    return
            else:
                dialog_pos = pos
            mw._dialogs_manager.show_shape_dialog(current_tool, dialog_pos)
            mw._is_drawing = False
            return

        shape = None

        if current_tool in (ToolType.POLYGON, ToolType.POLYLINE):
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

            if isinstance(shape, (LineShape, PolylineShape)):
                if shape.length() > 1.0:
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

        self.clear_temp_shape()

        temp_shape = mw._tool_manager.temp_shape
        if temp_shape is None or mw._scene is None:
            return

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
