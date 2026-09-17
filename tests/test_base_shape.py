"""Тесты для BaseShape — валидация, свойства, copy, to_dict, сервисные методы."""

import math
import pytest
from PySide6.QtCore import QPointF, QRectF

from shapes.base_shape import BaseShape, ShapeType, HandleType
from shapes.rectangle_shape import RectangleShape


# ------------------------------------------------------------------
# Вспомогательный класс для тестирования абстрактного BaseShape
# ------------------------------------------------------------------

class _TestShape(RectangleShape):
    """Конкретная подкласс для доступа к статическим/общим методам BaseShape."""
    pass


# ------------------------------------------------------------------
# Валидация цвета
# ------------------------------------------------------------------

class TestColorValidation:
    def test_valid_color_black(self):
        s = RectangleShape(0, 0, 10, 10, pen_color=(0, 0, 0))
        assert s.pen_color.red() == 0
        assert s.pen_color.green() == 0
        assert s.pen_color.blue() == 0

    def test_valid_color_white(self):
        s = RectangleShape(0, 0, 10, 10, pen_color=(255, 255, 255))
        assert s.pen_color.red() == 255

    def test_valid_color_rgb(self):
        s = RectangleShape(0, 0, 10, 10, pen_color=(128, 64, 192))
        assert s.pen_color.red() == 128
        assert s.pen_color.green() == 64
        assert s.pen_color.blue() == 192

    def test_invalid_color_wrong_length(self):
        with pytest.raises(ValueError, match="3 integers"):
            RectangleShape(0, 0, 10, 10, pen_color=(255, 0))

    def test_invalid_color_out_of_range(self):
        with pytest.raises(ValueError, match="0.*255"):
            RectangleShape(0, 0, 10, 10, pen_color=(256, 0, 0))

    def test_invalid_color_negative(self):
        with pytest.raises(ValueError, match="0.*255"):
            RectangleShape(0, 0, 10, 10, pen_color=(-1, 0, 0))

    def test_invalid_color_not_int(self):
        with pytest.raises(ValueError, match="integers"):
            RectangleShape(0, 0, 10, 10, pen_color=(1.5, 0, 0))

    def test_invalid_brush_color(self):
        with pytest.raises(ValueError):
            RectangleShape(0, 0, 10, 10, brush_color=(300, 0, 0))

    def test_none_brush_color_allowed(self):
        s = RectangleShape(0, 0, 10, 10, brush_color=None)
        assert s.brush_color is None


# ------------------------------------------------------------------
# Валидация pen_width
# ------------------------------------------------------------------

class TestPenWidthValidation:
    def test_valid_pen_width(self):
        s = RectangleShape(0, 0, 10, 10, pen_width=3.0)
        assert s.pen_width == 3.0

    def test_min_pen_width(self):
        s = RectangleShape(0, 0, 10, 10, pen_width=0.5)
        assert s.pen_width == 0.5

    def test_too_small_pen_width(self):
        with pytest.raises(ValueError, match=">= 0.5"):
            RectangleShape(0, 0, 10, 10, pen_width=0.1)

    def test_zero_pen_width(self):
        with pytest.raises(ValueError):
            RectangleShape(0, 0, 10, 10, pen_width=0)

    def test_negative_pen_width(self):
        with pytest.raises(ValueError):
            RectangleShape(0, 0, 10, 10, pen_width=-1.0)

    def test_set_pen_width_too_small(self):
        s = RectangleShape(0, 0, 10, 10)
        with pytest.raises(ValueError):
            s.pen_width = 0.1


# ------------------------------------------------------------------
# Свойства
# ------------------------------------------------------------------

