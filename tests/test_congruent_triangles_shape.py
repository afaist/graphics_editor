"""Тесты для CongruentTrianglesShape — два равных треугольника."""

from __future__ import annotations

import math

from PySide6.QtCore import QPointF

from shapes.base_shape import HandleType
from shapes.congruent_triangles_shape import CongruentTrianglesShape


class TestCongruentTrianglesCreation:
    def test_default_creation(self):
        v1 = [(0, 0), (100, 0), (50, 86.6)]
        v2 = [(200, 0), (300, 0), (250, 86.6)]
        ct = CongruentTrianglesShape(v1, v2)
        assert len(ct.vertices2) == 3

    def test_vertices2_is_copy(self):
        v1 = [(0, 0), (100, 0), (50, 86.6)]
        v2 = [(200, 0), (300, 0), (250, 86.6)]
        ct = CongruentTrianglesShape(v1, v2)
        vertices2 = ct.vertices2
        for i, v2_v in enumerate(vertices2):
            assert abs(v2_v.x() - v2[i][0]) < 0.01
            assert abs(v2_v.y() - v2[i][1]) < 0.01

    def test_shape_type(self):
        v1 = [(0, 0), (100, 0), (50, 86.6)]
        v2 = [(200, 0), (300, 0), (250, 86.6)]
        ct = CongruentTrianglesShape(v1, v2)
        assert ct.shape_type.value == "triangle_congruent"


class TestCongruentTrianglesGeometry:
    def test_offset_preserved(self):
        v1 = [(0, 0), (100, 0), (50, 86.6)]
        v2 = [(50, 50), (150, 50), (100, 136.6)]
        ct = CongruentTrianglesShape(v1, v2)
        assert ct._offset.x() == 50
        assert ct._offset.y() == 50

    def test_second_triangle_is_shifted(self):
        v1 = [(0, 0), (100, 0), (50, 86.6)]
        v2 = [(100, 100), (200, 100), (150, 186.6)]
        ct = CongruentTrianglesShape(v1, v2)
        for i, (v1_v, v2_v) in enumerate(zip(ct._vertices1, ct.vertices2)):
            dx = v2_v.x() - v1_v.x()
            dy = v2_v.y() - v1_v.y()
            assert abs(dx - 100) < 0.01
            assert abs(dy - 100) < 0.01

    def test_triangles_are_congruent(self):
        v1 = [(0, 0), (100, 0), (50, 86.6)]
        v2 = [(200, 200), (300, 200), (250, 286.6)]
        ct = CongruentTrianglesShape(v1, v2)
        # Стороны первого треугольника
        s1_1 = math.hypot(
            ct._vertices1[1].x() - ct._vertices1[0].x(),
            ct._vertices1[1].y() - ct._vertices1[0].y(),
        )
        s1_2 = math.hypot(
            ct._vertices1[2].x() - ct._vertices1[1].x(),
            ct._vertices1[2].y() - ct._vertices1[1].y(),
        )
        s1_3 = math.hypot(
            ct._vertices1[0].x() - ct._vertices1[2].x(),
            ct._vertices1[0].y() - ct._vertices1[2].y(),
        )
        # Стороны второго треугольника
        s2_1 = math.hypot(
            ct.vertices2[1].x() - ct.vertices2[0].x(), ct.vertices2[1].y() - ct.vertices2[0].y()
        )
        s2_2 = math.hypot(
            ct.vertices2[2].x() - ct.vertices2[1].x(), ct.vertices2[2].y() - ct.vertices2[1].y()
        )
        s2_3 = math.hypot(
            ct.vertices2[0].x() - ct.vertices2[2].x(), ct.vertices2[0].y() - ct.vertices2[2].y()
        )
        assert abs(s1_1 - s2_1) < 0.01
        assert abs(s1_2 - s2_2) < 0.01
        assert abs(s1_3 - s2_3) < 0.01


class TestCongruentTrianglesMove:
    def test_move_both_triangles(self):
        v1 = [(0, 0), (100, 0), (50, 86.6)]
        v2 = [(200, 0), (300, 0), (250, 86.6)]
        ct = CongruentTrianglesShape(v1, v2)
        ct.move(10, 20)
        # Проверяем, что все вершины сдвинулись на (10, 20)
        for v in ct._vertices1:
            assert abs(v.x() - 10) < 0.01 or abs(v.x() - 110) < 0.01 or abs(v.x() - 60) < 0.01
        for v in ct.vertices2:
            assert abs(v.x() - 210) < 0.01 or abs(v.x() - 310) < 0.01 or abs(v.x() - 260) < 0.01


