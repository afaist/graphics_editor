"""Тесты для ToolManager — переключение инструментов, создание/обновление фигур."""

import pytest
from PySide6.QtCore import QPointF

from tools.tool_manager import ToolManager, ToolType
from settings.settings import Settings


class TestToolManagerCreation:
    def test_default_tool(self):
        tm = ToolManager()
        assert tm.current_tool == ToolType.SELECT

    def test_is_drawing_tool_initially_false(self):
        tm = ToolManager()
        assert tm.is_drawing_tool is False

    def test_temp_shape_initially_none(self):
        tm = ToolManager()
        assert tm.temp_shape is None

    def test_start_point_initially_none(self):
        tm = ToolManager()
        assert tm.start_point is None


class TestToolSwitching:
    def test_switch_to_line_tool(self):
        tm = ToolManager()
        tm.current_tool = ToolType.LINE
        assert tm.current_tool == ToolType.LINE
        assert tm.is_drawing_tool is True

    def test_switch_to_rectangle_tool(self):
        tm = ToolManager()
        tm.current_tool = ToolType.RECTANGLE
        assert tm.current_tool == ToolType.RECTANGLE

    def test_switch_back_to_select(self):
        tm = ToolManager()
        tm.current_tool = ToolType.LINE
        tm.current_tool = ToolType.SELECT
        assert tm.current_tool == ToolType.SELECT
        assert tm.is_drawing_tool is False

    def test_switch_clears_temp(self):
        tm = ToolManager()
        settings = Settings()
        tm.current_tool = ToolType.RECTANGLE
        tm.start_shape(QPointF(0, 0), settings)
        assert tm.temp_shape is not None
        tm.current_tool = ToolType.LINE
        assert tm.temp_shape is None


class TestStartShape:
    def test_start_point_stored(self):
        tm = ToolManager()
        settings = Settings()
        tm.start_shape(QPointF(10, 20), settings)
        assert tm.start_point is not None
        assert abs(tm.start_point.x() - 10) < 1e-9

    def test_start_line_creates_temp(self):
        tm = ToolManager()
        settings = Settings()
        tm.current_tool = ToolType.LINE
        tm.start_shape(QPointF(0, 0), settings)
        assert tm.temp_shape is not None

    def test_start_rectangle_creates_temp(self):
        tm = ToolManager()
        settings = Settings()
        tm.current_tool = ToolType.RECTANGLE
        tm.start_shape(QPointF(0, 0), settings)
        assert tm.temp_shape is not None

    def test_start_ellipse_creates_temp(self):
        tm = ToolManager()
        settings = Settings()
        tm.current_tool = ToolType.ELLIPSE
        tm.start_shape(QPointF(0, 0), settings)
        assert tm.temp_shape is not None

    def test_start_point_creates_temp(self):
        tm = ToolManager()
        settings = Settings()
        tm.current_tool = ToolType.POINT
        tm.start_shape(QPointF(5, 10), settings)
        assert tm.temp_shape is not None

    def test_start_polygon_creates_temp(self):
        tm = ToolManager()
        settings = Settings()
        tm.current_tool = ToolType.POLYGON
        tm.start_shape(QPointF(0, 0), settings)
        assert tm.temp_shape is not None

    def test_start_polyline_creates_temp(self):
        tm = ToolManager()
        settings = Settings()
        tm.current_tool = ToolType.POLYLINE
        tm.start_shape(QPointF(0, 0), settings)
        assert tm.temp_shape is not None

    def test_start_text_creates_temp(self):
        tm = ToolManager()
        settings = Settings()
        tm.current_tool = ToolType.TEXT
        tm.start_shape(QPointF(0, 0), settings)
        assert tm.temp_shape is not None


class TestUpdateShape:
    def test_update_line(self):
        tm = ToolManager()
        settings = Settings()
        tm.current_tool = ToolType.LINE
        tm.start_shape(QPointF(0, 0), settings)
        tm.update_shape(QPointF(100, 50))
        assert tm.temp_shape is not None

    def test_update_rectangle(self):
        tm = ToolManager()
        settings = Settings()
        tm.current_tool = ToolType.RECTANGLE
        tm.start_shape(QPointF(0, 0), settings)
        tm.update_shape(QPointF(100, 50))
        assert tm.temp_shape is not None

    def test_update_no_temp_shape(self):
        tm = ToolManager()
        tm.update_shape(QPointF(100, 50))  # не должно вызвать ошибку


