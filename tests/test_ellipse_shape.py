"""Тесты для EllipseShape — contains, handles, трансформации."""

from PySide6.QtCore import QPointF

from shapes.base_shape import HandleType
from shapes.ellipse_shape import EllipseShape


class TestEllipseCreation:
    def test_default_properties(self):
        e = EllipseShape(0, 0, 80, 60)
        assert e.x == 0
        assert e.y == 0
        assert e.width == 80
        assert e.height == 60

    def test_radius_x_y(self):
        e = EllipseShape(0, 0, 100, 60)
        assert e.radius_x == 50.0
        assert e.radius_y == 30.0


class TestEllipseMove:
    def test_move(self):
        e = EllipseShape(0, 0, 80, 60)
        e.move(10, 20)
        assert e.x == 10
        assert e.y == 20


class TestEllipseScale:
    def test_scale_up(self):
        e = EllipseShape(0, 0, 80, 60)
        e.scale(2.0)
        assert e.width == 160
        assert e.height == 120

    def test_scale_min_size(self):
        e = EllipseShape(0, 0, 0.05, 0.05)
        e.scale(0.5)
        assert e.width >= 0.1
        assert e.height >= 0.1


class TestEllipseRotate:
    def test_rotate(self):
        e = EllipseShape(0, 0, 80, 60)
        e.rotate(45)
        assert e.rotation == 45.0


class TestEllipseContains:
    def test_point_at_center(self):
        e = EllipseShape(0, 0, 100, 60)
        assert e.contains_point(QPointF(50, 30)) is True

    def test_point_outside(self):
        e = EllipseShape(0, 0, 100, 60)
        assert e.contains_point(QPointF(200, 200)) is False

    def test_point_on_boundary(self):
        e = EllipseShape(0, 0, 100, 60)
        # На границе: (x-cx)^2/rx^2 + (y-cy)^2/ry^2 = 1
        # (0-50)^2/50^2 + (30-30)^2/30^2 = 1 + 0 = 1
        assert e.contains_point(QPointF(0, 30)) is True

    def test_point_inside(self):
        e = EllipseShape(0, 0, 100, 60)
        assert e.contains_point(QPointF(50, 30)) is True

    def test_point_outside_boundary(self):
        e = EllipseShape(0, 0, 100, 60)
        # (100-50)^2/50^2 + (30-30)^2/30^2 = 1
        # Point beyond boundary
        assert e.contains_point(QPointF(101, 30)) is False


class TestEllipseBoundingRect:
    def test_bounding_rect(self):
        e = EllipseShape(10, 20, 80, 60)
        br = e.bounding_rect()
        assert br.left() <= 10
        assert br.top() <= 20
        assert br.right() >= 90
        assert br.bottom() >= 80


class TestEllipseHandles:
    def test_get_handles_returns_8(self):
        e = EllipseShape(0, 0, 100, 60)
        handles = e.get_handles()
        assert len(handles) == 8

    def test_get_handle_type_corner(self):
        e = EllipseShape(0, 0, 100, 60)
        handles = e.get_handles()
        ht = e.get_handle_type(handles[0], tolerance=5.0)
        assert ht == HandleType.TOP_LEFT

    def test_get_handle_type_center(self):
        e = EllipseShape(0, 0, 100, 60)
        handles = e.get_handles()
        # handles 4-7 are center handles
        ht = e.get_handle_type(handles[4], tolerance=5.0)
        assert ht == HandleType.TOP_CENTER

    def test_get_handle_type_none(self):
        e = EllipseShape(0, 0, 100, 60)
        ht = e.get_handle_type(QPointF(500, 500), tolerance=5.0)
        assert ht == HandleType.NONE


class TestEllipseApplyHandleTransform:
    def test_left_center(self):
        e = EllipseShape(0, 0, 100, 60)
        e.apply_handle_transform(HandleType.LEFT_CENTER, QPointF(0, 30), QPointF(-20, 30))
        assert e.width == -20

    def test_right_center(self):
        e = EllipseShape(0, 0, 100, 60)
        e.apply_handle_transform(HandleType.RIGHT_CENTER, QPointF(100, 30), QPointF(150, 30))
        assert e.width == 150

    def test_top_center(self):
        e = EllipseShape(0, 0, 100, 60)
        e.apply_handle_transform(HandleType.TOP_CENTER, QPointF(50, 0), QPointF(50, -20))
        assert e.height == -20

    def test_bottom_center(self):
        e = EllipseShape(0, 0, 100, 60)
        e.apply_handle_transform(HandleType.BOTTOM_CENTER, QPointF(50, 60), QPointF(50, 100))
        assert e.height == 100


class TestEllipseSerialization:
    def test_to_dict(self):
        e = EllipseShape(10, 20, 80, 60)
        d = e.to_dict()
        assert d["x"] == 10
        assert d["y"] == 20
        assert d["width"] == 80
        assert d["height"] == 60
        assert d["type"] == "ellipse"

    def test_from_dict(self):
        data = {
            "id": 1,
            "type": "ellipse",
            "pen_color": (0, 255, 0),
            "pen_width": 2.0,
            "brush_color": (0, 0, 255),
            "rotation": 0.0,
            "group_id": None,
            "selected": False,
            "x": 5,
            "y": 10,
            "width": 80,
            "height": 40,
        }
        e = EllipseShape.from_dict(data)
        assert e.x == 5
        assert e.width == 80
        assert e.height == 40

    def test_roundtrip(self):
        e = EllipseShape(5, 15, 120, 80, pen_color=(255, 128, 64))
        e.id = 7
        d = e.to_dict()
        e2 = EllipseShape.from_dict(d)
        assert e2.x == 5
        assert e2.width == 120
        assert e2.height == 80
