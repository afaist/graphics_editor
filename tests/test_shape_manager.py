"""Тесты для ShapeManager — add/remove/select/move/copy/duplicate."""

import pytest
from PySide6.QtCore import QPointF

from shapes.rectangle_shape import RectangleShape
from shapes.line_shape import LineShape
from shapes.base_shape import ShapeType
from manager.shape_manager import ShapeManager


class TestShapeManagerCreation:
    def test_initial_state(self):
        sm = ShapeManager()
        assert sm.count == 0
        assert sm.shapes == []
        assert sm.selected_shapes == []
        assert sm.selected_ids == set()


class TestAddShape:
    def test_add_single_shape(self):
        sm = ShapeManager()
        r = RectangleShape(0, 0, 100, 50)
        sm.add_shape(r)
        assert sm.count == 1
        assert r.id == 0

    def test_add_multiple_shapes(self):
        sm = ShapeManager()
        r1 = RectangleShape(0, 0, 100, 50)
        r2 = RectangleShape(100, 0, 100, 50)
        sm.add_shape(r1)
        sm.add_shape(r2)
        assert sm.count == 2
        assert r1.id == 0
        assert r2.id == 1

    def test_add_shape_emits_signal(self):
        sm = ShapeManager()
        added_shapes = []
        sm.shape_added.connect(added_shapes.append)
        r = RectangleShape(0, 0, 100, 50)
        sm.add_shape(r)
        assert len(added_shapes) == 1
        assert added_shapes[0] is r


class TestRemoveShapes:
    def test_remove_one_shape(self):
        sm = ShapeManager()
        r = RectangleShape(0, 0, 100, 50)
        sm.add_shape(r)
        sm.remove_shapes({0})
        assert sm.count == 0

    def test_remove_nonexistent_shape(self):
        sm = ShapeManager()
        sm.remove_shapes({999})  # не должно вызвать ошибку
        assert sm.count == 0

    def test_remove_all_shapes(self):
        sm = ShapeManager()
        for i in range(5):
            sm.add_shape(RectangleShape(i * 10, 0, 100, 50))
        sm.remove_shapes({0, 1, 2, 3, 4})
        assert sm.count == 0


class TestRemoveAll:
    def test_remove_all(self):
        sm = ShapeManager()
        for i in range(5):
            sm.add_shape(RectangleShape(i * 10, 0, 100, 50))
        sm.remove_all()
        assert sm.count == 0
        assert sm.selected_ids == set()


class TestSelectShape:
    def test_select_single(self):
        sm = ShapeManager()
        r = RectangleShape(0, 0, 100, 50)
        sm.add_shape(r)
        sm.select_shape(0)
        assert 0 in sm.selected_ids
        assert r.selected is True

    def test_select_replace(self):
        sm = ShapeManager()
        r1 = RectangleShape(0, 0, 100, 50)
        r2 = RectangleShape(100, 0, 100, 50)
        sm.add_shape(r1)
        sm.add_shape(r2)
        sm.select_shape(0)
        sm.select_shape(1)
        assert sm.selected_ids == {1}

    def test_select_additive(self):
        sm = ShapeManager()
        r1 = RectangleShape(0, 0, 100, 50)
        r2 = RectangleShape(100, 0, 100, 50)
        sm.add_shape(r1)
        sm.add_shape(r2)
        sm.select_shape(0)
        sm.select_shape(1, additive=True)
        assert sm.selected_ids == {0, 1}


class TestSelectNone:
    def test_select_none(self):
        sm = ShapeManager()
        r = RectangleShape(0, 0, 100, 50)
        sm.add_shape(r)
        sm.select_shape(0)
        sm.select_none()
        assert sm.selected_ids == set()
        assert r.selected is False


class TestSelectAll:
    def test_select_all(self):
        sm = ShapeManager()
        for i in range(3):
            sm.add_shape(RectangleShape(i * 10, 0, 100, 50))
        sm.select_all()
        assert sm.selected_ids == {0, 1, 2}

    def test_select_all_empty(self):
        sm = ShapeManager()
        sm.select_all()
        assert sm.selected_ids == set()


class TestToggleSelection:
    def test_toggle_on(self):
        sm = ShapeManager()
        r = RectangleShape(0, 0, 100, 50)
        sm.add_shape(r)
        sm.toggle_selection(0)
        assert 0 in sm.selected_ids

    def test_toggle_off(self):
        sm = ShapeManager()
        r = RectangleShape(0, 0, 100, 50)
        sm.add_shape(r)
        sm.select_shape(0)
        sm.toggle_selection(0)
        assert 0 not in sm.selected_ids


