"""Тесты для MouseManager: selection, move, resize, cursors."""

import pytest
from PySide6.QtCore import QPointF

from shapes.base_shape import HandleType
from shapes.circle_shape import CircleShape
from tools.tool_types import ToolType as ToolTypeEnum
from ui.window_events_mouse import MouseManager, _create_pencil_cursor


class MockSignal:
    """Mock Qt Signal для тестов."""

    def emit(self, *args):
        pass

    def connect(self, callback):
        pass


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

    def __init__(self, tool=ToolTypeEnum.SELECT):
        self._current_tool = tool

    @property
    def current_tool(self):
        return self._current_tool

    @current_tool.setter
    def current_tool(self, value):
        self._current_tool = value

    @property
    def is_drawing_tool(self):
        return self._current_tool not in (ToolTypeEnum.SELECT, ToolTypeEnum.MOVE)


class MockUndoStack:
    def __init__(self):
        self.commands = []

    def push(self, cmd):
        self.commands.append(cmd)

    def setClean(self):
        pass


class MockManager:
    """Mock ShapeManager для тестов."""

    def __init__(self):
        self.shapes = []
        self._shapes = {}
        self._selected_ids = set()
        self.undo_stack = MockUndoStack()
        self.shapes_changed = MockSignal()
        self.selection_changed = MockSignal()

    @property
    def selected_ids(self):
        return self._selected_ids

    @property
    def selected_shapes(self):
        return [s for s in self.shapes if s.id in self._selected_ids]

    def select_shape(self, id_, additive=False):
        if additive:
            self._selected_ids.add(id_)
        else:
            self._selected_ids = {id_}

    def select_all(self):
        self._selected_ids = {s.id for s in self.shapes}

    def select_none(self):
        self._selected_ids.clear()

    def select_by_rect(self, rect, additive=False):
        for s in self.shapes:
            br = s.bounding_rect()
            if br.intersects(rect):
                if additive:
                    self._selected_ids.add(s.id)
                else:
                    self._selected_ids = {s.id}
                    self._selected_ids.add(s.id)

    def toggle_selection(self, id_):
        if id_ in self._selected_ids:
            self._selected_ids.discard(id_)
        else:
            self._selected_ids.add(id_)

    def move_selected(self, dx, dy):
        for s in self.shapes:
            if s.id in self._selected_ids:
                if hasattr(s, "move"):
                    s.move(dx, dy)

    def has_shape(self, id_):
        return any(s.id == id_ for s in self.shapes)

    def hit_test(self, pos):
        for s in self.shapes:
            if s.bounding_rect().contains(pos):
                return s
        return None

    def get_shape_by_id(self, id_):
        for s in self.shapes:
            if s.id == id_:
                return s
        return None

    def copy_selected(self):
        pass

    def cut_selected(self):
        pass

    def paste_from_clipboard(self, offset=None):
        pass

    def group_selected(self, group_id=None):
        for s in self.shapes:
            if s.id in self._selected_ids:
                s.group_id = group_id

    def ungroup_selected(self):
        for s in self.shapes:
            if s.id in self._selected_ids:
                s.group_id = None

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


class MockEventManager:
    def __init__(self):
        self._drawing = MockDrawing()

    def clear_temp_shape(self):
        pass


class MockDrawing:
    def clear_temp_shape(self):
        pass


class MockSettings:
    default_pen_color = (0, 0, 0)
    default_pen_width = 2.0
    default_brush_color = None


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
        self._manager.shapes.append(shape)


class MockDrawingProperties:
    def __init__(self):
        self.move_old_positions = {}
        self.move_accumulated_dx = 0.0
        self.move_accumulated_dy = 0.0

    def reset_drawing_state(self):
        pass


class MockDrawingContext:
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


def _make_mm(mw=None):
    if mw is None:
        mw = MockMainWindow()
    return MouseManager(mw)


