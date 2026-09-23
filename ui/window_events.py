"""Модуль обработки событий мыши и рисования для MainWindow."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtWidgets import QDialog

from shapes.base_shape import HandleType

if TYPE_CHECKING:
    from shapes.text_shape import TextShape

from tools.tool_manager import ToolType as ToolTypeEnum

if TYPE_CHECKING:
    from ui.main_window import MainWindow


class EventManager:
    """Управление событиями мыши, рисованием и временными фигурами."""

    def __init__(self, main_window: MainWindow):
        self._mw = main_window

    # ------------------------------------------------------------------
    # Обработка мыши
    # ------------------------------------------------------------------

    def on_canvas_mouse_press(self, event):
        """Обработка нажатия мыши на холсте."""
        mw = self._mw
        if mw._canvas is None:
            return
        pos = mw._canvas.mapToScene(event.pos())
        shift_pressed = event.modifiers() & Qt.KeyboardModifier.ShiftModifier

        current_tool = mw._tool_manager.current_tool

        if current_tool == ToolTypeEnum.SELECT:
            self.handle_selection_press(pos, shift_pressed)
        elif current_tool == ToolTypeEnum.MOVE:
            self.handle_move_press(pos, shift_pressed)
        else:
            mw._is_dragging = False
            mw._is_selecting = False
            self.start_drawing(pos, shift_pressed)

    def handle_selection_press(self, pos: QPointF, shift_pressed: bool):
        """Обработка выделения фигур."""
        mw = self._mw
        # Сначала проверяем, попали ли в ручку масштабирования
        if mw._manager.selected_shapes:
            self.handle_resize_press(pos)
            if mw._is_resizing:
                return
        hit_shape = mw._manager.hit_test(pos)

        if hit_shape:
            if shift_pressed:
                mw._manager.toggle_selection(hit_shape.id)
            else:
                if hit_shape.id not in mw._manager.selected_ids:
                    mw._manager.select_shape(hit_shape.id)
        else:
            if not shift_pressed:
                mw._manager.select_none()
            mw._selection_rect_start = pos
            mw._is_selecting = True
            self.update_cursor()

    def handle_move_press(self, pos: QPointF, shift_pressed: bool):
        """Обработка нажатия мыши в инструменте перемещения."""
        mw = self._mw
        if mw._is_moving:
            return
        # Если есть выделенные фигуры — сразу начинаем перемещение
        if mw._manager.selected_ids:
            mw._is_moving = True
            mw._selection_start_pos = pos
        else:
            # Иначе выделяем фигуру под курсором
            hit_shape = mw._manager.hit_test(pos)
            if hit_shape:
                mw._manager.select_shape(hit_shape.id)
                mw._is_moving = True
                mw._selection_start_pos = pos
            else:
                # Клик по пустому месту — сбрасываем выделение
                mw._manager.select_none()
                mw._is_moving = False

    def handle_move_move(self, current_pos: QPointF):
        """Перемещение выделенных фигур."""
        mw = self._mw
        if mw._selection_start_pos is None:
            return
        dx = current_pos.x() - mw._selection_start_pos.x()
        dy = current_pos.y() - mw._selection_start_pos.y()
        if abs(dx) > 1 or abs(dy) > 1:
            mw._manager.move_selected(dx, dy)
            mw._selection_start_pos = current_pos

    def handle_move_release(self):
        """Завершение перемещения."""
        mw = self._mw
        mw._is_moving = False
        mw._selection_start_pos = None

    def handle_resize_press(self, pos: QPointF):
        """Начало масштабирования за ручку."""
        mw = self._mw
        if mw._is_resizing:
            return
        # Ищем ручку среди выделенных фигур
        for shape in mw._manager.selected_shapes:
            handle_type = shape.get_handle_type(pos)
            if handle_type != HandleType.NONE:
                mw._is_resizing = True
                mw._resize_shape = shape
                mw._selection_start_pos = pos
                # Сохраняем состояние фигуры для undo
                mw._resize_shape_dict = shape.to_dict()
                return

    def handle_resize_move(self, current_pos: QPointF):
        """Масштабирование за ручку."""
        mw = self._mw
        if not mw._is_resizing or mw._resize_shape is None or mw._selection_start_pos is None:
            return
        mw._resize_shape.apply_handle_transform(
            mw._resize_shape.get_handle_type(current_pos),
            mw._selection_start_pos,
            current_pos,
        )
        mw._selection_start_pos = current_pos
        mw._manager.shapes_changed.emit()

    def handle_resize_release(self):
        """Завершение масштабирования."""
        mw = self._mw
        if mw._is_resizing and mw._resize_shape is not None and mw._resize_shape_dict is not None:
            # Создаём undo-команду для изменения свойств фигуры
            from manager.undo_commands import ResizeShapeCommand

            cmd = ResizeShapeCommand(mw._manager, mw._resize_shape.id, mw._resize_shape_dict)
            mw._manager.undo_stack.push(cmd)
        mw._is_resizing = False
        mw._resize_shape = None
        mw._resize_shape_dict = None
        mw._selection_start_pos = None

    def update_cursor(self):
        """Установить курсор в зависимости от текущего инструмента и состояния."""
        mw = self._mw
        if not mw._canvas:
            return
        tool = mw._tool_manager.current_tool
        if tool == ToolTypeEnum.MOVE:
            mw._canvas.setCursor(Qt.CursorShape.OpenHandCursor)
        elif tool == ToolTypeEnum.SELECT and mw._is_selecting:
            mw._canvas.setCursor(Qt.CursorShape.CrossCursor)
        elif tool == ToolTypeEnum.SELECT:
            mw._canvas.setCursor(Qt.CursorShape.PointingHandCursor)
        elif mw._tool_manager.is_drawing_tool:
            mw._canvas.setCursor(Qt.CursorShape.CrossCursor)
        else:
            mw._canvas.setCursor(Qt.CursorShape.ArrowCursor)

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

    def on_canvas_mouse_move(self, event):
        """Обработка движения мыши на холсте."""
        mw = self._mw
        if mw._canvas is None:
            return
        pos = mw._canvas.mapToScene(event.pos())
        mw._last_mouse_pos = pos
        shift_pressed = event.modifiers() & Qt.KeyboardModifier.ShiftModifier

        current_tool = mw._tool_manager.current_tool

        if mw._is_resizing:
            self.handle_resize_move(pos)
        elif current_tool == ToolTypeEnum.SELECT and not mw._is_selecting:
            # Обновляем курсор при наведении на фигуру/ручку
            if mw._manager.selected_shapes:
                for shape in mw._manager.selected_shapes:
                    handle_type = shape.get_handle_type(pos)
                    if handle_type != HandleType.NONE:
                        if handle_type in (
                            HandleType.TOP_LEFT,
                            HandleType.BOTTOM_RIGHT,
                        ):
                            mw._canvas.setCursor(Qt.CursorShape.SizeFDiagCursor)
                        elif handle_type in (
                            HandleType.TOP_RIGHT,
                            HandleType.BOTTOM_LEFT,
                        ):
                            mw._canvas.setCursor(Qt.CursorShape.SizeBDiagCursor)
                        elif handle_type in (
                            HandleType.TOP_CENTER,
                            HandleType.BOTTOM_CENTER,
                        ):
                            mw._canvas.setCursor(Qt.CursorShape.SizeVerCursor)
                        elif handle_type in (
                            HandleType.LEFT_CENTER,
                            HandleType.RIGHT_CENTER,
                        ):
                            mw._canvas.setCursor(Qt.CursorShape.SizeHorCursor)
                        else:
                            mw._canvas.setCursor(Qt.CursorShape.PointingHandCursor)
                        return
            mw._canvas.setCursor(Qt.CursorShape.PointingHandCursor)
        elif current_tool == ToolTypeEnum.SELECT:
            if mw._is_selecting:
                self.update_cursor()
        elif current_tool == ToolTypeEnum.MOVE:
            if mw._is_moving:
                self.handle_move_move(pos)
        elif mw._is_drawing and mw._tool_manager.temp_shape is not None:
            self.continue_drawing(pos, shift_pressed)
        elif current_tool == ToolTypeEnum.ARC:
            pass

    def move_selected_shapes(self, current_pos: QPointF):
        """Перемещение выделенных фигур."""
        mw = self._mw
        if mw._selection_start_pos is None:
            return
        dx = current_pos.x() - mw._selection_start_pos.x()
        dy = current_pos.y() - mw._selection_start_pos.y()

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
        """Обработка отпускания кнопки мыши на холсте."""
        mw = self._mw
        if mw._canvas is None:
            return
        pos = mw._canvas.mapToScene(event.pos())
        shift_pressed = event.modifiers() & Qt.KeyboardModifier.ShiftModifier

        current_tool = mw._tool_manager.current_tool

        if mw._is_resizing:
            self.handle_resize_release()
        elif current_tool == ToolTypeEnum.SELECT:
            if mw._is_selecting:
                self.finish_selection_rectangle()
                self.update_cursor()
        elif current_tool == ToolTypeEnum.MOVE:
            if mw._is_moving:
                self.handle_move_release()
        else:
            if mw._is_drawing:
                self.finish_drawing(pos, shift_pressed)
            mw._is_drawing = False

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
        from shapes.line_shape import LineShape
        from shapes.point_shape import PointShape
        from shapes.polyline_shape import PolylineShape
        from shapes.text_shape import TextShape
        from tools.tool_manager import ToolType

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
            self._show_shape_dialog(current_tool, dialog_pos)
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
            else:
                # Если текст пустой — отменяем создание
                pass

        self.clear_temp_shape()

    def _show_shape_dialog(self, tool_type, pos: QPointF):
        """Показывает диалог ввода параметров и создаёт фигуру."""
        from tools.tool_manager import ToolType
        from ui.shape_dialogs import create_dialog_for_tool

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
            if tool_type in (
                ToolType.TRIANGLE_EQUILATERAL,
                ToolType.TRIANGLE_ISOSCELES,
                ToolType.TRIANGLE_RIGHT,
                ToolType.TRIANGLE_OBTUSE,
            ):
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
        from tools.tool_manager import ToolType

        mw = self._mw
        pen_color = mw._settings.default_pen_color
        pen_width = mw._settings.default_pen_width
        brush_color = mw._settings.default_brush_color

        # Фигуры с вершинами: (build_fn, center_div, type_name, kwargs_fn)
        vertex_shapes: dict[ToolType, tuple] = {
            ToolType.TRIANGLE_EQUILATERAL: (
                lambda p: TriangleShape.build_equilateral(p.get("side_a", 100)),
                3,
                "equilateral",
                lambda p: {"side_a": p.get("side_a", 100)},
            ),
            ToolType.TRIANGLE_ISOSCELES: (
                lambda p: TriangleShape.build_isosceles(
                    p.get("side_a", 150), p.get("height", 86.6)
                ),
                3,
                "isosceles",
                lambda p: {"side_a": p.get("side_a", 150), "height": p.get("height", 86.6)},
            ),
            ToolType.TRIANGLE_RIGHT: (
                lambda p: TriangleShape.build_right(p.get("side_a", 100), p.get("side_b", 100)),
                3,
                "right",
                lambda p: {"side_a": p.get("side_a", 100), "side_b": p.get("side_b", 100)},
            ),
            ToolType.TRIANGLE_OBTUSE: (
                lambda p: TriangleShape.build_obtuse(
                    p.get("side_a", 100), p.get("side_b", 100), p.get("angle_deg", 120)
                ),
                3,
                "obtuse",
                lambda p: {
                    "side_a": p.get("side_a", 100),
                    "side_b": p.get("side_b", 100),
                    "angle_deg": p.get("angle_deg", 120),
                },
            ),
            ToolType.PARALLELOGRAM: (
                lambda p: ParallelogramShape.build(
                    p.get("side_a", 150), p.get("side_b", 100), p.get("angle_deg", 60)
                ),
                4,
                None,
                lambda p: {
                    "side_a": p.get("side_a", 150),
                    "side_b": p.get("side_b", 100),
                    "angle_deg": p.get("angle_deg", 60),
                },
            ),
            ToolType.TRAPEZOID_ISOSCELES: (
                lambda p: TrapezoidShape.build_isosceles(
                    p.get("base_a", 200), p.get("base_b", 100), p.get("angle_deg", 60)
                ),
                4,
                None,
                lambda p: {
                    "base_a": p.get("base_a", 200),
                    "base_b": p.get("base_b", 100),
                    "angle_deg": p.get("angle_deg", 60),
                    "trapezoid_type": "isosceles",
                },
            ),
            ToolType.TRAPEZOID: (
                lambda p: self._build_trapezoid_scalene(p),
                4,
                None,
                lambda p: p,
            ),
        }

        if tool_type in vertex_shapes:
            from shapes.parallelogram_shape import ParallelogramShape
            from shapes.trapezoid_shape import TrapezoidShape
            from shapes.triangle_shape import TriangleShape

            build_fn, center_div, type_name, kwargs_fn = vertex_shapes[tool_type]
            raw = build_fn(params)
            kwargs = kwargs_fn(params)

            if tool_type in (
                ToolType.TRIANGLE_EQUILATERAL,
                ToolType.TRIANGLE_ISOSCELES,
                ToolType.TRIANGLE_RIGHT,
                ToolType.TRIANGLE_OBTUSE,
            ):
                centered = TriangleShape.center_vertices(raw)
                centered = TriangleShape.flip_y(centered)
                centered = TriangleShape.order_vertices_clockwise(centered)
            elif tool_type == ToolType.PARALLELOGRAM:
                centered = ParallelogramShape.center_vertices(raw)
                centered = ParallelogramShape.order_vertices_clockwise(centered)
            else:
                centered = TrapezoidShape.center_vertices(raw)
                centered = TrapezoidShape.order_vertices_clockwise(centered)

            cx = sum(v[0] for v in centered) / center_div
            cy = sum(v[1] for v in centered) / center_div
            offset_x = pos.x() - cx
            offset_y = pos.y() - cy
            vertices = [(v[0] + offset_x, v[1] + offset_y) for v in centered]
            kwargs["vertices"] = vertices
            kwargs["pen_color"] = pen_color
            kwargs["pen_width"] = pen_width
            kwargs["brush_color"] = brush_color
            if type_name is not None:
                kwargs["triangle_type"] = type_name

            if tool_type in (
                ToolType.TRIANGLE_EQUILATERAL,
                ToolType.TRIANGLE_ISOSCELES,
                ToolType.TRIANGLE_RIGHT,
                ToolType.TRIANGLE_OBTUSE,
            ):
                return TriangleShape(**kwargs)
            elif tool_type == ToolType.PARALLELOGRAM:
                return ParallelogramShape(**kwargs)
            else:
                return TrapezoidShape(**kwargs)

        # Простые фигуры без вершин
        if tool_type == ToolType.ARC:
            from shapes.arc_shape import ArcShape

            return ArcShape(
                cx=pos.x(),
                cy=pos.y(),
                radius=params.get("radius", 100),
                start_angle=params.get("start_angle", 0),
                end_angle=params.get("end_angle", 180),
                pen_color=pen_color,
                pen_width=pen_width,
                brush_color=brush_color,
            )

        if tool_type == ToolType.ANGLE:
            from shapes.angle_shape import AngleShape

            return AngleShape(
                vertex=(pos.x(), pos.y()),
                side_a=params.get("side_a", 150),
                side_b=params.get("side_b", 100),
                angle_deg=params.get("angle_deg", 90),
                pen_color=pen_color,
                pen_width=pen_width,
                brush_color=brush_color,
            )

        if tool_type == ToolType.RECTANGLE:
            from shapes.rectangle_shape import RectangleShape

            return RectangleShape(
                x=pos.x(),
                y=pos.y(),
                width=params.get("width", 200),
                height=params.get("height", 150),
                pen_color=pen_color,
                pen_width=pen_width,
                brush_color=brush_color,
            )

        return None

    @staticmethod
    def _build_trapezoid_scalene(params: dict) -> list[tuple[float, float]]:
        """Построить произвольную трапецию с проверкой на равнобедренность."""
        from shapes.trapezoid_shape import TrapezoidShape

        top_width = params.get("top_width", 100)
        bottom_width = params.get("bottom_width", 200)
        height = params.get("height", 100)
        offset_left = params.get("offset_left", 0)

        offset_right = bottom_width - top_width - offset_left
        if abs(offset_left - offset_right) < 1e-6:
            offset_left = (bottom_width - top_width) / 2 + 10
            params["offset_left"] = offset_left

        return TrapezoidShape.build_scalene(top_width, bottom_width, height, offset_left)

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

        self.clear_temp_shape()
        mw._tool_manager.reset_current_shape()
