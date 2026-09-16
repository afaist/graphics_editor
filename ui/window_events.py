"""Модуль обработки событий мыши и рисования для MainWindow."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtWidgets import QDialog

from tools.tool_manager import ToolManager, ToolType as ToolTypeEnum
from shapes.base_shape import HandleType

if TYPE_CHECKING:
    from ui.main_window import MainWindow
    from ui.scene_items import ShapeSceneItem


class EventManager:
    """Управление событиями мыши, рисованием и временными фигурами.

    Обрабатывает два уровня событий:
    1. Canvas-уровень (mouse_pressed/moved/released) — для инструментов рисования
    2. Item-уровень (shape_selected/dragging/resized) — для выделения и трансформаций
    """

    def __init__(self, main_window: "MainWindow"):
        self._mw = main_window

    # ------------------------------------------------------------------
    # Обработка мыши
    # ------------------------------------------------------------------

    def on_canvas_mouse_press(self, event):
        """Обработка нажатия мыши на холсте.

        В SELECT-режиме обработка делегируется ShapeSceneItem через сигналы.
        В режиме рисования — обрабатывается здесь.
        """
        mw = self._mw
        if mw._canvas is None:
            return

        current_tool = mw._tool_manager.current_tool

        if current_tool == ToolTypeEnum.SELECT:
            # SELECT обрабатывается через сигналы ShapeSceneItem
            return

        mw._is_dragging = False
        mw._is_selecting = False

        pos = mw._canvas.mapToScene(event.pos())
        shift_pressed = event.modifiers() & Qt.KeyboardModifier.ShiftModifier
        self.start_drawing(pos, shift_pressed)

    def handle_selection_press(self, pos: QPointF, shift_pressed: bool):
        """Обработка выделения фигур."""
        mw = self._mw
        hit_shape = mw._manager.hit_test(pos)

        if hit_shape:
            if shift_pressed:
                mw._manager.toggle_selection(hit_shape.id)
            else:
                if hit_shape.id not in mw._manager.selected_ids:
                    mw._manager.select_shape(hit_shape.id)
            mw._selection_start_pos = pos
            mw._is_dragging = False
        else:
            if not shift_pressed:
                mw._manager.select_none()
            mw._selection_rect_start = pos
            mw._is_selecting = True

    def start_drawing(self, pos: QPointF, shift_pressed: bool):
        """Начало рисования новой фигуры."""
        mw = self._mw
        # ARC не создаёт временную фигуру — используется диалог
        if mw._tool_manager.current_tool == ToolTypeEnum.ARC:
            mw._is_drawing = True
            mw._start_point = pos
            return
        mw._is_drawing = True
        mw._tool_manager.start_shape(pos, mw._settings)
        self.update_temp_shape()

    def on_canvas_mouse_move(self, event):
        """Обработка движения мыши на холсте.

        В SELECT-режиме обработка перемещения делегируется ShapeSceneItem.
        В режиме рисования — обрабатывается здесь.
        """
        mw = self._mw
        if mw._canvas is None:
            return

        current_tool = mw._tool_manager.current_tool

        if current_tool == ToolTypeEnum.SELECT:
            # SELECT обрабатывается через сигналы ShapeSceneItem
            # Но обновляем координаты курсора
            pos = mw._canvas.mapToScene(event.pos())
            mw._last_mouse_pos = pos
            return

        pos = mw._canvas.mapToScene(event.pos())
        mw._last_mouse_pos = pos
        shift_pressed = event.modifiers() & Qt.KeyboardModifier.ShiftModifier

        if mw._is_drawing and mw._tool_manager.temp_shape is not None:
            self.continue_drawing(pos, shift_pressed)
        elif current_tool == ToolTypeEnum.ARC:
            # ARC не рисует временную фигуру — только запоминаем позицию
            pass

    def move_selected_shapes(self, current_pos: QPointF):
        """Перемещение выделенных фигур."""
        mw = self._mw
        if mw._selection_start_pos is None:
            return
        dx = current_pos.x() - mw._selection_start_pos.x()
        dy = current_pos.y() - mw._selection_start_pos.y()

        # Начинаем перемещение при любом движении мыши
        if abs(dx) > 1 or abs(dy) > 1:
            if not mw._is_dragging:
                mw._is_dragging = True
            mw._manager.move_selected(dx, dy)
            mw._selection_start_pos = current_pos

    def continue_drawing(self, pos: QPointF, shift_pressed: bool):
        """Продолжение рисования фигуры."""
        mw = self._mw
        mw._tool_manager.update_shape(pos, shift_pressed)
        self.update_temp_shape()

    def on_canvas_mouse_release(self, event):
        """Обработка отпускания кнопки мыши на холсте.

        Вызывается только для инструментов рисования (не SELECT).
        Для SELECT-инструмента обработка идёт через сигналы ShapeSceneItem
        и scene_clicked (для выделения рамкой).
        """
        mw = self._mw
        if mw._canvas is None:
            return

        current_tool = mw._tool_manager.current_tool

        if current_tool == ToolTypeEnum.SELECT:
            # SELECT обрабатывается через item-сигналы и scene_clicked
            # Но нужно завершить выделение рамкой, если оно было начато
            if mw._is_selecting:
                self.finish_selection_rectangle()
            return
        else:
            pos = mw._canvas.mapToScene(event.pos())
            shift_pressed = event.modifiers() & Qt.KeyboardModifier.ShiftModifier
            if mw._is_drawing:
                self.finish_drawing(pos, shift_pressed)
            mw._is_drawing = False

    # ------------------------------------------------------------------
    # Item-уровень: сигналы ShapeSceneItem
    # ------------------------------------------------------------------

    def on_shape_selected(self, item: "ShapeSceneItem", event):
        """Обработка выбора фигуры из ShapeSceneItem.

        Вызывается при клике на фигуру в SELECT-режиме.
        """
        mw = self._mw
        if item._shape is None:
            return

        shift_pressed = event.modifiers() & Qt.KeyboardModifier.ShiftModifier

        if shift_pressed:
            # Toggle selection
            mw._manager.toggle_selection(item._shape.id)
        else:
            if not item._shape.selected:
                mw._manager.select_shape(item._shape.id)

        mw._selection_start_pos = self._get_scene_pos(event)

    def on_shape_drag_started(self, item: "ShapeSceneItem", event):
        """Начало перетаскивания фигуры."""
        mw = self._mw
        mw._is_dragging = True
        mw._selection_start_pos = self._get_scene_pos(event)

    def on_shape_dragging(self, item: "ShapeSceneItem", event):
        """Перемещение фигуры (или группы выделенных фигур)."""
        mw = self._mw
        if not mw._is_dragging or mw._selection_start_pos is None:
            return

        current_pos = self._get_scene_pos(event)
        dx = current_pos.x() - mw._selection_start_pos.x()
        dy = current_pos.y() - mw._selection_start_pos.y()

        if abs(dx) > 1 or abs(dy) > 1:
            mw._manager.move_selected(dx, dy)
            mw._selection_start_pos = current_pos

    def on_shape_drag_finished(self, item: "ShapeSceneItem"):
        """Завершение перетаскивания фигуры."""
        mw = self._mw
        mw._is_dragging = False
        mw._selection_start_pos = None

    def on_shape_resized(self, item: "ShapeSceneItem"):
        """Обработка изменения размера фигуры через маркеры."""
        # Фигура уже изменилась через apply_handle_transform,
        # нужно только обновить сцену
        mw = self._mw
        if mw._canvas:
            mw._canvas.update()

    def on_scene_clicked(self, scene_pos: QPointF):
        """Обработка клика на пустом месте сцены (в SELECT-режиме).

        Начинает выделение рамкой.
        """
        mw = self._mw
        if not mw._manager:
            return
        # Снимаем выделение
        mw._manager.select_none()
        # Начинаем выделение рамкой
        mw._selection_rect_start = scene_pos
        mw._is_selecting = True

    # ------------------------------------------------------------------
    # Завершение операций
    # ------------------------------------------------------------------

    def finish_selection_rectangle(self):
        """Завершение выделения рамкой."""
        mw = self._mw
        if mw._selection_rect_start is None or mw._last_mouse_pos is None:
            return
        start = mw._selection_rect_start
        end = mw._last_mouse_pos
        selection_rect = QRectF(
            min(start.x(), end.x()),
            min(start.y(), end.y()),
            abs(end.x() - start.x()),
            abs(end.y() - start.y()),
        )

        if selection_rect.width() > 5 or selection_rect.height() > 5:
            mw._manager.select_by_rect(selection_rect)

        mw._is_selecting = False

    def finish_drawing(self, pos: QPointF, shift_pressed: bool):
        """Завершение рисования фигуры."""
        mw = self._mw
        from shapes.point_shape import PointShape
        from shapes.line_shape import LineShape
        from shapes.polyline_shape import PolylineShape
        from shapes.text_shape import TextShape
        from tools.tool_manager import ToolType

        current_tool = mw._tool_manager.current_tool

        # Новые фигуры с параметрическим вводом
        geometry_tools = (
            ToolType.TRIANGLE_EQUILATERAL,
            ToolType.TRIANGLE_ISOSCELES,
            ToolType.TRIANGLE_RIGHT,
            ToolType.TRIANGLE_OBTUSE,
            ToolType.PARALLELOGRAM,
            ToolType.TRAPEZOID_ISOSCELES,
            ToolType.TRAPEZOID,
            ToolType.ARC,
        )

        if current_tool in geometry_tools:
            # Для ARC используем позицию нажатия, а не отпускания
            dialog_pos = mw._start_point if current_tool == ToolTypeEnum.ARC else pos
            self._show_shape_dialog(current_tool, dialog_pos)
            mw._is_drawing = False
            return

        shape = None

        if current_tool in (ToolType.POLYGON, ToolType.POLYLINE):
            shape = mw._tool_manager.finish_current_shape()
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

    def _finish_text_drawing(self, shape: "TextShape"):
        """Завершение рисования текстовой фигуры с вводом текста."""
        from PySide6.QtWidgets import QLineEdit, QDialog, QVBoxLayout, QHBoxLayout, QPushButton

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
            else:
                # Если текст пустой — отменяем создание
                pass
        
        self.clear_temp_shape()

    def _show_shape_dialog(self, tool_type, pos: QPointF):
        """Показывает диалог ввода параметров и создаёт фигуру."""
        from PySide6.QtWidgets import QApplication
        from ui.shape_dialogs import create_dialog_for_tool
        from shapes.triangle_shape import TriangleShape
        from shapes.parallelogram_shape import ParallelogramShape
        from shapes.trapezoid_shape import TrapezoidShape
        from tools.tool_manager import ToolType
        
        mw = self._mw
        
        dialog = create_dialog_for_tool(tool_type)
        if dialog is None:
            return
        
        # Делаем главное окно родителем
        dialog.setParent(mw)
        dialog.setWindowTitle(dialog.windowTitle())
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            params = dialog.get_params()
            # Для треугольников используем выбранный тип из диалога
            if tool_type in (ToolType.TRIANGLE_EQUILATERAL, ToolType.TRIANGLE_ISOSCELES,
                             ToolType.TRIANGLE_RIGHT, ToolType.TRIANGLE_OBTUSE):
                triangle_type = params.get("triangle_type", "equilateral")
                type_map = {
                    "equilateral": ToolType.TRIANGLE_EQUILATERAL,
                    "isosceles": ToolType.TRIANGLE_ISOSCELES,
                    "right": ToolType.TRIANGLE_RIGHT,
                    "obtuse": ToolType.TRIANGLE_OBTUSE,
                }
                actual_tool_type = type_map.get(triangle_type, ToolType.TRIANGLE_EQUILATERAL)
            else:
                actual_tool_type = tool_type
            shape = self._create_shape_from_params(actual_tool_type, params, pos)
            if shape:
                mw.add_shape(shape)
        
        self.clear_temp_shape()

    def _create_shape_from_params(self, tool_type, params: dict, pos: QPointF):
        """Создаёт фигуру по параметрам из диалога."""
        from shapes.triangle_shape import TriangleShape
        from shapes.parallelogram_shape import ParallelogramShape
        from shapes.trapezoid_shape import TrapezoidShape
        from tools.tool_manager import ToolType
        from shapes.base_shape import ShapeType
        
        mw = self._mw
        pen_color = mw._settings.default_pen_color
        pen_width = mw._settings.default_pen_width
        brush_color = mw._settings.default_brush_color
        
        if tool_type == ToolType.TRIANGLE_EQUILATERAL:
            side = params.get("side_a", 100)
            raw = TriangleShape.build_equilateral(side)
            centered = TriangleShape.center_vertices(raw)
            centered = TriangleShape.flip_y(centered)  # Вершина вверх
            centered = TriangleShape.order_vertices_clockwise(centered)  # A=левый нижний, по часовой стрелке
            # Центрируем относительно позиции мыши
            cx = sum(v[0] for v in centered) / 3
            cy = sum(v[1] for v in centered) / 3
            offset_x = pos.x() - cx
            offset_y = pos.y() - cy
            vertices = [(v[0] + offset_x, v[1] + offset_y) for v in centered]
            return TriangleShape(
                vertices=vertices,
                triangle_type="equilateral",
                side_a=side,
                pen_color=pen_color,
                pen_width=pen_width,
                brush_color=brush_color,
            )
        
        elif tool_type == ToolType.TRIANGLE_ISOSCELES:
            base = params.get("side_a", 150)
            height = params.get("height", 86.6)
            raw = TriangleShape.build_isosceles(base, height)
            centered = TriangleShape.center_vertices(raw)
            centered = TriangleShape.flip_y(centered)
            centered = TriangleShape.order_vertices_clockwise(centered)
            cx = sum(v[0] for v in centered) / 3
            cy = sum(v[1] for v in centered) / 3
            offset_x = pos.x() - cx
            offset_y = pos.y() - cy
            vertices = [(v[0] + offset_x, v[1] + offset_y) for v in centered]
            return TriangleShape(
                vertices=vertices,
                triangle_type="isosceles",
                side_a=base,
                height=height,
                pen_color=pen_color,
                pen_width=pen_width,
                brush_color=brush_color,
            )
        
        elif tool_type == ToolType.TRIANGLE_RIGHT:
            leg_a = params.get("side_a", 100)
            leg_b = params.get("side_b", 100)
            raw = TriangleShape.build_right(leg_a, leg_b)
            centered = TriangleShape.center_vertices(raw)
            centered = TriangleShape.flip_y(centered)
            centered = TriangleShape.order_vertices_clockwise(centered)
            cx = sum(v[0] for v in centered) / 3
            cy = sum(v[1] for v in centered) / 3
            offset_x = pos.x() - cx
            offset_y = pos.y() - cy
            vertices = [(v[0] + offset_x, v[1] + offset_y) for v in centered]
            return TriangleShape(
                vertices=vertices,
                triangle_type="right",
                side_a=leg_a,
                side_b=leg_b,
                pen_color=pen_color,
                pen_width=pen_width,
                brush_color=brush_color,
            )
        
        elif tool_type == ToolType.TRIANGLE_OBTUSE:
            side_a = params.get("side_a", 100)
            side_b = params.get("side_b", 100)
            angle = params.get("angle_deg", 120)
            raw = TriangleShape.build_obtuse(side_a, side_b, angle)
            centered = TriangleShape.center_vertices(raw)
            centered = TriangleShape.flip_y(centered)
            centered = TriangleShape.order_vertices_clockwise(centered)
            cx = sum(v[0] for v in centered) / 3
            cy = sum(v[1] for v in centered) / 3
            offset_x = pos.x() - cx
            offset_y = pos.y() - cy
            vertices = [(v[0] + offset_x, v[1] + offset_y) for v in centered]
            return TriangleShape(
                vertices=vertices,
                triangle_type="obtuse",
                side_a=side_a,
                side_b=side_b,
                angle_deg=angle,
                pen_color=pen_color,
                pen_width=pen_width,
                brush_color=brush_color,
            )
        
        elif tool_type == ToolType.PARALLELOGRAM:
            side_a = params.get("side_a", 150)
            side_b = params.get("side_b", 100)
            angle = params.get("angle_deg", 60)
            raw = ParallelogramShape.build(side_a, side_b, angle)
            centered = ParallelogramShape.center_vertices(raw)
            centered = ParallelogramShape.order_vertices_clockwise(centered)
            cx = sum(v[0] for v in centered) / 4
            cy = sum(v[1] for v in centered) / 4
            offset_x = pos.x() - cx
            offset_y = pos.y() - cy
            vertices = [(v[0] + offset_x, v[1] + offset_y) for v in centered]
            return ParallelogramShape(
                vertices=vertices,
                side_a=side_a,
                side_b=side_b,
                angle_deg=angle,
                pen_color=pen_color,
                pen_width=pen_width,
                brush_color=brush_color,
            )
        
        elif tool_type == ToolType.TRAPEZOID_ISOSCELES:
            base_a = params.get("base_a", 200)
            base_b = params.get("base_b", 100)
            angle = params.get("angle_deg", 60)
            raw = TrapezoidShape.build_isosceles(base_a, base_b, angle)
            centered = TrapezoidShape.center_vertices(raw)
            centered = TrapezoidShape.order_vertices_clockwise(centered)
            cx = sum(v[0] for v in centered) / 4
            cy = sum(v[1] for v in centered) / 4
            offset_x = pos.x() - cx
            offset_y = pos.y() - cy
            vertices = [(v[0] + offset_x, v[1] + offset_y) for v in centered]
            return TrapezoidShape(
                vertices=vertices,
                trapezoid_type="isosceles",
                base_a=base_a,
                base_b=base_b,
                angle_deg=angle,
                pen_color=pen_color,
                pen_width=pen_width,
                brush_color=brush_color,
            )
        
        elif tool_type == ToolType.TRAPEZOID:
            top_width = params.get("top_width", 100)
            bottom_width = params.get("bottom_width", 200)
            height = params.get("height", 100)
            offset_left = params.get("offset_left", 0)
            
            # Проверка: для произвольной трапеции боковые стороны не должны совпадать
            # offset_right = bottom_width - top_width - offset_left
            # Неравенство боковых сторон: offset_left != offset_right
            # => offset_left != (bottom_width - top_width) / 2
            offset_right = bottom_width - top_width - offset_left
            if abs(offset_left - offset_right) < 1e-6:
                # Трапеция получается равнобедренной — корректируем offset_left
                offset_left = (bottom_width - top_width) / 2 + 10
                params["offset_left"] = offset_left
            
            raw = TrapezoidShape.build_scalene(top_width, bottom_width, height, offset_left)
            centered = TrapezoidShape.center_vertices(raw)
            centered = TrapezoidShape.order_vertices_clockwise(centered)
            cx = sum(v[0] for v in centered) / 4
            cy = sum(v[1] for v in centered) / 4
            offset_x = pos.x() - cx
            offset_y = pos.y() - cy
            vertices = [(v[0] + offset_x, v[1] + offset_y) for v in centered]
            return TrapezoidShape(
                vertices=vertices,
                trapezoid_type="scalene",
                top_width=top_width,
                bottom_width=bottom_width,
                height=height,
                offset_left=offset_left,
                pen_color=pen_color,
                pen_width=pen_width,
                brush_color=brush_color,
            )
        
        elif tool_type == ToolType.ARC:
            from shapes.arc_shape import ArcShape
            radius = params.get("radius", 100)
            start_angle = params.get("start_angle", 0)
            end_angle = params.get("end_angle", 180)
            return ArcShape(
                cx=pos.x(),
                cy=pos.y(),
                radius=radius,
                start_angle=start_angle,
                end_angle=end_angle,
                pen_color=pen_color,
                pen_width=pen_width,
                brush_color=brush_color,
            )
        
        return None

    # ------------------------------------------------------------------
    # Вспомогательные методы
    # ------------------------------------------------------------------

    def _get_scene_pos(self, event) -> QPointF:
        """Получает позицию курсора в координатах сцены из события."""
        if self._mw._canvas is None:
            return QPointF(0, 0)
        return self._mw._canvas.mapToScene(event.pos())

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

        self.clear_temp_shape()
        mw._tool_manager.reset_current_shape()
