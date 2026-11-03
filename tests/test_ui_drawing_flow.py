"""Интеграционные тесты UI-потока рисования фигур.

Тестируют полный цикл: press → move → release → фигура на сцене.
В отличие от unit-тестов shape-классов, эти тесты проверяют взаимодействие
менеджеров между собой.
"""

from PySide6.QtCore import QPointF, Qt

from shapes.base_shape import ShapeType
from shapes.line_shape import LineShape
from tools.tool_types import ToolType

# ====================================================================
# Простой класс-заглушка вместо unittest.mock.MagicMock
# ====================================================================
# MagicMock вызывает segfault при garbage collection из-за конфликта
# C++/Python garbage collectors в PySide6. Простой класс решает проблему.
# ====================================================================


class _Mock:
    """Простая заглушка вместо MagicMock — без segfault при GC."""

    def __init__(self, return_value=None):
        object.__setattr__(self, "_return_value", return_value)
        object.__setattr__(self, "_call_count", 0)
        object.__setattr__(self, "_call_args", None)
        object.__setattr__(self, "_call_args_list", [])
        object.__setattr__(self, "_side_effect", None)
        object.__setattr__(self, "_attrs", {})

    def __call__(self, *args, **kwargs):
        self._call_count += 1
        self._call_args = (args, kwargs)
        self._call_args_list.append((args, kwargs))
        if self._side_effect is not None:
            if callable(self._side_effect):
                return self._side_effect(*args, **kwargs)
            return self._side_effect
        if self._return_value is not None:
            return self._return_value
        return _Mock()

    def __setattr__(self, name, value):
        if name.startswith("_"):
            object.__setattr__(self, name, value)
        else:
            self._attrs[name] = value

    def __getattr__(self, name):
        if name.startswith("_"):
            raise AttributeError(name)
        # Map public names to private storage
        if name == "call_args":
            return self._call_args
        if name == "call_count":
            return self._call_count
        if name == "call_args_list":
            return self._call_args_list
        if name not in self._attrs:
            self._attrs[name] = _Mock()
        return self._attrs[name]

    def __getitem__(self, key):
        # Support subscripting for call_args[0][0] patterns
        if isinstance(self._call_args, tuple) and isinstance(key, int):
            return self._call_args[key]
        return self._attrs[key]

    def __iter__(self):
        return iter(self._attrs)

    def assert_called(self):
        if self._call_count == 0:
            raise AssertionError("Expected 'call' to have been called.")

    def assert_called_with(self, *args, **kwargs):
        if self._call_count == 0:
            raise AssertionError("Expected 'call' to have been called.")
        last = self._call_args
        # Compare positional args by identity for objects (shapes)
        last_args = last[0]
        if len(last_args) != len(args) or last[1] != kwargs:
            raise AssertionError(
                f"Expected call: args={args}, kwargs={kwargs}\n"
                f"Actual call: args={last_args}, kwargs={last[1]}"
            )
        for i, (expected, actual) in enumerate(zip(args, last_args)):
            if expected is not actual:
                raise AssertionError(
                    f"Expected call: args={args}, kwargs={kwargs}\n"
                    f"Actual call: args={last_args}, kwargs={last[1]}"
                )

    def assert_not_called(self):
        if self._call_count > 0:
            raise AssertionError("Expected 'call' NOT to have been called.")


def _make_mouse_event(pos_x, pos_y, shift=False):
    """Создать мок QMouseEvent без spec, чтобы избежать segfault в PySide6 GC."""
    event = _Mock()
    pos = _Mock()
    pos.x = lambda: pos_x
    pos.y = lambda: pos_y
    event.pos = lambda: pos

    if shift:
        event.modifiers = lambda: Qt.KeyboardModifier.ShiftModifier
    else:
        event.modifiers = lambda: Qt.KeyboardModifier.NoModifier
    return event


