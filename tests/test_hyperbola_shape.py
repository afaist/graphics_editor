"""Тесты для HyperbolaShape — contains, handles, трансформации."""

from PySide6.QtCore import QPointF

from shapes.base_shape import HandleType
from shapes.hyperbola_shape import HyperbolaShape


class TestHyperbolaCreation:
    def test_default_properties(self):
        h = HyperbolaShape(0, 0, 50, 30)
        assert h.cx == 0
        assert h.cy == 0
        assert h.semi_axis_a == 50
        assert h.semi_axis_b == 30
        assert h.direction == "horizontal"

    def test_vertical_direction(self):
        h = HyperbolaShape(10, 20, 40, 25, direction="vertical")
        assert h.direction == "vertical"
        assert h.cx == 10
        assert h.cy == 20

    def test_shape_type(self):
        h = HyperbolaShape(0, 0, 50, 30)
        assert h.shape_type.value == "hyperbola"

    def test_invalid_direction(self):
        try:
            HyperbolaShape(0, 0, 50, 30, direction="invalid")
            assert False, "Should raise ValueError"
        except ValueError:
            pass

    def test_default_colors(self):
        h = HyperbolaShape(0, 0, 50, 30)
        assert h.pen_color.red() == 0
        assert h.pen_color.green() == 0
        assert h.pen_color.blue() == 0


class TestHyperbolaProperties:
    def test_semi_axis_a_setter_min_clamp(self):
        h = HyperbolaShape(0, 0, 50, 30)
        h.semi_axis_a = 0.05
        assert h.semi_axis_a == 50  # setter ignores values < 0.1

    def test_semi_axis_a_setter_valid(self):
        h = HyperbolaShape(0, 0, 50, 30)
        h.semi_axis_a = 100
        assert h.semi_axis_a == 100

    def test_semi_axis_b_setter(self):
        h = HyperbolaShape(0, 0, 50, 30)
        h.semi_axis_b = 60
        assert h.semi_axis_b == 60


class TestHyperbolaPoints:
    def test_compute_points_horizontal(self):
        h = HyperbolaShape(0, 0, 50, 30, direction="horizontal")
        branches = h._compute_points(num_samples=100)
        assert len(branches) == 2  # two branches
        assert len(branches[0]) > 0
        assert len(branches[1]) > 0

    def test_compute_points_vertical(self):
        h = HyperbolaShape(0, 0, 50, 30, direction="vertical")
        branches = h._compute_points(num_samples=100)
        assert len(branches) == 2
        assert len(branches[0]) > 0
        assert len(branches[1]) > 0

    def test_branches_sorted(self):
        h = HyperbolaShape(0, 0, 50, 30, direction="horizontal")
        branches = h._compute_points(num_samples=100)
        # Right branch should be sorted by y
        right = branches[0]
        for i in range(1, len(right)):
            assert right[i][1] >= right[i - 1][1] - 0.1  # small tolerance


class TestHyperbolaMove:
    def test_move_positive(self):
        h = HyperbolaShape(0, 0, 50, 30)
        h.move(10, 20)
        assert h.cx == 10
        assert h.cy == 20

    def test_move_negative(self):
        h = HyperbolaShape(100, 100, 50, 30)
        h.move(-30, -40)
        assert h.cx == 70
        assert h.cy == 60


class TestHyperbolaScale:
    def test_scale_up(self):
        h = HyperbolaShape(0, 0, 50, 30)
        h.scale(2.0)
        assert h.semi_axis_a == 100
        assert h.semi_axis_b == 60

    def test_scale_down(self):
        h = HyperbolaShape(0, 0, 50, 30)
        h.scale(0.5)
        assert h.semi_axis_a == 25
        assert h.semi_axis_b == 15

    def test_scale_min_clamp_a(self):
        h = HyperbolaShape(0, 0, 0.05, 30)
        h.scale(0.5)
        assert h.semi_axis_a >= 0.1

    def test_scale_min_clamp_b(self):
        h = HyperbolaShape(0, 0, 50, 0.05)
        h.scale(0.5)
        assert h.semi_axis_b >= 0.1


class TestHyperbolaRotate:
    def test_rotate(self):
        h = HyperbolaShape(0, 0, 50, 30)
        h.rotate(45)
        assert h.rotation == 45.0

    def test_rotate_360(self):
        h = HyperbolaShape(0, 0, 50, 30)
        h.rotate(360)
        assert h.rotation == 0.0


class TestHyperbolaContains:
    def test_bounding_rect_contains_center(self):
        h = HyperbolaShape(50, 50, 50, 30)
        br = h.bounding_rect()
        assert br.contains(50, 50)

    def test_contains_near_center(self):
        h = HyperbolaShape(50, 50, 50, 30)
        assert h.contains_point(QPointF(50, 50)) is True


class TestHyperbolaBoundingRect:
    def test_bounding_rect_not_empty(self):
        h = HyperbolaShape(0, 0, 50, 30)
        br = h.bounding_rect()
        assert not br.isEmpty()
        assert br.width() > 0
        assert br.height() > 0

    def test_bounding_rect_with_offset(self):
        h = HyperbolaShape(100, 200, 75, 45)
        br = h.bounding_rect()
        assert br.left() < 100
        assert br.top() < 200


