"""Тесты для ShapeManager: select_by_rect, move_selected, cut/copy/paste, group/ungroup."""

import pytest
from PySide6.QtCore import QRectF

from manager.shape_manager import ShapeManager
from shapes.circle_shape import CircleShape
from shapes.rectangle_shape import RectangleShape


class TestShapeManagerSelectByRect:
    """Тесты выделения по прямоугольнику."""

    def _make_manager(self):
        mgr = ShapeManager()
        # Добавляем несколько фигур
        c1 = CircleShape(cx=50, cy=50, radius=20, pen_color=(0, 0, 0), pen_width=2)
        c2 = CircleShape(cx=200, cy=200, radius=20, pen_color=(0, 0, 0), pen_width=2)
        r1 = RectangleShape(x=100, y=100, width=50, height=50, pen_color=(0, 0, 0), pen_width=2)
        mgr.add_shape(c1)
        mgr.add_shape(c2)
        mgr.add_shape(r1)
        return mgr

    def test_select_by_rect_single_shape(self):
        mgr = self._make_manager()
        rect = QRectF(40, 40, 30, 30)
        mgr.select_by_rect(rect)
        assert len(mgr.selected_ids) == 1

    def test_select_by_rect_no_shapes(self):
        mgr = self._make_manager()
        rect = QRectF(999, 999, 10, 10)
        mgr.select_by_rect(rect)
        assert len(mgr.selected_ids) == 0

    def test_select_by_rect_additive(self):
        mgr = self._make_manager()
        mgr.select_shape(0)  # выделяем первую
        rect = QRectF(40, 40, 30, 30)
        mgr.select_by_rect(rect)
        # Должно добавить к существующему выделению
        assert len(mgr.selected_ids) >= 1

    def test_select_by_rect_non_additive(self):
        mgr = self._make_manager()
        mgr.select_shape(0)
        assert 0 in mgr.selected_ids
        rect = QRectF(190, 190, 30, 30)
        mgr.select_by_rect(rect)
        # select_by_rect заменяет выделение
        assert 0 not in mgr.selected_ids


class TestShapeManagerMoveSelected:
    """Тесты перемещения выделенных фигур."""

    def _make_manager(self):
        mgr = ShapeManager()
        c1 = CircleShape(cx=50, cy=50, radius=20, pen_color=(0, 0, 0), pen_width=2)
        c2 = CircleShape(cx=100, cy=100, radius=20, pen_color=(0, 0, 0), pen_width=2)
        mgr.add_shape(c1)
        mgr.add_shape(c2)
        mgr.select_shape(0)
        mgr.select_shape(1, additive=True)
        return mgr

    def test_move_selected_shifts_all(self):
        mgr = self._make_manager()
        mgr.move_selected(10, 20)
        shapes = mgr.shapes
        assert shapes[0]._cx == pytest.approx(60)
        assert shapes[0]._cy == pytest.approx(70)
        assert shapes[1]._cx == pytest.approx(110)
        assert shapes[1]._cy == pytest.approx(120)

    def test_move_selected_no_selection(self):
        mgr = ShapeManager()
        c = CircleShape(cx=50, cy=50, radius=20, pen_color=(0, 0, 0), pen_width=2)
        mgr.add_shape(c)
        mgr.move_selected(10, 20)
        # Без выделения — ничего не должно произойти
        assert c._cx == 50

    def test_move_selected_emits_signal(self):
        mgr = self._make_manager()
        emitted = []
        mgr.shapes_changed.connect(lambda: emitted.append(True))
        mgr.move_selected(10, 20)
        assert len(emitted) > 0


class TestShapeManagerCutCopyPaste:
    """Тесты cut, copy, paste."""

    def _make_manager(self):
        mgr = ShapeManager()
        c1 = CircleShape(cx=50, cy=50, radius=20, pen_color=(0, 0, 0), pen_width=2)
        c2 = CircleShape(cx=100, cy=100, radius=20, pen_color=(0, 0, 0), pen_width=2)
        mgr.add_shape(c1)
        mgr.add_shape(c2)
        mgr.select_shape(0)
        return mgr

    def test_copy_copies_data(self):
        mgr = self._make_manager()
        mgr.copy_selected()
        assert mgr._clipboard is not None
        assert len(mgr._clipboard) > 0

    def test_copy_no_selection(self):
        mgr = ShapeManager()
        c = CircleShape(cx=50, cy=50, radius=20, pen_color=(0, 0, 0), pen_width=2)
        mgr.add_shape(c)
        mgr.copy_selected()
        # clipboard пустой (не None)
        assert mgr._clipboard == []

    def test_cut_removes_and_copies(self):
        mgr = self._make_manager()
        initial_count = mgr.count
        mgr.cut_selected()
        assert mgr.count == initial_count - 1
        assert mgr._clipboard is not None

    def test_cut_no_selection(self):
        mgr = ShapeManager()
        c = CircleShape(cx=50, cy=50, radius=20, pen_color=(0, 0, 0), pen_width=2)
        mgr.add_shape(c)
        initial_count = mgr.count
        mgr.cut_selected()
        assert mgr.count == initial_count

    def test_paste_with_clipboard(self):
        mgr = self._make_manager()
        mgr.copy_selected()
        initial_count = mgr.count
        mgr.paste_from_clipboard()
        assert mgr.count == initial_count + 1

    def test_paste_no_clipboard(self):
        mgr = ShapeManager()
        initial_count = mgr.count
        mgr.paste_from_clipboard()
        assert mgr.count == initial_count


