"""Интеграционные тесты UI-потока рисования фигур.

Тестируют полный цикл: press → move → release → фигура на сцене.
В отличие от unit-тестов shape-классов, эти тесты проверяют взаимодействие
менеджеров между собой.
"""

from unittest.mock import MagicMock

from PySide6.QtCore import Qt
from PySide6.QtGui import QMouseEvent

from shapes.base_shape import ShapeType
from shapes.line_shape import LineShape


def _make_mouse_event(pos_x, pos_y, shift=False):
    """Создать мок QMouseEvent."""
    event = MagicMock(spec=QMouseEvent)
    pos = MagicMock()
    pos.x = lambda: pos_x
    pos.y = lambda: pos_y
    event.pos = lambda: pos

    # modifiers() должен возвращать Qt.KeyboardModifiers (Flag enum)
    if shift:
        event.modifiers = lambda: Qt.KeyboardModifier.ShiftModifier
    else:
        event.modifiers = lambda: Qt.KeyboardModifier.NoModifier
    return event


class TestLineDrawingFlow:
    """Тест полного цикла рисования отрезка/луча/прямой."""

    def _create_mw(self):
        """Создать мок MainWindow с минимальной настройкой."""
        mw = MagicMock()
        mw._is_drawing = False
        mw._is_resizing = False
        mw._is_selecting = False
        mw._is_moving = False
        mw._selection_start_pos = None
        mw._resize_shape = None
        mw._resize_shape_dict = None
        mw._resize_handle_type = MagicMock()

        # Менеджер фигур
        mw._manager = MagicMock()
        mw._manager.selected_shapes = []
        mw._manager.selected_ids = set()
        mw._manager.shapes_changed = MagicMock()
        mw._manager.shapes_changed.emit = MagicMock()

        # Undo stack
        mw._manager.undo_stack = MagicMock()

        # Scene
        mw._scene = MagicMock()
        mw._scene.addItem = MagicMock()

        # Tool manager
        mw._tool_manager = MagicMock()
        mw._tool_manager.current_tool = None
        mw._tool_manager.temp_shape = None
        mw._tool_manager.start_shape = MagicMock()
        mw._tool_manager.update_shape = MagicMock()
        mw._tool_manager.finish_shape = MagicMock(return_value=None)
        mw._tool_manager.reset_current_shape = MagicMock()

        # Drawing context
        mw._drawing = MagicMock()
        mw._drawing.is_drawing = False
        mw._drawing.start_point = None

        # Canvas
        mw._canvas = MagicMock()
        from PySide6.QtCore import QPointF

        mw._canvas.mapToScene = lambda p: QPointF(p.x(), p.y())

        # Event manager
        from ui.window_events import EventManager

        mw._event_manager = EventManager(mw)

        return mw

    def test_line_press_starts_drawing(self):
        """Нажатие мыши при активном инструменте LINE должно запустить рисование."""
        mw = self._create_mw()
        from tools.tool_types import ToolType

        mw._tool_manager.current_tool = ToolType.LINE

        # Имитация нажатия
        event = _make_mouse_event(100, 100)

        # start_shape должен быть вызван
        mw._tool_manager.start_shape = MagicMock()
        mw._tool_manager.temp_shape = LineShape(100, 100, 100, 100)

        mw._event_manager.on_canvas_mouse_press(event)

        # _is_drawing должен быть True (это атрибут MainWindow, а не DrawingContext)
        assert mw._is_drawing is True

    def test_line_move_updates_temp_shape(self):
        """Движение мыши должно обновлять временную фигуру."""
        mw = self._create_mw()
        from tools.tool_types import ToolType

        mw._tool_manager.current_tool = ToolType.LINE
        mw._is_drawing = True
        mw._tool_manager.temp_shape = LineShape(100, 100, 100, 100)

        # Имитация движения мыши
        event = _make_mouse_event(150, 150)

        mw._event_manager.on_canvas_mouse_move(event)

        # update_shape должен быть вызван с новой позицией
        mw._tool_manager.update_shape.assert_called()
        call_args = mw._tool_manager.update_shape.call_args
        # Позиция должна быть (150, 150)
        assert call_args[0][0].x() == 150
        assert call_args[0][0].y() == 150

    def test_line_release_finishes_drawing(self):
        """Отпускание мыши должно завершить рисование и добавить фигуру."""
        mw = self._create_mw()
        from tools.tool_types import ToolType

        mw._tool_manager.current_tool = ToolType.LINE
        mw._is_drawing = True

        # Создаём финальную фигуру
        final_shape = LineShape(100, 100, 200, 150)
        mw._tool_manager.finish_shape = MagicMock(return_value=final_shape)

        # Имитация отпускания
        event = _make_mouse_event(200, 150)

        mw._event_manager.on_canvas_mouse_release(event)

        # add_shape должен быть вызван на mw (это MagicMock)
        mw.add_shape.assert_called_with(final_shape)

    def test_line_no_length_check(self):
        """Короткие линии (length < 1) должны добавляться без проверки длины."""
        mw = self._create_mw()
        from tools.tool_types import ToolType

        mw._tool_manager.current_tool = ToolType.LINE
        mw._is_drawing = True

        # Создаём очень короткую линию (длина ~0)
        short_line = LineShape(100, 100, 100.5, 100.5)
        assert short_line.length() < 1.0  # Длина меньше 1 пикселя
        mw._tool_manager.finish_shape = MagicMock(return_value=short_line)

        event = _make_mouse_event(100, 100)

        mw._event_manager.on_canvas_mouse_release(event)

        # Короткая линия должна быть добавлена
        mw.add_shape.assert_called()

    def test_ray_drawing(self):
        """Луч (RAY) должен рисоваться корректно."""
        mw = self._create_mw()
        from tools.tool_types import ToolType

        mw._tool_manager.current_tool = ToolType.RAY
        mw._is_drawing = True

        ray = LineShape(0, 0, 100, 100, shape_type=ShapeType.RAY)
        mw._tool_manager.finish_shape = MagicMock(return_value=ray)

        event = _make_mouse_event(100, 100)

        mw._event_manager.on_canvas_mouse_release(event)

        mw.add_shape.assert_called()
        # Проверяем, что тип фигуры — луч
        called_shape = mw.add_shape.call_args[0][0]
        assert called_shape.shape_type == ShapeType.RAY

    def test_infinite_line_drawing(self):
        """Бесконечная прямая (INFINITE_LINE) должна рисоваться."""
        mw = self._create_mw()
        from tools.tool_types import ToolType

        mw._tool_manager.current_tool = ToolType.INFINITE_LINE
        mw._is_drawing = True

        inf_line = LineShape(0, 0, 50, 50, shape_type=ShapeType.INFINITE_LINE)
        mw._tool_manager.finish_shape = MagicMock(return_value=inf_line)

        event = _make_mouse_event(50, 50)

        mw._event_manager.on_canvas_mouse_release(event)

        mw.add_shape.assert_called()
        called_shape = mw.add_shape.call_args[0][0]
        assert called_shape.shape_type == ShapeType.INFINITE_LINE


