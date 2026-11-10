"""Тесты для CircumscribedQuadrilateralShape — вписанный в окружность четырёхугольник."""

from __future__ import annotations

import math

from PySide6.QtCore import QPointF

from shapes.base_shape import HandleType
from shapes.circumscribed_quadrilateral_shape import CircumscribedQuadrilateralShape


class TestCircumscribedQuadrilateralCreation:
    def test_default_creation(self):
        cq = CircumscribedQuadrilateralShape(0, 0, 100)
        assert cq.cx == 0
        assert cq.cy == 0
        assert cq.radius == 100
        assert len(cq.angles) == 4

    def test_custom_angles(self):
        angles = [0.0, math.pi / 2, math.pi, math.pi * 1.5]
        cq = CircumscribedQuadrilateralShape(50, 50, 80, angles=angles)
        assert cq.angles == angles

    def test_min_radius_clamp(self):
        cq = CircumscribedQuadrilateralShape(0, 0, 5)
        assert cq.radius == 10.0

    def test_shape_type(self):
        cq = CircumscribedQuadrilateralShape(0, 0, 100)
        assert cq.shape_type.value == "circumscribed_quadrilateral"


class TestCircumscribedQuadrilateralVertices:
    def test_vertices_count(self):
        cq = CircumscribedQuadrilateralShape(0, 0, 100)
        assert len(cq.vertices) == 4

    def test_vertices_on_circle(self):
        cq = CircumscribedQuadrilateralShape(0, 0, 100)
        for v in cq.vertices:
            dist = math.hypot(v.x() - cq.cx, v.y() - cq.cy)
            assert abs(dist - cq.radius) < 0.01

    def test_vertex_positions_known_angles(self):
        angles = [0.0, math.pi / 2, math.pi, math.pi * 1.5]
        cq = CircumscribedQuadrilateralShape(0, 0, 100, angles=angles)
        verts = cq.vertices
        assert abs(verts[0].x() - 100) < 0.01
        assert abs(verts[0].y() - 0) < 0.01
        assert abs(verts[1].x() - 0) < 0.01
        assert abs(verts[1].y() - 100) < 0.01


class TestCircumscribedQuadrilateralInteriorAngles:
    def test_interior_angles_count(self):
        cq = CircumscribedQuadrilateralShape(0, 0, 100)
        assert len(cq.interior_angles) == 4

    def test_interior_angles_positive(self):
        cq = CircumscribedQuadrilateralShape(0, 0, 100)
        for angle in cq.interior_angles:
            assert angle >= 0

    def test_square_interior_angles(self):
        angles = [0.0, math.pi / 2, math.pi, math.pi * 1.5]
        cq = CircumscribedQuadrilateralShape(0, 0, 100, angles=angles)
        for angle in cq.interior_angles:
            assert 89 <= angle <= 91  # квадрат — все углы 90°


class TestCircumscribedQuadrilateralMove:
    def test_move_positive(self):
        cq = CircumscribedQuadrilateralShape(0, 0, 100)
        cq.move(10, 20)
        assert cq.cx == 10
        assert cq.cy == 20

    def test_move_negative(self):
        cq = CircumscribedQuadrilateralShape(100, 100, 50)
        cq.move(-30, -40)
        assert cq.cx == 70
        assert cq.cy == 60


class TestCircumscribedQuadrilateralScale:
    def test_scale_up(self):
        cq = CircumscribedQuadrilateralShape(0, 0, 100)
        cq.scale(2.0)
        assert cq.radius == 200

    def test_scale_down(self):
        cq = CircumscribedQuadrilateralShape(0, 0, 100)
        cq.scale(0.5)
        assert cq.radius == 50

    def test_scale_min_clamp(self):
        cq = CircumscribedQuadrilateralShape(0, 0, 0.05)
        cq.scale(0.5)
        assert cq.radius >= 0.1


class TestCircumscribedQuadrilateralRotate:
    def test_rotate(self):
        cq = CircumscribedQuadrilateralShape(0, 0, 100)
        cq.rotate(45)
        assert cq.rotation == 45.0


class TestCircumscribedQuadrilateralBoundingRect:
    def test_bounding_rect_contains_circle(self):
        cq = CircumscribedQuadrilateralShape(0, 0, 100)
        br = cq.bounding_rect()
        assert br.left() <= -100
        assert br.right() >= 100
        assert br.top() <= -100
        assert br.bottom() >= 100


class TestCircumscribedQuadrilateralHandles:
    def test_get_handles_returns_4(self):
        cq = CircumscribedQuadrilateralShape(0, 0, 50)
        handles = cq.get_handles()
        assert len(handles) == 4

    def test_handles_on_circle(self):
        cq = CircumscribedQuadrilateralShape(0, 0, 100)
        handles = cq.get_handles()
        for h in handles:
            dist = math.hypot(h.x() - cq.cx, h.y() - cq.cy)
            assert abs(dist - cq.radius) < 0.01

    def test_get_handle_type_returns_type(self):
        cq = CircumscribedQuadrilateralShape(0, 0, 50)
        handles = cq.get_handles()
        ht = cq.get_handle_type(handles[0], tolerance=5.0)
        assert ht != HandleType.NONE


class TestCircumscribedQuadrilateralApplyHandleTransform:
    def test_apply_handle_transform_changes_angle(self):
        cq = CircumscribedQuadrilateralShape(0, 0, 100)
        initial_angles = list(cq.angles)
        cq.apply_handle_transform(
            HandleType.TOP_LEFT,
            QPointF(0, 0),
            QPointF(100, 100),
            vertex_index=0,
        )
        assert cq.angles[0] != initial_angles[0]

    def test_vertex_moves_to_circle(self):
        cq = CircumscribedQuadrilateralShape(0, 0, 100)
        cq.apply_handle_transform(
            HandleType.TOP_LEFT,
            QPointF(0, 0),
            QPointF(150, 0),
            vertex_index=0,
        )
        v = cq.vertices[0]
        dist = math.hypot(v.x() - cq.cx, v.y() - cq.cy)
        assert abs(dist - cq.radius) < 0.01


class TestCircumscribedQuadrilateralSerialization:
    def test_to_dict_contains_required_fields(self):
        cq = CircumscribedQuadrilateralShape(10, 20, 100)
        d = cq.to_dict()
        assert "cx" in d
        assert "cy" in d
        assert "radius" in d
        assert "angles" in d

    def test_from_dict_restores_shape(self):
        cq = CircumscribedQuadrilateralShape(10, 20, 100)
        d = cq.to_dict()
        cq2 = CircumscribedQuadrilateralShape.from_dict(d)
        assert cq2.cx == cq.cx
        assert cq2.cy == cq.cy
        assert cq2.radius == cq.radius

    def test_roundtrip_preserves_angles(self):
        angles = [0.0, math.pi / 3, math.pi * 2 / 3, math.pi]
        cq = CircumscribedQuadrilateralShape(0, 0, 100, angles=angles)
        d = cq.to_dict()
        cq2 = CircumscribedQuadrilateralShape.from_dict(d)
        for a1, a2 in zip(cq.angles, cq2.angles):
            assert abs(a1 - a2) < 0.01
