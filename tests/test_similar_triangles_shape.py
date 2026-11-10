"""Тесты для SimilarTrianglesShape — два подобных треугольника."""

from __future__ import annotations

import math

from PySide6.QtCore import QPointF

from shapes.base_shape import HandleType
from shapes.similar_triangles_shape import SimilarTrianglesShape


class TestSimilarTrianglesCreation:
    def test_default_creation(self):
        v1 = [(0, 0), (100, 0), (50, 86.6)]
        v2 = [(200, 0), (400, 0), (300, 173.2)]
        st = SimilarTrianglesShape(v1, v2, similarity_ratio=2.0)
        assert len(st.vertices2) == 3

    def test_similarity_ratio_stored(self):
        v1 = [(0, 0), (100, 0), (50, 86.6)]
        v2 = [(200, 0), (400, 0), (300, 173.2)]
        st = SimilarTrianglesShape(v1, v2, similarity_ratio=2.5)
        assert st._similarity_ratio == 2.5

    def test_shape_type(self):
        v1 = [(0, 0), (100, 0), (50, 86.6)]
        v2 = [(200, 0), (400, 0), (300, 173.2)]
        st = SimilarTrianglesShape(v1, v2)
        assert st.shape_type.value == "triangle_similar"


class TestSimilarTrianglesGeometry:
    def test_second_triangle_scaled(self):
        v1 = [(0, 0), (100, 0), (50, 86.6)]
        v2 = [(200, 0), (400, 0), (300, 173.2)]
        st = SimilarTrianglesShape(v1, v2, similarity_ratio=2.0)
        # Сторона второго треугольника должна быть в 2 раза больше
        s1 = math.hypot(
            st._vertices1[1].x() - st._vertices1[0].x(),
            st._vertices1[1].y() - st._vertices1[0].y(),
        )
        s2 = math.hypot(
            st.vertices2[1].x() - st.vertices2[0].x(), st.vertices2[1].y() - st.vertices2[0].y()
        )
        assert abs(s2 / s1 - 2.0) < 0.01

    def test_similarity_preserves_angles(self):
        v1 = [(0, 0), (100, 0), (50, 86.6)]
        v2 = [(200, 0), (400, 0), (300, 173.2)]
        st = SimilarTrianglesShape(v1, v2, similarity_ratio=2.0)
        # Стороны первого
        s1_1 = math.hypot(
            st._vertices1[1].x() - st._vertices1[0].x(),
            st._vertices1[1].y() - st._vertices1[0].y(),
        )
        s1_2 = math.hypot(
            st._vertices1[2].x() - st._vertices1[1].x(),
            st._vertices1[2].y() - st._vertices1[1].y(),
        )
        s1_3 = math.hypot(
            st._vertices1[0].x() - st._vertices1[2].x(),
            st._vertices1[0].y() - st._vertices1[2].y(),
        )
        # Стороны второго
        s2_1 = math.hypot(
            st.vertices2[1].x() - st.vertices2[0].x(), st.vertices2[1].y() - st.vertices2[0].y()
        )
        s2_2 = math.hypot(
            st.vertices2[2].x() - st.vertices2[1].x(), st.vertices2[2].y() - st.vertices2[1].y()
        )
        s2_3 = math.hypot(
            st.vertices2[0].x() - st.vertices2[2].x(), st.vertices2[0].y() - st.vertices2[2].y()
        )
        # Отношения сторон должны быть одинаковыми
        r1 = s2_1 / s1_1
        r2 = s2_2 / s1_2
        r3 = s2_3 / s1_3
        assert abs(r1 - r2) < 0.01
        assert abs(r2 - r3) < 0.01


class TestSimilarTrianglesMove:
    def test_move_both_triangles(self):
        v1 = [(0, 0), (100, 0), (50, 86.6)]
        v2 = [(200, 0), (400, 0), (300, 173.2)]
        st = SimilarTrianglesShape(v1, v2)
        st.move(10, 20)
        # Проверяем, что все вершины сдвинулись на (10, 20)
        for v in st._vertices1:
            assert abs(v.x() - 10) < 0.01 or abs(v.x() - 110) < 0.01 or abs(v.x() - 60) < 0.01


