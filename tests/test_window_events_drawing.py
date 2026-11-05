"""Тесты для DrawingManager: start_drawing, finish_drawing, clear_temp_shape."""

from PySide6.QtCore import QPointF

from tools.tool_types import ToolType as ToolTypeEnum
from ui.window_events_drawing import (
    COMPOSED_FINISH_TOOLS,
    GEOMETRY_DIALOG_TOOLS,
    GEOMETRY_FINISH_TOOLS,
    START_POINT_DIALOG_TOOLS,
    DrawingManager,
)


class TestConstants:
    """Тесты модульных констант."""

    def test_geometry_dialog_tools_contains_arc(self):
        assert ToolTypeEnum.ARC in GEOMETRY_DIALOG_TOOLS

    def test_geometry_dialog_tools_contains_angle(self):
        assert ToolTypeEnum.ANGLE in GEOMETRY_DIALOG_TOOLS

    def test_geometry_dialog_tools_contains_rectangle(self):
        assert ToolTypeEnum.RECTANGLE not in GEOMETRY_DIALOG_TOOLS

    def test_geometry_finish_tools_contains_rectangle(self):
        assert ToolTypeEnum.RECTANGLE in GEOMETRY_FINISH_TOOLS

    def test_geometry_finish_tools_contains_arc(self):
        assert ToolTypeEnum.ARC in GEOMETRY_FINISH_TOOLS

    def test_composed_finish_tools_contains_polygon(self):
        assert ToolTypeEnum.POLYGON in COMPOSED_FINISH_TOOLS

    def test_composed_finish_tools_contains_polyline(self):
        assert ToolTypeEnum.POLYLINE in COMPOSED_FINISH_TOOLS

    def test_composed_finish_tools_contains_graph_linear(self):
        assert ToolTypeEnum.GRAPH_LINEAR in COMPOSED_FINISH_TOOLS

    def test_composed_finish_tools_does_not_contain_circle(self):
        assert ToolTypeEnum.CIRCLE not in COMPOSED_FINISH_TOOLS

    def test_start_point_dialog_tools_contains_arc(self):
        assert ToolTypeEnum.ARC in START_POINT_DIALOG_TOOLS

    def test_start_point_dialog_tools_contains_rectangle(self):
        assert ToolTypeEnum.RECTANGLE not in START_POINT_DIALOG_TOOLS

    def test_all_constants_are_frozensets(self):
        assert isinstance(GEOMETRY_DIALOG_TOOLS, frozenset)
        assert isinstance(GEOMETRY_FINISH_TOOLS, frozenset)
        assert isinstance(COMPOSED_FINISH_TOOLS, frozenset)
        assert isinstance(START_POINT_DIALOG_TOOLS, frozenset)

    def test_constants_are_not_empty(self):
        assert len(GEOMETRY_DIALOG_TOOLS) > 0
        assert len(GEOMETRY_FINISH_TOOLS) > 0
        assert len(COMPOSED_FINISH_TOOLS) > 0
        assert len(START_POINT_DIALOG_TOOLS) > 0


class MockCanvas:
    """Mock canvas для тестов."""

    def __init__(self):
        self.last_cursor = None

    def mapToScene(self, pos):
        return pos

    def setCursor(self, cursor):
        self.last_cursor = cursor


class MockToolManager:
    """Mock ToolManager для тестов."""

    def __init__(self):
        self._current_tool = ToolTypeEnum.SELECT
        self._temp_shape = None

    @property
    def current_tool(self):
        return self._current_tool

    @current_tool.setter
    def current_tool(self, value):
        self._current_tool = value

    @property
    def temp_shape(self):
        return self._temp_shape

    def start_shape(self, pos, settings):
        pass

    def update_shape(self, pos, shift_pressed):
        pass

    def finish_shape(self, pos):
        return None

    def finish_current_shape(self, settings):
        return None

    def reset_current_shape(self):
        pass

    @property
    def is_drawing_tool(self):
        return True


class MockEventManager:
    """Mock EventManager для тестов."""

    def __init__(self):
        self._dialogs = MockDialogs()
        self._drawing = MockDrawing()

    def clear_temp_shape(self):
        pass


class MockDialogs:
    """Mock Dialogs для тестов."""

    def show_shape_dialog(self, tool_type, pos):
        pass


class MockDrawing:
    """Mock Drawing для тестов."""

    def clear_temp_shape(self):
        pass


class MockUndoStack:
    """Mock UndoStack для тестов."""

    def push(self, cmd):
        pass

    def setClean(self):
        pass


class MockManager:
    """Mock ShapeManager для тестов."""

    def __init__(self):
        self.shapes = []
        self._selected_ids = set()
        self.undo_stack = MockUndoStack()

    @property
    def selected_ids(self):
        return self._selected_ids

    @property
    def selected_shapes(self):
        return self.shapes

    def select_shape(self, id_, additive=False):
        self._selected_ids.add(id_)

    def select_all(self):
        pass

    def select_none(self):
        self._selected_ids.clear()

    def select_by_rect(self, rect, additive=False):
        pass

    def move_selected(self, dx, dy):
        pass

    def has_shape(self, id_):
        return True

    def hit_test(self, pos):
        return None

    def get_shape_by_id(self, id_):
        return None

    def copy_selected(self):
        pass

    def cut_selected(self):
        pass

    def paste_clipboard(self):
        pass

    def group_selected(self):
        pass

    def ungroup_selected(self):
        pass

    def duplicate_selected(self):
        pass

    def bring_forward(self):
        pass

    def send_backward(self):
        pass

    def bring_to_front(self):
        pass

    def send_to_back(self):
        pass

    def shapes_changed(self):
        pass

    selection_changed = shapes_changed


