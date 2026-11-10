"""Тесты для SharyginTriangleShape — треугольник Шарыгина."""

from __future__ import annotations

import math

from PySide6.QtCore import QPointF

from shapes.base_shape import HandleType
from shapes.sharygin_triangle_shape import SharyginTriangleShape


class TestSharyginTriangleCreation:
    def test_default_creation(self):
        vertices = [(0, 0), (100, 0), (50, 86.6)]
        st = SharyginTriangleShape(vertices)
        assert len(st.original_vertices) == 3
        assert len(st.sharygin_vertices) == 3

    def test_size_parameter(self):
        vertices = [(0, 0), (100, 0), (50, 86.6)]
        st = SharyginTriangleShape(vertices, size=300)
        assert st.size == 300

    def test_shape_type(self):
        vertices = [(0, 0), (100, 0), (50, 86.6)]
        st = SharyginTriangleShape(vertices)
        assert st.shape_type.value == "triangle_sharygin"


class TestSharyginTriangleGeometry:
    def test_sharygin_vertices_inside_original(self):
        """Вершины треугольника Шарыгина лежат на сторонах исходного."""
        vertices = [(0, 0), (100, 0), (50, 86.6)]
        st = SharyginTriangleShape(vertices)
        for v in st.sharygin_vertices:
            # Каждая вершина должна быть внутри или на границе оригинального треугольника
            assert st.contains_point(v)

    def test_sharygin_vertices_count(self):
        vertices = [(0, 0), (100, 0), (50, 86.6)]
        st = SharyginTriangleShape(vertices)
        assert len(st.sharygin_vertices) == 3

    def test_original_vertices_preserved(self):
        vertices = [(0, 0), (100, 0), (50, 86.6)]
        st = SharyginTriangleShape(vertices)
        for i, (orig, expected) in enumerate(zip(st.original_vertices, vertices)):
            assert abs(orig.x() - expected[0]) < 0.01
            assert abs(orig.y() - expected[1]) < 0.01


class TestSharyginTriangleMove:
    def test_move_both_sets(self):
        vertices = [(0, 0), (100, 0), (50, 86.6)]
        st = SharyginTriangleShape(vertices)
        st.move(10, 20)
        for v in st.original_vertices:
            assert v.x() >= 10
        for v in st.sharygin_vertices:
            assert v.x() >= 10


class TestSharyginTriangleScale:
    def test_scale_up(self):
        vertices = [(0, 0), (100, 0), (50, 86.6)]
        st = SharyginTriangleShape(vertices)
        st.scale(2.0)
        s = math.hypot(
            st.original_vertices[1].x() - st.original_vertices[0].x(),
            st.original_vertices[1].y() - st.original_vertices[0].y(),
        )
        assert abs(s - 200) < 0.01

    def test_scale_down(self):
        vertices = [(0, 0), (100, 0), (50, 86.6)]
        st = SharyginTriangleShape(vertices)
        st.scale(0.5)
        s = math.hypot(
            st.original_vertices[1].x() - st.original_vertices[0].x(),
            st.original_vertices[1].y() - st.original_vertices[0].y(),
        )
        assert abs(s - 50) < 0.01


class TestSharyginTriangleContainsPoint:
    def test_point_in_original_triangle(self):
        vertices = [(0, 0), (100, 0), (50, 86.6)]
        st = SharyginTriangleShape(vertices)
        assert st.contains_point(QPointF(50, 20))

    def test_point_in_sharygin_triangle(self):
        vertices = [(0, 0), (100, 0), (50, 86.6)]
        st = SharyginTriangleShape(vertices)
        # Центр треугольника Шарыгина
        cx = sum(v.x() for v in st.sharygin_vertices) / 3
        cy = sum(v.y() for v in st.sharygin_vertices) / 3
        assert st.contains_point(QPointF(cx, cy))

    def test_point_outside(self):
        vertices = [(0, 0), (100, 0), (50, 86.6)]
        st = SharyginTriangleShape(vertices)
        assert not st.contains_point(QPointF(200, 200))


class TestSharyginTriangleBoundingRect:
    def test_bounding_rect_contains_both(self):
        vertices = [(0, 0), (100, 0), (50, 86.6)]
        st = SharyginTriangleShape(vertices)
        br = st.bounding_rect()
        assert br.left() <= 0
        assert br.right() >= 100
        assert br.top() <= 0
        assert br.bottom() >= 86.6


class TestSharyginTriangleHandles:
    def test_get_handles_returns_6(self):
        vertices = [(0, 0), (100, 0), (50, 86.6)]
        st = SharyginTriangleShape(vertices)
        handles = st.get_handles()
        assert len(handles) == 6

    def test_handles_types(self):
        vertices = [(0, 0), (100, 0), (50, 86.6)]
        st = SharyginTriangleShape(vertices)
        handles = st.get_handles()
        for h in handles:
            ht = st.get_handle_type(h, tolerance=5.0)
            assert ht != HandleType.NONE


class TestSharyginTriangleApplyHandleTransform:
    def test_apply_handle_transform_changes_vertex(self):
        vertices = [(0, 0), (100, 0), (50, 86.6)]
        st = SharyginTriangleShape(vertices)
        initial_x = st.original_vertices[0].x()
        st.apply_handle_transform(
            HandleType.TOP_LEFT,
            QPointF(0, 0),
            QPointF(20, 20),
        )
        assert st.original_vertices[0].x() != initial_x

    def test_sharygin_recomputed_after_transform(self):
        vertices = [(0, 0), (100, 0), (50, 86.6)]
        st = SharyginTriangleShape(vertices)
        initial_sharygin = [QPointF(v.x(), v.y()) for v in st.sharygin_vertices]
        st.apply_handle_transform(
            HandleType.TOP_LEFT,
            QPointF(0, 0),
            QPointF(20, 20),
        )
        # Треугольник Шарыгина должен пересчитаться
        assert any(
            abs(v.x() - initial_sharygin[i].x()) > 0.01 for i, v in enumerate(st.sharygin_vertices)
        )


class TestSharyginTriangleSerialization:
    def test_to_dict_contains_required_fields(self):
        vertices = [(0, 0), (100, 0), (50, 86.6)]
        st = SharyginTriangleShape(vertices)
        d = st.to_dict()
        assert "original_vertices" in d
        assert "sharygin_vertices" in d
        assert "size" in d

    def test_from_dict_restores_shape(self):
        vertices = [(0, 0), (100, 0), (50, 86.6)]
        st = SharyginTriangleShape(vertices)
        d = st.to_dict()
        st2 = SharyginTriangleShape.from_dict(d)
        assert len(st2.original_vertices) == 3
        assert len(st2.sharygin_vertices) == 3

    def test_roundtrip_preserves_vertices(self):
        vertices = [(0, 0), (100, 0), (50, 86.6)]
        st = SharyginTriangleShape(vertices)
        d = st.to_dict()
        st2 = SharyginTriangleShape.from_dict(d)
        for i, (v1, v2) in enumerate(zip(st.original_vertices, st2.original_vertices)):
            assert abs(v1.x() - v2.x()) < 0.01
            assert abs(v1.y() - v2.y()) < 0.01
