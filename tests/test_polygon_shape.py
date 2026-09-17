"""Тесты для PolygonShape — вершины, area, perimeter, трансформации."""

import pytest
from PySide6.QtCore import QPointF

from shapes.polygon_shape import PolygonShape
from shapes.base_shape import HandleType


class TestPolygonCreation:
    def test_empty_polygon(self):
        p = PolygonShape()
        assert p.vertex_count() == 0

    def test_polygon_with_vertices(self):
        p = PolygonShape(vertices=[(0, 0), (100, 0), (100, 100)])
        assert p.vertex_count() == 3

    def test_vertices_property(self):
        p = PolygonShape(vertices=[(0, 0), (100, 0)])
        verts = p.vertices
        assert len(verts) == 2


class TestPolygonVertexOperations:
    def test_add_vertex(self):
        p = PolygonShape()
        p.add_vertex(10, 20)
        assert p.vertex_count() == 1
        assert abs(p.vertices[0].x() - 10) < 1e-9

    def test_remove_vertex(self):
        p = PolygonShape(vertices=[(0, 0), (10, 10), (20, 20)])
        p.remove_vertex(1)
        assert p.vertex_count() == 2

    def test_remove_vertex_invalid_index(self):
        p = PolygonShape(vertices=[(0, 0)])
        p.remove_vertex(5)  # не должно вызвать ошибку
        assert p.vertex_count() == 1

    def test_insert_vertex(self):
        p = PolygonShape(vertices=[(0, 0), (20, 20)])
        p.insert_vertex(1, 10, 10)
        assert p.vertex_count() == 3
        assert abs(p.vertices[1].x() - 10) < 1e-9

    def test_insert_vertex_at_end(self):
        p = PolygonShape(vertices=[(0, 0)])
        p.insert_vertex(1, 10, 10)
        assert p.vertex_count() == 2


class TestPolygonArea:
    def test_square_area(self):
        p = PolygonShape(vertices=[(0, 0), (100, 0), (100, 100), (0, 100)])
        assert abs(p.area() - 10000.0) < 1e-6

    def test_triangle_area(self):
        p = PolygonShape(vertices=[(0, 0), (10, 0), (0, 10)])
        assert abs(p.area() - 50.0) < 1e-6

    def test_empty_polygon_area(self):
        p = PolygonShape()
        assert p.area() == 0.0

    def test_two_vertices_area(self):
        p = PolygonShape(vertices=[(0, 0), (10, 10)])
        assert p.area() == 0.0


class TestPolygonPerimeter:
    def test_square_perimeter(self):
        p = PolygonShape(vertices=[(0, 0), (100, 0), (100, 100), (0, 100)])
        assert abs(p.perimeter() - 400.0) < 1e-6

    def test_empty_polygon_perimeter(self):
        p = PolygonShape()
        assert p.perimeter() == 0.0

    def test_one_vertex_perimeter(self):
        p = PolygonShape(vertices=[(50, 50)])
        assert p.perimeter() == 0.0


class TestPolygonMove:
    def test_move(self):
        p = PolygonShape(vertices=[(0, 0), (100, 0), (100, 100)])
        p.move(10, 20)
        assert abs(p.vertices[0].x() - 10) < 1e-9
        assert abs(p.vertices[0].y() - 20) < 1e-9
        assert abs(p.vertices[2].x() - 110) < 1e-9


class TestPolygonScale:
    def test_scale(self):
        # Масштабирование от центроида: центр = (66.67, 33.33)
        p = PolygonShape(vertices=[(0, 0), (100, 0), (100, 100)])
        p.scale(2.0)
        # vertices[1] = (100, 0): x = 66.67 + (100-66.67)*2 = 133.33
        assert abs(p.vertices[1].x() - 133.33333333333331) < 0.01

    def test_scale_zero(self):
        with pytest.raises(ValueError, match="positive"):
            p = PolygonShape(vertices=[(0, 0), (100, 0)])
            p.scale(0)

    def test_scale_negative(self):
        with pytest.raises(ValueError, match="positive"):
            p = PolygonShape(vertices=[(0, 0), (100, 0)])
            p.scale(-1.0)


