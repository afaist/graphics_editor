"""Тесты для ParabolaShape — contains, handles, трансформации."""

from PySide6.QtCore import QPointF

from shapes.base_shape import HandleType
from shapes.parabola_shape import ParabolaShape


class TestParabolaCreation:
    def test_default_properties(self):
        p = ParabolaShape(0, 0, 80)
        assert p.vertex_x == 0
        assert p.vertex_y == 0
        assert p.focal_length == 80
        assert p.direction == "up"

    def test_custom_direction(self):
        p = ParabolaShape(10, 20, 50, direction="down")
        assert p.direction == "down"
        assert p.vertex_x == 10
        assert p.vertex_y == 20

    def test_shape_type(self):
        p = ParabolaShape(0, 0, 50)
        assert p.shape_type.value == "parabola"

    def test_invalid_direction(self):
        from shapes.parabola_shape import ParabolaShape

        try:
            ParabolaShape(0, 0, 50, direction="invalid")
            assert False, "Should raise ValueError"
        except ValueError:
            pass

    def test_default_colors(self):
        p = ParabolaShape(0, 0, 50)
        assert p.pen_color.red() == 0
        assert p.pen_color.green() == 0
        assert p.pen_color.blue() == 0


class TestParabolaProperties:
    def test_a_coefficient(self):
        p = ParabolaShape(0, 0, 10)
        # a = 1 / (4 * p) = 1 / 40 = 0.025
        assert abs(p.a - 0.025) < 0.001

    def test_focal_length_setter_min_clamp(self):
        p = ParabolaShape(0, 0, 50)
        p.focal_length = 0.05
        assert p.focal_length == 50  # setter ignores values < 0.1

    def test_focal_length_setter_valid(self):
        p = ParabolaShape(0, 0, 50)
        p.focal_length = 100
        assert p.focal_length == 100


class TestParabolaPoints:
    def test_compute_points_up(self):
        p = ParabolaShape(0, 0, 50, direction="up")
        points = p._compute_points(num_samples=100)
        assert len(points) > 0
        # Vertex should be near the origin
        # All points should have y >= 0 for direction="up"
        for x, y in points:
            assert y >= -0.1  # small tolerance for floating point

    def test_compute_points_down(self):
        p = ParabolaShape(0, 0, 50, direction="down")
        points = p._compute_points(num_samples=100)
        assert len(points) > 0
        for x, y in points:
            assert y <= 0.1

    def test_compute_points_right(self):
        p = ParabolaShape(0, 0, 50, direction="right")
        points = p._compute_points(num_samples=100)
        assert len(points) > 0

    def test_compute_points_left(self):
        p = ParabolaShape(0, 0, 50, direction="left")
        points = p._compute_points(num_samples=100)
        assert len(points) > 0


class TestParabolaMove:
    def test_move_positive(self):
        p = ParabolaShape(0, 0, 50)
        p.move(10, 20)
        assert p.vertex_x == 10
        assert p.vertex_y == 20

    def test_move_negative(self):
        p = ParabolaShape(100, 100, 50)
        p.move(-30, -40)
        assert p.vertex_x == 70
        assert p.vertex_y == 60


class TestParabolaScale:
    def test_scale_up(self):
        p = ParabolaShape(0, 0, 50)
        p.scale(2.0)
        assert p.focal_length == 100

    def test_scale_down(self):
        p = ParabolaShape(0, 0, 50)
        p.scale(0.5)
        assert p.focal_length == 25

    def test_scale_min_clamp(self):
        p = ParabolaShape(0, 0, 0.05)
        p.scale(0.5)
        assert p.focal_length >= 0.1


class TestParabolaRotate:
    def test_rotate(self):
        p = ParabolaShape(0, 0, 50)
        p.rotate(45)
        assert p.rotation == 45.0

    def test_rotate_360(self):
        p = ParabolaShape(0, 0, 50)
        p.rotate(360)
        assert p.rotation == 0.0