class MockMainWindow:
    """Mock MainWindow для тестов."""

    def __init__(self):
        self._canvas = MockCanvas()
        self._tool_manager = MockToolManager()
        self._manager = MockManager()
        self._event_manager = MockEventManager()
        self._settings = MockSettings()
        self._is_drawing = False
        self._is_dragging = False
        self._is_selecting = False
        self._is_moving = False
        self._is_resizing = False
        self._start_point = None
        self._last_mouse_pos = None
        self._selection_start_pos = None
        self._selection_rect_start = None
        self._temp_shape_item = None
        self._undo_stack = MockUndoStack()
        self._drawing_properties = MockDrawingProperties()
        self._resize_shape = None
        self._resize_shape_dict = None
        self._resize_handle_type = None
        self._drawing = MockDrawingContext()

    def add_shape(self, shape):
        pass

    def _update_statusbar(self):
        pass


class MockSettings:
    """Mock Settings для тестов."""

    default_pen_color = (0, 0, 0)
    default_pen_width = 2.0
    default_brush_color = None


class MockDrawingProperties:
    """Mock DrawingProperties для тестов."""

    def __init__(self):
        self.move_old_positions = {}
        self.move_accumulated_dx = 0.0
        self.move_accumulated_dy = 0.0

    def reset_drawing_state(self):
        pass


class MockDrawingContext:
    """Mock DrawingContext для тестов."""

    is_drawing = False
    is_dragging = False
    is_selecting = False
    is_moving = False
    is_resizing = False
    resize_shape = None
    resize_shape_dict = None
    resize_handle_type = None
    start_point = None
    last_mouse_pos = None
    selection_start_pos = None
    selection_rect_start = None
    temp_shape_item = None
    move_old_positions = {}
    move_accumulated_dx = 0.0
    move_accumulated_dy = 0.0

    def reset_drawing(self):
        pass


class TestDrawingManager:
    """Тесты DrawingManager."""

    def test_start_drawing_geometry_tool(self):
        mw = MockMainWindow()
        mw._tool_manager.current_tool = ToolTypeEnum.ARC
        dm = DrawingManager(mw)
        dm.start_drawing(QPointF(100, 100), False)
        assert mw._is_drawing is True
        assert mw._start_point == QPointF(100, 100)

    def test_start_drawing_normal_tool(self):
        mw = MockMainWindow()
        mw._tool_manager.current_tool = ToolTypeEnum.LINE
        dm = DrawingManager(mw)
        dm.start_drawing(QPointF(100, 100), False)
        assert mw._is_drawing is True

    def test_start_drawing_circle(self):
        mw = MockMainWindow()
        mw._tool_manager.current_tool = ToolTypeEnum.CIRCLE
        dm = DrawingManager(mw)
        dm.start_drawing(QPointF(100, 100), False)
        assert mw._is_drawing is True

    def test_clear_temp_shape_no_item(self):
        mw = MockMainWindow()
        mw._temp_shape_item = None
        dm = DrawingManager(mw)
        dm.clear_temp_shape()
        # Не должно вызвать ошибку

    def test_clear_temp_shape_with_item(self):
        mw = MockMainWindow()
        mw._scene = None
        item = MockTempItem()
        mw._temp_shape_item = item
        dm = DrawingManager(mw)
        dm.clear_temp_shape()
        assert mw._temp_shape_item is None

    def test_reset_drawing_state(self):
        mw = MockMainWindow()
        mw._is_drawing = True
        mw._is_dragging = True
        mw._is_selecting = True
        dm = DrawingManager(mw)
        dm.reset_drawing_state()
        assert mw._is_drawing is False
        assert mw._is_dragging is False
        assert mw._is_selecting is False
        assert mw._is_moving is False
        assert mw._is_resizing is False


class MockTempItem:
    """Mock QGraphicsItem для тестов."""

    def scene(self):
        return None


class TestFinishDrawing:
    """Тесты finish_drawing."""

    def test_finish_drawing_geometry_tool(self):
        mw = MockMainWindow()
        mw._tool_manager.current_tool = ToolTypeEnum.RECTANGLE
        mw._start_point = QPointF(50, 50)
        dm = DrawingManager(mw)
        dm.finish_drawing(QPointF(100, 100), False)
        assert mw._is_drawing is False

    def test_finish_drawing_arc(self):
        mw = MockMainWindow()
        mw._tool_manager.current_tool = ToolTypeEnum.ARC
        mw._start_point = QPointF(50, 50)
        dm = DrawingManager(mw)
        dm.finish_drawing(QPointF(100, 100), False)
        assert mw._is_drawing is False

    def test_finish_drawing_polygon(self):
        mw = MockMainWindow()
        mw._tool_manager.current_tool = ToolTypeEnum.POLYGON
        dm = DrawingManager(mw)
        dm.finish_drawing(QPointF(100, 100), False)
        assert mw._is_drawing is False
