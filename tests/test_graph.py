"""Тесты для GraphShape."""

from __future__ import annotations

from PySide6.QtCore import QPointF

from shapes.graph_shape import GRAPH_FUNCTIONS, GraphShape

GRAPH_KWARGS = {
    "func_name": "linear",
    "params": {},
    "pen_color": (0, 0, 0),
    "pen_width": 1.0,
    "width": 450,
    "height": 300,
    "font_size": 10,
    "x_range": 10,
    "x_steps": 500,
}


def _make_graph(**overrides) -> GraphShape:
    kwargs = {**GRAPH_KWARGS, **overrides}
    x = kwargs.pop("x", 0)
    y = kwargs.pop("y", 0)
    return GraphShape(x, y, **kwargs)


class TestGraphCreation:
    """Тесты создания графика."""

    def test_create_default_graph(self):
        graph = _make_graph()
        assert graph.func_name == "linear"
        assert graph.params == {}

    def test_create_with_params(self):
        graph = _make_graph(func_name="quadratic", params={"a": 2.0, "b": 3.0, "c": 1.0})
        assert graph.func_name == "quadratic"
        assert graph.params == {"a": 2.0, "b": 3.0, "c": 1.0}

    def test_create_with_pen(self):
        graph = _make_graph(pen_color=(255, 0, 0), pen_width=3)
        assert graph._pen.widthF() == 3
        assert graph._pen.color().red() == 255

    def test_all_graph_functions_exist(self):
        expected = ["linear", "quadratic", "sin", "cos", "tan", "log", "exp", "sqrt"]
        assert list(GRAPH_FUNCTIONS.keys()) == expected


class TestGraphProperties:
    """Тесты свойств графика."""

    def test_set_func_name(self):
        graph = _make_graph()
        graph.func_name = "quadratic"
        assert graph.func_name == "quadratic"
        assert graph._render_dirty is True

    def test_set_params(self):
        graph = _make_graph()
        graph.params = {"a": 2.0}
        assert graph.params == {"a": 2.0}
        assert graph._render_dirty is True


class TestGraphBoundingRect:
    """Тесты bounding_rect."""

    def test_empty_bounding_rect(self):
        graph = _make_graph()
        br = graph.bounding_rect()
        assert br.width() > 0
        assert br.height() > 0

    def test_bounding_rect_contains_position(self):
        graph = _make_graph(x=50, y=50)
        br = graph.bounding_rect()
        assert br.contains(QPointF(50, 50))


class TestGraphContains:
    """Тесты contains."""

    def test_point_inside(self):
        graph = _make_graph()
        br = graph.bounding_rect()
        assert graph.contains_point(QPointF(br.center()))

    def test_point_outside(self):
        graph = _make_graph()
        assert graph.contains_point(QPointF(-1000, -1000)) is False


class TestGraphHandles:
    """Тесты маркеров преобразования."""

    def test_get_handles(self):
        graph = _make_graph()
        handles = graph.get_handles()
        assert len(handles) == 4

    def test_get_handle_type_none(self):
        graph = _make_graph()
        assert graph.get_handle_type(QPointF(-9999, -9999)).name == "NONE"


class TestGraphSerialization:
    """Тесты сериализации."""

    def test_to_dict(self):
        graph = _make_graph(func_name="sin", params={"a": 2.0, "b": 1.5}, x=10, y=20)
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
            "width": 450,
            "height": 300,
            "font_size": 10,
            "x_range": 10,
            "x_steps": 500,
        }
        graph = GraphShape.from_dict(data)
        assert graph._x == 100
        assert graph._y == 200
        assert graph.func_name == "cos"
        assert graph.params["a"] == 1.0

    def test_roundtrip(self):
        original = _make_graph(x=50, y=75, func_name="exp", params={"a": 3.0, "b": 0.5})
        data = original.to_dict()
        restored = GraphShape.from_dict(data)
        assert restored.func_name == original.func_name
        assert restored.params == original.params


class TestGraphRotateScale:
    """Тесты rotate и scale (no-op)."""

    def test_rotate_is_noop(self):
        graph = _make_graph()
        graph.rotate(90)
        assert graph._x == 0

    def test_scale_is_noop(self):
        graph = _make_graph()
        graph.scale(2.0)
        assert graph._x == 0


class TestTangentSegmentation:
    """Тесты для корректной обработки тангенса с разрывами."""

    def test_tangent_has_plot_method(self):
        """Проверяет, что у GraphShape есть метод для рисования тангенса."""
        graph = _make_graph(func_name="tan")
        assert hasattr(graph, "_plot_tangent")
        assert callable(getattr(graph, "_plot_tangent"))

    def test_tangent_bounding_rect(self):
        """Проверяет bounding rect для тангенса."""
        graph = _make_graph(func_name="tan", x=10, y=20)
        rect = graph.bounding_rect()
        assert rect.x() == 10
        assert rect.y() == 20

    def test_tangent_params(self):
        """Проверяет параметры тангенса."""
        graph = _make_graph(func_name="tan", params={"a": 2.0, "b": 1.5})
        assert graph.func_name == "tan"
        assert graph.params == {"a": 2.0, "b": 1.5}

    def test_tangent_to_dict(self):
        """Проверяет сериализацию тангенса."""
        graph = _make_graph(func_name="tan", params={"a": 1.5, "b": 2.0})
        data = graph.to_dict()
        assert data["func_name"] == "tan"
        assert data["params"]["a"] == 1.5
        assert data["params"]["b"] == 2.0

    def test_tangent_from_dict(self):
        """Проверяет десериализацию тангенса."""
        data = {
            "type": "graph",
            "x": 0,
            "y": 0,
            "width": 450,
            "height": 300,
            "func_name": "tan",
            "params": {"a": 1.0, "b": 1.0},
            "pen_color": [0, 0, 0],
            "pen_width": 2.0,
            "font_size": 10,
            "x_range": 10,
            "x_steps": 500,
        }
        graph = GraphShape.from_dict(data)
        assert graph.func_name == "tan"
        assert graph.params == {"a": 1.0, "b": 1.0}