class TestCongruentTrianglesScale:
    def test_scale_up(self):
        v1 = [(0, 0), (100, 0), (50, 86.6)]
        v2 = [(200, 0), (300, 0), (250, 86.6)]
        ct = CongruentTrianglesShape(v1, v2)
        ct.scale(2.0)
        # Сторона должна удвоиться
        s = math.hypot(
            ct._vertices1[1].x() - ct._vertices1[0].x(),
            ct._vertices1[1].y() - ct._vertices1[0].y(),
        )
        assert abs(s - 200) < 0.01

    def test_scale_down(self):
        v1 = [(0, 0), (100, 0), (50, 86.6)]
        v2 = [(200, 0), (300, 0), (250, 86.6)]
        ct = CongruentTrianglesShape(v1, v2)
        ct.scale(0.5)
        s = math.hypot(
            ct._vertices1[1].x() - ct._vertices1[0].x(),
            ct._vertices1[1].y() - ct._vertices1[0].y(),
        )
        assert abs(s - 50) < 0.01


class TestCongruentTrianglesContainsPoint:
    def test_point_in_first_triangle(self):
        v1 = [(0, 0), (100, 0), (50, 86.6)]
        v2 = [(200, 0), (300, 0), (250, 86.6)]
        ct = CongruentTrianglesShape(v1, v2)
        assert ct.contains_point(QPointF(50, 20))

    def test_point_in_second_triangle(self):
        v1 = [(0, 0), (100, 0), (50, 86.6)]
        v2 = [(200, 0), (300, 0), (250, 86.6)]
        ct = CongruentTrianglesShape(v1, v2)
        assert ct.contains_point(QPointF(250, 20))

    def test_point_outside(self):
        v1 = [(0, 0), (100, 0), (50, 86.6)]
        v2 = [(200, 0), (300, 0), (250, 86.6)]
        ct = CongruentTrianglesShape(v1, v2)
        assert not ct.contains_point(QPointF(150, 50))


class TestCongruentTrianglesBoundingRect:
    def test_bounding_rect_contains_both(self):
        v1 = [(0, 0), (100, 0), (50, 86.6)]
        v2 = [(200, 0), (300, 0), (250, 86.6)]
        ct = CongruentTrianglesShape(v1, v2)
        br = ct.bounding_rect()
        assert br.left() <= 0
        assert br.right() >= 300
        assert br.top() <= 0
        assert br.bottom() >= 86.6


class TestCongruentTrianglesHandles:
    def test_get_handles_returns_6(self):
        v1 = [(0, 0), (100, 0), (50, 86.6)]
        v2 = [(200, 0), (300, 0), (250, 86.6)]
        ct = CongruentTrianglesShape(v1, v2)
        handles = ct.get_handles()
        assert len(handles) == 6

    def test_handles_types(self):
        v1 = [(0, 0), (100, 0), (50, 86.6)]
        v2 = [(200, 0), (300, 0), (250, 86.6)]
        ct = CongruentTrianglesShape(v1, v2)
        handles = ct.get_handles()
        for h in handles:
            ht = ct.get_handle_type(h, tolerance=5.0)
            assert ht != HandleType.NONE


class TestCongruentTrianglesSerialization:
    def test_to_dict_contains_required_fields(self):
        v1 = [(0, 0), (100, 0), (50, 86.6)]
        v2 = [(200, 0), (300, 0), (250, 86.6)]
        ct = CongruentTrianglesShape(v1, v2)
        d = ct.to_dict()
        assert "vertices1" in d
        assert "offset" in d

    def test_from_dict_restores_shape(self):
        v1 = [(0, 0), (100, 0), (50, 86.6)]
        v2 = [(200, 0), (300, 0), (250, 86.6)]
        ct = CongruentTrianglesShape(v1, v2)
        d = ct.to_dict()
        ct2 = CongruentTrianglesShape.from_dict(d)
        assert len(ct2._vertices1) == 3
        assert len(ct2.vertices2) == 3
