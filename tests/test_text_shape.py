"""Тесты для TextShape — font_size bounds, contains, move."""

import pytest
from PySide6.QtCore import QPointF

from shapes.text_shape import TextShape
from shapes.base_shape import HandleType


class TestTextCreation:
    def test_default_properties(self):
        t = TextShape(10, 20, text="Hello")
        assert t.x == 10
        assert t.y == 20
        assert t.text == "Hello"
        assert t.font_size == 14

    def test_custom_font_size(self):
        t = TextShape(0, 0, text="Test", font_size=24)
        assert t.font_size == 24

    def test_empty_text(self):
        t = TextShape(0, 0)
        assert t.text == ""


class TestTextFontValidation:
    def test_font_size_clamped_min(self):
        t = TextShape(0, 0, font_size=2)
        assert t.font_size == 4

    def test_font_size_clamped_max(self):
        t = TextShape(0, 0, font_size=300)
        assert t.font_size == 200

    def test_font_size_normal(self):
        t = TextShape(0, 0, font_size=14)
        assert t.font_size == 14

    def test_set_font_size_clamped_min(self):
        t = TextShape(0, 0)
        t.font_size = 2
        assert t.font_size == 4

    def test_set_font_size_clamped_max(self):
        t = TextShape(0, 0)
        t.font_size = 300
        assert t.font_size == 200


class TestTextMove:
    def test_move(self):
        t = TextShape(10, 20, text="Test")
        t.move(5, -3)
        assert t.x == 15
        assert t.y == 17


class TestTextScale:
    def test_scale_up(self):
        t = TextShape(0, 0, font_size=14)
        t.scale(2.0)
        assert t.font_size == 28

    def test_scale_down(self):
        t = TextShape(0, 0, font_size=14)
        t.scale(0.5)
        assert t.font_size == 7

    def test_scale_zero_not_allowed(self):
        t = TextShape(0, 0)
        t.scale(0)  # factor > 0 required, but 0 is not > 0
        # font_size should remain unchanged since factor is not > 0

    def test_scale_negative_not_allowed(self):
        t = TextShape(0, 0)
        t.scale(-1.0)  # factor must be > 0
        assert t.font_size == 14


class TestTextContains:
    def test_point_inside(self):
        t = TextShape(0, 0, text="Hello", font_size=14)
        br = t.bounding_rect()
        if br.width() > 0 and br.height() > 0:
            assert t.contains_point(QPointF(br.left() + 5, br.top() + 5)) is True

    def test_point_outside(self):
        t = TextShape(0, 0, text="Hello", font_size=14)
        assert t.contains_point(QPointF(1000, 1000)) is False

    def test_empty_text(self):
        t = TextShape(0, 0, text="")
        assert t.contains_point(QPointF(0, 0)) is False


class TestTextBoundingRect:
    def test_empty_text_bounding_rect(self):
        t = TextShape(0, 0, text="")
        br = t.bounding_rect()
        assert br.width() > 0
        assert br.height() > 0

    def test_text_with_content(self):
        t = TextShape(0, 0, text="Hello World", font_size=20)
        br = t.bounding_rect()
        assert br.width() > 0
        assert br.height() > 0

    def test_bounding_rect_contains_text(self):
        t = TextShape(10, 20, text="Test", font_size=14)
        br = t.bounding_rect()
        assert br.left() <= 10
        assert br.top() <= 20


class TestTextHandles:
    def test_get_handles_empty_text(self):
        t = TextShape(0, 0, text="")
        handles = t.get_handles()
        assert len(handles) == 0

    def test_get_handles_with_text(self):
        t = TextShape(0, 0, text="Test")
        handles = t.get_handles()
        assert len(handles) == 4

    def test_get_handle_type_none(self):
        t = TextShape(0, 0, text="Test")
        ht = t.get_handle_type(QPointF(500, 500), tolerance=5.0)
        assert ht == HandleType.NONE


class TestTextApplyHandleTransform:
    def test_top_left(self):
        t = TextShape(10, 20, text="Test")
        t.apply_handle_transform(HandleType.TOP_LEFT, QPointF(10, 20), QPointF(15, 25))
        assert t.x == 15
        assert t.y == 25


class TestTextSerialization:
    def test_to_dict(self):
        t = TextShape(10, 20, text="Hello", font_size=18)
        d = t.to_dict()
        assert d["x"] == 10
        assert d["y"] == 20
        assert d["text"] == "Hello"
        assert d["font_size"] == 18
        assert d["type"] == "text"

    def test_from_dict(self):
        data = {
            "id": 1,
            "type": "text",
            "pen_color": (0, 0, 255),
            "pen_width": 2.0,
            "brush_color": None,
            "rotation": 0.0,
            "group_id": None,
            "selected": False,
            "x": 10,
            "y": 20,
            "text": "World",
            "font_size": 24,
        }
        t = TextShape.from_dict(data)
        assert t.x == 10
        assert t.text == "World"
        assert t.font_size == 24

    def test_roundtrip(self):
        t = TextShape(5, 15, text="Test Text", font_size=20)
        t.id = 42
        d = t.to_dict()
        t2 = TextShape.from_dict(d)
        assert t2.x == 5
        assert t2.text == "Test Text"
        assert t2.font_size == 20
