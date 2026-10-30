"""Тесты для CircleShape — contains, handles, трансформации."""

from PySide6.QtCore import QPointF

from shapes.base_shape import HandleType
from shapes.circle_shape import CircleShape


class TestCircleCreation:
    def test_default_properties(self):
        c = CircleShape(0, 0, 50)
        assert c.cx == 0
        assert c.cy == 0
        assert c.radius == 50

    def test_custom_pen_color(self):
        c = CircleShape(10, 20, 30, pen_color=(255, 128, 64))
        assert c.pen_color.red() == 255
        assert c.pen_color.green() == 128
        assert c.pen_color.blue() == 64

    def test_shape_type(self):
        c = CircleShape(0, 0, 50)
        assert c.shape_type.value == "circle"


class TestCircleProperties:
    def test_radius_setter_min_clamp(self):
        c = CircleShape(0, 0, 50)
        c.radius = 0.05
        assert c.radius == 50  # setter ignores values < 0.1

    def test_radius_setter_valid(self):
        c = CircleShape(0, 0, 50)
        c.radius = 100
        assert c.radius == 100

    def test_brush_color(self):
        c = CircleShape(0, 0, 50, brush_color=(0, 255, 0))
        assert c.brush_color is not None
        assert c.brush_color.green() == 255


class TestCircleMove:
    def test_move_positive(self):
        c = CircleShape(0, 0, 50)
        c.move(10, 20)
        assert c.cx == 10
        assert c.cy == 20

    def test_move_negative(self):
        c = CircleShape(100, 100, 50)
        c.move(-30, -40)
        assert c.cx == 70
        assert c.cy == 60


class TestCircleScale:
    def test_scale_up(self):
        c = CircleShape(0, 0, 50)
        c.scale(2.0)
        assert c.radius == 100

    def test_scale_down(self):
        c = CircleShape(0, 0, 50)
        c.scale(0.5)
        assert c.radius == 25

    def test_scale_min_clamp(self):
        c = CircleShape(0, 0, 0.05)
        c.scale(0.5)
        assert c.radius >= 0.1


class TestCircleRotate:
    def test_rotate(self):
        c = CircleShape(0, 0, 50)
        c.rotate(45)
        assert c.rotation == 45.0

    def test_rotate_360(self):
        c = CircleShape(0, 0, 50)
        c.rotate(360)
        assert c.rotation == 0.0

    def test_rotate_negative(self):
        c = CircleShape(0, 0, 50)
        c.rotate(-90)
        assert c.rotation == 270.0


class TestCircleContains:
    def test_point_at_center(self):
        c = CircleShape(50, 50, 50)
        assert c.contains_point(QPointF(50, 50)) is True

    def test_point_inside(self):
        c = CircleShape(50, 50, 50)
        assert c.contains_point(QPointF(60, 50)) is True

    def test_point_on_boundary(self):
        c = CircleShape(50, 50, 50)
        assert c.contains_point(QPointF(100, 50)) is True

    def test_point_outside(self):
        c = CircleShape(50, 50, 50)
        assert c.contains_point(QPointF(101, 50)) is False

    def test_point_far_outside(self):
        c = CircleShape(0, 0, 50)
        assert c.contains_point(QPointF(200, 200)) is False

    def test_point_diagonal_inside(self):
        c = CircleShape(0, 0, 50)
        # distance = sqrt(30^2 + 40^2) = 50
        assert c.contains_point(QPointF(30, 40)) is True

    def test_point_diagonal_outside(self):
        c = CircleShape(0, 0, 50)
        # distance = sqrt(31^2 + 41^2) > 50
        assert c.contains_point(QPointF(31, 41)) is False


class TestCircleBoundingRect:
    def test_bounding_rect(self):
        c = CircleShape(50, 50, 50)
        br = c.bounding_rect()
        # br should contain the circle with padding
        assert br.left() <= 0
        assert br.top() <= 0
        assert br.right() >= 100
        assert br.bottom() >= 100
        assert br.width() == br.height()  # circle bounding rect is square

    def test_bounding_rect_with_offset(self):
        c = CircleShape(100, 200, 75)
        br = c.bounding_rect()
        assert br.left() <= 25
        assert br.top() <= 125
        assert br.right() >= 175
        assert br.bottom() >= 275


