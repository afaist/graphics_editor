"""Тесты для PolylineShape — вершины, length, трансформации."""

import pytest
from PySide6.QtCore import QPointF

from shapes.polyline_shape import PolylineShape
from shapes.base_shape import HandleType


class TestPolylineCreation:
    def test_empty_polyline(self):
        p = PolylineShape()
        assert p.vertex_count() == 0

    def test_polyline_with_vertices(self):
        p = PolylineShape(vertices=[(0, 0), (50, 50), (100, 0)])
        assert p.vertex_count() == 3


class TestPolylineVertexOperations:
    def test_add_vertex(self):
        p = PolylineShape()
        p.add_vertex(10, 20)
        assert p.vertex_count() == 1

    def test_remove_vertex(self):
        p = PolylineShape(vertices=[(0, 0), (10, 10), (20, 20)])
        p.remove_vertex(1)
        assert p.vertex_count() == 2

    def test_remove_vertex_last_not_allowed(self):
        p = PolylineShape(vertices=[(0, 0), (10, 10), (20, 20)])
        p.remove_vertex(2)  # последнюю нельзя удалить
        assert p.vertex_count() == 3

    def test_clear(self):
        p = PolylineShape(vertices=[(0, 0), (10, 10)])
        p.clear()
        assert p.vertex_count() == 0

    def test_add_points_from_list(self):
        from PySide6.QtCore import QPointF
        p = PolylineShape(vertices=[(0, 0)])
        p.add_points_from_list([QPointF(10, 10), QPointF(20, 20)])
        assert p.vertex_count() == 3


class TestPolylineLength:
    def test_two_vertices(self):
        p = PolylineShape(vertices=[(0, 0), (3, 4)])
        assert abs(p.length() - 5.0) < 1e-9

    def test_three_vertices(self):
        p = PolylineShape(vertices=[(0, 0), (10, 0), (10, 10)])
        assert abs(p.length() - 20.0) < 1e-9

    def test_empty_polyline_length(self):
        p = PolylineShape()
        assert p.length() == 0.0

    def test_single_vertex_length(self):
        p = PolylineShape(vertices=[(0, 0)])
        assert p.length() == 0.0


class TestPolylineMove:
    def test_move(self):
        p = PolylineShape(vertices=[(0, 0), (50, 50), (100, 0)])
        p.move(10, -5)
        assert abs(p.vertices[0].x() - 10) < 1e-9
        assert abs(p.vertices[0].y() - (-5)) < 1e-9
        assert abs(p.vertices[1].x() - 60) < 1e-9


class TestPolylineScale:
    def test_scale(self):
        # Масштабирование от центроида: центр = (66.67, 33.33)
        p = PolylineShape(vertices=[(0, 0), (100, 0), (100, 100)])
        p.scale(2.0)
        # vertices[1] = (100, 0): x = 66.67 + (100-66.67)*2 = 133.33
        assert abs(p.vertices[1].x() - 133.33333333333331) < 0.01


class TestPolylineRotate:
    def test_rotate(self):
        p = PolylineShape(vertices=[(0, 0), (100, 0), (100, 100)])
        p.rotate(90)
        assert len(p.vertices) == 3

    def test_rotate_empty(self):
        p = PolylineShape()
        p.rotate(45)  # не должно вызвать ошибку


class TestPolylineBoundingRect:
    def test_bounding_rect(self):
        p = PolylineShape(vertices=[(10, 20), (110, 20), (110, 120)])
        br = p.bounding_rect()
        assert br.left() <= 10
        assert br.right() >= 110
        assert br.top() <= 20
        assert br.bottom() >= 120

    def test_empty_polyline_bounding_rect(self):
        p = PolylineShape()
        br = p.bounding_rect()
        assert br.width() == 0
        assert br.height() == 0


class TestPolylineHandles:
    def test_get_handles(self):
        p = PolylineShape(vertices=[(0, 0), (50, 50), (100, 0)])
        handles = p.get_handles()
        assert len(handles) == 3

    def test_get_handle_type_vertex(self):
        p = PolylineShape(vertices=[(0, 0), (100, 0)])
        ht = p.get_handle_type(QPointF(0, 0), tolerance=5.0)
        assert ht != HandleType.NONE

    def test_get_handle_type_none(self):
        p = PolylineShape(vertices=[(0, 0), (100, 0)])
        ht = p.get_handle_type(QPointF(500, 500), tolerance=5.0)
        assert ht == HandleType.NONE


class TestPolylineApplyHandleTransform:
    def test_move_vertex(self):
        p = PolylineShape(vertices=[(0, 0), (100, 0)])
        p.apply_handle_transform(HandleType.TOP_LEFT, QPointF(0, 0), QPointF(10, 10))
        assert abs(p.vertices[0].x() - 10) < 1e-9


class TestPolylineSerialization:
    def test_to_dict(self):
        p = PolylineShape(vertices=[(0, 0), (50, 50), (100, 0)])
        d = p.to_dict()
        assert d["type"] == "polyline"
        assert len(d["vertices"]) == 3

    def test_from_dict(self):
        data = {
            "id": 1,
            "type": "polyline",
            "pen_color": (0, 0, 255),
            "pen_width": 3.0,
            "brush_color": None,
            "rotation": 0.0,
            "group_id": None,
            "selected": False,
            "vertices": [{"x": 0, "y": 0}, {"x": 50, "y": 50}, {"x": 100, "y": 0}],
        }
        p = PolylineShape.from_dict(data)
        assert p.vertex_count() == 3

    def test_roundtrip(self):
        p = PolylineShape(vertices=[(0, 0), (30, 40), (60, 0)])
        p.id = 42
        d = p.to_dict()
        p2 = PolylineShape.from_dict(d)
        assert p2.vertex_count() == 3
        assert abs(p2.vertices[1].x() - 30) < 1e-9
