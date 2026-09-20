"""Тесты для поворота фигур — применение rotation в draw()."""


from PySide6.QtGui import QPainter

from shapes.angle_shape import AngleShape
from shapes.arc_shape import ArcShape
from shapes.ellipse_shape import EllipseShape
from shapes.line_shape import LineShape, ShapeType
from shapes.parallelogram_shape import ParallelogramShape
from shapes.point_shape import PointShape
from shapes.polygon_shape import PolygonShape
from shapes.polyline_shape import PolylineShape
from shapes.rectangle_shape import RectangleShape
from shapes.text_shape import TextShape
from shapes.trapezoid_shape import TrapezoidShape
from shapes.triangle_shape import TriangleShape

# ------------------------------------------------------------------
# RectangleShape — поворот
# ------------------------------------------------------------------


class TestRectangleRotation:
    def test_rotation_stored(self):
        s = RectangleShape(0, 0, 100, 50)
        s._rotation = 45.0
        assert s._rotation == 45.0

    def test_draw_with_rotation_no_crash(self):
        s = RectangleShape(10, 10, 100, 50)
        s._rotation = 30.0
        # draw() должен работать без исключений
        # QPainter в offscreen-режиме создаётся из QImage
        from PySide6.QtGui import QImage

        img = QImage(200, 200, QImage.Format.Format_RGB32)
        painter = QPainter(img)
        s.draw(painter)
        painter.end()

    def test_draw_with_zero_rotation(self):
        s = RectangleShape(10, 10, 100, 50)
        s._rotation = 0.0
        from PySide6.QtGui import QImage

        img = QImage(200, 200, QImage.Format.Format_RGB32)
        painter = QPainter(img)
        s.draw(painter)
        painter.end()

    def test_rotation_normalized(self):
        s = RectangleShape(0, 0, 100, 50)
        s._rotation = 400.0
        # rotation не нормализуется автоматически в свойстве
        assert s._rotation == 400.0


# ------------------------------------------------------------------
# EllipseShape — поворот
# ------------------------------------------------------------------


class TestEllipseRotation:
    def test_rotation_stored(self):
        s = EllipseShape(0, 0, 80, 60)
        s._rotation = 90.0
        assert s._rotation == 90.0

    def test_draw_with_rotation_no_crash(self):
        s = EllipseShape(10, 10, 80, 60)
        s._rotation = 45.0
        from PySide6.QtGui import QImage

        img = QImage(200, 200, QImage.Format.Format_RGB32)
        painter = QPainter(img)
        s.draw(painter)
        painter.end()


# ------------------------------------------------------------------
# LineShape — поворот
# ------------------------------------------------------------------


class TestLineRotation:
    def test_rotation_stored(self):
        s = LineShape(0, 0, 100, 0, shape_type=ShapeType.LINE)
        s._rotation = 60.0
        assert s._rotation == 60.0

    def test_draw_with_rotation_no_crash(self):
        s = LineShape(10, 10, 100, 50, shape_type=ShapeType.LINE)
        s._rotation = 30.0
        from PySide6.QtGui import QImage

        img = QImage(200, 200, QImage.Format.Format_RGB32)
        painter = QPainter(img)
        s.draw(painter)
        painter.end()

    def test_ray_draw_with_rotation(self):
        s = LineShape(0, 0, 100, 0, shape_type=ShapeType.RAY)
        s._rotation = 45.0
        from PySide6.QtGui import QImage

        img = QImage(200, 200, QImage.Format.Format_RGB32)
        painter = QPainter(img)
        s.draw(painter)
        painter.end()

    def test_infinite_line_draw_with_rotation(self):
        s = LineShape(0, 0, 100, 100, shape_type=ShapeType.INFINITE_LINE)
        s._rotation = 20.0
        from PySide6.QtGui import QImage

        img = QImage(200, 200, QImage.Format.Format_RGB32)
        painter = QPainter(img)
        s.draw(painter)
        painter.end()


# ------------------------------------------------------------------
# PolygonShape — поворот
# ------------------------------------------------------------------


class TestPolygonRotation:
    def test_rotation_stored(self):
        s = PolygonShape(vertices=[(0, 0), (100, 0), (100, 100)])
        s._rotation = 15.0
        assert s._rotation == 15.0

    def test_draw_with_rotation_no_crash(self):
        s = PolygonShape(vertices=[(10, 10), (100, 10), (100, 100)])
        s._rotation = 25.0
        from PySide6.QtGui import QImage

        img = QImage(200, 200, QImage.Format.Format_RGB32)
        painter = QPainter(img)
        s.draw(painter)
        painter.end()


