"""Тесты для PencilShape: add_point, move, rotate, scale, bounding_rect."""

import pytest
from PySide6.QtCore import QPointF, QRectF

from shapes.base_shape import HandleType, ShapeType
from shapes.pencil_shape import PencilShape


class TestPencilShape:
    """Тесты создания и базовых операций PencilShape."""

    def _make_shape(self, **kwargs):
        defaults = {
            "points": [(0, 0), (50, 30), (100, 0)],
            "pen_color": (0, 0, 0),
            "pen_width": 2.0,
            "brush_color": None,
            "selected": False,
        }
        defaults.update(kwargs)
        return PencilShape(**defaults)

    def test_shape_type(self):
        s = self._make_shape()
        assert s._get_shape_type() == ShapeType.PENCIL

    def test_points_accessible(self):
        s = self._make_shape()
        assert len(s._points) == 3

    def test_empty_points(self):
        s = PencilShape(points=[], pen_color=(0, 0, 0), pen_width=2, brush_color=None)
        assert s._points == []

    def test_add_point(self):
        s = self._make_shape(points=[])
        s.add_point(10, 20)
        assert len(s._points) == 1
        assert s._points[0].x() == 10
        assert s._points[0].y() == 20

    def test_add_multiple_points(self):
        s = self._make_shape(points=[])
        s.add_point(0, 0)
        s.add_point(50, 50)
        s.add_point(100, 0)
        assert len(s._points) == 3

    def test_move(self):
        s = self._make_shape()
        s.move(10, 20)
        assert s._points[0].x() == pytest.approx(10)
        assert s._points[0].y() == pytest.approx(20)
        assert s._points[1].x() == pytest.approx(60)
        assert s._points[1].y() == pytest.approx(50)

    def test_move_empty(self):
        s = PencilShape(points=[], pen_color=(0, 0, 0), pen_width=2)
        s.move(10, 20)
        assert s._points == []

    def test_bounding_rect_empty(self):
        s = PencilShape(points=[], pen_color=(0, 0, 0), pen_width=2)
        assert s.bounding_rect() == QRectF()

    def test_bounding_rect_single_point(self):
        s = PencilShape(points=[(50, 50)], pen_color=(0, 0, 0), pen_width=6)
        br = s.bounding_rect()
        # pad = pen_width/2 + 2 = 5
        assert br.x() == pytest.approx(45)
        assert br.y() == pytest.approx(45)
        assert br.width() == pytest.approx(10)
        assert br.height() == pytest.approx(10)

    def test_bounding_rect_two_points(self):
        s = PencilShape(points=[(0, 0), (100, 50)], pen_color=(0, 0, 0), pen_width=2)
        br = s.bounding_rect()
        # pad = pen_width/2 + 2 = 3
        assert br.x() == pytest.approx(-3)
        assert br.y() == pytest.approx(-3)
        assert br.width() == pytest.approx(106)
        assert br.height() == pytest.approx(56)

    def test_bounding_rect_three_points(self):
        s = self._make_shape()
        br = s.bounding_rect()
        assert br.width() > 0
        assert br.height() > 0

    def test_contains_point_on_line(self):
        s = self._make_shape()
        # Точка на первом отрезке
        mid = QPointF(25, 15)
        assert s.contains_point(mid)

    def test_contains_point_far_from_line(self):
        s = self._make_shape()
        far = QPointF(999, 999)
        assert not s.contains_point(far)

    def test_contains_point_empty(self):
        s = PencilShape(points=[], pen_color=(0, 0, 0), pen_width=2)
        assert not s.contains_point(QPointF(0, 0))

    def test_contains_point_single_point(self):
        s = PencilShape(points=[(50, 50)], pen_color=(0, 0, 0), pen_width=2)
        # С одним пунктом contains_point должен вернуть False (< 2 points)
        assert not s.contains_point(QPointF(50, 50))

    def test_rotate(self):
        s = self._make_shape()
        orig_points = [(p.x(), p.y()) for p in s._points]
        s.rotate(90)
        new_points = [(p.x(), p.y()) for p in s._points]
        assert orig_points != new_points

    def test_rotate_empty(self):
        s = PencilShape(points=[], pen_color=(0, 0, 0), pen_width=2)
        s.rotate(90)
        assert s._points == []

    def test_scale(self):
        s = self._make_shape()
        orig_points = [(p.x(), p.y()) for p in s._points]
        s.scale(2.0)
        new_points = [(p.x(), p.y()) for p in s._points]
        assert orig_points != new_points

    def test_scale_empty(self):
        s = PencilShape(points=[], pen_color=(0, 0, 0), pen_width=2)
        s.scale(2.0)
        assert s._points == []

    def test_get_handles(self):
        s = self._make_shape()
        handles = s.get_handles()
        assert len(handles) == 3

    def test_handle_positions(self):
        s = self._make_shape()
        positions = s._handle_positions()
        assert len(positions) == 3

    def test_get_handle_type_none(self):
        s = self._make_shape()
        ht = s.get_handle_type(QPointF(-9999, -9999))
        assert ht == HandleType.NONE

    def test_get_handle_type_near_vertex(self):
        s = self._make_shape()
        ht = s.get_handle_type(QPointF(0, 0), tolerance=5.0)
        # Первая вершина в (0, 0)
        assert ht != HandleType.NONE

    def test_apply_handle_transform_move(self):
        s = self._make_shape()
        orig_x = s._points[0].x()
        s.apply_handle_transform(
            HandleType.MOVE,
            QPointF(orig_x, s._points[0].y()),
            QPointF(orig_x + 10, s._points[0].y()),
        )
        assert s._points[0].x() == pytest.approx(orig_x + 10)

    def test_to_dict(self):
        s = self._make_shape()
        d = s.to_dict()
        assert "id" in d
        assert "type" in d
        assert "points" in d

    def test_from_dict(self):
        s = self._make_shape()
        d = s.to_dict()
        s2 = PencilShape.from_dict(d)
        assert s2._get_shape_type() == ShapeType.PENCIL
        assert len(s2._points) == 3

    def test_get_position_data(self):
        s = self._make_shape()
        data = s.get_position_data()
        assert "points" in data

    def test_restore_position_data(self):
        s = self._make_shape()
        data = s.get_position_data()
        s.move(100, 100)
        s.restore_position_data(data)
        br = s.bounding_rect()
        assert br.x() < 100

    def test_get_properties(self):
        s = self._make_shape()
        props = s.get_properties()
        assert "pen_color" in props

    def test_apply_properties(self):
        s = self._make_shape()
        s.apply_properties({"pen_color": (255, 0, 0)})
        # pen_color может быть QColor — проверяем RGB
        pc = s.pen_color
        if hasattr(pc, "red"):
            assert pc.red() == 255
            assert pc.green() == 0
            assert pc.blue() == 0

    def test_selected_property(self):
        s = self._make_shape(selected=True)
        assert s.selected is True
        s.selected = False
        assert s.selected is False

    def test_rotation_property(self):
        s = self._make_shape()
        assert s.rotation == 0
        s.rotation = 45
        assert s.rotation == 45

    def test_pen_style_property(self):
        s = self._make_shape()
        assert s._pen_style == 1  # SolidLine

    def test_bounding_rect_with_thick_pen(self):
        s = PencilShape(points=[(0, 0), (100, 0)], pen_color=(0, 0, 0), pen_width=10)
        br = s.bounding_rect()
        # pad = pen_width/2 + 2 = 7
        assert br.x() == pytest.approx(-7)
        assert br.y() == pytest.approx(-7)