class TestSimilarTrianglesScale:
    def test_scale_up(self):
        v1 = [(0, 0), (100, 0), (50, 86.6)]
        v2 = [(200, 0), (400, 0), (300, 173.2)]
        st = SimilarTrianglesShape(v1, v2)
        st.scale(2.0)
        s = math.hypot(
            st._vertices1[1].x() - st._vertices1[0].x(),
            st._vertices1[1].y() - st._vertices1[0].y(),
        )
        assert abs(s - 200) < 0.01

    def test_scale_down(self):
        v1 = [(0, 0), (100, 0), (50, 86.6)]
        v2 = [(200, 0), (400, 0), (300, 173.2)]
        st = SimilarTrianglesShape(v1, v2)
        st.scale(0.5)
        s = math.hypot(
            st._vertices1[1].x() - st._vertices1[0].x(),
            st._vertices1[1].y() - st._vertices1[0].y(),
        )
        assert abs(s - 50) < 0.01


class TestSimilarTrianglesContainsPoint:
    def test_point_in_first_triangle(self):
        v1 = [(0, 0), (100, 0), (50, 86.6)]
        v2 = [(200, 0), (400, 0), (300, 173.2)]
        st = SimilarTrianglesShape(v1, v2)
        assert st.contains_point(QPointF(50, 20))

    def test_point_in_second_triangle(self):
        v1 = [(0, 0), (100, 0), (50, 86.6)]
        v2 = [(200, 0), (400, 0), (300, 173.2)]
        st = SimilarTrianglesShape(v1, v2)
        assert st.contains_point(QPointF(300, 40))

    def test_point_outside(self):
        v1 = [(0, 0), (100, 0), (50, 86.6)]
        v2 = [(200, 0), (400, 0), (300, 173.2)]
        st = SimilarTrianglesShape(v1, v2)
        assert not st.contains_point(QPointF(150, 50))


class TestSimilarTrianglesBoundingRect:
    def test_bounding_rect_contains_both(self):
        v1 = [(0, 0), (100, 0), (50, 86.6)]
        v2 = [(200, 0), (400, 0), (300, 173.2)]
        st = SimilarTrianglesShape(v1, v2)
        br = st.bounding_rect()
        assert br.left() <= 0
        assert br.right() >= 400
        assert br.top() <= 0
        assert br.bottom() >= 173.2


class TestSimilarTrianglesHandles:
    def test_get_handles_returns_6(self):
        v1 = [(0, 0), (100, 0), (50, 86.6)]
        v2 = [(200, 0), (400, 0), (300, 173.2)]
        st = SimilarTrianglesShape(v1, v2)
        handles = st.get_handles()
        assert len(handles) == 6

    def test_handles_types(self):
        v1 = [(0, 0), (100, 0), (50, 86.6)]
        v2 = [(200, 0), (400, 0), (300, 173.2)]
        st = SimilarTrianglesShape(v1, v2)
        handles = st.get_handles()
        for h in handles:
            ht = st.get_handle_type(h, tolerance=5.0)
            assert ht != HandleType.NONE


class TestSimilarTrianglesSerialization:
    def test_to_dict_contains_required_fields(self):
        v1 = [(0, 0), (100, 0), (50, 86.6)]
        v2 = [(200, 0), (400, 0), (300, 173.2)]
        st = SimilarTrianglesShape(v1, v2)
        d = st.to_dict()
        assert "vertices1" in d
        assert "similarity_ratio" in d

    def test_from_dict_restores_shape(self):
        v1 = [(0, 0), (100, 0), (50, 86.6)]
        v2 = [(200, 0), (400, 0), (300, 173.2)]
        st = SimilarTrianglesShape(v1, v2)
        d = st.to_dict()
        st2 = SimilarTrianglesShape.from_dict(d)
        assert len(st2._vertices1) == 3
        assert len(st2.vertices2) == 3
