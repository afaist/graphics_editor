"""Тесты для RegularPolygonShape — show_angles и дополнительные проверки."""

from shapes.regular_polygon_shape import RegularPolygonShape


class TestRegularPolygonShowAngles:
    def test_default_show_angles_false(self):
        p = RegularPolygonShape(num_sides=6, radius=50)
        assert p.show_angles is False

    def test_show_angles_true(self):
        p = RegularPolygonShape(num_sides=6, radius=50, show_angles=True)
        assert p.show_angles is True

    def test_show_angles_setter(self):
        p = RegularPolygonShape(num_sides=6, radius=50)
        p.show_angles = True
        assert p.show_angles is True

    def test_show_angles_false(self):
        p = RegularPolygonShape(num_sides=6, radius=50, show_angles=True)
        p.show_angles = False
        assert p.show_angles is False


class TestRegularPolygonInteriorAngle:
    def test_triangle_angle(self):
        assert RegularPolygonShape(num_sides=3, radius=50).show_angles is False

    def test_square_angle(self):
        assert RegularPolygonShape(num_sides=4, radius=50).show_angles is False

    def test_pentagon_angle(self):
        assert RegularPolygonShape(num_sides=5, radius=50).show_angles is False

    def test_hexagon_angle(self):
        assert RegularPolygonShape(num_sides=6, radius=50).show_angles is False

    def test_decagon_angle(self):
        assert RegularPolygonShape(num_sides=10, radius=50).show_angles is False


class TestRegularPolygonSerializationShowAngles:
    def test_to_dict_includes_show_angles(self):
        p = RegularPolygonShape(num_sides=5, radius=80, show_angles=True)
        d = p.to_dict()
        assert d["show_angles"] is True

    def test_from_dict_restores_show_angles(self):
        data = {
            "id": 1,
            "type": "regular_pentagon",
            "pen_color": (0, 0, 0),
            "pen_width": 2.0,
            "brush_color": None,
            "rotation": 0.0,
            "group_id": None,
            "selected": False,
            "num_sides": 5,
            "radius": 80,
            "center_x": 100,
            "center_y": 200,
            "show_angles": True,
        }
        p = RegularPolygonShape.from_dict(data)
        assert p.show_angles is True
        assert p.num_sides == 5
        assert p.radius == 80

    def test_roundtrip_preserves_show_angles(self):
        p = RegularPolygonShape(num_sides=7, radius=120, show_angles=True)
        p.id = 99
        d = p.to_dict()
        p2 = RegularPolygonShape.from_dict(d)
        assert p2.show_angles is True
        assert p2.num_sides == 7
        assert p2.radius == 120

    def test_from_dict_defaults_show_angles_false(self):
        data = {
            "id": 1,
            "type": "square",
            "pen_color": (0, 0, 0),
            "pen_width": 2.0,
            "brush_color": None,
            "rotation": 0.0,
            "group_id": None,
            "selected": False,
            "num_sides": 4,
            "radius": 50,
            "center_x": 0,
            "center_y": 0,
        }
        p = RegularPolygonShape.from_dict(data)
        assert p.show_angles is False  # default when not in dict