class TestLineDrawingFlow:
    """Тест полного цикла рисования отрезка/луча/прямой.

    Тесты вызывают DrawingManager напрямую, так как EventManager.__init__
    создаёт MouseManager/DrawingManager/DialogManager, которые при GC
    вызывают segfault из-за конфликта C++/Python garbage collectors.
    """

    def _create_mw(self):
        """Создать мок MainWindow с минимальной настройкой."""
        mw = _Mock()
        mw._is_drawing = False
        mw._is_resizing = False
        mw._is_selecting = False
        mw._is_moving = False
        mw._selection_start_pos = None
        mw._resize_shape = None
        mw._resize_shape_dict = None
        mw._resize_handle_type = _Mock()

        # Менеджер фигур
        mw._manager = _Mock()
        mw._manager.selected_shapes = []
        mw._manager.selected_ids = set()
        mw._manager.shapes_changed = _Mock()
        mw._manager.shapes_changed.emit = _Mock()

        # Undo stack
        mw._manager.undo_stack = _Mock()

        # Scene
        mw._scene = _Mock()
        mw._scene.addItem = _Mock()

        # Tool manager
        mw._tool_manager = _Mock()
        mw._tool_manager.current_tool = None
        mw._tool_manager.temp_shape = None
        mw._tool_manager.start_shape = _Mock()
        mw._tool_manager.update_shape = _Mock()
        mw._tool_manager.finish_shape = _Mock(return_value=None)
        mw._tool_manager.reset_current_shape = _Mock()

        # Drawing context
        mw._drawing = _Mock()
        mw._drawing.is_drawing = False
        mw._drawing.start_point = None

        # Canvas
        mw._canvas = _Mock()
        mw._canvas.mapToScene = lambda p: QPointF(p.x(), p.y())

        mw._temp_shape_item = None

        return mw
        """Нажатие мыши при активном инструменте LINE должно запустить рисование."""
        mw = self._create_mw()
        from ui.window_events_drawing import DrawingManager

        mw._tool_manager.current_tool = ToolType.LINE

        # start_shape должен быть вызван
        mw._tool_manager.start_shape = _Mock()
        mw._tool_manager.temp_shape = LineShape(100, 100, 100, 100)

        # Создаём DrawingManager и вызываем start_shape напрямую
        dm = DrawingManager(mw)
        dm.start_drawing(QPointF(100, 100), False)

        # _is_drawing должен быть True (это атрибут MainWindow, а не DrawingContext)
        assert mw._is_drawing is True

    def test_line_move_updates_temp_shape(self):
        """Движение мыши должно обновлять временную фигуру."""
        mw = self._create_mw()
        from ui.window_events_drawing import DrawingManager

        mw._tool_manager.current_tool = ToolType.LINE
        mw._is_drawing = True
        mw._tool_manager.temp_shape = LineShape(100, 100, 100, 100)

        # Создаём DrawingManager
        dm = DrawingManager(mw)

        # Имитация движения мыши
        dm.continue_drawing(QPointF(150, 150), False)

        # update_shape должен быть вызван с новой позицией
        mw._tool_manager.update_shape.assert_called()
        call_args = mw._tool_manager.update_shape.call_args
        # Позиция должна быть (150, 150)
        assert call_args[0][0].x() == 150
        assert call_args[0][0].y() == 150

    def test_line_release_finishes_drawing(self):
        """Отпускание мыши должно завершить рисование и добавить фигуру."""
        mw = self._create_mw()
        from ui.window_events_drawing import DrawingManager

        mw._tool_manager.current_tool = ToolType.LINE
        mw._is_drawing = True

        # Создаём финальную фигуру
        final_shape = LineShape(100, 100, 200, 150)
        mw._tool_manager.finish_shape = _Mock(return_value=final_shape)

        # Создаём DrawingManager и вызываем finish_shape напрямую
        dm = DrawingManager(mw)
        dm.finish_drawing(QPointF(200, 150), False)

        # add_shape должен быть вызван на mw (это _Mock)
        mw.add_shape.assert_called_with(final_shape)

    def test_line_no_length_check(self):
        """Короткие линии (length < 1) должны добавляться без проверки длины."""
        mw = self._create_mw()
        from ui.window_events_drawing import DrawingManager

        mw._tool_manager.current_tool = ToolType.LINE
        mw._is_drawing = True

        # Создаём очень короткую линию (длина ~0)
        short_line = LineShape(100, 100, 100.5, 100.5)
        assert short_line.length() < 1.0  # Длина меньше 1 пикселя
        mw._tool_manager.finish_shape = _Mock(return_value=short_line)

        dm = DrawingManager(mw)
        dm.finish_drawing(QPointF(100, 100), False)

        # Короткая линия должна быть добавлена
        mw.add_shape.assert_called()

    def test_ray_drawing(self):
        """Луч (RAY) должен рисоваться корректно."""
        mw = self._create_mw()
        from ui.window_events_drawing import DrawingManager

        mw._tool_manager.current_tool = ToolType.RAY
        mw._is_drawing = True

        ray = LineShape(0, 0, 100, 100, shape_type=ShapeType.RAY)
        mw._tool_manager.finish_shape = _Mock(return_value=ray)

        dm = DrawingManager(mw)
        dm.finish_drawing(QPointF(100, 100), False)

        mw.add_shape.assert_called()
        # Проверяем, что тип фигуры — луч
        called_shape = mw.add_shape.call_args[0][0]
        assert called_shape.shape_type == ShapeType.RAY

    def test_infinite_line_drawing(self):
        """Бесконечная прямая (INFINITE_LINE) должна рисоваться."""
        mw = self._create_mw()
        from ui.window_events_drawing import DrawingManager

        mw._tool_manager.current_tool = ToolType.INFINITE_LINE
        mw._is_drawing = True

        inf_line = LineShape(0, 0, 50, 50, shape_type=ShapeType.INFINITE_LINE)
        mw._tool_manager.finish_shape = _Mock(return_value=inf_line)

        dm = DrawingManager(mw)
        dm.finish_drawing(QPointF(50, 50), False)

        mw.add_shape.assert_called()
        called_shape = mw.add_shape.call_args[0][0]
        assert called_shape.shape_type == ShapeType.INFINITE_LINE


