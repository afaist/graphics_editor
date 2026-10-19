"""Инструменты рисования."""

from __future__ import annotations

from PySide6.QtCore import QObject, QPointF, Signal
from PySide6.QtWidgets import QDialog

from shapes.base_shape import BaseShape, ShapeType
from shapes.ellipse_shape import EllipseShape
from shapes.formula_shape import FormulaShape
from shapes.graph_shape import GraphShape
from shapes.line_shape import LineShape
from shapes.point_shape import PointShape
from shapes.polygon_shape import PolygonShape
from shapes.polyline_shape import PolylineShape
from shapes.text_shape import TextShape
from tools.tool_types import ToolType


class ToolManager(QObject):
    """Управление активным инструментом и временными фигурами."""

    tool_changed = Signal(str)
    temp_shape_updated = Signal()
    temp_shape_started = Signal()

    def __init__(self):
        super().__init__()
        self._current_tool: ToolType = ToolType.SELECT
        self._temp_shape: BaseShape | None = None
        self._start_point: QPointF | None = None
        self._polyline_vertices: list = []
        self._polygon_vertices: list = []

    # ------------------------------------------------------------------
    # Свойства
    # ------------------------------------------------------------------

    @property
    def current_tool(self) -> ToolType:
        return self._current_tool

    @current_tool.setter
    def current_tool(self, tool: ToolType) -> None:
        self._current_tool = tool
        self._clear_temp()
        self.tool_changed.emit(tool.value)

    @property
    def is_drawing_tool(self) -> bool:
        return self._current_tool not in (ToolType.SELECT, ToolType.MOVE)

    @property
    def start_point(self) -> QPointF | None:
        return self._start_point

    @property
    def temp_shape(self) -> BaseShape | None:
        return self._temp_shape

    # ------------------------------------------------------------------
    # Старт рисования
    # ------------------------------------------------------------------

    def start_shape(self, point: QPointF, settings) -> None:
        self._clear_temp()
        self._start_point = point
        self.temp_shape_started.emit()

        pen_color = settings.default_pen_color
        pen_width = settings.default_pen_width

        # Инициализация вершин для POLYGON/POLYLINE
        if self._current_tool == ToolType.POLYGON:
            self._polygon_vertices = [point]
        elif self._current_tool == ToolType.POLYLINE:
            self._polyline_vertices = [point]

        # Словарь фабрик для создания временных фигур
        factories: dict[ToolType, tuple] = {
            ToolType.POINT: (
                lambda: PointShape(
                    point.x(),
                    point.y(),
                    pen_color=pen_color,
                    pen_width=pen_width,
                    brush_color=settings.default_brush_color,
                ),
            ),
            ToolType.LINE: (
                lambda: LineShape(
                    point.x(),
                    point.y(),
                    point.x(),
                    point.y(),
                    shape_type=ShapeType.LINE,
                    pen_color=pen_color,
                    pen_width=pen_width,
                ),
            ),
            ToolType.RAY: (
                lambda: LineShape(
                    point.x(),
                    point.y(),
                    point.x(),
                    point.y(),
                    shape_type=ShapeType.RAY,
                    pen_color=pen_color,
                    pen_width=pen_width,
                ),
            ),
            ToolType.INFINITE_LINE: (
                lambda: LineShape(
                    point.x(),
                    point.y(),
                    point.x(),
                    point.y(),
                    shape_type=ShapeType.INFINITE_LINE,
                    pen_color=pen_color,
                    pen_width=pen_width,
                ),
            ),
            ToolType.ELLIPSE: (
                lambda: EllipseShape(
                    point.x(),
                    point.y(),
                    0,
                    0,
                    pen_color=pen_color,
                    pen_width=pen_width,
                    brush_color=settings.default_brush_color,
                ),
            ),
            ToolType.POLYGON: (
                lambda: PolygonShape(
                    vertices=[(point.x(), point.y())],
                    pen_color=pen_color,
                    pen_width=pen_width,
                    brush_color=settings.default_brush_color,
                ),
            ),
            ToolType.POLYLINE: (
                lambda: PolylineShape(
                    vertices=[(point.x(), point.y())],
                    pen_color=pen_color,
                    pen_width=pen_width,
                ),
            ),
            ToolType.TEXT: (
                lambda: TextShape(
                    point.x(),
                    point.y(),
                    text="",
                    pen_color=pen_color,
                    pen_width=pen_width,
                ),
            ),
        }

        # RECTANGLE, ARC, ANGLE не создают временную фигуру — через диалог
        if self._current_tool in factories:
            self._temp_shape = factories[self._current_tool][0]()

    def update_shape(self, point: QPointF, shift_pressed: bool = False) -> None:
        if self._temp_shape is None or self._start_point is None:
            return

        x, y = point.x(), point.y()
        sx, sy = self._start_point.x(), self._start_point.y()

        if self._current_tool in (ToolType.LINE, ToolType.RAY, ToolType.INFINITE_LINE):
            if shift_pressed:
                x, y = self._constrain_angle(sx, sy, x, y)
            if hasattr(self._temp_shape, "set_end_point"):
                self._temp_shape.set_end_point(x, y)

        elif self._current_tool == ToolType.RECTANGLE or self._current_tool == ToolType.ELLIPSE:
            if shift_pressed:
                size = max(abs(x - sx), abs(y - sy))
                x = sx + size * (1 if x >= sx else -1)
                y = sy + size * (1 if y >= sy else -1)
            if hasattr(self._temp_shape, "set_size"):
                self._temp_shape.set_size(x - sx, y - sy)

        elif self._current_tool == ToolType.POLYGON:
            self._polygon_vertices.append(point)
            if hasattr(self._temp_shape, "add_vertex"):
                self._temp_shape.add_vertex(point.x(), point.y())

        elif self._current_tool == ToolType.POLYLINE:
            self._polyline_vertices.append(point)
            if hasattr(self._temp_shape, "add_vertex"):
                self._temp_shape.add_vertex(point.x(), point.y())

        elif self._current_tool == ToolType.TEXT:
            # Текст — одно нажатие, обновление не требуется
            pass

        # ARC не обновляется — используется диалог

        self.temp_shape_updated.emit()

    def finish_current_shape(self, settings) -> BaseShape | None:
        """Завершает рисование текущей фигуры, учитывая её тип."""
        if self._current_tool == ToolType.TEXT:
            return self.finish_text()
        elif self._current_tool == ToolType.RECTANGLE:
            return self.finish_rectangle(settings)
        elif self._current_tool == ToolType.FORMULA:
            return self.finish_formula(settings)
        elif self._current_tool in (
            ToolType.GRAPH_LINEAR,
            ToolType.GRAPH_QUADRATIC,
            ToolType.GRAPH_SIN,
            ToolType.GRAPH_COS,
            ToolType.GRAPH_TAN,
            ToolType.GRAPH_LOG,
            ToolType.GRAPH_EXP,
            ToolType.GRAPH_SQRT,
        ):
            return self.finish_graph(settings)
        elif self._current_tool in (ToolType.POLYGON,):
            return self.finish_polygon()
        elif self._current_tool in (ToolType.POLYLINE,):
            return self.finish_polyline()
        else:
            # Для остальных инструментов (line, rect, ellipse, point)
            # finish_shape просто возвращает текущую временную фигуру
            return self.finish_shape()

    def finish_shape(self, point: QPointF | None = None) -> BaseShape | None:
        if self._temp_shape is None:
            return None
        shape = self._temp_shape

        self._clear_temp()
        return shape

    def add_polyline_vertex(self, point: QPointF) -> None:
        if self._temp_shape and self._current_tool == ToolType.POLYLINE:
            if hasattr(self._temp_shape, "add_vertex"):
                self._temp_shape.add_vertex(point.x(), point.y())
            self.temp_shape_updated.emit()

    def finish_polyline(self) -> BaseShape | None:
        if self._temp_shape and self._current_tool == ToolType.POLYLINE:
            shape = self._temp_shape
            self._clear_temp()
            return shape
        return None

    def finish_polygon(self, close: bool = True) -> BaseShape | None:
        if self._temp_shape and self._current_tool == ToolType.POLYGON:
            # Если нужно замкнуть полигон, добавляем первую вершину в конец
            if close and len(self._polygon_vertices) >= 3:
                first_point = self._polygon_vertices[0]
                if hasattr(self._temp_shape, "add_vertex"):
                    self._temp_shape.add_vertex(first_point.x(), first_point.y())
            shape = self._temp_shape
            self._clear_temp()
            return shape
        return None

    def can_finish_polygon(self) -> bool:
        if self._current_tool != ToolType.POLYGON:
            return False
        if not self._polygon_vertices:  # явно проверяем на пустоту
            return False
        return len(self._polygon_vertices) >= 3

    def can_finish_polyline(self) -> bool:
        if self._current_tool != ToolType.POLYLINE:
            return False
        if not self._polyline_vertices:
            return False
        return len(self._polyline_vertices) >= 2

    def finish_text(self) -> BaseShape | None:
        """Завершает создание текстовой фигуры."""
        if self._current_tool == ToolType.TEXT and self._temp_shape:
            shape = self._temp_shape
            self._clear_temp()
            return shape
        return None

    def finish_rectangle(self, settings) -> BaseShape | None:
        """Завершает создание прямоугольника через диалог."""
        if self._current_tool != ToolType.RECTANGLE or self._start_point is None:
            return None

        from ui.shape_dialogs import create_dialog_for_tool

        dialog = create_dialog_for_tool(ToolType.RECTANGLE)
        if dialog is None or dialog.exec() != QDialog.DialogCode.Accepted:
            self._clear_temp()
            return None

        params = dialog.get_params()
        width = params["width"]
        height = params["height"]

        from shapes.rectangle_shape import RectangleShape

        pen_color = settings.default_pen_color
        pen_width = settings.default_pen_width

        shape = RectangleShape(
            self._start_point.x(),
            self._start_point.y(),
            width,
            height,
            pen_color=pen_color,
            pen_width=pen_width,
            brush_color=settings.default_brush_color,
        )

        self._clear_temp()
        return shape

    def finish_formula(self, settings) -> BaseShape | None:
        """Завершает создание формулы через диалог."""
        if self._current_tool != ToolType.FORMULA or self._start_point is None:
            return None

        from ui.formula_dialog import FormulaEditorDialog

        dialog = FormulaEditorDialog(parent=None, settings=settings)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            self._clear_temp()
            return None

        params = dialog.get_params()
        latex = params.get("latex", "")
        if not latex.strip():
            self._clear_temp()
            return None

        font_family = params.get("font_family", settings.formula_default_font_family)
        font_size = params.get("font_size", settings.formula_default_font_size)

        pen_color = settings.default_pen_color
        pen_width = settings.default_pen_width

        shape = FormulaShape(
            self._start_point.x(),
            self._start_point.y(),
            latex_text=latex,
            font_size=font_size,
            font_family=font_family,
            pen_color=pen_color,
            pen_width=pen_width,
        )

        self._clear_temp()
        return shape

    def finish_graph(self, settings) -> BaseShape | None:
        """Завершает создание графика через диалог."""
        if (
            self._current_tool
            not in (
                ToolType.GRAPH_LINEAR,
                ToolType.GRAPH_QUADRATIC,
                ToolType.GRAPH_SIN,
                ToolType.GRAPH_COS,
                ToolType.GRAPH_TAN,
                ToolType.GRAPH_LOG,
                ToolType.GRAPH_EXP,
                ToolType.GRAPH_SQRT,
            )
            or self._start_point is None
        ):
            return None

        from ui.graph_dialog import GraphEditorDialog

        # Определяем начальный тип функции из tool type
        func_map = {
            ToolType.GRAPH_LINEAR: "linear",
            ToolType.GRAPH_QUADRATIC: "quadratic",
            ToolType.GRAPH_SIN: "sin",
            ToolType.GRAPH_COS: "cos",
            ToolType.GRAPH_TAN: "tan",
            ToolType.GRAPH_LOG: "log",
            ToolType.GRAPH_EXP: "exp",
            ToolType.GRAPH_SQRT: "sqrt",
        }
        initial_func = func_map.get(self._current_tool, "linear")

        dialog = GraphEditorDialog(
            parent=None,
            func_name=initial_func,
            settings=settings,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            self._clear_temp()
            return None

        params = dialog.get_params()
        func_name = params.get("func_name", "linear")
        graph_params = params.get("params", {})
        graph_width = params.get("width", settings.graph_default_width)
        graph_height = params.get("height", settings.graph_default_height)
        graph_font_size = params.get("font_size", settings.graph_default_font_size)
        graph_x_range = params.get("x_range", settings.graph_default_x_range)
        graph_x_steps = params.get("x_steps", settings.graph_default_x_steps)

        if not func_name:
            self._clear_temp()
            return None

        pen_color = settings.default_pen_color
        pen_width = params.get("pen_width", settings.default_pen_width)

        shape = GraphShape(
            self._start_point.x(),
            self._start_point.y(),
            func_name=func_name,
            params=graph_params,
            pen_color=pen_color,
            pen_width=pen_width,
            width=graph_width,
            height=graph_height,
            font_size=graph_font_size,
            x_range=graph_x_range,
            x_steps=graph_x_steps,
        )

        self._clear_temp()
        return shape

    # ------------------------------------------------------------------
    # Сервисные методы
    # ------------------------------------------------------------------

    def reset_current_shape(self) -> None:
        """Публичный метод для сброса состояния рисования."""
        self._clear_temp()

    def _clear_temp(self) -> None:
        """Очищает временные данные рисования."""
        self._temp_shape = None
        self._start_point = None
        self._polygon_vertices.clear()
        self._polyline_vertices.clear()

    @staticmethod
    def _constrain_angle(x1: float, y1: float, x2: float, y2: float) -> tuple[float, float]:
        """Привязка к углам 0, 45, 90, 135, 180, 225, 270, 315 градусов."""
        import math

        angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
        angles = [0, 45, 90, 135, 180, 225, 270, 315]
        best = min(angles, key=lambda a: abs(angle - a))
        rad = math.radians(best)
        dist = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        return (
            x1 + dist * math.cos(rad),
            y1 + dist * math.sin(rad),
        )