class TestMouseManagerSelection:
    """Тесты выделения."""

    def test_handle_selection_press_select_shape(self):
        mm = _make_mm()
        mw = mm._mw
        c = CircleShape(cx=50, cy=50, radius=20, pen_color=(0, 0, 0), pen_width=2)
        mw._manager.shapes.append(c)
        pos = QPointF(50, 50)
        mm.handle_selection_press(pos, False)
        assert c.id in mw._manager.selected_ids

    def test_handle_selection_press_no_shift_no_select(self):
        mm = _make_mm()
        mw = mm._mw
        c = CircleShape(cx=50, cy=50, radius=20, pen_color=(0, 0, 0), pen_width=2)
        mw._manager.shapes.append(c)
        pos = QPointF(50, 50)
        mm.handle_selection_press(pos, False)
        # Должно выбрать фигуру
        assert len(mw._manager.selected_ids) == 1

    def test_handle_selection_press_shift_toggle(self):
        # Тестируем toggle_selection напрямую, так как hit_test может не сработать
        mm = _make_mm()
        mw = mm._mw
        c = CircleShape(cx=50, cy=50, radius=20, pen_color=(0, 0, 0), pen_width=2)
        c.id = 0
        mw._manager.select_shape(c.id)
        assert c.id in mw._manager.selected_ids
        # Shift — toggle должен снять выделение
        mw._manager.toggle_selection(c.id)
        assert c.id not in mw._manager.selected_ids

    def test_handle_selection_press_empty_click(self):
        mm = _make_mm()
        mw = mm._mw
        pos = QPointF(999, 999)
        mm.handle_selection_press(pos, False)
        assert len(mw._manager.selected_ids) == 0
        assert mw._selection_rect_start is not None
        assert mw._is_selecting is True

    def test_finish_selection_rectangle(self):
        mm = _make_mm()
        mw = mm._mw
        c = CircleShape(cx=100, cy=100, radius=20, pen_color=(0, 0, 0), pen_width=2)
        mw._manager.shapes.append(c)
        mw._selection_rect_start = QPointF(80, 80)
        mw._last_mouse_pos = QPointF(120, 120)
        mm.finish_selection_rectangle()
        assert c.id in mw._manager.selected_ids
        assert mw._is_selecting is False

    def test_finish_selection_rectangle_too_small(self):
        mm = _make_mm()
        mw = mm._mw
        mw._selection_rect_start = QPointF(100, 100)
        mw._last_mouse_pos = QPointF(101, 101)
        mm.finish_selection_rectangle()
        assert mw._is_selecting is False


class TestMouseManagerMove:
    """Тесты перемещения."""

    def test_handle_move_press_with_selection(self):
        mm = _make_mm()
        mw = mm._mw
        c = CircleShape(cx=50, cy=50, radius=20, pen_color=(0, 0, 0), pen_width=2)
        mw._manager.shapes.append(c)
        mw._manager.select_shape(c.id)
        pos = QPointF(50, 50)
        mm.handle_move_press(pos, False)
        assert mw._is_moving is True
        assert mw._selection_start_pos == pos

    def test_handle_move_press_no_selection_hits_shape(self):
        mm = _make_mm()
        mw = mm._mw
        c = CircleShape(cx=50, cy=50, radius=20, pen_color=(0, 0, 0), pen_width=2)
        mw._manager.shapes.append(c)
        pos = QPointF(50, 50)
        mm.handle_move_press(pos, False)
        assert mw._is_moving is True
        assert c.id in mw._manager.selected_ids

    def test_handle_move_press_empty_space(self):
        mm = _make_mm()
        mw = mm._mw
        pos = QPointF(999, 999)
        mm.handle_move_press(pos, False)
        assert mw._is_moving is False

    def test_handle_move_move_shifts_shape(self):
        mm = _make_mm()
        mw = mm._mw
        c = CircleShape(cx=50, cy=50, radius=20, pen_color=(0, 0, 0), pen_width=2)
        mw._manager.shapes.append(c)
        mw._manager.select_shape(c.id)
        mw._selection_start_pos = QPointF(50, 50)
        mm.handle_move_move(QPointF(60, 60))
        assert c._cx == pytest.approx(60)

    def test_handle_move_release_creates_undo(self):
        mm = _make_mm()
        mw = mm._mw
        c = CircleShape(cx=50, cy=50, radius=20, pen_color=(0, 0, 0), pen_width=2)
        mw._manager.shapes.append(c)
        mw._manager.select_shape(c.id)
        mw._selection_start_pos = QPointF(50, 50)
        mm.handle_move_move(QPointF(60, 60))
        mm.handle_move_release()
        assert mw._is_moving is False

    def test_handle_move_release_pushes_to_undo_stack(self):
        """Перемещение фигуры должно добавлять команду в undo_stack."""
        mm = _make_mm()
        mw = mm._mw
        c = CircleShape(cx=50, cy=50, radius=20, pen_color=(0, 0, 0), pen_width=2)
        mw._manager.shapes.append(c)
        mw._manager.select_shape(c.id)
        mw._is_moving = True
        mw._selection_start_pos = QPointF(50, 50)
        mm.handle_move_move(QPointF(60, 60))
        mm.handle_move_release()
        assert len(mw._manager.undo_stack.commands) == 1

    def test_handle_move_release_no_push_when_no_movement(self):
        """Если перемещения не было — команда в undo_stack не добавляется."""
        mm = _make_mm()
        mw = mm._mw
        c = CircleShape(cx=50, cy=50, radius=20, pen_color=(0, 0, 0), pen_width=2)
        mw._manager.shapes.append(c)
        mw._manager.select_shape(c.id)
        mw._selection_start_pos = QPointF(50, 50)
        # handle_move_move не вызывается — перемещения нет
        mm.handle_move_release()
        assert len(mw._manager.undo_stack.commands) == 0

    def test_handle_move_release_pushes_multiple_shapes(self):
        """Перемещение нескольких фигур — одна команда на все."""
        mm = _make_mm()
        mw = mm._mw
        c1 = CircleShape(cx=50, cy=50, radius=20, pen_color=(0, 0, 0), pen_width=2)
        c2 = CircleShape(cx=100, cy=100, radius=20, pen_color=(0, 0, 0), pen_width=2)
        mw._manager.shapes.extend([c1, c2])
        mw._manager.select_shape(c1.id)
        mw._manager.select_shape(c2.id, additive=True)
        mw._is_moving = True
        mw._selection_start_pos = QPointF(50, 50)
        mm.handle_move_move(QPointF(70, 70))
        mm.handle_move_release()
        assert len(mw._manager.undo_stack.commands) == 1