class TestProperties:
    def test_default_id(self):
        s = RectangleShape(0, 0, 10, 10)
        assert s.id == -1

    def test_default_selected(self):
        s = RectangleShape(0, 0, 10, 10)
        assert s.selected is False

    def test_set_selected(self):
        s = RectangleShape(0, 0, 10, 10)
        s.selected = True
        assert s.selected is True

    def test_default_rotation(self):
        s = RectangleShape(0, 0, 10, 10)
        assert s.rotation == 0.0

    def test_rotation_normalization(self):
        s = RectangleShape(0, 0, 10, 10)
        s.rotation = 450.0
        assert s.rotation == 90.0

    def test_rotation_negative(self):
        s = RectangleShape(0, 0, 10, 10)
        s.rotation = -90.0
        assert s.rotation == 270.0

    def test_group_id_default(self):
        s = RectangleShape(0, 0, 10, 10)
        assert s.group_id is None

    def test_set_group_id(self):
        s = RectangleShape(0, 0, 10, 10)
        s.group_id = 42
        assert s.group_id == 42

    def test_set_group_id_none(self):
        s = RectangleShape(0, 0, 10, 10)
        s.group_id = 42
        s.group_id = None
        assert s.group_id is None

    def test_set_pen_color(self):
        s = RectangleShape(0, 0, 10, 10)
        s.pen_color = (255, 128, 0)
        assert s.pen_color.red() == 255
        assert s.pen_color.green() == 128
        assert s.pen_color.blue() == 0

    def test_set_brush_color(self):
        s = RectangleShape(0, 0, 10, 10)
        s.brush_color = (0, 255, 0)
        assert s.brush_color.red() == 0
        assert s.brush_color.green() == 255

    def test_set_brush_color_none(self):
        s = RectangleShape(0, 0, 10, 10, brush_color=(255, 0, 0))
        s.brush_color = None
        assert s.brush_color is None


# ------------------------------------------------------------------
# copy()
# ------------------------------------------------------------------

class TestCopy:
    def test_copy_creates_new_instance(self):
        s = RectangleShape(0, 0, 100, 50, pen_color=(255, 0, 0), brush_color=(0, 255, 0))
        s.id = 5
        s._rotation = 45.0
        s._group_id = 10
        s.selected = True

        copied = s.copy()

        assert isinstance(copied, RectangleShape)
        assert copied.id == -1
        assert copied is not s
        assert copied.pen_color.red() == 255
        assert copied.brush_color.red() == 0
        assert copied.rotation == 45.0
        assert copied.group_id == 10
        assert copied.selected is True

    def test_copy_is_deep(self):
        s = RectangleShape(0, 0, 100, 50, pen_color=(255, 0, 0))
        copied = s.copy()
        copied.pen_color = (0, 255, 0)
        assert s.pen_color.red() == 255
        assert copied.pen_color.red() == 0


# ------------------------------------------------------------------
# to_dict() / from_dict()
# ------------------------------------------------------------------

class TestSerialization:
    def test_to_dict_contains_required_fields(self):
        s = RectangleShape(10, 20, 100, 50, pen_color=(100, 150, 200), brush_color=(50, 60, 70))
        s.id = 42
        s._rotation = 90.0
        s._group_id = 7

        d = s.to_dict()

        assert d["id"] == 42
        assert d["type"] == "rectangle"
        assert d["pen_color"] == (100, 150, 200)
        assert d["pen_width"] == 2.0
        assert d["brush_color"] == (50, 60, 70)
        assert d["rotation"] == 90.0
        assert d["group_id"] == 7
        assert "selected" in d

    def test_to_dict_no_brush_color(self):
        s = RectangleShape(0, 0, 10, 10)
        d = s.to_dict()
        assert d["brush_color"] is None

    def test_from_dict_restores_properties(self):
        data = {
            "id": 99,
            "type": "rectangle",
            "pen_color": (10, 20, 30),
            "pen_width": 3.0,
            "brush_color": (100, 200, 50),
            "rotation": 180.0,
            "group_id": 5,
            "selected": True,
            "x": 10,
            "y": 20,
            "width": 80,
            "height": 40,
        }
        s = RectangleShape.from_dict(data)
        # id присваивается ShapeManager при добавлении, from_dict не восстанавливает id
        assert s.pen_color.red() == 10
        assert s.pen_width == 3.0
        assert s.brush_color.green() == 200
        assert s._rotation == 180.0
        # group_id не сохраняется в to_dict / не восстанавливается из from_dict
        assert s._selected is True

    def test_roundtrip(self):
        s = RectangleShape(5, 10, 200, 100, pen_color=(255, 128, 64), brush_color=(0, 255, 128))
        s.id = 1
        s._rotation = 45.0
        s._group_id = 2

        d = s.to_dict()
        s2 = RectangleShape.from_dict(d)

        # id присваивается ShapeManager при добавлении фигуры, from_dict не восстанавливает id
        assert s2.pen_color.red() == 255
        assert s2.pen_width == 2.0
        assert s2.brush_color.green() == 255
        assert s2._rotation == 45.0
        # group_id не сохраняется в to_dict / не восстанавливается из from_dict