class TestParabolaContains:
    def test_contains_vertex(self):
        p = ParabolaShape(50, 50, 50)
        assert p.contains_point(QPointF(50, 50)) is True

    def test_contains_near_vertex(self):
        p = ParabolaShape(50, 50, 50)
        assert p.contains_point(QPointF(51, 51)) is True

    def test_bounding_rect_contains_vertex(self):
        p = ParabolaShape(50, 50, 50)
        br = p.bounding_rect()
        assert br.contains(50, 50)


class TestParabolaBoundingRect:
    def test_bounding_rect_not_empty(self):
        p = ParabolaShape(0, 0, 50)
        br = p.bounding_rect()
        assert not br.isEmpty()
        assert br.width() > 0
        assert br.height() > 0

    def test_bounding_rect_with_offset(self):
        p = ParabolaShape(100, 200, 75)
        br = p.bounding_rect()
        assert br.left() < 100
        assert br.top() < 200


class TestParabolaHandles:
    def test_get_handles_returns_1(self):
        p = ParabolaShape(0, 0, 50)
        handles = p.get_handles()
        assert len(handles) == 1

    def test_handles_positions(self):
        p = ParabolaShape(100, 100, 50)
        handles = p.get_handles()
        assert handles[0].x() == 100
        assert handles[0].y() == 100

    def test_get_handle_type_vertex(self):
        p = ParabolaShape(0, 0, 50)
        handles = p.get_handles()
        ht = p.get_handle_type(handles[0], tolerance=5.0)
        assert ht == HandleType.TOP_LEFT

    def test_get_handle_type_none(self):
        p = ParabolaShape(0, 0, 50)
        ht = p.get_handle_type(QPointF(500, 500), tolerance=5.0)
        assert ht == HandleType.NONE


class TestParabolaApplyHandleTransform:
    def test_vertex_move(self):
        p = ParabolaShape(100, 100, 50)
        p.apply_handle_transform(HandleType.TOP_LEFT, QPointF(100, 100), QPointF(120, 130))
        assert p.vertex_x == 120
        assert p.vertex_y == 130
        assert p.focal_length == 50  # focal_length unchanged


class TestParabolaSerialization:
    def test_to_dict(self):
        p = ParabolaShape(10, 20, 50, direction="down", pen_color=(255, 0, 0))
        d = p.to_dict()
        assert d["vertex_x"] == 10
        assert d["vertex_y"] == 20
        assert d["focal_length"] == 50
        assert d["direction"] == "down"
        assert d["type"] == "parabola"

    def test_from_dict(self):
        data = {
            "id": 1,
            "type": "parabola",
            "pen_color": (0, 255, 0),
            "pen_width": 3.0,
            "brush_color": None,
            "rotation": 0.0,
            "group_id": None,
            "selected": False,
            "vertex_x": 50,
            "vertex_y": 100,
            "focal_length": 75,
            "direction": "right",
        }
        p = ParabolaShape.from_dict(data)
        assert p.vertex_x == 50
        assert p.vertex_y == 100
        assert p.focal_length == 75
        assert p.direction == "right"

    def test_roundtrip(self):
        p = ParabolaShape(25, 75, 60, direction="left", pen_color=(128, 64, 32))
        p.id = 42
        d = p.to_dict()
        p2 = ParabolaShape.from_dict(d)
        assert p2.vertex_x == 25
        assert p2.vertex_y == 75
        assert p2.focal_length == 60
        assert p2.direction == "left"
        # id is not restored by from_dict (known limitation)


class TestParabolaPositionData:
    def test_get_position_data(self):
        p = ParabolaShape(100, 200, 50, direction="right")
        data = p.get_position_data()
        assert data["vertex_x"] == 100
        assert data["vertex_y"] == 200
        assert data["focal_length"] == 50
        assert data["direction"] == "right"

    def test_restore_position_data(self):
        p = ParabolaShape(0, 0, 10)
        p.restore_position_data(
            {
                "vertex_x": 50,
                "vertex_y": 100,
                "focal_length": 75,
                "direction": "down",
            }
        )
        assert p.vertex_x == 50
        assert p.vertex_y == 100
        assert p.focal_length == 75
        assert p.direction == "down"
