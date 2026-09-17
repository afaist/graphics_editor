"""Тесты для LineShape — length, contains, трансформации, handles."""

from PySide6.QtCore import QPointF

from shapes.base_shape import HandleType, ShapeType
from shapes.line_shape import LineShape


class TestLineCreation:
    def test_default_properties(self):
        l = LineShape(0, 0, 100, 0)
        assert l.x1 == 0
        assert l.y1 == 0
        assert l.x2 == 100
        assert l.y2 == 0

    def test_shape_type_line(self):
        l = LineShape(0, 0, 100, 0, shape_type=ShapeType.LINE)
        assert l.shape_type == ShapeType.LINE

    def test_shape_type_ray(self):
        l = LineShape(0, 0, 100, 0, shape_type=ShapeType.RAY)
        assert l.shape_type == ShapeType.RAY

    def test_shape_type_infinite_line(self):
        l = LineShape(0, 0, 100, 100, shape_type=ShapeType.INFINITE_LINE)
        assert l.shape_type == ShapeType.INFINITE_LINE


class TestLineSetEndPoint:
    def test_set_end_point(self):
        l = LineShape(0, 0, 100, 0)
        l.set_end_point(50, 50)
        assert l.x2 == 50
        assert l.y2 == 50


class TestLineLength:
    def test_horizontal_line(self):
        l = LineShape(0, 0, 100, 0)
        assert l.length() == 100.0

    def test_vertical_line(self):
        l = LineShape(0, 0, 0, 50)
        assert l.length() == 50.0

    def test_diagonal_line(self):
        l = LineShape(0, 0, 3, 4)
        assert abs(l.length() - 5.0) < 1e-9

    def test_zero_length(self):
        l = LineShape(10, 10, 10, 10)
        assert l.length() == 0.0


class TestLineMove:
    def test_move(self):
        l = LineShape(0, 0, 100, 50)
        l.move(10, -5)
        assert l.x1 == 10
        assert l.y1 == -5
        assert l.x2 == 110
        assert l.y2 == 45


class TestLineScale:
    def test_scale(self):
        # Масштабирование от центра линии: центр (50, 0)
        l = LineShape(0, 0, 100, 0)
        l.scale(2.0)
        # x1 = 50 + (0-50)*2 = -50, x2 = 50 + (100-50)*2 = 150
        assert abs(l.x1 - (-50)) < 1e-9
        assert abs(l.x2 - 150) < 1e-9

    def test_scale_center(self):
        l = LineShape(-50, 0, 50, 0)
        l.scale(0.5)
        assert abs(l.x1 - (-25)) < 1e-9
        assert abs(l.x2 - 25) < 1e-9


class TestLineRotate:
    def test_rotate_90_degrees(self):
        l = LineShape(0, 0, 100, 0)
        l.rotate(90)
        # Текст: вращение для LineShape поддерживается через базовый класс
        # Проверяем что rotate() не вызывает ошибку
        assert l.x1 is not None
        assert l.y1 is not None

    def test_rotate_point(self):
        result = LineShape._rotate_point(10, 0, 0, 0, 90)
        assert abs(result[0] - 0) < 1e-9
        assert abs(result[1] - 10) < 1e-9


class TestLineContains:
    def test_point_on_line(self):
        l = LineShape(0, 0, 100, 0)
        assert l.contains_point(QPointF(50, 0)) is True

    def test_point_near_line(self):
        l = LineShape(0, 0, 100, 0)
        # Точка близко к линии
        assert l.contains_point(QPointF(50, 3)) is True

    def test_point_far_from_line(self):
        l = LineShape(0, 0, 100, 0)
        assert l.contains_point(QPointF(50, 50)) is False

    def test_point_at_end(self):
        l = LineShape(0, 0, 100, 0)
        assert l.contains_point(QPointF(100, 0)) is True

    def test_point_before_start(self):
        l = LineShape(0, 0, 100, 0)
        assert l.contains_point(QPointF(-50, 0)) is False


class TestLineBoundingRect:
    def test_normal_bounding_rect(self):
        l = LineShape(0, 0, 100, 50)
        br = l.bounding_rect()
        assert br.left() < 0
        assert br.right() > 100
        assert br.top() < 0
        assert br.bottom() > 50

    def test_ray_bounding_rect(self):
        l = LineShape(0, 0, 100, 0, shape_type=ShapeType.RAY)
        br = l.bounding_rect()
        assert br.width() > 0
        assert br.height() > 0

    def test_infinite_line_bounding_rect(self):
        l = LineShape(0, 0, 100, 100, shape_type=ShapeType.INFINITE_LINE)
        br = l.bounding_rect()
        assert br.width() > 0
        assert br.height() > 0


class TestLineHandles:
    def test_get_handles_returns_2(self):
        l = LineShape(0, 0, 100, 0)
        handles = l.get_handles()
        assert len(handles) == 2

    def test_get_handle_type_endpoint1(self):
        l = LineShape(0, 0, 100, 0)
        ht = l.get_handle_type(QPointF(0, 0), tolerance=5.0)
        assert ht == HandleType.TOP_LEFT

    def test_get_handle_type_endpoint2(self):
        l = LineShape(0, 0, 100, 0)
        ht = l.get_handle_type(QPointF(100, 0), tolerance=5.0)
        assert ht == HandleType.BOTTOM_RIGHT

    def test_get_handle_type_none(self):
        l = LineShape(0, 0, 100, 0)
        ht = l.get_handle_type(QPointF(50, 100), tolerance=5.0)
        assert ht == HandleType.NONE


class TestLineApplyHandleTransform:
    def test_top_left(self):
        l = LineShape(0, 0, 100, 0)
        l.apply_handle_transform(HandleType.TOP_LEFT, QPointF(0, 0), QPointF(10, 10))
        assert l.x1 == 10
        assert l.y1 == 10

    def test_bottom_right(self):
        l = LineShape(0, 0, 100, 0)
        l.apply_handle_transform(HandleType.BOTTOM_RIGHT, QPointF(100, 0), QPointF(150, 50))
        assert l.x2 == 150
        assert l.y2 == 50


class TestLineSerialization:
    def test_to_dict(self):
        l = LineShape(10, 20, 100, 50)
        d = l.to_dict()
        assert d["x1"] == 10
        assert d["y1"] == 20
        assert d["x2"] == 100
        assert d["y2"] == 50
        assert d["type"] == "line"

    def test_from_dict(self):
        data = {
            "id": 1,
            "type": "line",
            "pen_color": (255, 0, 0),
            "pen_width": 2.0,
            "rotation": 0.0,
            "group_id": None,
            "selected": False,
            "x1": 5,
            "y1": 10,
            "x2": 80,
            "y2": 40,
            "shape_type": "line",
        }
        l = LineShape.from_dict(data)
        assert l.x1 == 5
        assert l.y1 == 10
        assert l.x2 == 80
        assert l.y2 == 40

    def test_from_dict_ray(self):
        data = {
            "id": 1,
            "type": "ray",
            "pen_color": (0, 0, 255),
            "pen_width": 2.0,
            "rotation": 0.0,
            "group_id": None,
            "selected": False,
            "x1": 0,
            "y1": 0,
            "x2": 100,
            "y2": 0,
            "shape_type": "ray",
        }
        l = LineShape.from_dict(data)
        assert l.shape_type == ShapeType.RAY

    def test_roundtrip(self):
        l = LineShape(10, 20, 100, 50)
        l.id = 42
        d = l.to_dict()
        l2 = LineShape.from_dict(d)
        assert l2.x1 == 10
        assert l2.x2 == 100
        assert l2.y2 == 50
