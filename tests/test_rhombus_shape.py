"""Тесты для RhombusShape: build, center, order, properties, handles."""

import pytest
from PySide6.QtCore import QPointF

from shapes.base_shape import HandleType, ShapeType
from shapes.rhombus_shape import RhombusShape


class TestRhombusBuild:
    """Тесты статических методов построения."""

    def test_build_returns_four_vertices(self):
        verts = RhombusShape.build(50, 30, center=(0, 0))
        assert len(verts) == 4

    def test_build_left_vertex(self):
        verts = RhombusShape.build(50, 30, center=(0, 0))
        # A — левая: (cx - dx, cy)
        assert verts[0] == pytest.approx((-50, 0))

    def test_build_top_vertex(self):
        verts = RhombusShape.build(50, 30, center=(0, 0))
        # B — верхняя: (cx, cy - dy)
        assert verts[1] == pytest.approx((0, -30))

    def test_build_right_vertex(self):
        verts = RhombusShape.build(50, 30, center=(0, 0))
        # C — правая: (cx + dx, cy)
        assert verts[2] == pytest.approx((50, 0))

    def test_build_bottom_vertex(self):
        verts = RhombusShape.build(50, 30, center=(0, 0))
        # D — нижняя: (cx, cy + dy)
        assert verts[3] == pytest.approx((0, 30))

    def test_build_with_custom_center(self):
        verts = RhombusShape.build(50, 30, center=(100, 200))
        assert verts[0] == pytest.approx((50, 200))
        assert verts[2] == pytest.approx((150, 200))

    def test_build_default_center(self):
        verts = RhombusShape.build(50, 30)
        assert verts[0] == pytest.approx((-50, 0))


class TestRhombusCenter:
    """Тесты центрирования вершин."""

    def test_center_vertices(self):
        verts = [(0, 0), (100, 0), (100, 100), (0, 100)]
        centered = RhombusShape.center_vertices(verts)
        cx = sum(v[0] for v in centered) / 4
        cy = sum(v[1] for v in centered) / 4
        assert cx == pytest.approx(0)
        assert cy == pytest.approx(0)

    def test_center_vertices_empty(self):
        with pytest.raises(ZeroDivisionError):
            RhombusShape.center_vertices([])


class TestRhombusOrder:
    """Тесты порядка вершин."""

    def test_order_returns_same_count(self):
        verts = [(-50, 0), (0, -30), (50, 0), (0, 30)]
        ordered = RhombusShape.order_vertices_clockwise(verts)
        assert len(ordered) == 4

    def test_order_preserves_vertices(self):
        verts = [(-50, 0), (0, -30), (50, 0), (0, 30)]
        ordered = RhombusShape.order_vertices_clockwise(verts)
        for v in verts:
            assert v in ordered

    def test_order_empty(self):
        assert RhombusShape.order_vertices_clockwise([]) == []


class TestRhombusShape:
    """Тесты экземпляра RhombusShape."""

    def _make_shape(self, **kwargs):
        defaults = {
            "center": (0, 0),
            "dx": 50,
            "dy": 30,
            "pen_color": (0, 0, 0),
            "pen_width": 2.0,
            "brush_color": None,
            "selected": False,
        }
        defaults.update(kwargs)
        return RhombusShape(**defaults)

    def test_shape_type(self):
        s = self._make_shape()
        assert s._get_shape_type() == ShapeType.RHOMBUS

    def test_show_heights_default(self):
        s = self._make_shape()
        assert s.show_heights is False

    def test_show_diagonals_default(self):
        s = self._make_shape()
        assert s.show_diagonals is False

    def test_height_from_vertex_default(self):
        s = self._make_shape()
        assert s.height_from_vertex == -1

    def test_set_show_heights(self):
        s = self._make_shape()
        s.show_heights = True
        assert s.show_heights is True

    def test_set_show_diagonals(self):
        s = self._make_shape()
        s.show_diagonals = True
        assert s.show_diagonals is True

    def test_set_height_from_vertex(self):
        s = self._make_shape()
        s.height_from_vertex = 1
        assert s.height_from_vertex == 1

    def test_move(self):
        s = self._make_shape()
        orig_cx = s._center_x
        s.move(10, 20)
        assert s._center_x == pytest.approx(orig_cx + 10)

    def test_bounding_rect(self):
        s = self._make_shape()
        br = s.bounding_rect()
        assert br.width() > 0
        assert br.height() > 0

    def test_contains_point_inside(self):
        s = self._make_shape()
        center = QPointF(s._center_x, s._center_y)
        assert s.contains_point(center)

    def test_get_handles(self):
        s = self._make_shape()
        handles = s.get_handles()
        assert len(handles) == 4

    def test_handle_positions(self):
        s = self._make_shape()
        positions = s._handle_positions()
        assert len(positions) == 4

    def test_get_handle_type_none(self):
        s = self._make_shape()
        ht = s.get_handle_type(QPointF(-9999, -9999))
        assert ht == HandleType.NONE

    def test_rotate(self):
        s = self._make_shape()
        s.rotate(90)
        # Вращение должно изменить положение вершин
        assert len(s.get_handles()) == 4

    def test_scale(self):
        s = self._make_shape()
        orig_br = s.bounding_rect()
        s.scale(2.0)
        new_br = s.bounding_rect()
        assert new_br.width() > orig_br.width() * 1.5

    def test_to_dict(self):
        s = self._make_shape()
        d = s.to_dict()
        assert "id" in d
        assert "type" in d
        assert "center" in d

    def test_from_dict(self):
        s = self._make_shape()
        d = s.to_dict()
        s2 = RhombusShape.from_dict(d)
        assert s2._get_shape_type() == ShapeType.RHOMBUS

    def test_get_position_data(self):
        s = self._make_shape()
        data = s.get_position_data()
        assert "center" in data
        assert "dx" in data
        assert "dy" in data

    def test_restore_position_data(self):
        s = self._make_shape()
        data = s.get_position_data()
        s.move(100, 100)
        s.restore_position_data(data)
        # Должно восстановиться
        assert s._center_x == pytest.approx(data["center"][0])

    def test_get_properties(self):
        s = self._make_shape()
        props = s.get_properties()
        assert "pen_color" in props

    def test_apply_properties(self):
        s = self._make_shape()
        # apply_properties не должен вызывать ошибку
        s.apply_properties({"pen_color": (255, 255, 255)})

    def test_selected_property(self):
        s = self._make_shape(selected=True)
        assert s.selected is True
        s.selected = False
        assert s.selected is False

    def test_rotation_property(self):
        s = self._make_shape()
        assert s.rotation == 0
        s.rotation = 45
        assert s.rotation == 45
