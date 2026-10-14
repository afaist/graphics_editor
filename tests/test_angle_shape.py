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


# ======================================================================
# Тесты для новых типов углов
# ======================================================================


@pytest.fixture
def adjacent_angle():
    return AngleShape(
        vertex=(0.0, 0.0),
        side_a=100.0,
        side_b=80.0,
        angle_deg=60.0,
        side_c=100.0,
        angle_type="adjacent",
        pen_color=(0, 0, 0),
        pen_width=2.0,
    )


@pytest.fixture
def vertical_angle():
    return AngleShape(
        vertex=(0.0, 0.0),
        side_a=100.0,
        side_b=80.0,
        angle_deg=60.0,
        side_c=100.0,
        angle_type="vertical",
        pen_color=(0, 0, 0),
        pen_width=2.0,
    )


@pytest.fixture
def transversal_angle():
    return AngleShape(
        vertex=(0.0, 0.0),
        side_a=150.0,
        side_b=100.0,
        angle_deg=45.0,
        parallel_distance=150.0,
        angle_type="transversal",
        pen_color=(0, 0, 0),
        pen_width=2.0,
    )


class TestAdjacentAngle:
    """Тесты для смежных углов (adjacent)."""

    def test_creation(self):
        shape = AngleShape(
            vertex=(0, 0),
            side_a=100,
            side_b=80,
            angle_deg=60,
            side_c=100,
            angle_type="adjacent",
        )
        assert shape.angle_type == "adjacent"
        assert shape.side_c == 100

    def test_end_point_c_horizontal_left(self, adjacent_angle):
        """Сторона C горизонтально влево."""
        vc = adjacent_angle.end_point_c()
        assert abs(vc.x() - (-100)) < 0.01
        assert abs(vc.y() - 0) < 0.01

    def test_get_handles_returns_four(self, adjacent_angle):
        """У смежных углов 4 ручки."""
        handles = adjacent_angle.get_handles()
        assert len(handles) == 4

    def test_handles_include_vertex_and_endpoints(self, adjacent_angle):
        handles = adjacent_angle.get_handles()
        assert handles[0] == adjacent_angle.vertex
        assert handles[1] == adjacent_angle.end_point_a()
        assert handles[2] == adjacent_angle.end_point_b()
        assert handles[3] == adjacent_angle.end_point_c()

    def test_bounding_rect_contains_all_points(self, adjacent_angle):
        br = adjacent_angle.bounding_rect()
        assert br.contains(adjacent_angle.vertex)
        assert br.contains(adjacent_angle.end_point_a())
        assert br.contains(adjacent_angle.end_point_b())
        assert br.contains(adjacent_angle.end_point_c())

    def test_sum_angles_180(self, adjacent_angle):
        """α + β = 180°."""
        alpha = adjacent_angle.angle_deg
        beta = 180.0 - alpha
        assert abs(alpha + beta - 180.0) < 0.01

    def test_get_position_data(self, adjacent_angle):
        data = adjacent_angle.get_position_data()
        assert data["angle_type"] == "adjacent"
        assert "side_c" in data

    def test_restore_position_data(self, adjacent_angle):
        data = adjacent_angle.get_position_data()
        adjacent_angle._side_c = 50.0
        adjacent_angle.restore_position_data(data)
        assert adjacent_angle.side_c == 100.0

    def test_to_dict(self, adjacent_angle):
        d = adjacent_angle.to_dict()
        assert d["angle_type"] == "adjacent"
        assert "side_c" in d

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
            "vertex": {"x": 0, "y": 0},
            "side_a": 100,
            "side_b": 80,
            "angle_deg": 60,
            "angle_type": "adjacent",
            "side_c": 120,
        }
        shape = AngleShape.from_dict(data)
        assert shape.angle_type == "adjacent"
        assert shape.side_c == 120

    def test_roundtrip(self, adjacent_angle):
        d = adjacent_angle.to_dict()
        d["id"] = 99
        new_shape = AngleShape.from_dict(d)
        assert new_shape.id == 99
        assert new_shape.angle_type == "adjacent"
        assert new_shape.side_c == adjacent_angle.side_c


