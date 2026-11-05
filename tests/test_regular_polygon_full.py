"""Тесты для RegularPolygonShape: build, area, side_length, properties, handles."""

import math

import pytest
from PySide6.QtCore import QPointF

from shapes.base_shape import HandleType, ShapeType
from shapes.regular_polygon_shape import RegularPolygonShape


class TestRegularPolygonBuild:
    """Тесты создания правильного многоугольника."""

    def _make_shape(self, **kwargs):
        defaults = {
            "num_sides": 6,
            "radius": 100,
            "center": (0, 0),
            "pen_color": (0, 0, 0),
            "pen_width": 2.0,
            "brush_color": None,
            "selected": False,
        }
        defaults.update(kwargs)
        return RegularPolygonShape(**defaults)

    def test_hexagon_has_6_vertices(self):
        s = self._make_shape(num_sides=6)
        assert len(s.vertices) == 6

    def test_triangle_has_3_vertices(self):
        s = self._make_shape(num_sides=3)
        assert len(s.vertices) == 3

    def test_pentagon_has_5_vertices(self):
        s = self._make_shape(num_sides=5)
        assert len(s.vertices) == 5

    def test_square_has_4_vertices(self):
        s = self._make_shape(num_sides=4)
        assert len(s.vertices) == 4

    def test_vertices_on_circle(self):
        s = self._make_shape(radius=100)
        for v in s.vertices:
            dx = v.x() - s._center_x
            dy = v.y() - s._center_y
            dist = math.sqrt(dx * dx + dy * dy)
            assert dist == pytest.approx(100, abs=1.0)

    def test_labels_match_vertex_count(self):
        s = self._make_shape(num_sides=6)
        assert len(s.labels) == 6

    def test_labels_are_alphabetical(self):
        s = self._make_shape(num_sides=5)
        assert s.labels == ["A", "B", "C", "D", "E"]

    def test_center_position(self):
        s = self._make_shape(center=(50, 100))
        assert s._center_x == 50
        assert s._center_y == 100


class TestRegularPolygonGeometry:
    """Тесты геометрических вычислений."""

    def test_area_hexagon(self):
        s = RegularPolygonShape(
            num_sides=6,
            radius=100,
            center=(0, 0),
            pen_color=(0, 0, 0),
            pen_width=2,
            brush_color=None,
            selected=False,
        )
        # Площадь правильного шестиугольника: (3√3/2) * r²
        expected = (3 * math.sqrt(3) / 2) * 100 * 100
        assert s.area() == pytest.approx(expected, rel=0.01)

    def test_area_triangle(self):
        s = RegularPolygonShape(
            num_sides=3,
            radius=100,
            center=(0, 0),
            pen_color=(0, 0, 0),
            pen_width=2,
            brush_color=None,
            selected=False,
        )
        expected = 0.5 * 3 * 100 * 100 * math.sin(2 * math.pi / 3)
        assert s.area() == pytest.approx(expected)

    def test_side_length_hexagon(self):
        s = RegularPolygonShape(
            num_sides=6,
            radius=100,
            center=(0, 0),
            pen_color=(0, 0, 0),
            pen_width=2,
            brush_color=None,
            selected=False,
        )
        # Для шестиугольника сторона = радиус
        assert s.side_length() == pytest.approx(100)

    def test_side_length_triangle(self):
        s = RegularPolygonShape(
            num_sides=3,
            radius=100,
            center=(0, 0),
            pen_color=(0, 0, 0),
            pen_width=2,
            brush_color=None,
            selected=False,
        )
        expected = 2 * 100 * math.sin(math.pi / 3)
        assert s.side_length() == pytest.approx(expected)