# ------------------------------------------------------------------
# PolylineShape — поворот
# ------------------------------------------------------------------


class TestPolylineRotation:
    def test_rotation_stored(self):
        s = PolylineShape(vertices=[(0, 0), (50, 50), (100, 0)])
        s._rotation = 10.0
        assert s._rotation == 10.0

    def test_draw_with_rotation_no_crash(self):
        s = PolylineShape(vertices=[(10, 10), (50, 50), (100, 10)])
        s._rotation = 40.0
        from PySide6.QtGui import QImage

        img = QImage(200, 200, QImage.Format.Format_RGB32)
        painter = QPainter(img)
        s.draw(painter)
        painter.end()


# ------------------------------------------------------------------
# ArcShape — поворот
# ------------------------------------------------------------------


class TestArcRotation:
    def test_rotation_stored(self):
        s = ArcShape(cx=0, cy=0, radius=50, start_angle=0, end_angle=90)
        s._rotation = 30.0
        assert s._rotation == 30.0

    def test_draw_with_rotation_no_crash(self):
        s = ArcShape(cx=50, cy=50, radius=50, start_angle=0, end_angle=90)
        s._rotation = 45.0
        from PySide6.QtGui import QImage

        img = QImage(200, 200, QImage.Format.Format_RGB32)
        painter = QPainter(img)
        s.draw(painter)
        painter.end()


# ------------------------------------------------------------------
# TextShape — поворот
# ------------------------------------------------------------------


class TestTextRotation:
    def test_rotation_stored(self):
        s = TextShape(10, 20, text="Hello")
        s._rotation = 15.0
        assert s._rotation == 15.0

    def test_draw_with_rotation_no_crash(self):
        s = TextShape(10, 20, text="Test")
        s._rotation = 20.0
        from PySide6.QtGui import QImage

        img = QImage(200, 200, QImage.Format.Format_RGB32)
        painter = QPainter(img)
        s.draw(painter)
        painter.end()


# ------------------------------------------------------------------
# PointShape — поворот
# ------------------------------------------------------------------


class TestPointRotation:
    def test_rotation_stored(self):
        s = PointShape(10, 20, radius=3.0)
        s._rotation = 90.0
        assert s._rotation == 90.0

    def test_draw_with_rotation_no_crash(self):
        s = PointShape(50, 50, radius=5.0)
        s._rotation = 45.0
        from PySide6.QtGui import QImage

        img = QImage(200, 200, QImage.Format.Format_RGB32)
        painter = QPainter(img)
        s.draw(painter)
        painter.end()


# ------------------------------------------------------------------
# TriangleShape — поворот
# ------------------------------------------------------------------


class TestTriangleRotation:
    def test_rotation_stored(self):
        verts = TriangleShape.build_equilateral(100)
        s = TriangleShape(vertices=verts)
        s._rotation = 30.0
        assert s._rotation == 30.0

    def test_draw_with_rotation_no_crash(self):
        verts = TriangleShape.build_equilateral(100)
        s = TriangleShape(vertices=verts)
        s._rotation = 60.0
        from PySide6.QtGui import QImage

        img = QImage(200, 200, QImage.Format.Format_RGB32)
        painter = QPainter(img)
        s.draw(painter)
        painter.end()


# ------------------------------------------------------------------
# ParallelogramShape — поворот
# ------------------------------------------------------------------


class TestParallelogramRotation:
    def test_rotation_stored(self):
        verts = ParallelogramShape.build(150, 100, 60)
        s = ParallelogramShape(vertices=verts)
        s._rotation = 25.0
        assert s._rotation == 25.0

    def test_draw_with_rotation_no_crash(self):
        verts = ParallelogramShape.build(150, 100, 60)
        s = ParallelogramShape(vertices=verts)
        s._rotation = 45.0
        from PySide6.QtGui import QImage

        img = QImage(200, 200, QImage.Format.Format_RGB32)
        painter = QPainter(img)
        s.draw(painter)
        painter.end()


# ------------------------------------------------------------------
# TrapezoidShape — поворот
# ------------------------------------------------------------------


