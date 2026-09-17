"""Тесты для PointShape — move, scale, contains, radius."""

import pytest
from PySide6.QtCore import QPointF

from shapes.base_shape import HandleType
from shapes.point_shape import PointShape


class TestPointCreation:
    def test_default_properties(self):
        p = PointShape(10.0, 20.0)
        assert p.x == 10.0
        assert p.y == 20.0
        assert p.radius == 2.0

    def test_custom_radius(self):
        p = PointShape(5.0, 5.0, radius=5.0)
        assert p.radius == 5.0

    def test_default_brush_color(self):
        p = PointShape(0, 0)
        assert p.brush_color is not None
        assert p.brush_color.red() == 255


class TestPointRadiusValidation:
    def test_radius_too_small(self):
        with pytest.raises(ValueError, match="at least 1.0"):
            PointShape(0, 0, radius=0.5)

    def test_radius_minimum(self):
        p = PointShape(0, 0, radius=1.0)
        assert p.radius == 1.0

    def test_radius_normal(self):
        p = PointShape(0, 0, radius=10.0)
        assert p.radius == 10.0


class TestPointMove:
    def test_move_positive(self):
        p = PointShape(10, 20)
        p.move(5, -3)
        assert p.x == 15
        assert p.y == 17

    def test_move_negative(self):
        p = PointShape(10, 20)
        p.move(-10, -20)
        assert p.x == 0
        assert p.y == 0

    def test_move_zero(self):
        p = PointShape(10, 20)
        p.move(0, 0)
        assert p.x == 10
        assert p.y == 20


class TestPointScale:
    def test_scale_up(self):
        p = PointShape(0, 0, radius=5.0)
        p.scale(2.0)
        assert p.radius == 10.0

    def test_scale_down(self):
        p = PointShape(0, 0, radius=5.0)
        p.scale(0.5)
        assert p.radius == 2.5

    def test_scale_min_radius(self):
        p = PointShape(0, 0, radius=1.0)
        p.scale(0.1)
        assert p.radius >= 1.0

    def test_scale_zero(self):
        with pytest.raises(ValueError, match="positive"):
            p = PointShape(0, 0, radius=5.0)
            p.scale(0)

    def test_scale_negative(self):
        with pytest.raises(ValueError, match="positive"):
            p = PointShape(0, 0, radius=5.0)
            p.scale(-1.0)


class TestPointRotate:
    def test_rotate(self):
        p = PointShape(0, 0)
        p.rotate(90)
        assert p.rotation == 90.0


class TestPointContains:
    def test_point_at_center(self):
        p = PointShape(10, 20, radius=3.0)
        assert p.contains_point(QPointF(10, 20)) is True

    def test_point_near_center(self):
        p = PointShape(10, 20, radius=3.0)
        assert p.contains_point(QPointF(12, 21)) is True

    def test_point_far(self):
        p = PointShape(10, 20, radius=3.0)
        assert p.contains_point(QPointF(100, 200)) is False

    def test_point_at_tolerance_boundary(self):
        p = PointShape(0, 0, radius=2.0)
        # tolerance_radius = 2 + 4 = 6
        # distance 6 should be inside
        assert p.contains_point(QPointF(6, 0)) is True


class TestPointBoundingRect:
    def test_bounding_rect(self):
        p = PointShape(10, 20, radius=3.0)
        br = p.bounding_rect()
        # r + 4 = 7 padding
        assert abs(br.left() - (10 - 7)) < 1e-9
        assert abs(br.top() - (20 - 7)) < 1e-9
        assert abs(br.width() - 14) < 1e-9
        assert abs(br.height() - 14) < 1e-9


class TestPointHandles:
    def test_get_handles(self):
        p = PointShape(10, 20, radius=3.0)
        handles = p.get_handles()
        assert len(handles) == 1
        assert abs(handles[0].x() - 10) < 1e-9
        assert abs(handles[0].y() - 20) < 1e-9

    def test_get_handle_type_inside(self):
        p = PointShape(10, 20, radius=3.0)
        ht = p.get_handle_type(QPointF(10, 20), tolerance=5.0)
        assert ht == HandleType.MOVE

    def test_get_handle_type_outside(self):
        p = PointShape(10, 20, radius=3.0)
        ht = p.get_handle_type(QPointF(100, 200), tolerance=5.0)
        assert ht == HandleType.NONE


class TestPointApplyHandleTransform:
    def test_move_handle(self):
        p = PointShape(10, 20)
        p.apply_handle_transform(HandleType.MOVE, QPointF(10, 20), QPointF(30, 40))
        assert p.x == 30
        assert p.y == 40


class TestPointSerialization:
    def test_to_dict(self):
        p = PointShape(10, 20, radius=5.0)
        p.id = 1
        d = p.to_dict()
        assert d["x"] == 10
        assert d["y"] == 20
        assert d["radius"] == 5.0
        assert d["type"] == "point"

    def test_from_dict(self):
        data = {
            "id": 5,
            "type": "point",
            "pen_color": (255, 0, 0),
            "pen_width": 2.0,
            "brush_color": (0, 255, 0),
            "rotation": 0.0,
            "group_id": None,
            "selected": False,
            "x": 15,
            "y": 25,
            "radius": 4.0,
        }
        p = PointShape.from_dict(data)
        assert p.x == 15
        assert p.y == 25
        assert p.radius == 4.0
        assert p.id == 5

    def test_roundtrip(self):
        p = PointShape(5, 10, radius=3.0)
        p.id = 42
        d = p.to_dict()
        p2 = PointShape.from_dict(d)
        assert p2.x == 5
        assert p2.y == 10
        assert p2.radius == 3.0