class TestSelectByRect:
    def test_select_by_rect(self):
        sm = ShapeManager()
        r1 = RectangleShape(0, 0, 50, 50)
        r2 = RectangleShape(60, 0, 50, 50)
        sm.add_shape(r1)
        sm.add_shape(r2)
        from PySide6.QtCore import QRectF
        rect = QRectF(10, -10, 50, 70)
        selected = sm.select_by_rect(rect)
        assert 0 in selected

    def test_select_by_rect_no_match(self):
        sm = ShapeManager()
        r = RectangleShape(0, 0, 50, 50)
        sm.add_shape(r)
        from PySide6.QtCore import QRectF
        rect = QRectF(200, 200, 50, 50)
        selected = sm.select_by_rect(rect)
        assert len(selected) == 0


class TestHitTest:
    def test_hit_test_finds_shape(self):
        sm = ShapeManager()
        r = RectangleShape(0, 0, 100, 50)
        sm.add_shape(r)
        result = sm.hit_test(QPointF(50, 25))
        assert result is r

    def test_hit_test_no_shape(self):
        sm = ShapeManager()
        result = sm.hit_test(QPointF(50, 50))
        assert result is None


class TestMoveSelected:
    def test_move_selected(self):
        sm = ShapeManager()
        r = RectangleShape(0, 0, 100, 50)
        sm.add_shape(r)
        sm.select_shape(0)
        sm.move_selected(10, 20)
        assert r.x == 10
        assert r.y == 20

    def test_move_selected_none_selected(self):
        sm = ShapeManager()
        r = RectangleShape(0, 0, 100, 50)
        sm.add_shape(r)
        sm.move_selected(10, 20)  # ничего не выделено
        assert r.x == 0


class TestCopyPaste:
    def test_copy_selected(self):
        sm = ShapeManager()
        r = RectangleShape(0, 0, 100, 50)
        sm.add_shape(r)
        sm.select_shape(0)
        sm.copy_selected()
        assert sm.clipboard_shapes is not None
        assert len(sm.clipboard_shapes) == 1

    def test_paste_from_clipboard(self):
        sm = ShapeManager()
        r = RectangleShape(0, 0, 100, 50)
        sm.add_shape(r)
        sm.select_shape(0)
        sm.copy_selected()
        pasted = sm.paste_from_clipboard(QPointF(20, 20))
        assert len(pasted) == 1
        assert sm.count == 2

    def test_paste_empty_clipboard(self):
        sm = ShapeManager()
        pasted = sm.paste_from_clipboard()
        assert pasted == []


class TestGroupUngroup:
    def test_group_selected(self):
        sm = ShapeManager()
        r = RectangleShape(0, 0, 100, 50)
        sm.add_shape(r)
        sm.select_shape(0)
        sm.group_selected(42)
        assert r.group_id == 42

    def test_ungroup_selected(self):
        sm = ShapeManager()
        r = RectangleShape(0, 0, 100, 50)
        sm.add_shape(r)
        r.group_id = 42
        sm.select_shape(0)
        sm.ungroup_selected()
        assert r.group_id is None


class TestZOrder:
    def test_bring_to_front(self):
        sm = ShapeManager()
        r1 = RectangleShape(0, 0, 100, 50)
        r2 = RectangleShape(50, 0, 100, 50)
        sm.add_shape(r1)
        sm.add_shape(r2)
        sm.select_shape(0)
        sm.bring_to_front()
        shapes = sm.shapes
        assert shapes[-1] is r1

    def test_send_to_back(self):
        sm = ShapeManager()
        r1 = RectangleShape(0, 0, 100, 50)
        r2 = RectangleShape(50, 0, 100, 50)
        sm.add_shape(r1)
        sm.add_shape(r2)
        sm.select_shape(0)
        sm.send_to_back()
        shapes = sm.shapes
        assert shapes[0] is r1


class TestDeleteSelected:
    def test_delete_selected(self):
        sm = ShapeManager()
        r = RectangleShape(0, 0, 100, 50)
        sm.add_shape(r)
        sm.select_shape(0)
        sm.delete_selected()
        assert sm.count == 0

    def test_delete_selected_none(self):
        sm = ShapeManager()
        r = RectangleShape(0, 0, 100, 50)
        sm.add_shape(r)
        sm.delete_selected()  # ничего не выделено
        assert sm.count == 1


class TestGetSelectedProperties:
    def test_get_selected_properties(self):
        sm = ShapeManager()
        r = RectangleShape(0, 0, 100, 50, pen_color=(100, 200, 50))
        r._rotation = 45.0
        sm.add_shape(r)
        sm.select_shape(0)
        props = sm.get_selected_properties()
        assert props is not None
        assert props["pen_color"] == (100, 200, 50)
        assert props["rotation"] == 45.0

    def test_get_selected_properties_none_selected(self):
        sm = ShapeManager()
        props = sm.get_selected_properties()
        assert props is None


class TestSetSelectedProperties:
    def test_set_selected_properties(self):
        sm = ShapeManager()
        r = RectangleShape(0, 0, 100, 50, pen_color=(0, 0, 0))
        sm.add_shape(r)
        sm.select_shape(0)
        sm.set_selected_properties({"pen_color": (255, 128, 0), "pen_width": 5.0})
        assert r.pen_color.red() == 255
        assert r.pen_width == 5.0