class TestRegularPolygonProperties:
    """Тесты property-сеттеров."""

    def _make_shape(self, **kwargs):
        defaults = {
            "num_sides": 6,
            "radius": 100,
            "center": (0, 0),
            "pen_color": (0, 0, 0),
            "pen_width": 2.0,
            "brush_color": None,
            "selected": False,
        }
        defaults.update(kwargs)
        return RegularPolygonShape(**defaults)

    def test_set_num_sides(self):
        s = self._make_shape()
        s.num_sides = 8
        assert s.num_sides == 8
        assert len(s.vertices) == 8

    def test_set_num_sides_minimum(self):
        s = self._make_shape()
        s.num_sides = 2  # должно быть не меньше 3
        assert s.num_sides >= 3

    def test_set_radius(self):
        s = self._make_shape()
        s.radius = 150
        assert s.radius == 150

    def test_set_radius_minimum(self):
        s = self._make_shape()
        s.radius = -10  # должно быть не меньше 1
        assert s.radius >= 1

    def test_set_show_angles(self):
        s = self._make_shape()
        s.show_angles = True
        assert s.show_angles is True

    def test_set_show_heights_stub(self):
        s = self._make_shape()
        s.show_heights = True
        assert s.show_heights is False  # stub

    def test_set_show_diagonals_stub(self):
        s = self._make_shape()
        s.show_diagonals = True
        assert s.show_diagonals is False  # stub

    def test_set_show_bisectors_stub(self):
        s = self._make_shape()
        s.show_bisectors = True
        assert s.show_bisectors is False  # stub

    def test_set_show_circumcircle(self):
        s = self._make_shape()
        s.show_circumcircle = True
        assert s.show_circumcircle is True

    def test_set_height_from_vertex_stub(self):
        s = self._make_shape()
        s.height_from_vertex = 1
        assert s.height_from_vertex == -1  # stub


class TestRegularPolygonMethods:
    """Тесты методов экземпляра."""

    def _make_shape(self, **kwargs):
        defaults = {
            "num_sides": 6,
            "radius": 100,
            "center": (0, 0),
            "pen_color": (0, 0, 0),
            "pen_width": 2.0,
            "brush_color": None,
            "selected": False,
        }
        defaults.update(kwargs)
        return RegularPolygonShape(**defaults)

    def test_bounding_rect(self):
        s = self._make_shape()
        br = s.bounding_rect()
        assert br.width() > 0
        assert br.height() > 0

    def test_contains_point_center(self):
        s = self._make_shape()
        center = QPointF(s._center_x, s._center_y)
        assert s.contains_point(center)

    def test_get_handles(self):
        s = self._make_shape()
        handles = s.get_handles()
        assert len(handles) == s.num_sides

    def test_handle_positions(self):
        s = self._make_shape()
        positions = s._handle_positions()
        assert len(positions) == s.num_sides

    def test_get_handle_type_none(self):
        s = self._make_shape()
        ht = s.get_handle_type(QPointF(-9999, -9999))
        assert ht == HandleType.NONE

    def test_get_shape_type(self):
        s = self._make_shape()
        # Для num_sides=6 это REGULAR_HEXAGON
        assert s._get_shape_type() == ShapeType.REGULAR_HEXAGON

    def test_get_shape_type_triangle(self):
        s = self._make_shape(num_sides=3)
        assert s._get_shape_type() == ShapeType.REGULAR_TRIANGLE

    def test_get_shape_type_square(self):
        s = self._make_shape(num_sides=4)
        assert s._get_shape_type() == ShapeType.SQUARE

    def test_to_dict(self):
        s = self._make_shape()
        d = s.to_dict()
        assert "id" in d
        assert "type" in d
        assert "num_sides" in d

    def test_from_dict(self):
        s = self._make_shape()
        d = s.to_dict()
        s2 = RegularPolygonShape.from_dict(d)
        assert s2.num_sides == s.num_sides
        assert s2.radius == s.radius

    def test_get_position_data(self):
        s = self._make_shape()
        data = s.get_position_data()
        assert "center" in data
        assert "num_sides" in data
        assert "radius" in data

    def test_restore_position_data(self):
        s = self._make_shape()
        data = s.get_position_data()
        s._center_x = 999
        s._center_y = 999
        s.restore_position_data(data)
        assert s._center_x == pytest.approx(data["center"][0])

    def test_get_properties(self):
        s = self._make_shape()
        props = s.get_properties()
        assert "num_sides" in props
        assert "radius" in props

    def test_apply_properties(self):
        s = self._make_shape()
        s.apply_properties({"num_sides": 8})
        assert s.num_sides == 8

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
