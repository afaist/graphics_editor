"""Тесты для GraphShape."""

from __future__ import annotations

from PySide6.QtCore import QPointF

from shapes.graph_shape import GRAPH_FUNCTIONS, GraphShape


class TestGraphCreation:
    """Тесты создания графика."""

    def test_create_default_graph(self):
        graph = GraphShape(0, 0)
        assert graph.func_name == "linear"
        assert graph.params == {}

    def test_create_with_params(self):
        graph = GraphShape(10, 20, func_name="quadratic", params={"a": 2.0, "b": 3.0, "c": 1.0})
        assert graph.func_name == "quadratic"
        assert graph.params == {"a": 2.0, "b": 3.0, "c": 1.0}

    def test_create_with_pen(self):
        graph = GraphShape(0, 0, pen_color=(255, 0, 0), pen_width=3)
        assert graph._pen.widthF() == 3
        assert graph._pen.color().red() == 255

    def test_all_graph_functions_exist(self):
        expected = ["linear", "quadratic", "sin", "cos", "tan", "log", "exp", "sqrt"]
        assert list(GRAPH_FUNCTIONS.keys()) == expected


class TestGraphProperties:
    """Тесты свойств графика."""

    def test_set_func_name(self):
        graph = GraphShape(0, 0)
        graph.func_name = "quadratic"
        assert graph.func_name == "quadratic"
        assert graph._render_dirty is True

    def test_set_params(self):
        graph = GraphShape(0, 0)
        graph.params = {"a": 2.0}
        assert graph.params == {"a": 2.0}
        assert graph._render_dirty is True


class TestGraphBoundingRect:
    """Тесты bounding_rect."""

    def test_empty_bounding_rect(self):
        graph = GraphShape(0, 0)
        br = graph.bounding_rect()
        assert br.width() > 0
        assert br.height() > 0

    def test_bounding_rect_contains_position(self):
        graph = GraphShape(50, 50)
        br = graph.bounding_rect()
        assert br.contains(QPointF(50, 50))


class TestGraphContains:
    """Тесты contains."""

    def test_point_inside(self):
        graph = GraphShape(0, 0)
        br = graph.bounding_rect()
        assert graph.contains_point(QPointF(br.center()))

    def test_point_outside(self):
        graph = GraphShape(0, 0)
        assert graph.contains_point(QPointF(-1000, -1000)) is False


class TestGraphHandles:
    """Тесты маркеров преобразования."""

    def test_get_handles(self):
        graph = GraphShape(0, 0)
        handles = graph.get_handles()
        assert len(handles) == 4

    def test_get_handle_type_none(self):
        graph = GraphShape(0, 0)
        assert graph.get_handle_type(QPointF(-9999, -9999)).name == "NONE"


class TestGraphSerialization:
    """Тесты сериализации."""

    def test_to_dict(self):
        graph = GraphShape(10, 20, func_name="sin", params={"a": 2.0, "b": 1.5})
        data = graph.to_dict()
        assert data["type"] == "graph"
        assert data["x"] == 10
        assert data["y"] == 20
        assert data["func_name"] == "sin"
        assert data["params"]["a"] == 2.0

    def test_from_dict(self):
        data = {
            "type": "graph",
            "x": 100,
            "y": 200,
            "func_name": "cos",
            "params": {"a": 1.0, "b": 2.0},
            "pen_color": [0, 0, 0],
            "pen_width": 2,
        }
        graph = GraphShape.from_dict(data)
        assert graph._x == 100
        assert graph._y == 200
        assert graph.func_name == "cos"
        assert graph.params["a"] == 1.0

    def test_roundtrip(self):
        original = GraphShape(50, 75, func_name="exp", params={"a": 3.0, "b": 0.5})
        data = original.to_dict()
        restored = GraphShape.from_dict(data)
        assert restored.func_name == original.func_name
        assert restored.params == original.params


class TestGraphRotateScale:
    """Тесты rotate и scale (no-op)."""

    def test_rotate_is_noop(self):
        graph = GraphShape(0, 0)
        graph.rotate(90)
        assert graph._x == 0

    def test_scale_is_noop(self):
        graph = GraphShape(0, 0)
        graph.scale(2.0)
        assert graph._x == 0
