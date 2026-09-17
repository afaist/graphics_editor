"""Тесты для ShapeRegistry — регистрация, создание, очистка."""

import pytest
from PySide6.QtGui import QColor
from shapes.registry import ShapeRegistry
from shapes.base_shape import BaseShape, HandleType
from shapes.rectangle_shape import RectangleShape


class TestShapeRegistry:
    """Тесты для ShapeRegistry."""

    def setup_method(self):
        ShapeRegistry.clear()

    def teardown_method(self):
        ShapeRegistry.clear()

    def test_register_and_get_factory(self):
        def factory(data):
            return None

        ShapeRegistry.register("test_type", factory)
        factory_result = ShapeRegistry.get_factory("test_type")
        assert factory_result is factory

    def test_get_factory_unknown_type(self):
        result = ShapeRegistry.get_factory("unknown_type")
        assert result is None

    def test_create_with_registered_factory(self):
        created_shapes = []

        def factory(data):
            s = RectangleShape.__new__(RectangleShape)
            s.id = data.get("id", -1)
            s._x = 0
            s._y = 0
            s._width = 10
            s._height = 10
            s._rotation = 0.0
            s._selected = False
            s._group_id = None
            s._pen_color = QColor(0, 0, 0)
            s._pen_width = 1.0
            s._brush_color = None
            created_shapes.append(s)
            return s

        ShapeRegistry.register("test", factory)
        result = ShapeRegistry.create("test", {"id": 1})

        assert result is not None
        assert result.id == 1
        assert len(created_shapes) == 1

    def test_create_with_unknown_type(self):
        result = ShapeRegistry.create("unknown", {})
        assert result is None

    def test_register_all(self):
        ShapeRegistry.register_all()

        # Проверяем, что все основные типы зарегистрированы
        expected_types = [
            "point", "line", "ray", "infinite_line",
            "rectangle", "ellipse", "polygon", "polyline",
            "arc", "text",
            "triangle_equilateral", "triangle_isosceles",
            "triangle_right", "triangle_obtuse",
            "parallelogram",
            "trapezoid_isosceles", "trapezoid",
        ]

        for shape_type in expected_types:
            factory = ShapeRegistry.get_factory(shape_type)
            assert factory is not None, f"Factory for {shape_type} not registered"

    def test_clear(self):
        ShapeRegistry.register_all()
        ShapeRegistry.clear()

        assert ShapeRegistry.get_factory("rectangle") is None
        assert ShapeRegistry.get_factory("point") is None

    def test_clear_does_not_affect_other_types(self):
        ShapeRegistry.register("custom", lambda d: None)
        ShapeRegistry.clear()
        assert ShapeRegistry.get_factory("custom") is None

    def test_get_shape_class(self):
        ShapeRegistry.register_all()

        rect_class = ShapeRegistry.get_shape_class("rectangle")
        assert rect_class is not None

        from shapes.rectangle_shape import RectangleShape
        assert rect_class is RectangleShape

    def test_get_shape_class_unknown(self):
        result = ShapeRegistry.get_shape_class("unknown_type")
        assert result is None

    def test_get_shape_class_caches(self):
        ShapeRegistry.register_all()

        class1 = ShapeRegistry.get_shape_class("rectangle")
        class2 = ShapeRegistry.get_shape_class("rectangle")
        assert class1 is class2

    def test_multiple_registrations_override(self):
        factory1 = lambda d: "first"
        factory2 = lambda d: "second"

        ShapeRegistry.register("test", factory1)
        assert ShapeRegistry.get_factory("test")(None) == "first"

        ShapeRegistry.register("test", factory2)
        assert ShapeRegistry.get_factory("test")(None) == "second"