class TestTempShapeUpdate:
    """Тесты обновления временных фигур на сцене."""

    def _create_mw(self):
        """Создать мок MainWindow с минимальной настройкой."""
        mw = _Mock()
        mw._is_drawing = False
        mw._is_resizing = False
        mw._is_selecting = False
        mw._is_moving = False
        mw._selection_start_pos = None
        mw._resize_shape = None
        mw._resize_shape_dict = None
        mw._resize_handle_type = _Mock()

        mw._manager = _Mock()
        mw._manager.selected_shapes = []
        mw._manager.selected_ids = set()
        mw._manager.shapes_changed = _Mock()
        mw._manager.shapes_changed.emit = _Mock()

        mw._manager.undo_stack = _Mock()

        mw._scene = _Mock()
        mw._scene.addItem = _Mock()
        mw._scene.removeItem = _Mock()

        mw._tool_manager = _Mock()
        mw._tool_manager.current_tool = None
        mw._tool_manager.temp_shape = None
        mw._tool_manager.start_shape = _Mock()
        mw._tool_manager.update_shape = _Mock()
        mw._tool_manager.finish_shape = _Mock(return_value=None)
        mw._tool_manager.reset_current_shape = _Mock()

        mw._drawing = _Mock()
        mw._drawing.is_drawing = False
        mw._drawing.start_point = None

        mw._canvas = _Mock()
        mw._canvas.mapToScene = lambda p: QPointF(p.x(), p.y())

        mw._temp_shape_item = None

        return mw

    def test_update_temp_shape_does_not_remove_existing(self):
        """update_temp_shape должен обновлять существующий item, а не удалять/добавлять.

        При отсутствии существующего элемента addItem вызывается (создание нового).
        При наличии существующего элемента ни addItem, ни removeItem не вызываются.
        """
        mw = self._create_mw()
        from ui.window_events_drawing import DrawingManager

        mw._tool_manager.current_tool = None
        mw._is_drawing = True

        # Создаём временную фигуру
        temp_shape = LineShape(100, 100, 100, 100)
        mw._tool_manager.temp_shape = temp_shape

        # Создаём DrawingManager с моком
        dm = DrawingManager(mw)

        # Вызываем update_temp_shape
        dm.update_temp_shape()

        # removeItem НЕ должен вызываться (нет существующего элемента для удаления)
        mw._scene.removeItem.assert_not_called()
        # addItem вызывается, т.к. элемента ещё нет на сцене
        mw._scene.addItem.assert_called()
