"""Тесты для ParallelogramShape: build, center, order, properties, handles."""

import math

import pytest
from PySide6.QtCore import QPointF

from shapes.base_shape import HandleType, ShapeType
from shapes.parallelogram_shape import ParallelogramShape


class TestParallelogramBuild:
    """Тесты статических методов построения."""

    def test_build_returns_four_vertices(self):
        verts = ParallelogramShape.build(100, 80, 60)
        assert len(verts) == 4

    def test_build_first_vertex_at_origin(self):
        verts = ParallelogramShape.build(100, 80, 60)
        assert verts[0] == (0, 0)

    def test_build_second_vertex_on_x_axis(self):
        verts = ParallelogramShape.build(100, 80, 60)
        assert verts[1] == (100, 0)

    def test_build_with_90_degrees_is_rectangle(self):
        verts = ParallelogramShape.build(100, 50, 90)
        # При 90° cos=0, sin=1 → (100, 50) и (0, 50)
        assert verts[2] == pytest.approx((100, 50))
        assert verts[3] == pytest.approx((0, 50))

    def test_build_with_45_degrees(self):
        verts = ParallelogramShape.build(100, 100, 45)
        cos45 = math.cos(math.radians(45))
        sin45 = math.sin(math.radians(45))
        assert verts[2] == pytest.approx((100 + 100 * cos45, 100 * sin45))
        assert verts[3] == pytest.approx((100 * cos45, 100 * sin45))


class TestParallelogramCenter:
    """Тесты центрирования вершин."""

    def test_center_vertices_symmetric(self):
        verts = [(0, 0), (100, 0), (100, 100), (0, 100)]
        centered = ParallelogramShape.center_vertices(verts)
        cx = sum(v[0] for v in centered) / 4
        cy = sum(v[1] for v in centered) / 4
        assert cx == pytest.approx(0)
        assert cy == pytest.approx(0)

    def test_center_vertices_empty_raises(self):
        # center_vertices не обрабатывает пустой список — деление на 0
        with pytest.raises(ZeroDivisionError):
            ParallelogramShape.center_vertices([])


class TestParallelogramOrder:
    """Тесты порядка вершин."""

    def test_order_returns_same_count(self):
        verts = [(0, 0), (100, 0), (100, 100), (0, 100)]
        ordered = ParallelogramShape.order_vertices_clockwise(verts)
        assert len(ordered) == 4

    def test_order_preserves_all_vertices(self):
        verts = [(0, 0), (100, 0), (100, 100), (0, 100)]
        ordered = ParallelogramShape.order_vertices_clockwise(verts)
        for v in verts:
            assert v in ordered

    def test_order_empty(self):
        assert ParallelogramShape.order_vertices_clockwise([]) == []

    def test_order_single_vertex(self):
        assert ParallelogramShape.order_vertices_clockwise([(1, 2)]) == [(1, 2)]


class TestParallelogramShape:
    """Тесты экземпляра ParallelogramShape."""

    def _make_shape(self, **kwargs):
        defaults = {
            "vertices": [(0, 0), (100, 0), (120, 80), (20, 80)],
            "pen_color": (0, 0, 0),
            "pen_width": 2.0,
            "brush_color": None,
            "selected": False,
        }
        defaults.update(kwargs)
        return ParallelogramShape(**defaults)

    def test_shape_type(self):
        s = self._make_shape()
        assert s._get_shape_type() == ShapeType.PARALLELOGRAM

    def test_vertices_accessible(self):
        s = self._make_shape()
        assert len(s.vertices) == 4

    def test_show_heights_default(self):
        s = self._make_shape()
        assert s.show_heights is False

    def test_show_diagonals_default(self):
        s = self._make_shape()
        assert s.show_diagonals is False

    def test_show_circumcircle_default(self):
        s = self._make_shape()
        assert s.show_circumcircle is False

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

    def test_set_show_circumcircle(self):
        s = self._make_shape()
        s.show_circumcircle = True
        assert s.show_circumcircle is True

    def test_set_height_from_vertex(self):
        s = self._make_shape()
        s.height_from_vertex = 1
        assert s.height_from_vertex == 1

    def test_set_show_bisectors_stub(self):
        s = self._make_shape()
        s.show_bisectors = True
        assert s.show_bisectors is False  # stub всегда False

    def test_set_show_angles_stub(self):
        s = self._make_shape()
        s.show_angles = True
        assert s.show_angles is False  # stub всегда False

    def test_move(self):
        s = self._make_shape()
        s.move(10, 20)
        assert s.vertices[0].x() == pytest.approx(10)
        assert s.vertices[0].y() == pytest.approx(20)

    def test_bounding_rect(self):
        s = self._make_shape()
        br = s.bounding_rect()
        assert br.width() > 0
        assert br.height() > 0

    def test_contains_point_inside(self):
        s = self._make_shape()
        br = s.bounding_rect()
        center = br.center()
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

    def test_apply_handle_transform_move(self):
        s = self._make_shape()
        orig_x = s.vertices[0].x()
        orig_y = s.vertices[0].y()
        s.apply_handle_transform(
            HandleType.MOVE,
            QPointF(orig_x, orig_y),
            QPointF(orig_x + 10, orig_y),
        )
        assert s.vertices[0].x() == pytest.approx(orig_x + 10)

    def test_to_dict(self):
        s = self._make_shape()
        d = s.to_dict()
        assert "id" in d
        assert "type" in d
        assert "vertices" in d

    def test_from_dict(self):
        s = self._make_shape()
        d = s.to_dict()
        s2 = ParallelogramShape.from_dict(d)
        assert s2._get_shape_type() == ShapeType.PARALLELOGRAM
        assert len(s2.vertices) == 4

    def test_get_position_data(self):
        s = self._make_shape()
        data = s.get_position_data()
        assert "vertices" in data

    def test_restore_position_data(self):
        s = self._make_shape()
        data = s.get_position_data()
        s.move(100, 100)
        s.restore_position_data(data)
        br = s.bounding_rect()
        assert br.x() < 100  # restored to original position

    def test_rotate(self):
        s = self._make_shape()
        orig_verts = [(v.x(), v.y()) for v in s.vertices]
        s.rotate(90)
        # Вершины должны измениться
        new_verts = [(v.x(), v.y()) for v in s.vertices]
        assert orig_verts != new_verts

    def test_scale(self):
        s = self._make_shape()
        orig_br = s.bounding_rect()
        s.scale(2.0)
        new_br = s.bounding_rect()
        assert new_br.width() > orig_br.width() * 1.5

    def test_get_properties(self):
        s = self._make_shape()
        props = s.get_properties()
        assert "_shape_type" in props
        assert "_side_a" in props
        assert "_side_b" in props

    def test_apply_properties(self):
        s = self._make_shape()
        s.apply_properties({"_side_a": 120})
        assert s._side_a == 120

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

    def test_group_id_property(self):
        s = self._make_shape()
        assert s.group_id is None
        s.group_id = 42
        assert s.group_id == 42