class TestFinishShape:
    def test_finish_line(self):
        tm = ToolManager()
        settings = Settings()
        tm.current_tool = ToolType.LINE
        tm.start_shape(QPointF(0, 0), settings)
        tm.update_shape(QPointF(100, 50))
        shape = tm.finish_shape()
        assert shape is not None

    def test_finish_rectangle(self):
        tm = ToolManager()
        settings = Settings()
        tm.current_tool = ToolType.RECTANGLE
        tm.start_shape(QPointF(0, 0), settings)
        tm.update_shape(QPointF(100, 50))
        shape = tm.finish_shape()
        assert shape is not None

    def test_finish_no_temp_shape(self):
        tm = ToolManager()
        shape = tm.finish_shape()
        assert shape is None

    def test_finish_clears_temp(self):
        tm = ToolManager()
        settings = Settings()
        tm.current_tool = ToolType.RECTANGLE
        tm.start_shape(QPointF(0, 0), settings)
        tm.finish_shape()
        assert tm.temp_shape is None


class TestFinishPolygon:
    def test_can_finish_polygon_false_initially(self):
        tm = ToolManager()
        assert tm.can_finish_polygon() is False

    def test_can_finish_polygon_true_with_3_vertices(self):
        tm = ToolManager()
        settings = Settings()
        tm.current_tool = ToolType.POLYGON
        tm.start_shape(QPointF(0, 0), settings)
        tm.update_shape(QPointF(100, 0))
        tm.update_shape(QPointF(100, 100))
        assert tm.can_finish_polygon() is True

    def test_can_finish_polygon_false_with_2_vertices(self):
        tm = ToolManager()
        settings = Settings()
        tm.current_tool = ToolType.POLYGON
        tm.start_shape(QPointF(0, 0), settings)
        tm.update_shape(QPointF(100, 0))
        assert tm.can_finish_polygon() is False

    def test_finish_polygon(self):
        tm = ToolManager()
        settings = Settings()
        tm.current_tool = ToolType.POLYGON
        tm.start_shape(QPointF(0, 0), settings)
        tm.update_shape(QPointF(100, 0))
        tm.update_shape(QPointF(100, 100))
        shape = tm.finish_polygon()
        assert shape is not None


class TestFinishPolyline:
    def test_can_finish_polyline_false_initially(self):
        tm = ToolManager()
        assert tm.can_finish_polyline() is False

    def test_can_finish_polyline_true_with_2_vertices(self):
        tm = ToolManager()
        settings = Settings()
        tm.current_tool = ToolType.POLYLINE
        tm.start_shape(QPointF(0, 0), settings)
        tm.update_shape(QPointF(100, 0))
        assert tm.can_finish_polyline() is True

    def test_finish_polyline(self):
        tm = ToolManager()
        settings = Settings()
        tm.current_tool = ToolType.POLYLINE
        tm.start_shape(QPointF(0, 0), settings)
        tm.update_shape(QPointF(100, 0))
        shape = tm.finish_polyline()
        assert shape is not None


class TestResetCurrentShape:
    def test_reset_clears_temp(self):
        tm = ToolManager()
        settings = Settings()
        tm.current_tool = ToolType.RECTANGLE
        tm.start_shape(QPointF(0, 0), settings)
        tm.reset_current_shape()
        assert tm.temp_shape is None


class TestConstrainAngle:
    def test_constrain_0_degrees(self):
        result = ToolManager._constrain_angle(0, 0, 100, 0)
        assert abs(result[0] - 100) < 1e-9
        assert abs(result[1]) < 1e-9

    def test_constrain_90_degrees(self):
        result = ToolManager._constrain_angle(0, 0, 0, 100)
        assert abs(result[0]) < 1e-9
        assert abs(result[1] - 100) < 1e-9

    def test_constrain_45_degrees(self):
        result = ToolManager._constrain_angle(0, 0, 100, 100)
        dist = (result[0] ** 2 + result[1] ** 2) ** 0.5
        assert abs(dist - 100 * 2 ** 0.5) < 1e-9
        assert abs(result[0] - result[1]) < 1e-9
