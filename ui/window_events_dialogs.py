"""Диалоги создания фигур и фабрика фигур по параметрам."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QPointF

from shapes.angle_shape import AngleShape
from shapes.arc_shape import ArcShape
from shapes.parallelogram_shape import ParallelogramShape
from shapes.platonic_solid_shape import PlatonicSolidShape
from shapes.rectangle_shape import RectangleShape
from shapes.rhombus_shape import RhombusShape
from shapes.trapezoid_shape import TrapezoidShape
from shapes.triangle_shape import TriangleShape
from tools.tool_types import ToolType

if TYPE_CHECKING:
    from shapes.quadrilateral_shape import QuadrilateralShape
    from ui.main_window import MainWindow


class DialogManager:
    """Управление диалогами ввода параметров фигур и созданием фигур."""

    def __init__(self, main_window: MainWindow):
        self._mw = main_window

    # ------------------------------------------------------------------
    # Оркестрация диалогов
    # ------------------------------------------------------------------

    def show_shape_dialog(self, tool_type, pos: QPointF) -> None:
        """Показывает диалог ввода параметров и создаёт фигуру."""
        mw = self._mw
        from ui.shape_dialogs import create_dialog_for_tool

        dialog = create_dialog_for_tool(tool_type)
        if dialog is None:
            return

        # Делаем главное окно родителем
        dialog.setParent(mw)
        dialog.setWindowTitle(dialog.windowTitle())

        from PySide6.QtWidgets import QDialog

        if dialog.exec() == QDialog.DialogCode.Accepted:
            params = dialog.get_params()
            # Для треугольников используем выбранный тип из диалога
            if tool_type in (
                ToolType.TRIANGLE_EQUILATERAL,
                ToolType.TRIANGLE_ISOSCELES,
                ToolType.TRIANGLE_RIGHT,
                ToolType.TRIANGLE_OBTUSE,
            ):
                triangle_type = params.get("triangle_type", "equilateral")
                type_map = {
                    "equilateral": ToolType.TRIANGLE_EQUILATERAL,
                    "isosceles": ToolType.TRIANGLE_ISOSCELES,
                    "right": ToolType.TRIANGLE_RIGHT,
                    "obtuse": ToolType.TRIANGLE_OBTUSE,
                }
                actual_tool_type = type_map.get(triangle_type, ToolType.TRIANGLE_EQUILATERAL)
            else:
                actual_tool_type = tool_type
            shape = self._create_shape_from_params(actual_tool_type, params, pos)
            if shape:
                mw.add_shape(shape)

        mw._event_manager._drawing.clear_temp_shape()

    # ------------------------------------------------------------------
    # Фабрика фигур по параметрам
    # ------------------------------------------------------------------

    def _create_shape_from_params(self, tool_type, params: dict, pos: QPointF):
        """Создаёт фигуру по параметрам из диалога."""
        mw = self._mw
        pen_color = mw._settings.default_pen_color
        pen_width = mw._settings.default_pen_width
        brush_color = mw._settings.default_brush_color

        # Фигуры с вершинами: (build_fn, center_div, type_name, kwargs_fn)
        vertex_shapes: dict[ToolType, tuple] = {
            ToolType.TRIANGLE_EQUILATERAL: (
                lambda p: TriangleShape.build_equilateral(p.get("side_a", 100)),
                3,
                "equilateral",
                lambda p: {
                    "side_a": p.get("side_a", 100),
                    "draw_height": p.get("draw_height", False),
                    "draw_median": p.get("draw_median", False),
                    "draw_bisector": p.get("draw_bisector", False),
                    "vertex_index": p.get("vertex_index", 0),
                    "draw_circumscribed": p.get("draw_circumscribed", False),
                    "draw_inscribed": p.get("draw_inscribed", False),
                    "draw_angles": p.get("draw_angles", False),
                },
            ),
            ToolType.TRIANGLE_ISOSCELES: (
                lambda p: TriangleShape.build_isosceles(
                    p.get("side_a", 150), p.get("height", 86.6)
                ),
                3,
                "isosceles",
                lambda p: {
                    "side_a": p.get("side_a", 150),
                    "height": p.get("height", 86.6),
                    "draw_height": p.get("draw_height", False),
                    "draw_median": p.get("draw_median", False),
                    "draw_bisector": p.get("draw_bisector", False),
                    "vertex_index": p.get("vertex_index", 0),
                    "draw_circumscribed": p.get("draw_circumscribed", False),
                    "draw_inscribed": p.get("draw_inscribed", False),
                    "draw_angles": p.get("draw_angles", False),
                },
            ),
            ToolType.TRIANGLE_RIGHT: (
                lambda p: TriangleShape.build_right(p.get("side_a", 100), p.get("side_b", 100)),
                3,
                "right",
                lambda p: {
                    "side_a": p.get("side_a", 100),
                    "side_b": p.get("side_b", 100),
                    "draw_height": p.get("draw_height", False),
                    "draw_median": p.get("draw_median", False),
                    "draw_bisector": p.get("draw_bisector", False),
                    "vertex_index": p.get("vertex_index", 0),
                    "draw_circumscribed": p.get("draw_circumscribed", False),
                    "draw_inscribed": p.get("draw_inscribed", False),
                    "draw_angles": p.get("draw_angles", False),
                },
            ),
            ToolType.TRIANGLE_OBTUSE: (
                lambda p: TriangleShape.build_obtuse(
                    p.get("side_a", 100), p.get("side_b", 100), p.get("angle_deg", 120)
                ),
                3,
                "obtuse",
                lambda p: {
                    "side_a": p.get("side_a", 100),
                    "side_b": p.get("side_b", 100),
                    "angle_deg": p.get("angle_deg", 120),
                    "draw_height": p.get("draw_height", False),
                    "draw_median": p.get("draw_median", False),
                    "draw_bisector": p.get("draw_bisector", False),
                    "vertex_index": p.get("vertex_index", 0),
                    "draw_circumscribed": p.get("draw_circumscribed", False),
                    "draw_inscribed": p.get("draw_inscribed", False),
                    "draw_angles": p.get("draw_angles", False),
                },
            ),
            ToolType.PARALLELOGRAM: (
                lambda p: ParallelogramShape.build(
                    p.get("side_a", 150), p.get("side_b", 100), p.get("angle_deg", 60)
                ),
                4,
                None,
                lambda p: {
                    "side_a": p.get("side_a", 150),
                    "side_b": p.get("side_b", 100),
                    "angle_deg": p.get("angle_deg", 60),
                    "show_heights": p.get("show_heights", False),
                    "show_diagonals": p.get("show_diagonals", False),
                    "show_circumcircle": p.get("show_circumcircle", False),
                    "height_from_vertex": p.get("height_from_vertex", -1),
                },
            ),
            ToolType.TRAPEZOID_ISOSCELES: (
                lambda p: TrapezoidShape.build_isosceles(
                    p.get("base_a", 200), p.get("base_b", 100), p.get("angle_deg", 60)
                ),
                4,
                None,
                lambda p: {
                    "base_a": p.get("base_a", 200),
                    "base_b": p.get("base_b", 100),
                    "angle_deg": p.get("angle_deg", 60),
                    "trapezoid_type": "isosceles",
                    "show_midline": p.get("show_midline", False),
                    "show_heights": p.get("show_heights", False),
                    "show_diagonals": p.get("show_diagonals", False),
                    "show_circumcircle": p.get("show_circumcircle", False),
                    "height_from_vertex": p.get("height_from_vertex", -1),
                },
            ),
            ToolType.TRAPEZOID: (
                lambda p: self._build_trapezoid_scalene(p),
                4,
                None,
                lambda p: {
                    **p,
                    "show_midline": p.get("show_midline", False),
                    "show_heights": p.get("show_heights", False),
                    "show_diagonals": p.get("show_diagonals", False),
                    "show_circumcircle": p.get("show_circumcircle", False),
                    "height_from_vertex": p.get("height_from_vertex", -1),
                },
            ),
            ToolType.RHOMBUS: (
                lambda p: RhombusShape.build(p.get("side_a", 100), p.get("side_b", 75)),
                4,
                None,
                lambda p: {
                    "dx": p.get("side_a", 100),
                    "dy": p.get("side_b", 75),
                    "show_heights": p.get("show_heights", False),
                    "show_diagonals": p.get("show_diagonals", False),
                    "height_from_vertex": p.get("height_from_vertex", -1),
                },
            ),
        }

        if tool_type in vertex_shapes:
            build_fn, center_div, type_name, kwargs_fn = vertex_shapes[tool_type]
            raw = build_fn(params)
            kwargs = kwargs_fn(params)

            if tool_type in (
                ToolType.TRIANGLE_EQUILATERAL,
                ToolType.TRIANGLE_ISOSCELES,
                ToolType.TRIANGLE_RIGHT,
                ToolType.TRIANGLE_OBTUSE,
            ):
                centered = TriangleShape.center_vertices(raw)
                centered = TriangleShape.flip_y(centered)
                centered = TriangleShape.order_vertices_clockwise(centered)
            elif tool_type == ToolType.PARALLELOGRAM:
                centered = ParallelogramShape.center_vertices(raw)
                centered = ParallelogramShape.order_vertices_clockwise(centered)
            elif tool_type == ToolType.RHOMBUS:
                centered = RhombusShape.center_vertices(raw)
                centered = RhombusShape.order_vertices_clockwise(centered)
            else:
                centered = TrapezoidShape.center_vertices(raw)
                centered = TrapezoidShape.order_vertices_clockwise(centered)

            cx = sum(v[0] for v in centered) / center_div
            cy = sum(v[1] for v in centered) / center_div
            offset_x = pos.x() - cx
            offset_y = pos.y() - cy
            vertices = [(v[0] + offset_x, v[1] + offset_y) for v in centered]
            kwargs["vertices"] = vertices
            kwargs["pen_color"] = pen_color
            kwargs["pen_width"] = pen_width
            kwargs["brush_color"] = brush_color
            if type_name is not None:
                kwargs["triangle_type"] = type_name

            if tool_type in (
                ToolType.TRIANGLE_EQUILATERAL,
                ToolType.TRIANGLE_ISOSCELES,
                ToolType.TRIANGLE_RIGHT,
                ToolType.TRIANGLE_OBTUSE,
            ):
                return TriangleShape(**kwargs)
            elif tool_type == ToolType.PARALLELOGRAM:
                return ParallelogramShape(**kwargs)
            elif tool_type == ToolType.RHOMBUS:
                return RhombusShape(
                    center=(pos.x(), pos.y()),
                    **{k: v for k, v in kwargs.items() if k != "vertices"},
                )
            else:
                return TrapezoidShape(**kwargs)

        # Неправильный четырёхугольник
        if tool_type == ToolType.QUADRILATERAL_IRREGULAR:
            return self._create_quadrilateral(params, pos, pen_color, pen_width, brush_color)

        # Треугольник Шарыгина
        if tool_type == ToolType.TRIANGLE_SHARYGIN:
            from shapes.sharygin_triangle_shape import SharyginTriangleShape

            size = params.get("size", 200)
            raw_vertices = TriangleShape.build_equilateral(size)
            centered = TriangleShape.center_vertices(raw_vertices)
            centered = TriangleShape.flip_y(centered)
            centered = TriangleShape.order_vertices_clockwise(centered)
            cx = sum(v[0] for v in centered) / 3
            cy = sum(v[1] for v in centered)
            shifted = [(v[0] - cx + pos.x(), v[1] - cy + pos.y()) for v in centered]

            return SharyginTriangleShape(
                vertices=shifted,
                size=size,
                pen_color=pen_color,
                pen_width=pen_width,
                brush_color=brush_color,
            )

        # Простые фигуры без вершин
        if tool_type == ToolType.ARC:
            return ArcShape(
                cx=pos.x(),
                cy=pos.y(),
                radius=params.get("radius", 100),
                start_angle=params.get("start_angle", 0),
                end_angle=params.get("end_angle", 180),
                pen_color=pen_color,
                pen_width=pen_width,
                brush_color=brush_color,
            )

        if tool_type == ToolType.CIRCLE:
            from shapes.circle_shape import CircleShape

            return CircleShape(
                cx=pos.x(),
                cy=pos.y(),
                radius=params.get("radius", 100),
                pen_color=pen_color,
                pen_width=pen_width,
                brush_color=brush_color,
            )

        if tool_type == ToolType.PARABOLA:
            from shapes.parabola_shape import ParabolaShape

            return ParabolaShape(
                vertex_x=pos.x(),
                vertex_y=pos.y(),
                focal_length=params.get("focal_length", 80),
                direction=params.get("direction", "up"),
                pen_color=pen_color,
                pen_width=pen_width,
                brush_color=brush_color,
            )

        if tool_type == ToolType.HYPERBOLA:
            from shapes.hyperbola_shape import HyperbolaShape

            return HyperbolaShape(
                cx=pos.x(),
                cy=pos.y(),
                semi_axis_a=params.get("semi_axis_a", 80),
                semi_axis_b=params.get("semi_axis_b", 60),
                direction=params.get("direction", "horizontal"),
                pen_color=pen_color,
                pen_width=pen_width,
                brush_color=brush_color,
            )

        if tool_type == ToolType.ANGLE:
            return AngleShape(
                vertex=(pos.x(), pos.y()),
                side_a=params.get("side_a", 150),
                side_b=params.get("side_b", 100),
                angle_deg=params.get("angle_deg", 90),
                pen_color=pen_color,
                pen_width=pen_width,
                brush_color=brush_color,
                angle_type="single",
            )

        if tool_type == ToolType.ANGLE_ADJACENT:
            return AngleShape(
                vertex=(pos.x(), pos.y()),
                side_a=params.get("side_a", 150),
                side_b=params.get("side_b", 100),
                angle_deg=params.get("angle_deg", 90),
                side_c=params.get("side_c", 150),
                pen_color=pen_color,
                pen_width=pen_width,
                brush_color=brush_color,
                angle_type="adjacent",
            )

        if tool_type == ToolType.ANGLE_VERTICAL:
            return AngleShape(
                vertex=(pos.x(), pos.y()),
                side_a=params.get("side_a", 150),
                side_b=params.get("side_b", 100),
                angle_deg=params.get("angle_deg", 90),
                side_c=params.get("side_c", 150),
                pen_color=pen_color,
                pen_width=pen_width,
                brush_color=brush_color,
                angle_type="vertical",
            )

        if tool_type == ToolType.ANGLE_TRANSVERSAL:
            return AngleShape(
                vertex=(pos.x(), pos.y()),
                side_a=params.get("side_a", 150),
                side_b=params.get("side_b", 100),
                angle_deg=params.get("angle_deg", 45),
                parallel_distance=params.get("parallel_distance", 150),
                pen_color=pen_color,
                pen_width=pen_width,
                brush_color=brush_color,
                angle_type="transversal",
            )

        if tool_type == ToolType.RECTANGLE:
            return RectangleShape(
                x=pos.x(),
                y=pos.y(),
                width=params.get("width", 200),
                height=params.get("height", 150),
                pen_color=pen_color,
                pen_width=pen_width,
                brush_color=brush_color,
                show_diagonals=params.get("show_diagonals", False),
                show_circumcircle=params.get("show_circumcircle", False),
            )

        # Правильные многоугольники
        regular_polygon_tools = (
            ToolType.REGULAR_TRIANGLE,
            ToolType.SQUARE,
            ToolType.REGULAR_PENTAGON,
            ToolType.REGULAR_HEXAGON,
        )
        if tool_type in regular_polygon_tools:
            from shapes.regular_polygon_shape import RegularPolygonShape

            num_sides_map = {
                ToolType.REGULAR_TRIANGLE: 3,
                ToolType.SQUARE: 4,
                ToolType.REGULAR_PENTAGON: 5,
                ToolType.REGULAR_HEXAGON: 6,
            }
            num_sides = params.get("num_sides", num_sides_map.get(tool_type, 6))
            radius = params.get("radius", 100)
            return RegularPolygonShape(
                num_sides=num_sides,
                radius=radius,
                center=(pos.x(), pos.y()),
                pen_color=pen_color,
                pen_width=pen_width,
                brush_color=brush_color,
                selected=False,
                show_angles=params.get("show_angles", False),
                show_diagonals=params.get("show_diagonals", False),
                show_circumcircle=params.get("show_circumcircle", False),
            )

        # Платоновы тела
        platonic_tools = (
            ToolType.TETRAHEDRON,
            ToolType.CUBE,
            ToolType.OCTAHEDRON,
            ToolType.DODECAHEDRON,
            ToolType.ICOSAHEDRON,
        )
        if tool_type in platonic_tools:
            solid_type_map = {
                ToolType.TETRAHEDRON: "tetrahedron",
                ToolType.CUBE: "cube",
                ToolType.OCTAHEDRON: "octahedron",
                ToolType.DODECAHEDRON: "dodecahedron",
                ToolType.ICOSAHEDRON: "icosahedron",
            }
            solid_type = params.get("solid_type", solid_type_map.get(tool_type, "tetrahedron"))
            size = params.get("size", 150)
            return self._create_platonic_solid(
                solid_type=solid_type,
                size=size,
                pos=pos,
                pen_color=pen_color,
                pen_width=pen_width,
                brush_color=brush_color,
            )

        return None

    @staticmethod
    def _create_platonic_solid(
        solid_type: str,
        size: float,
        pos: QPointF,
        pen_color: tuple,
        pen_width: float,
        brush_color: tuple | None,
    ):
        """Создать платоново тело через 3D-2D проекцию."""

        return PlatonicSolidShape(
            solid_type=solid_type,
            size=size,
            center=(pos.x(), pos.y()),
            pen_color=pen_color,
            pen_width=pen_width,
            brush_color=brush_color,
            selected=False,
        )

    @staticmethod
    def _build_trapezoid_scalene(params: dict) -> list[tuple[float, float]]:
        """Построить произвольную трапецию с проверкой на равнобедренность."""
        top_width = params.get("top_width", 100)
        bottom_width = params.get("bottom_width", 200)
        height = params.get("height", 100)
        offset_left = params.get("offset_left", 0)

        offset_right = bottom_width - top_width - offset_left
        if abs(offset_left - offset_right) < 1e-6:
            offset_left = (bottom_width - top_width) / 2 + 10

        return TrapezoidShape.build_scalene(top_width, bottom_width, height, offset_left)

    @staticmethod
    def _create_quadrilateral(
        params: dict,
        pos: QPointF,
        pen_color: tuple,
        pen_width: float,
        brush_color: tuple | None,
    ) -> QuadrilateralShape:
        """Построить неправильный четырёхугольник по 4 сторонам и углу."""
        import math

        from shapes.quadrilateral_shape import QuadrilateralShape

        a = params.get("side_a", 150)
        b = params.get("side_b", 120)
        c = params.get("side_c", 180)
        d = params.get("side_d", 130)
        angle_deg = params.get("angle_deg", 75)
        angle_rad = math.radians(angle_deg)

        # Строим четырёхугольник: AB=a, BC=b, CD=c, DA=d
        # Угол при A = angle_deg
        x0, y0 = 0.0, 0.0
        x1, y1 = a, 0.0  # AB горизонтально
        x2 = x1 + b * math.cos(angle_rad)
        y2 = y1 - b * math.sin(angle_rad)  # Y вверх (будет инвертировано)
        # CD = c, DA = d — решаем систему
        # D находится на расстоянии d от A и c от C
        # (x3-x0)^2 + (y3-y0)^2 = d^2
        # (x3-x2)^2 + (y3-y2)^2 = c^2
        # Решаем геометрически
        dist_AC = math.sqrt((x2 - x0) ** 2 + (y2 - y0) ** 2)
        if dist_AC > c + d or dist_AC < abs(c - d):
            # Не получается — используем упрощённый вариант
            x3 = d * math.cos(angle_rad / 2)
            y3 = d * math.sin(angle_rad / 2)
        else:
            # Косинусная теорема для треугольника ACD
            cos_D = (c**2 + d**2 - dist_AC**2) / (2 * c * d) if c * d != 0 else 0
            cos_D = max(-1, min(1, cos_D))  # clamp
            angle_DAC = math.acos(cos_D)
            angle_OA = math.atan2(y2, x2)
            x3 = d * math.cos(angle_OA + angle_DAC)
            y3 = d * math.sin(angle_OA + angle_DAC)

        vertices = [(x0, y0), (x1, y1), (x2, y2), (x3, y3)]
        # Инвертируем Y для Qt
        vertices = [(v[0], -v[1]) for v in vertices]
        # Центрируем
        cx = sum(v[0] for v in vertices) / 4
        cy = sum(v[1] for v in vertices) / 4
        vertices = [(v[0] - cx + pos.x(), v[1] - cy + pos.y()) for v in vertices]

        return QuadrilateralShape(
            vertices=vertices,
            pen_color=pen_color,
            pen_width=pen_width,
            brush_color=brush_color,
            show_heights=params.get("show_heights", False),
            show_diagonals=params.get("show_diagonals", False),
            show_bisectors=params.get("show_bisectors", False),
            show_angles=params.get("show_angles", False),
            show_circumcircle=params.get("show_circumcircle", False),
            height_from_vertex=params.get("height_from_vertex", -1),
        )
