"""Тесты для RectangleShape — свойства, трансформации, contains, handles."""

from PySide6.QtCore import QPointF

from shapes.base_shape import HandleType
from shapes.rectangle_shape import RectangleShape


class TestRectangleCreation:
    def test_default_properties(self):
        r = RectangleShape(0, 0, 100, 50)
        assert r.x == 0
        assert r.y == 0
        assert r.width == 100
        assert r.height == 50

    def test_custom_colors(self):
        r = RectangleShape(10, 20, 80, 40, pen_color=(255, 0, 0), brush_color=(0, 255, 0))
        assert r.pen_color.red() == 255
        assert r.brush_color.green() == 255

    def test_right_and_bottom(self):
        r = RectangleShape(10, 20, 100, 50)
        assert r.right == 110
        assert r.bottom == 70


class TestRectangleMove:
    def test_move_positive(self):
        r = RectangleShape(0, 0, 100, 50)
        r.move(10, 20)
        assert r.x == 10
        assert r.y == 20

    def test_move_negative(self):
        r = RectangleShape(0, 0, 100, 50)
        r.move(-5, -10)
        assert r.x == -5
        assert r.y == -10

    def test_move_zero(self):
        r = RectangleShape(5, 10, 100, 50)
        r.move(0, 0)
        assert r.x == 5
        assert r.y == 10


class TestRectangleScale:
    def test_scale_up(self):
        r = RectangleShape(0, 0, 100, 50)
        r.scale(2.0)
        assert r.width == 200
        assert r.height == 100

    def test_scale_down(self):
        r = RectangleShape(0, 0, 100, 50)
        r.scale(0.5)
        assert r.width == 50
        assert r.height == 25

    def test_scale_min_size(self):
        r = RectangleShape(0, 0, 0.05, 0.05)
        r.scale(0.5)
        assert r.width >= 0.1
        assert r.height >= 0.1


class TestRectangleRotate:
    def test_rotate(self):
        r = RectangleShape(0, 0, 100, 50)
        r.rotate(90)
        assert r.rotation == 90.0

    def test_rotate_full_circle(self):
        r = RectangleShape(0, 0, 100, 50)
        r.rotate(360)
        assert r.rotation == 0.0


class TestRectangleContains:
    def test_point_inside(self):
        r = RectangleShape(0, 0, 100, 50)
        assert r.contains_point(QPointF(50, 25)) is True

    def test_point_outside(self):
        r = RectangleShape(0, 0, 100, 50)
        assert r.contains_point(QPointF(200, 200)) is False

    def test_point_on_edge(self):
        r = RectangleShape(0, 0, 100, 50)
        assert r.contains_point(QPointF(0, 0)) is True

    def test_point_at_center(self):
        r = RectangleShape(10, 20, 100, 50)
        assert r.contains_point(QPointF(60, 45)) is True


class TestRectangleBoundingRect:
    def test_bounding_rect(self):
        r = RectangleShape(10, 20, 100, 50)
        br = r.bounding_rect()
        assert br.left() <= 10
        assert br.top() <= 20
        assert br.right() >= 110
        assert br.bottom() >= 70

    def test_bounding_rect_with_pen_width(self):
        r = RectangleShape(0, 0, 100, 50, pen_width=5.0)
        br = r.bounding_rect()
        # padding = max(5/2 + 5, 6) = 6
        assert br.left() <= -6
        assert br.top() <= -6


class TestRectangleHandles:
    def test_get_handles_returns_4(self):
        r = RectangleShape(0, 0, 100, 50)
        handles = r.get_handles()
        assert len(handles) == 4

    def test_get_handle_type_corner(self):
        r = RectangleShape(0, 0, 100, 50)
        handles = r.get_handles()
        ht = r.get_handle_type(handles[0], tolerance=5.0)
        assert ht != HandleType.NONE

    def test_get_handle_type_outside(self):
        r = RectangleShape(0, 0, 100, 50)
        ht = r.get_handle_type(QPointF(500, 500), tolerance=5.0)
        assert ht == HandleType.NONE


class TestRectangleApplyHandleTransform:
    def test_top_left(self):
        r = RectangleShape(0, 0, 100, 50)
        # Вершины в clockwise: A(0,50)=BL, D(0,0)=TL, C(100,0)=TR, B(100,50)=BR
        r.apply_handle_transform(HandleType.TOP_LEFT, QPointF(0, 0), QPointF(10, 20))
        # D (top-left) перемещён в (10, 20) — индекс 1
        assert r.vertices[1].x() == 10
        assert r.vertices[1].y() == 20

    def test_bottom_right(self):
        r = RectangleShape(0, 0, 100, 50)
        # Вершины в clockwise: A(0,50)=BL, D(0,0)=TL, C(100,0)=TR, B(100,50)=BR
        r.apply_handle_transform(HandleType.BOTTOM_RIGHT, QPointF(100, 50), QPointF(150, 80))
        # B (bottom-right) перемещён в (150, 80) — индекс 3
        assert r.vertices[3].x() == 150
        assert r.vertices[3].y() == 80


class TestRectangleSerialization:
    def test_to_dict(self):
        r = RectangleShape(10, 20, 100, 50)
        d = r.to_dict()
        assert d["x"] == 10
        assert d["y"] == 20
        assert d["width"] == 100
        assert d["height"] == 50
        assert d["type"] == "rectangle"

    def test_from_dict(self):
        data = {
            "id": 1,
            "type": "rectangle",
            "pen_color": (255, 0, 0),
            "pen_width": 3.0,
            "brush_color": (0, 255, 0),
            "rotation": 0.0,
            "group_id": None,
            "selected": False,
            "x": 5,
            "y": 10,
            "width": 80,
            "height": 40,
        }
        r = RectangleShape.from_dict(data)
        assert r.x == 5
        assert r.y == 10
        assert r.width == 80
        assert r.height == 40
        assert r.pen_color.red() == 255

    def test_roundtrip(self):
        r = RectangleShape(5, 15, 120, 60, pen_color=(100, 200, 50), brush_color=(255, 100, 200))
        r.id = 7
        d = r.to_dict()
        r2 = RectangleShape.from_dict(d)
        assert r2.x == 5
        assert r2.width == 120
        assert r2.height == 60
        assert r2.pen_color.blue() == 50