class TestShapeManagerGroupUngroup:
    """Тесты группировки и разгруппировки."""

    def _make_manager(self):
        mgr = ShapeManager()
        c1 = CircleShape(cx=50, cy=50, radius=20, pen_color=(0, 0, 0), pen_width=2)
        c2 = CircleShape(cx=100, cy=100, radius=20, pen_color=(0, 0, 0), pen_width=2)
        mgr.add_shape(c1)
        mgr.add_shape(c2)
        mgr.select_shape(0)
        mgr.select_shape(1, additive=True)
        return mgr

    def test_group_shapes(self):
        mgr = self._make_manager()
        mgr.group_selected(42)
        shapes = mgr.shapes
        assert shapes[0].group_id == 42
        assert shapes[1].group_id == 42

    def test_group_no_selection(self):
        mgr = ShapeManager()
        c = CircleShape(cx=50, cy=50, radius=20, pen_color=(0, 0, 0), pen_width=2)
        mgr.add_shape(c)
        mgr.group_selected(42)
        assert c.group_id is None

    def test_ungroup_shapes(self):
        mgr = self._make_manager()
        mgr.group_selected(42)
        assert mgr.shapes[0].group_id == 42
        mgr.ungroup_selected()
        assert mgr.shapes[0].group_id is None


class TestShapeManagerMisc:
    """Тесты остальных методов ShapeManager."""

    def test_has_shape(self):
        mgr = ShapeManager()
        c = CircleShape(cx=50, cy=50, radius=20, pen_color=(0, 0, 0), pen_width=2)
        mgr.add_shape(c)
        assert mgr.has_shape(c.id) is True
        assert mgr.has_shape(999) is False

    def test_get_shape_by_id(self):
        mgr = ShapeManager()
        c = CircleShape(cx=50, cy=50, radius=20, pen_color=(0, 0, 0), pen_width=2)
        mgr.add_shape(c)
        found = mgr.get_shape_by_id(c.id)
        assert found is c

    def test_get_shape_by_id_not_found(self):
        mgr = ShapeManager()
        found = mgr.get_shape_by_id(999)
        assert found is None

    def test_select_all(self):
        mgr = ShapeManager()
        c1 = CircleShape(cx=50, cy=50, radius=20, pen_color=(0, 0, 0), pen_width=2)
        c2 = CircleShape(cx=100, cy=100, radius=20, pen_color=(0, 0, 0), pen_width=2)
        mgr.add_shape(c1)
        mgr.add_shape(c2)
        mgr.select_all()
        assert len(mgr.selected_ids) == 2

    def test_select_none(self):
        mgr = ShapeManager()
        c = CircleShape(cx=50, cy=50, radius=20, pen_color=(0, 0, 0), pen_width=2)
        mgr.add_shape(c)
        mgr.select_shape(c.id)
        mgr.select_none()
        assert len(mgr.selected_ids) == 0

    def test_toggle_selection(self):
        mgr = ShapeManager()
        c = CircleShape(cx=50, cy=50, radius=20, pen_color=(0, 0, 0), pen_width=2)
        mgr.add_shape(c)
        mgr.toggle_selection(c.id)
        assert c.id in mgr.selected_ids
        mgr.toggle_selection(c.id)
        assert c.id not in mgr.selected_ids

    def test_count(self):
        mgr = ShapeManager()
        assert mgr.count == 0
        c = CircleShape(cx=50, cy=50, radius=20, pen_color=(0, 0, 0), pen_width=2)
        mgr.add_shape(c)
        assert mgr.count == 1

    def test_selected_shapes(self):
        mgr = ShapeManager()
        c1 = CircleShape(cx=50, cy=50, radius=20, pen_color=(0, 0, 0), pen_width=2)
        c2 = CircleShape(cx=100, cy=100, radius=20, pen_color=(0, 0, 0), pen_width=2)
        mgr.add_shape(c1)
        mgr.add_shape(c2)
        mgr.select_shape(c1.id)
        assert len(mgr.selected_shapes) == 1
        assert mgr.selected_shapes[0] is c1

    def test_selected_ids(self):
        mgr = ShapeManager()
        c = CircleShape(cx=50, cy=50, radius=20, pen_color=(0, 0, 0), pen_width=2)
        mgr.add_shape(c)
        mgr.select_shape(c.id)
        assert c.id in mgr.selected_ids
        assert isinstance(mgr.selected_ids, set)

    def test_shapes_property(self):
        mgr = ShapeManager()
        c = CircleShape(cx=50, cy=50, radius=20, pen_color=(0, 0, 0), pen_width=2)
        mgr.add_shape(c)
        shapes = mgr.shapes
        assert len(shapes) == 1
        assert shapes[0] is c

    def test_undo_stack_property(self):
        mgr = ShapeManager()
        assert mgr.undo_stack is not None

    def test_undo_stack_setter_invalid(self):
        mgr = ShapeManager()
        with pytest.raises(ValueError):
            mgr.undo_stack = "not a stack"