class TestHyperbolaHandles:
    def test_get_handles_horizontal(self):
        h = HyperbolaShape(0, 0, 50, 30, direction="horizontal")
        handles = h.get_handles()
        assert len(handles) == 3

    def test_get_handles_vertical(self):
        h = HyperbolaShape(0, 0, 50, 30, direction="vertical")
        handles = h.get_handles()
        assert len(handles) == 3

    def test_handles_horizontal_positions(self):
        h = HyperbolaShape(100, 100, 50, 30, direction="horizontal")
        handles = h.get_handles()
        # Handle 0: center
        assert handles[0].x() == 100
        assert handles[0].y() == 100
        # Handle 1: left vertex
        assert handles[1].x() == 50
        assert handles[1].y() == 100
        # Handle 2: right vertex
        assert handles[2].x() == 150
        assert handles[2].y() == 100

    def test_handles_vertical_positions(self):
        h = HyperbolaShape(100, 100, 50, 30, direction="vertical")
        handles = h.get_handles()
        # Handle 0: center
        assert handles[0].x() == 100
        assert handles[0].y() == 100
        # Handle 1: top vertex
        assert handles[1].x() == 100
        assert handles[1].y() == 50
        # Handle 2: bottom vertex
        assert handles[2].x() == 100
        assert handles[2].y() == 150

    def test_get_handle_type_center(self):
        h = HyperbolaShape(0, 0, 50, 30)
        handles = h.get_handles()
        ht = h.get_handle_type(handles[0], tolerance=5.0)
        assert ht == HandleType.TOP_LEFT

    def test_get_handle_type_none(self):
        h = HyperbolaShape(0, 0, 50, 30)
        ht = h.get_handle_type(QPointF(500, 500), tolerance=5.0)
        assert ht == HandleType.NONE


class TestHyperbolaApplyHandleTransform:
    def test_center_move(self):
        h = HyperbolaShape(100, 100, 50, 30)
        h.apply_handle_transform(HandleType.TOP_LEFT, QPointF(100, 100), QPointF(120, 130))
        assert h.cx == 120
        assert h.cy == 130
        assert h.semi_axis_a == 50
        assert h.semi_axis_b == 30

    def test_right_vertex_resize_horizontal(self):
        h = HyperbolaShape(0, 0, 50, 30, direction="horizontal")
        h.apply_handle_transform(HandleType.BOTTOM_RIGHT, QPointF(50, 0), QPointF(100, 0))
        assert h.semi_axis_a == 100

    def test_top_vertex_resize_vertical(self):
        h = HyperbolaShape(0, 0, 50, 30, direction="vertical")
        h.apply_handle_transform(HandleType.TOP_CENTER, QPointF(0, -50), QPointF(0, -100))
        assert h.semi_axis_a == 100

    def test_min_semi_axis_a_protection(self):
        h = HyperbolaShape(0, 0, 0.05, 30)
        h.apply_handle_transform(HandleType.BOTTOM_RIGHT, QPointF(0, 0), QPointF(0.01, 0))
        assert h.semi_axis_a >= 0.1


class TestHyperbolaSerialization:
    def test_to_dict(self):
        h = HyperbolaShape(10, 20, 50, 30, direction="vertical", pen_color=(255, 0, 0))
        d = h.to_dict()
        assert d["cx"] == 10
        assert d["cy"] == 20
        assert d["semi_axis_a"] == 50
        assert d["semi_axis_b"] == 30
        assert d["direction"] == "vertical"
        assert d["type"] == "hyperbola"

    def test_from_dict(self):
        data = {
            "id": 1,
            "type": "hyperbola",
            "pen_color": (0, 255, 0),
            "pen_width": 3.0,
            "brush_color": None,
            "rotation": 0.0,
            "group_id": None,
            "selected": False,
            "cx": 50,
            "cy": 100,
            "semi_axis_a": 75,
            "semi_axis_b": 45,
            "direction": "horizontal",
        }
        h = HyperbolaShape.from_dict(data)
        assert h.cx == 50
        assert h.cy == 100
        assert h.semi_axis_a == 75
        assert h.semi_axis_b == 45
        assert h.direction == "horizontal"

    def test_roundtrip(self):
        h = HyperbolaShape(25, 75, 60, 40, direction="vertical", pen_color=(128, 64, 32))
        h.id = 42
        d = h.to_dict()
        h2 = HyperbolaShape.from_dict(d)
        assert h2.cx == 25
        assert h2.cy == 75
        assert h2.semi_axis_a == 60
        assert h2.semi_axis_b == 40
        assert h2.direction == "vertical"
        # id is not restored by from_dict (known limitation)


class TestHyperbolaPositionData:
    def test_get_position_data(self):
        h = HyperbolaShape(100, 200, 50, 30, direction="horizontal")
        data = h.get_position_data()
        assert data["cx"] == 100
        assert data["cy"] == 200
        assert data["semi_axis_a"] == 50
        assert data["semi_axis_b"] == 30
        assert data["direction"] == "horizontal"

    def test_restore_position_data(self):
        h = HyperbolaShape(0, 0, 10, 5)
        h.restore_position_data(
            {
                "cx": 50,
                "cy": 100,
                "semi_axis_a": 75,
                "semi_axis_b": 45,
                "direction": "vertical",
            }
        )
        assert h.cx == 50
        assert h.cy == 100
        assert h.semi_axis_a == 75
        assert h.semi_axis_b == 45
        assert h.direction == "vertical"
