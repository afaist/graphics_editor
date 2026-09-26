"""Тесты для EventManager — обработка событий мыши и ресайза."""

from unittest.mock import MagicMock

from PySide6.QtCore import QPointF

from shapes.base_shape import HandleType
from shapes.ellipse_shape import EllipseShape


class TestHandleResizePress:
    """Тесты начала масштабирования за ручку."""

    def test_resize_press_detects_handle(self):
        """handle_resize_press должен найти ручку и сохранить handle_type."""
        mw = MagicMock()
        mw._is_resizing = False
        mw._manager.selected_shapes = []

        ellipse = EllipseShape(0, 0, 100, 60)
        ellipse.id = 1
        mw._manager.selected_shapes = [ellipse]

        from ui.window_events import EventManager

        em = EventManager(mw)
        handle_pos = QPointF(0, 0)  # TOP_LEFT corner
        em.handle_resize_press(handle_pos)

        assert mw._is_resizing is True
        assert mw._resize_shape is ellipse
        assert mw._resize_handle_type == HandleType.TOP_LEFT

    def test_resize_press_no_handle(self):
        """handle_resize_press не должен начинать ресайз вне ручки."""
        mw = MagicMock()
        mw._is_resizing = False
        mw._manager.selected_shapes = []

        ellipse = EllipseShape(0, 0, 100, 60)
        mw._manager.selected_shapes = [ellipse]

        from ui.window_events import EventManager

        em = EventManager(mw)
        far_away = QPointF(500, 500)
        em.handle_resize_press(far_away)

        assert mw._is_resizing is False

    def test_resize_press_already_resizing(self):
        """handle_resize_press игнорирует повторное нажатие."""
        mw = MagicMock()
        mw._is_resizing = True

        from ui.window_events import EventManager

        em = EventManager(mw)
        em.handle_resize_press(QPointF(0, 0))

        # Не должно быть изменений
        assert mw._is_resizing is True


class TestHandleResizeMove:
    """Тесты масштабирования за ручку."""

    def test_resize_sticks_to_handle(self):
        """Ресайз должен "запомнить" ручку и не терять её при движении мыши."""
        mw = MagicMock()
        mw._is_resizing = True
        mw._selection_start_pos = QPointF(0, 0)
        mw._resize_handle_type = HandleType.BOTTOM_RIGHT

        ellipse = EllipseShape(0, 0, 100, 60)
        ellipse.id = 1
        mw._resize_shape = ellipse

        mw._manager.shapes_changed.emit = MagicMock()

        from ui.window_events import EventManager

        em = EventManager(mw)
        # Двигаем мышь далеко от исходной ручки
        # dx = 150 - 0 = 150, dy = 120 - 0 = 120
        # width = 100 + 150 = 250, height = 60 + 120 = 180
        em.handle_resize_move(QPointF(150, 120))

        # Ресайз должен продолжаться — width и height изменились
        assert ellipse.width == 250
        assert ellipse.height == 180
        mw._manager.shapes_changed.emit.assert_called_once()

    def test_resize_fails_without_handle_type(self):
        """Если handle_type = NONE, ресайз не должен менять фигуру."""
        mw = MagicMock()
        mw._is_resizing = True
        mw._selection_start_pos = QPointF(0, 0)
        mw._resize_handle_type = HandleType.NONE

        ellipse = EllipseShape(0, 0, 100, 60)
        mw._resize_shape = ellipse
        mock_signal = MagicMock()
        mw._manager.shapes_changed.emit = mock_signal

        from ui.window_events import EventManager

        em = EventManager(mw)
        em.handle_resize_move(QPointF(150, 120))

        # Фигура не изменилась
        assert ellipse.width == 100
        assert ellipse.height == 60

    def test_resize_left_handle_shifts_position(self):
        """Левая ручка должна сдвигать позицию и менять ширину."""
        mw = MagicMock()
        mw._is_resizing = True
        mw._selection_start_pos = QPointF(0, 30)
        mw._resize_handle_type = HandleType.LEFT_CENTER

        ellipse = EllipseShape(0, 0, 100, 60)
        mw._resize_shape = ellipse
        mock_signal = MagicMock()
        mw._manager.shapes_changed.emit = mock_signal

        from ui.window_events import EventManager

        em = EventManager(mw)
        em.handle_resize_move(QPointF(-30, 30))

        assert ellipse.x == -30
        assert ellipse.width == 130

    def test_resize_with_shift(self):
        """Shift+drag должен сохранять пропорции через max(delta)."""
        mw = MagicMock()
        mw._is_resizing = True
        mw._selection_start_pos = QPointF(0, 0)
        mw._resize_handle_type = HandleType.BOTTOM_RIGHT

        ellipse = EllipseShape(0, 0, 100, 60)
        mw._resize_shape = ellipse
        mock_signal = MagicMock()
        mw._manager.shapes_changed.emit = mock_signal

        from ui.window_events import EventManager

        em = EventManager(mw)
        # dx=50, dy=20, shift=True → delta=max(50,20)=50
        em.handle_resize_move(QPointF(50, 20), shift_pressed=True)

        assert ellipse.width == 150
        assert ellipse.height == 110  # 60 + 50


class TestHandleResizeRelease:
    """Тесты завершения масштабирования."""

    def test_resize_release_clears_state(self):
        """handle_resize_release должен сбросить все флаги."""
        mw = MagicMock()
        mw._is_resizing = True
        mw._resize_shape = EllipseShape(0, 0, 100, 60)
        mw._resize_shape.id = 1
        mw._resize_shape_dict = {"x": 0, "y": 0, "width": 100, "height": 60}
        mw._resize_handle_type = HandleType.BOTTOM_RIGHT
        mw._selection_start_pos = QPointF(0, 0)

        mock_undo_stack = MagicMock()
        mw._manager.undo_stack = mock_undo_stack

        from ui.window_events import EventManager

        em = EventManager(mw)
        em.handle_resize_release()

        assert mw._is_resizing is False
        assert mw._resize_shape is None
        assert mw._resize_shape_dict is None
        assert mw._resize_handle_type == HandleType.NONE
        assert mw._selection_start_pos is None
        mock_undo_stack.push.assert_called_once()