class TestCircleHandles:
    def test_get_handles_returns_4(self):
        c = CircleShape(0, 0, 50)
        handles = c.get_handles()
        assert len(handles) == 4

    def test_handles_positions(self):
        c = CircleShape(100, 100, 50)
        handles = c.get_handles()
        # Handle 0: center
        assert handles[0].x() == 100
        assert handles[0].y() == 100
        # Handle 1: right
        assert handles[1].x() == 150
        assert handles[1].y() == 100
        # Handle 2: top
        assert handles[2].x() == 100
        assert handles[2].y() == 50
        # Handle 3: left
        assert handles[3].x() == 50
        assert handles[3].y() == 100

    def test_get_handle_type_center(self):
        c = CircleShape(0, 0, 50)
        handles = c.get_handles()
        ht = c.get_handle_type(handles[0], tolerance=5.0)
        assert ht == HandleType.TOP_LEFT

    def test_get_handle_type_right(self):
        c = CircleShape(0, 0, 50)
        handles = c.get_handles()
        # handle[1] = right point -> HandleType(i+2) = HandleType(3) = TOP_RIGHT
        ht = c.get_handle_type(handles[1], tolerance=5.0)
        assert ht == HandleType.TOP_RIGHT

    def test_get_handle_type_none(self):
        c = CircleShape(0, 0, 50)
        ht = c.get_handle_type(QPointF(500, 500), tolerance=5.0)
        assert ht == HandleType.NONE


class TestCircleApplyHandleTransform:
    def test_center_move(self):
        c = CircleShape(100, 100, 50)
        c.apply_handle_transform(HandleType.TOP_LEFT, QPointF(100, 100), QPointF(120, 130))
        assert c.cx == 120
        assert c.cy == 130
        assert c.radius == 50  # radius unchanged

    def test_right_handle_resize(self):
        c = CircleShape(0, 0, 50)
        c.apply_handle_transform(HandleType.BOTTOM_RIGHT, QPointF(50, 0), QPointF(100, 0))
        assert c.radius == 100

    def test_top_handle_resize(self):
        c = CircleShape(0, 0, 50)
        c.apply_handle_transform(HandleType.TOP_CENTER, QPointF(0, -50), QPointF(0, -100))
        assert c.radius == 100

    def test_left_handle_resize(self):
        c = CircleShape(0, 0, 50)
        c.apply_handle_transform(HandleType.LEFT_CENTER, QPointF(-50, 0), QPointF(-100, 0))
        assert c.radius == 100

    def test_min_radius_protection(self):
        c = CircleShape(0, 0, 0.05)
        c.apply_handle_transform(HandleType.BOTTOM_RIGHT, QPointF(0, 0), QPointF(0.01, 0))
        assert c.radius >= 0.1


class TestCircleSerialization:
    def test_to_dict(self):
        c = CircleShape(10, 20, 50, pen_color=(255, 0, 0))
        d = c.to_dict()
        assert d["cx"] == 10
        assert d["cy"] == 20
        assert d["radius"] == 50
        assert d["type"] == "circle"

    def test_from_dict(self):
        data = {
            "id": 1,
            "type": "circle",
            "pen_color": (0, 255, 0),
            "pen_width": 3.0,
            "brush_color": (0, 0, 255),
            "rotation": 0.0,
            "group_id": None,
            "selected": False,
            "cx": 50,
            "cy": 100,
            "radius": 75,
        }
        c = CircleShape.from_dict(data)
        assert c.cx == 50
        assert c.cy == 100
        assert c.radius == 75
        assert c.pen_width == 3.0

    def test_roundtrip(self):
        c = CircleShape(25, 75, 60, pen_color=(128, 64, 32))
        c.id = 42
        d = c.to_dict()
        c2 = CircleShape.from_dict(d)
        assert c2.cx == 25
        assert c2.cy == 75
        assert c2.radius == 60
        # id is not restored by from_dict (known limitation)


class TestCirclePositionData:
    def test_get_position_data(self):
        c = CircleShape(100, 200, 50)
        data = c.get_position_data()
        assert data["cx"] == 100
        assert data["cy"] == 200
        assert data["radius"] == 50

    def test_restore_position_data(self):
        c = CircleShape(0, 0, 10)
        c.restore_position_data({"cx": 50, "cy": 100, "radius": 75})
        assert c.cx == 50
        assert c.cy == 100
        assert c.radius == 75