class TestTempShapeUpdate:
    """Тесты обновления временных фигур на сцене."""

    def _create_mw(self):
        """Создать мок MainWindow с минимальной настройкой."""
        mw = MagicMock()
        mw._is_drawing = False
        mw._is_resizing = False
        mw._is_selecting = False
        mw._is_moving = False
        mw._selection_start_pos = None
        mw._resize_shape = None
        mw._resize_shape_dict = None
        mw._resize_handle_type = MagicMock()

        mw._manager = MagicMock()
        mw._manager.selected_shapes = []
        mw._manager.selected_ids = set()
        mw._manager.shapes_changed = MagicMock()
        mw._manager.shapes_changed.emit = MagicMock()
        mw._manager.undo_stack = MagicMock()

        mw._scene = MagicMock()
        mw._scene.addItem = MagicMock()

        mw._tool_manager = MagicMock()
        mw._tool_manager.current_tool = None
        mw._tool_manager.temp_shape = None
        mw._tool_manager.start_shape = MagicMock()
        mw._tool_manager.update_shape = MagicMock()
        mw._tool_manager.finish_shape = MagicMock(return_value=None)
        mw._tool_manager.reset_current_shape = MagicMock()

        mw._drawing = MagicMock()
        mw._drawing.is_drawing = False
        mw._drawing.start_point = None

        mw._canvas = MagicMock()
        from PySide6.QtCore import QPointF

        mw._canvas.mapToScene = lambda p: QPointF(p.x(), p.y())

        from ui.window_events import EventManager

        mw._event_manager = EventManager(mw)
        return mw

    def test_update_temp_shape_does_not_remove_existing(self):
        """update_temp_shape должен обновлять существующий item, а не удалять/добавлять."""
        mw = self._create_mw()
        from ui.window_events_drawing import DrawingManager

        dm = DrawingManager(mw)

        # Создаём временную фигуру
        temp_shape = LineShape(0, 0, 100, 100)
        mw._tool_manager.temp_shape = temp_shape

        # Создаём существующий item
        from ui.scene_items import ShapeSceneItem

        existing_item = ShapeSceneItem(temp_shape)
        existing_item.setZValue(1000)

        # Мокаем scene() чтобы возвращал mw._scene
        existing_item.scene = lambda: mw._scene

        mw._scene.addItem = MagicMock()
        mw._scene.removeItem = MagicMock()
        mw._temp_shape_item = existing_item

        # Обновляем фигуру
        new_shape = LineShape(0, 0, 200, 200)
        mw._tool_manager.temp_shape = new_shape

        dm.update_temp_shape()

        # removeItem НЕ должен вызываться — обновляем существующий item
        mw._scene.removeItem.assert_not_called()
        # addItem НЕ должен вызываться — item уже на сцене
        mw._scene.addItem.assert_not_called()

        # Item должен быть обновлён (подготовлен и перерисован)
        assert existing_item._shape is new_shape