class TestTrapezoidRotation:
    def test_rotation_stored(self):
        verts = TrapezoidShape.build_isosceles(200, 100, 60)
        s = TrapezoidShape(vertices=verts, trapezoid_type="isosceles")
        s._rotation = 35.0
        assert s._rotation == 35.0

    def test_scalene_draw_with_rotation(self):
        verts = TrapezoidShape.build_scalene(100, 200, 100, 20)
        s = TrapezoidShape(vertices=verts, trapezoid_type="scalene")
        s._rotation = 20.0
        from PySide6.QtGui import QImage

        img = QImage(200, 200, QImage.Format.Format_RGB32)
        painter = QPainter(img)
        s.draw(painter)
        painter.end()


# ------------------------------------------------------------------
# AngleShape — поворот
# ------------------------------------------------------------------


class TestAngleRotation:
    def test_rotation_stored(self):
        s = AngleShape(vertex=(0, 0), side_a=100, side_b=100, angle_deg=90)
        s._rotation = 45.0
        assert s._rotation == 45.0

    def test_draw_with_rotation_no_crash(self):
        s = AngleShape(vertex=(50, 50), side_a=100, side_b=80, angle_deg=60)
        s._rotation = 30.0
        from PySide6.QtGui import QImage

        img = QImage(200, 200, QImage.Format.Format_RGB32)
        painter = QPainter(img)
        s.draw(painter)
        painter.end()


# ------------------------------------------------------------------
# Интеграция: все фигуры рисуются с rotation
# ------------------------------------------------------------------


class TestAllShapesRotationIntegration:
    """Проверка что все фигуры рисуются без исключений при rotation != 0."""

    def _make_image(self):
        from PySide6.QtGui import QImage

        return QImage(400, 400, QImage.Format.Format_RGB32)

    def _paint_shape(self, shape):
        img = self._make_image()
        painter = QPainter(img)
        shape.draw(painter)
        painter.end()

    def test_rectangle(self):
        s = RectangleShape(10, 10, 100, 50)
        s._rotation = 37.5
        self._paint_shape(s)

    def test_ellipse(self):
        s = EllipseShape(10, 10, 80, 60)
        s._rotation = 72.3
        self._paint_shape(s)

    def test_line(self):
        s = LineShape(10, 10, 100, 50, shape_type=ShapeType.LINE)
        s._rotation = 15.7
        self._paint_shape(s)

    def test_ray(self):
        s = LineShape(10, 10, 100, 50, shape_type=ShapeType.RAY)
        s._rotation = 22.1
        self._paint_shape(s)

    def test_infinite_line(self):
        s = LineShape(10, 10, 100, 100, shape_type=ShapeType.INFINITE_LINE)
        s._rotation = 44.4
        self._paint_shape(s)

    def test_polygon(self):
        s = PolygonShape(vertices=[(10, 10), (100, 10), (100, 100)])
        s._rotation = 55.5
        self._paint_shape(s)

    def test_polyline(self):
        s = PolylineShape(vertices=[(10, 10), (50, 50), (100, 10)])
        s._rotation = 66.6
        self._paint_shape(s)

    def test_arc(self):
        s = ArcShape(cx=50, cy=50, radius=50, start_angle=0, end_angle=90)
        s._rotation = 88.8
        self._paint_shape(s)

    def test_text(self):
        s = TextShape(10, 20, text="Test text")
        s._rotation = 12.3
        self._paint_shape(s)

    def test_point(self):
        s = PointShape(50, 50, radius=5.0)
        s._rotation = 33.3
        self._paint_shape(s)

    def test_triangle(self):
        verts = TriangleShape.build_equilateral(100)
        s = TriangleShape(vertices=verts)
        s._rotation = 27.7
        self._paint_shape(s)

    def test_parallelogram(self):
        verts = ParallelogramShape.build(150, 100, 60)
        s = ParallelogramShape(vertices=verts)
        s._rotation = 41.1
        self._paint_shape(s)

    def test_trapezoid_isosceles(self):
        verts = TrapezoidShape.build_isosceles(200, 100, 60)
        s = TrapezoidShape(vertices=verts, trapezoid_type="isosceles")
        s._rotation = 53.9
        self._paint_shape(s)

    def test_trapezoid_scalene(self):
        verts = TrapezoidShape.build_scalene(100, 200, 100, 20)
        s = TrapezoidShape(vertices=verts, trapezoid_type="scalene")
        s._rotation = 19.2
        self._paint_shape(s)

    def test_angle(self):
        s = AngleShape(vertex=(50, 50), side_a=100, side_b=80, angle_deg=60)
        s._rotation = 77.7
        self._paint_shape(s)
