"""Тесты для TrapezoidShape: build_isosceles, build_scalene, center, order, properties."""

import pytest
from PySide6.QtCore import QPointF

from shapes.base_shape import HandleType, ShapeType
from shapes.trapezoid_shape import TrapezoidShape


class TestTrapezoidBuildIsosceles:
    """Тесты построения равнобедренной трапеции."""

    def test_build_returns_four_vertices(self):
        verts = TrapezoidShape.build_isosceles(200, 100, 60)
        assert len(verts) == 4

    def test_build_lower_base_larger(self):
        verts = TrapezoidShape.build_isosceles(200, 100, 60)
        # Нижнее основание = base_a (200), верхнее = base_b (100)
        assert verts[1][0] - verts[0][0] == pytest.approx(200)

    def test_build_height_positive(self):
        verts = TrapezoidShape.build_isosceles(200, 100, 60)
        h = abs(verts[2][1])
        assert h > 0

    def test_build_clamps_min_height(self):
        verts = TrapezoidShape.build_isosceles(200, 199, 1)  # очень маленький угол
        # Высота должна быть >= 1
        h = abs(verts[2][1])
        assert h >= 1.0

    def test_build_swap_bases(self):
        # Если base_a <= base_b, они меняются местами
        verts = TrapezoidShape.build_isosceles(100, 200, 60)
        # Нижнее основание должно быть больше
        assert verts[1][0] - verts[0][0] == pytest.approx(200)


class TestTrapezoidBuildScalene:
    """Тесты построения произвольной трапеции."""

    def test_build_returns_four_vertices(self):
        verts = TrapezoidShape.build_scalene(100, 200, 100, 20)
        assert len(verts) == 4

    def test_build_height_positive(self):
        verts = TrapezoidShape.build_scalene(100, 200, 100, 20)
        h = abs(verts[2][1])
        assert h == pytest.approx(100)

    def test_build_clamps_min_height(self):
        verts = TrapezoidShape.build_scalene(100, 200, 0.5, 20)
        h = abs(verts[2][1])
        assert h >= 1.0


class TestTrapezoidCenter:
    """Тесты центрирования вершин."""

    def test_center_vertices(self):
        verts = [(0, 0), (200, 0), (150, -100), (50, -100)]
        centered = TrapezoidShape.center_vertices(verts)
        cx = sum(v[0] for v in centered) / 4
        cy = sum(v[1] for v in centered) / 4
        assert cx == pytest.approx(0)
        assert cy == pytest.approx(0)

    def test_center_vertices_empty(self):
        with pytest.raises(ZeroDivisionError):
            TrapezoidShape.center_vertices([])


class TestTrapezoidOrder:
    """Тесты порядка вершин."""

    def test_order_returns_same_count(self):
        verts = [(0, 0), (200, 0), (150, -100), (50, -100)]
        ordered = TrapezoidShape.order_vertices_clockwise(verts)
        assert len(ordered) == 4

    def test_order_preserves_vertices(self):
        verts = [(0, 0), (200, 0), (150, -100), (50, -100)]
        ordered = TrapezoidShape.order_vertices_clockwise(verts)
        for v in verts:
            assert v in ordered

    def test_order_empty(self):
        assert TrapezoidShape.order_vertices_clockwise([]) == []


class TestTrapezoidShape:
    """Тесты экземпляра TrapezoidShape."""

    def _make_shape(self, **kwargs):
        defaults = {
            "vertices": [(-100, 0), (100, 0), (50, -100), (-50, -100)],
            "pen_color": (0, 0, 0),
            "pen_width": 2.0,
            "brush_color": None,
            "selected": False,
            "trapezoid_type": "isosceles",
        }
        defaults.update(kwargs)
        return TrapezoidShape(**defaults)

    def test_shape_type(self):
        s = self._make_shape(trapezoid_type="isosceles")
        assert s._get_shape_type() == ShapeType.TRAPEZOID_ISOSCELES

    def test_shape_type_scalene(self):
        s = self._make_shape(trapezoid_type="scalene")
        assert s._get_shape_type() == ShapeType.TRAPEZOID

    def test_show_midline_default(self):
        s = self._make_shape()
        assert s.show_midline is False

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

    def test_set_show_midline(self):
        s = self._make_shape()
        s.show_midline = True
        assert s.show_midline is True

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
        s.height_from_vertex = 2
        assert s.height_from_vertex == 2

    def test_set_show_bisectors_stub(self):
        s = self._make_shape()
        s.show_bisectors = True
        assert s.show_bisectors is False

    def test_set_show_angles_stub(self):
        s = self._make_shape()
        s.show_angles = True
        assert s.show_angles is False

    def test_move(self):
        s = self._make_shape()
        s.move(10, 20)
        assert s.vertices[0].x() == pytest.approx(-90)

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

    def test_rotate(self):
        s = self._make_shape()
        orig_verts = [(v.x(), v.y()) for v in s.vertices]
        s.rotate(90)
        new_verts = [(v.x(), v.y()) for v in s.vertices]
        assert orig_verts != new_verts

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
        assert "vertices" in d

    def test_from_dict(self):
        s = self._make_shape()
        d = s.to_dict()
        s2 = TrapezoidShape.from_dict(d)
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
        assert br.x() < 100

    def test_get_properties(self):
        s = self._make_shape()
        props = s.get_properties()
        assert "pen_color" in props

    def test_apply_properties(self):
        s = self._make_shape()
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

    def test_group_id_property(self):
        s = self._make_shape()
        assert s.group_id is None
        s.group_id = 42
        assert s.group_id == 42