class TestVerticalAngle:
    """Тесты для вертикальных углов (vertical)."""

    def test_creation(self):
        shape = AngleShape(
            vertex=(0, 0),
            side_a=100,
            side_b=80,
            angle_deg=60,
            side_c=100,
            angle_type="vertical",
        )
        assert shape.angle_type == "vertical"

    def test_end_point_c_horizontal_left(self, vertical_angle):
        """Сторона C горизонтально влево, длина = side_a."""
        vc = vertical_angle.end_point_c()
        assert abs(vc.x() - (-100)) < 0.01
        assert abs(vc.y() - 0) < 0.01

    def test_end_point_d_opposite_b(self, vertical_angle):
        """Сторона D противоположна B (угол + 180°)."""
        vd = vertical_angle.end_point_d()
        rad = math.radians(60 + 180)
        expected_x = 80 * math.cos(-rad)
        expected_y = 80 * math.sin(-rad)
        assert abs(vd.x() - expected_x) < 0.01
        assert abs(vd.y() - expected_y) < 0.01

    def test_get_handles_returns_five(self, vertical_angle):
        """У вертикальных углов 5 ручек."""
        handles = vertical_angle.get_handles()
        assert len(handles) == 5

    def test_handles_include_all_endpoints(self, vertical_angle):
        handles = vertical_angle.get_handles()
        assert handles[0] == vertical_angle.vertex
        assert handles[1] == vertical_angle.end_point_a()
        assert handles[2] == vertical_angle.end_point_b()
        assert handles[3] == vertical_angle.end_point_c()
        assert handles[4] == vertical_angle.end_point_d()

    def test_bounding_rect_contains_all_points(self, vertical_angle):
        br = vertical_angle.bounding_rect()
        assert br.contains(vertical_angle.vertex)
        assert br.contains(vertical_angle.end_point_a())
        assert br.contains(vertical_angle.end_point_b())
        assert br.contains(vertical_angle.end_point_c())
        assert br.contains(vertical_angle.end_point_d())

    def test_vertical_angles_equal(self):
        """Вертикальные углы равны: α = γ."""
        shape = AngleShape((0, 0), 100, 80, 45, angle_type="vertical")
        assert shape.angle_deg == 45
        # γ должен быть равен α (проверяется при рисовании)

    def test_get_position_data(self, vertical_angle):
        data = vertical_angle.get_position_data()
        assert data["angle_type"] == "vertical"
        assert "side_c" in data

    def test_to_dict(self, vertical_angle):
        d = vertical_angle.to_dict()
        assert d["angle_type"] == "vertical"
        assert "side_c" in d

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
            "vertex": {"x": 0, "y": 0},
            "side_a": 100,
            "side_b": 80,
            "angle_deg": 60,
            "angle_type": "vertical",
            "side_c": 100,
        }
        shape = AngleShape.from_dict(data)
        assert shape.angle_type == "vertical"

    def test_roundtrip(self, vertical_angle):
        d = vertical_angle.to_dict()
        d["id"] = 88
        new_shape = AngleShape.from_dict(d)
        assert new_shape.id == 88
        assert new_shape.angle_type == "vertical"


class TestTransversalAngle:
    """Тесты для трансверсали (transversal)."""

    def test_creation(self):
        shape = AngleShape(
            vertex=(0, 0),
            side_a=150,
            side_b=100,
            angle_deg=45,
            parallel_distance=150,
            angle_type="transversal",
        )
        assert shape.angle_type == "transversal"
        assert shape.parallel_distance == 150

    def test_get_handles_returns_three(self, transversal_angle):
        """У трансверсали 3 ручки."""
        handles = transversal_angle.get_handles()
        assert len(handles) == 3

    def test_bounding_rect_larger_than_single(self, transversal_angle):
        """Bounding box трансверсали больше из-за параллельных прямых."""
        br = transversal_angle.bounding_rect()
        assert br.width() > 200  # параллельные прямые длинные
        assert br.height() > 100  # расстояние между параллельными

    def test_get_position_data(self, transversal_angle):
        data = transversal_angle.get_position_data()
        assert data["angle_type"] == "transversal"
        assert "parallel_distance" in data

    def test_restore_position_data(self, transversal_angle):
        data = transversal_angle.get_position_data()
        transversal_angle._parallel_distance = 50.0
        transversal_angle.restore_position_data(data)
        assert transversal_angle.parallel_distance == 150.0

    def test_to_dict(self, transversal_angle):
        d = transversal_angle.to_dict()
        assert d["angle_type"] == "transversal"
        assert "parallel_distance" in d

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
            "vertex": {"x": 0, "y": 0},
            "side_a": 150,
            "side_b": 100,
            "angle_deg": 45,
            "angle_type": "transversal",
            "parallel_distance": 150,
        }
        shape = AngleShape.from_dict(data)
        assert shape.angle_type == "transversal"
        assert shape.parallel_distance == 150

    def test_roundtrip(self, transversal_angle):
        d = transversal_angle.to_dict()
        d["id"] = 77
        new_shape = AngleShape.from_dict(d)
        assert new_shape.id == 77
        assert new_shape.angle_type == "transversal"
        assert new_shape.parallel_distance == transversal_angle.parallel_distance


class TestAngleTypeSwitching:
    """Тесты переключения между типами углов."""

    def test_single_to_adjacent(self):
        shape = AngleShape((0, 0), 100, 80, 90, angle_type="single")
        assert shape.angle_type == "single"
        shape._angle_type = "adjacent"
        assert shape.angle_type == "adjacent"
        # end_point_c должна существовать
        vc = shape.end_point_c()
        assert vc.x() < 0  # горизонтально влево

    def test_single_to_vertical(self):
        shape = AngleShape((0, 0), 100, 80, 90, angle_type="single")
        shape._angle_type = "vertical"
        assert shape.angle_type == "vertical"
        vd = shape.end_point_d()
        assert vd is not None

    def test_serialization_preserves_type(self):
        for angle_type in ("single", "adjacent", "vertical", "transversal"):
            if angle_type == "single":
                shape = AngleShape((0, 0), 100, 80, 90, angle_type=angle_type)
            elif angle_type in ("adjacent", "vertical"):
                shape = AngleShape((0, 0), 100, 80, 90, side_c=100, angle_type=angle_type)
            else:
                shape = AngleShape(
                    (0, 0), 150, 100, 45, parallel_distance=150, angle_type=angle_type
                )

            d = shape.to_dict()
            assert d["angle_type"] == angle_type

            new_shape = AngleShape.from_dict(d)
            assert new_shape.angle_type == angle_type