class TestPolygonRotate:
    def test_rotate(self):
        p = PolygonShape(vertices=[(0, 0), (100, 0), (100, 100)])
        p.rotate(90)
        # Вершины должны быть повернуты
        assert len(p.vertices) == 3

    def test_rotate_empty(self):
        p = PolygonShape()
        p.rotate(45)  # не должно вызвать ошибку


class TestPolygonContains:
    def test_point_inside_square(self):
        p = PolygonShape(vertices=[(0, 0), (100, 0), (100, 100), (0, 100)])
        assert p.contains_point(QPointF(50, 50)) is True

    def test_point_outside(self):
        p = PolygonShape(vertices=[(0, 0), (100, 0), (100, 100), (0, 100)])
        assert p.contains_point(QPointF(200, 200)) is False

    def test_too_few_vertices(self):
        p = PolygonShape(vertices=[(0, 0), (100, 0)])
        assert p.contains_point(QPointF(50, 0)) is False


class TestPolygonBoundingRect:
    def test_bounding_rect(self):
        p = PolygonShape(vertices=[(10, 20), (110, 20), (110, 120), (10, 120)])
        br = p.bounding_rect()
        assert br.left() <= 10
        assert br.top() <= 20
        assert br.right() >= 110
        assert br.bottom() >= 120

    def test_empty_polygon_bounding_rect(self):
        p = PolygonShape()
        br = p.bounding_rect()
        assert br.width() == 0
        assert br.height() == 0


class TestPolygonHandles:
    def test_get_handles(self):
        p = PolygonShape(vertices=[(0, 0), (100, 0), (100, 100)])
        handles = p.get_handles()
        assert len(handles) == 3

    def test_get_handle_type_vertex(self):
        p = PolygonShape(vertices=[(0, 0), (100, 0)])
        ht = p.get_handle_type(QPointF(0, 0), tolerance=5.0)
        assert ht != HandleType.NONE

    def test_get_handle_type_none(self):
        p = PolygonShape(vertices=[(0, 0), (100, 0)])
        ht = p.get_handle_type(QPointF(500, 500), tolerance=5.0)
        assert ht == HandleType.NONE


class TestPolygonApplyHandleTransform:
    def test_move_vertex(self):
        p = PolygonShape(vertices=[(0, 0), (100, 0), (100, 100)])
        p.apply_handle_transform(HandleType.TOP_LEFT, QPointF(0, 0), QPointF(10, 10))
        assert abs(p.vertices[0].x() - 10) < 1e-9


class TestPolygonSerialization:
    def test_to_dict(self):
        p = PolygonShape(vertices=[(0, 0), (100, 0), (100, 100)])
        d = p.to_dict()
        assert d["type"] == "polygon"
        assert len(d["vertices"]) == 3
        assert d["vertices"][0]["x"] == 0

    def test_from_dict(self):
        data = {
            "id": 1,
            "type": "polygon",
            "pen_color": (255, 0, 0),
            "pen_width": 2.0,
            "brush_color": (0, 255, 0),
            "rotation": 0.0,
            "group_id": None,
            "selected": False,
            "vertices": [{"x": 0, "y": 0}, {"x": 100, "y": 0}, {"x": 100, "y": 100}],
        }
        p = PolygonShape.from_dict(data)
        assert p.vertex_count() == 3
        assert abs(p.vertices[1].x() - 100) < 1e-9

    def test_roundtrip(self):
        p = PolygonShape(vertices=[(0, 0), (50, 50), (100, 0)])
        p.id = 42
        d = p.to_dict()
        p2 = PolygonShape.from_dict(d)
        assert p2.vertex_count() == 3
        assert abs(p2.vertices[1].x() - 50) < 1e-9
