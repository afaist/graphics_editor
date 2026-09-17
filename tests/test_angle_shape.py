"""Тесты для фигуры AngleShape."""

import math

import pytest
from PySide6.QtCore import QPointF

from shapes.angle_shape import AngleShape
from shapes.base_shape import HandleType, ShapeType


@pytest.fixture
def angle_shape():
    return AngleShape(
        vertex=(0.0, 0.0),
        side_a=100.0,
        side_b=80.0,
        angle_deg=90.0,
        pen_color=(0, 0, 0),
        pen_width=2.0,
    )


class TestCreation:
    def test_creation_valid_params(self):
        shape = AngleShape((10, 20), 50, 60, 45)
        assert shape.vertex == QPointF(10, 20)
        assert shape.side_a == 50
        assert shape.side_b == 60
        assert shape.angle_deg == 45

    def test_default_colors(self):
        shape = AngleShape((0, 0), 100, 100, 90)
        assert shape.pen_color.red() == 0
        assert shape.pen_color.green() == 0
        assert shape.pen_color.blue() == 0

    def test_shape_type(self, angle_shape):
        assert angle_shape.shape_type == ShapeType.ANGLE

    def test_angle_modulo(self):
        shape = AngleShape((0, 0), 100, 100, 400)
        assert shape.angle_deg == 40

    def test_negative_angle(self):
        shape = AngleShape((0, 0), 100, 100, -90)
        assert shape.angle_deg == 270

    def test_min_side_length(self):
        shape = AngleShape((0, 0), -5, -3, 90)
        assert shape.side_a >= 0.1
        assert shape.side_b >= 0.1


class TestGeometry:
    def test_end_point_a_horizontal(self, angle_shape):
        ep = angle_shape.end_point_a()
        assert abs(ep.x() - 100) < 0.01
        assert abs(ep.y() - 0) < 0.01

    def test_end_point_b_90_deg(self, angle_shape):
        """При 90° вторая сторона идёт вертикально вверх (в Qt Y вниз, -rad)."""
        ep = angle_shape.end_point_b()
        assert abs(ep.x() - 0) < 0.01
        assert abs(ep.y() - (-80)) < 0.01

    def test_end_point_b_0_deg(self):
        shape = AngleShape((0, 0), 100, 50, 0)
        ep = shape.end_point_b()
        assert abs(ep.x() - 50) < 0.01
        assert abs(ep.y() - 0) < 0.01

    def test_end_point_b_180_deg(self):
        shape = AngleShape((0, 0), 100, 50, 180)
        ep = shape.end_point_b()
        # При 180°: cos(-180) = -1, sin(-180) = 0 → (-50, 0)
        assert abs(ep.x() - (-50)) < 0.01
        assert abs(ep.y() - 0) < 0.01

    def test_bisector_angle(self, angle_shape):
        bis = angle_shape._bisector_angle()
        expected = -math.radians(45)
        assert abs(bis - expected) < 0.001


class TestBoundingRect:
    def test_bounding_rect_not_empty(self, angle_shape):
        br = angle_shape.bounding_rect()
        assert not br.isEmpty()

    def test_bounding_rect_contains_vertex(self, angle_shape):
        br = angle_shape.bounding_rect()
        assert br.contains(angle_shape.vertex)

    def test_bounding_rect_contains_end_a(self, angle_shape):
        br = angle_shape.bounding_rect()
        assert br.contains(angle_shape.end_point_a())

    def test_bounding_rect_contains_end_b(self, angle_shape):
        br = angle_shape.bounding_rect()
        assert br.contains(angle_shape.end_point_b())

    def test_bounding_rect_with_offset_vertex(self):
        shape = AngleShape((50, 50), 100, 80, 90)
        br = shape.bounding_rect()
        assert br.left() <= 50
        assert br.top() <= 50
        assert br.right() >= 150
        assert br.bottom() >= -30  # vertex.y - side_b at 90deg = 50 - 80 = -30


class TestDraw:
    def test_draw_no_exception(self, angle_shape, qapp):
        from PySide6.QtCore import Qt
        from PySide6.QtGui import QPainter, QPixmap

        pixmap = QPixmap(200, 200)
        pixmap.fill(Qt.GlobalColor.white)
        painter = QPainter(pixmap)
        try:
            angle_shape.draw(painter)
        finally:
            painter.end()


class TestContainsPoint:
    def test_contains_vertex(self, angle_shape):
        assert angle_shape.contains_point(QPointF(0, 0))

    def test_contains_on_side_a(self, angle_shape):
        assert angle_shape.contains_point(QPointF(50, 0))

    def test_contains_on_side_b_90(self, angle_shape):
        assert angle_shape.contains_point(QPointF(0, -40))

    def test_not_contains_far_point(self, angle_shape):
        assert not angle_shape.contains_point(QPointF(500, 500))

    def test_not_contains_between_lines(self, angle_shape):
        # Точка между сторонами, но далеко от вершины
        assert not angle_shape.contains_point(QPointF(50, -50))

    def test_point_to_segment_distance_zero(self):
        _ = AngleShape((0, 0), 100, 100, 90)
        dist = AngleShape._point_to_segment_distance(
            QPointF(50, 0), QPointF(0, 0), QPointF(100, 0)
        )
        assert abs(dist) < 0.01


class TestMove:
    def test_move_positive(self, angle_shape):
        angle_shape.move(10, 20)
        assert abs(angle_shape.vertex.x() - 10) < 0.01
        assert abs(angle_shape.vertex.y() - 20) < 0.01

    def test_move_negative(self, angle_shape):
        angle_shape.move(-5, -3)
        assert abs(angle_shape.vertex.x() - (-5)) < 0.01
        assert abs(angle_shape.vertex.y() - (-3)) < 0.01