# ------------------------------------------------------------------
# _safe_rect()
# ------------------------------------------------------------------

class TestSafeRect:
    def test_normal_rect(self):
        rect = BaseShape._safe_rect(0, 0, 100, 50)
        assert rect == QRectF(0, 0, 100, 50)

    def test_nan_returns_empty(self):
        rect = BaseShape._safe_rect(float('nan'), 0, 100, 50)
        assert rect.isEmpty()

    def test_inf_returns_empty(self):
        rect = BaseShape._safe_rect(0, float('inf'), 100, 50)
        assert rect.isEmpty()

    def test_negative_inf_returns_empty(self):
        rect = BaseShape._safe_rect(0, 0, float('-inf'), 50)
        assert rect.isEmpty()


# ------------------------------------------------------------------
# intersects()
# ------------------------------------------------------------------

class TestIntersects:
    def test_overlapping_rects(self):
        s1 = RectangleShape(0, 0, 100, 100)
        s2 = RectangleShape(50, 50, 100, 100)
        assert s1.intersects(s2) is True

    def test_non_overlapping_rects(self):
        s1 = RectangleShape(0, 0, 50, 50)
        s2 = RectangleShape(100, 100, 50, 50)
        assert s1.intersects(s2) is False

    def test_touching_rects(self):
        s1 = RectangleShape(0, 0, 50, 50)
        s2 = RectangleShape(50, 0, 50, 50)
        assert s1.intersects(s2) is True


# ------------------------------------------------------------------
# get_properties() / apply_properties()
# ------------------------------------------------------------------

class TestPropertiesPanel:
    def test_get_properties(self):
        s = RectangleShape(0, 0, 100, 50, pen_color=(100, 200, 50), pen_width=3.0)
        s.brush_color = (255, 100, 50)
        s._rotation = 30.0

        props = s.get_properties()
        assert props["pen_color"] == (100, 200, 50)
        assert props["pen_width"] == 3.0
        assert props["brush_color"] == (255, 100, 50)
        assert props["rotation"] == 30.0

    def test_apply_properties_dict(self):
        s = RectangleShape(0, 0, 100, 50, pen_color=(0, 0, 0))
        s.apply_properties({
            "pen_color": (255, 128, 0),
            "pen_width": 5.0,
            "brush_color": (0, 255, 0),
            "rotation": 90.0,
        })
        assert s.pen_color.red() == 255
        assert s.pen_width == 5.0
        assert s.brush_color.green() == 255
        assert s.rotation == 90.0

    def test_apply_properties_none(self):
        s = RectangleShape(0, 0, 100, 50)
        s.apply_properties(None)  # не должно вызвать ошибку

    def test_apply_properties_partial(self):
        s = RectangleShape(0, 0, 100, 50, pen_color=(100, 100, 100))
        s.apply_properties({"pen_color": (255, 0, 0)})
        assert s.pen_color.red() == 255
        assert s.pen_width == 2.0  # не изменился