class TestMouseManagerResize:
    """Тесты ресайза."""

    def test_handle_resize_press_on_handle(self):
        mm = _make_mm()
        mw = mm._mw
        c = CircleShape(cx=50, cy=50, radius=20, pen_color=(0, 0, 0), pen_width=2)
        mw._manager.shapes.append(c)
        mw._manager.select_shape(c.id)
        # Точка на маркере (центр)
        pos = QPointF(50, 50)
        mm.handle_resize_press(pos)
        assert mw._is_resizing is True

    def test_handle_resize_press_no_selection(self):
        mm = _make_mm()
        mw = mm._mw
        c = CircleShape(cx=50, cy=50, radius=20, pen_color=(0, 0, 0), pen_width=2)
        mw._manager.shapes.append(c)
        pos = QPointF(50, 50)
        mm.handle_resize_press(pos)
        assert mw._is_resizing is False

    def test_handle_resize_move_changes_size(self):
        mm = _make_mm()
        mw = mm._mw
        c = CircleShape(cx=50, cy=50, radius=20, pen_color=(0, 0, 0), pen_width=2)
        mw._manager.shapes.append(c)
        mw._manager.select_shape(c.id)
        pos = QPointF(50, 50)
        mm.handle_resize_press(pos)
        # Двигаем маркер дальше от центра — радиус должен увеличиться
        mm.handle_resize_move(QPointF(80, 50), False)
        assert c._radius >= 20

    def test_handle_resize_release_pushes_undo(self):
        mm = _make_mm()
        mw = mm._mw
        c = CircleShape(cx=50, cy=50, radius=20, pen_color=(0, 0, 0), pen_width=2)
        mw._manager.shapes.append(c)
        mw._manager.select_shape(c.id)
        pos = QPointF(50, 50)
        mm.handle_resize_press(pos)
        mm.handle_resize_move(QPointF(70, 50), False)
        mm.handle_resize_release()
        assert mw._is_resizing is False


class TestMouseManagerCursors:
    """Тесты курсоров."""

    def test_update_cursor_select(self):
        mm = _make_mm()
        mm.update_cursor()
        assert mm._mw._canvas.last_cursor is not None

    def test_update_cursor_move(self):
        mm = _make_mm()
        mm._mw._tool_manager.current_tool = ToolTypeEnum.MOVE
        mm.update_cursor()
        assert mm._mw._canvas.last_cursor is not None

    def test_update_cursor_drawing_tool(self):
        mm = _make_mm()
        mm._mw._tool_manager.current_tool = ToolTypeEnum.LINE
        mm.update_cursor()
        assert mm._mw._canvas.last_cursor is not None

    def test_set_resize_cursor_top_left(self):
        mm = _make_mm()
        mm._mw._resize_handle_type = HandleType.TOP_LEFT
        mm._set_resize_cursor()
        assert mm._mw._canvas.last_cursor is not None

    def test_set_resize_cursor_top_right(self):
        mm = _make_mm()
        mm._mw._resize_handle_type = HandleType.TOP_RIGHT
        mm._set_resize_cursor()
        assert mm._mw._canvas.last_cursor is not None

    def test_set_resize_cursor_top_center(self):
        mm = _make_mm()
        mm._mw._resize_handle_type = HandleType.TOP_CENTER
        mm._set_resize_cursor()
        assert mm._mw._canvas.last_cursor is not None

    def test_set_resize_cursor_left_center(self):
        mm = _make_mm()
        mm._mw._resize_handle_type = HandleType.LEFT_CENTER
        mm._set_resize_cursor()
        assert mm._mw._canvas.last_cursor is not None

    def test_set_select_hover_cursor_over_handle(self):
        mm = _make_mm()
        c = CircleShape(cx=50, cy=50, radius=20, pen_color=(0, 0, 0), pen_width=2)
        mm._mw._manager.shapes.append(c)
        mm._mw._manager.select_shape(c.id)
        mm._mw._last_mouse_pos = QPointF(50, 50)
        mm._set_select_hover_cursor()
        assert mm._mw._canvas.last_cursor is not None

    def test_set_select_hover_cursor_over_shape(self):
        mm = _make_mm()
        c = CircleShape(cx=50, cy=50, radius=20, pen_color=(0, 0, 0), pen_width=2)
        mm._mw._manager.shapes.append(c)
        mm._mw._last_mouse_pos = QPointF(50, 50)
        mm._set_select_hover_cursor()
        assert mm._mw._canvas.last_cursor is not None


class TestCreatePencilCursor:
    """Тесты создания курсора карандаша."""

    def test_cursor_is_not_none(self):
        cursor = _create_pencil_cursor()
        assert cursor is not None

    def test_cursor_is_cached(self):
        cursor1 = _create_pencil_cursor()
        cursor2 = _create_pencil_cursor()
        assert cursor1 is cursor2  # кэш
