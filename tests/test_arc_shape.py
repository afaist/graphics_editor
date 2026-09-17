"""Тесты для ArcShape — span_angle, bounding, трансформации."""

import pytest
from PySide6.QtCore import QPointF

from shapes.arc_shape import ArcShape
from shapes.base_shape import HandleType


class TestArcCreation:
    def test_default_properties(self):
        a = ArcShape(0, 0, 50)
        assert a.cx == 0
        assert a.cy == 0
        assert a.radius == 50
        assert a.start_angle == 0.0
        assert a.end_angle == 90.0

    def test_custom_angles(self):
        a = ArcShape(0, 0, 50, start_angle=45.0, end_angle=135.0)
        assert a.start_angle == 45.0
        assert a.end_angle == 135.0


class TestArcAngleNormalization:
    def test_start_angle_normalization(self):
        a = ArcShape(0, 0, 50)
        a.start_angle = 450.0
        assert a.start_angle == 90.0

    def test_end_angle_normalization(self):
        a = ArcShape(0, 0, 50)
        a.end_angle = 720.0
        assert a.end_angle == 0.0

    def test_negative_angle(self):
        a = ArcShape(0, 0, 50)
        a.start_angle = -90.0
        assert a.start_angle == 270.0


class TestArcSpanAngle:
    def test_normal_span(self):
        a = ArcShape(0, 0, 50, start_angle=0.0, end_angle=90.0)
        assert abs(a.span_angle - 90.0) < 1e-6

    def test_full_circle(self):
        a = ArcShape(0, 0, 50, start_angle=0.0, end_angle=360.0)
        assert abs(a.span_angle - 360.0) < 1e-6

    def test_wrap_around(self):
        a = ArcShape(0, 0, 50, start_angle=270.0, end_angle=90.0)
        assert abs(a.span_angle - 180.0) < 1e-6

    def test_same_angles(self):
        a = ArcShape(0, 0, 50, start_angle=45.0, end_angle=45.0)
        assert abs(a.span_angle - 360.0) < 1e-6


class TestArcMove:
    def test_move(self):
        a = ArcShape(0, 0, 50)
        a.move(10, 20)
        assert a.cx == 10
        assert a.cy == 20


class TestArcScale:
    def test_scale_up(self):
        a = ArcShape(0, 0, 50)
        a.scale(2.0)
        assert a.radius == 100.0

    def test_scale_min_radius(self):
        a = ArcShape(0, 0, 0.05)
        a.scale(0.5)
        assert a.radius >= 0.1


class TestArcBoundingRect:
    def test_bounding_rect(self):
        a = ArcShape(0, 0, 50)
        br = a.bounding_rect()
        assert br.left() <= -5
        assert br.top() <= -5
        assert br.right() >= 55
        assert br.bottom() >= 55

    def test_bounding_rect_offset(self):
        a = ArcShape(100, 100, 50)
        br = a.bounding_rect()
        assert br.left() <= 95
        assert br.top() <= 95
        assert br.right() >= 155
        assert br.bottom() >= 155


class TestArcHandles:
    def test_get_handles_returns_4(self):
        a = ArcShape(0, 0, 50)
        handles = a.get_handles()
        assert len(handles) == 4

    def test_get_handle_type_corner(self):
        a = ArcShape(0, 0, 50)
        handles = a.get_handles()
        ht = a.get_handle_type(handles[0], tolerance=5.0)
        assert ht != HandleType.NONE

    def test_get_handle_type_none(self):
        a = ArcShape(0, 0, 50)
        ht = a.get_handle_type(QPointF(500, 500), tolerance=5.0)
        assert ht == HandleType.NONE


class TestArcApplyHandleTransform:
    def test_top_left(self):
        a = ArcShape(0, 0, 50)
        a.apply_handle_transform(HandleType.TOP_LEFT, QPointF(-50, -50), QPointF(-10, -10))
        assert a.cx == -10
        assert a.cy == -10

    def test_bottom_right(self):
        a = ArcShape(0, 0, 50)
        a.apply_handle_transform(HandleType.BOTTOM_RIGHT, QPointF(50, 50), QPointF(70, 70))
        assert abs(a.radius - 70) < 1e-9


class TestArcSerialization:
    def test_to_dict(self):
        a = ArcShape(10, 20, 50, start_angle=45.0, end_angle=135.0)
        d = a.to_dict()
        assert d["cx"] == 10
        assert d["cy"] == 20
        assert d["radius"] == 50
        assert d["start_angle"] == 45.0
        assert d["end_angle"] == 135.0
        assert d["type"] == "arc"

    def test_from_dict(self):
        data = {
            "id": 1,
            "type": "arc",
            "pen_color": (255, 0, 0),
            "pen_width": 2.0,
            "brush_color": None,
            "rotation": 0.0,
            "group_id": None,
            "selected": False,
            "cx": 10,
            "cy": 20,
            "radius": 50,
            "start_angle": 45.0,
            "end_angle": 135.0,
        }
        a = ArcShape.from_dict(data)
        assert a.cx == 10
        assert a.radius == 50
        assert a.start_angle == 45.0
        assert a.end_angle == 135.0

    def test_roundtrip(self):
        a = ArcShape(5, 15, 30, start_angle=90.0, end_angle=270.0)
        a.id = 42
        d = a.to_dict()
        a2 = ArcShape.from_dict(d)
        assert a2.cx == 5
        assert a2.radius == 30
        assert abs(a2.start_angle - 90.0) < 1e-6