class TestScale:
    def test_scale_up(self, angle_shape):
        angle_shape.scale(2.0)
        assert abs(angle_shape.side_a - 200) < 0.01
        assert abs(angle_shape.side_b - 160) < 0.01

    def test_scale_down(self, angle_shape):
        angle_shape.scale(0.5)
        assert abs(angle_shape.side_a - 50) < 0.01
        assert abs(angle_shape.side_b - 40) < 0.01

    def test_scale_min_clamp(self, angle_shape):
        angle_shape._side_a = 0.05
        angle_shape.scale(1.0)
        assert angle_shape.side_a >= 0.1


class TestRotate:
    def test_rotate_vertex(self, angle_shape):
        angle_shape.rotate(90, QPointF(0, 0))
        # Vertex (0,0) rotated around (0,0) should stay at (0,0)
        assert abs(angle_shape.vertex.x()) < 0.01
        assert abs(angle_shape.vertex.y()) < 0.01

    def test_rotate_around_vertex(self, angle_shape):
        center = angle_shape.vertex
        angle_shape.rotate(45, center)
        # Vertex should not move when rotating around itself
        assert abs(angle_shape.vertex.x()) < 0.01
        assert abs(angle_shape.vertex.y()) < 0.01


class TestHandles:
    def test_get_handles_returns_three(self, angle_shape):
        handles = angle_shape.get_handles()
        assert len(handles) == 3

    def test_handles_positions(self, angle_shape):
        handles = angle_shape.get_handles()
        assert handles[0] == angle_shape.vertex
        assert handles[1] == angle_shape.end_point_a()
        assert handles[2] == angle_shape.end_point_b()

    def test_get_handle_type_vertex(self, angle_shape):
        ht = angle_shape.get_handle_type(angle_shape.vertex)
        assert ht == HandleType.TOP_LEFT

    def test_get_handle_type_end_a(self, angle_shape):
        ht = angle_shape.get_handle_type(angle_shape.end_point_a())
        assert ht == HandleType.BOTTOM_RIGHT

    def test_get_handle_type_end_b(self, angle_shape):
        ht = angle_shape.get_handle_type(angle_shape.end_point_b())
        assert ht == HandleType.BOTTOM_CENTER

    def test_get_handle_type_none(self, angle_shape):
        ht = angle_shape.get_handle_type(QPointF(999, 999))
        assert ht == HandleType.NONE

    def test_apply_handle_vertex(self, angle_shape):
        angle_shape.apply_handle_transform(
            HandleType.TOP_LEFT, angle_shape.vertex, QPointF(10, 20)
        )
        assert abs(angle_shape.vertex.x() - 10) < 0.01
        assert abs(angle_shape.vertex.y() - 20) < 0.01

    def test_apply_handle_side_a(self, angle_shape):
        old_a = angle_shape.side_a
        angle_shape.apply_handle_transform(
            HandleType.BOTTOM_RIGHT, angle_shape.end_point_a(), QPointF(200, 0)
        )
        assert angle_shape.side_a > old_a

    def test_apply_handle_side_b(self, angle_shape):
        old_b = angle_shape.side_b
        angle_shape.apply_handle_transform(
            HandleType.BOTTOM_CENTER, angle_shape.end_point_b(), QPointF(0, -150)
        )
        assert angle_shape.side_b > old_b


class TestProperties:
    def test_get_properties(self, angle_shape):
        props = angle_shape.get_properties()
        assert "_shape_type" in props
        assert "_side_a" in props
        assert "_side_b" in props
        assert "_angle_deg" in props
        assert props["_side_a"] == 100
        assert props["_side_b"] == 80
        assert props["_angle_deg"] == 90

    def test_apply_properties(self, angle_shape):
        angle_shape.apply_properties({"_side_a": 200, "_side_b": 150, "_angle_deg": 45})
        assert angle_shape.side_a == 200
        assert angle_shape.side_b == 150
        assert angle_shape.angle_deg == 45

    def test_apply_properties_none(self, angle_shape):
        angle_shape.apply_properties(None)
        assert angle_shape.side_a == 100


class TestSerialization:
    def test_to_dict(self, angle_shape):
        d = angle_shape.to_dict()
        assert d["type"] == "angle"
        assert "vertex" in d
        assert d["side_a"] == 100
        assert d["side_b"] == 80
        assert d["angle_deg"] == 90

    def test_from_dict(self):
        data = {
            "id": 1,
            "type": "angle",
            "pen_color": (0, 0, 0),
            "pen_width": 2.0,
            "brush_color": None,
            "selected": False,
            "rotation": 0.0,
            "group_id": None,
            "vertex": {"x": 10, "y": 20},
            "side_a": 120,
            "side_b": 80,
            "angle_deg": 60,
        }
        shape = AngleShape.from_dict(data)
        assert shape.id == 1
        assert shape.vertex == QPointF(10, 20)
        assert shape.side_a == 120
        assert shape.side_b == 80
        assert shape.angle_deg == 60
        assert shape.shape_type == ShapeType.ANGLE

    def test_roundtrip(self, angle_shape):
        d = angle_shape.to_dict()
        d["id"] = 42
        new_shape = AngleShape.from_dict(d)
        assert new_shape.id == 42
        assert abs(new_shape.vertex.x() - angle_shape.vertex.x()) < 0.01
        assert abs(new_shape.vertex.y() - angle_shape.vertex.y()) < 0.01
        assert new_shape.side_a == angle_shape.side_a
        assert new_shape.side_b == angle_shape.side_b
        assert new_shape.angle_deg == angle_shape.angle_deg
