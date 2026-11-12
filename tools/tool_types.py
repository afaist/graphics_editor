"""Типы инструментов графического редактора."""

from __future__ import annotations

from enum import Enum


class ToolType(Enum):
    """Типы инструментов."""

    SELECT = "select"
    MOVE = "move"
    POINT = "point"
    LINE = "line"
    RAY = "ray"
    INFINITE_LINE = "infinite_line"
    RECTANGLE = "rectangle"
    ELLIPSE = "ellipse"
    CIRCLE = "circle"
    POLYGON = "polygon"
    PENCIL = "pencil"
    POLYLINE = "polyline"
    ARC = "arc"
    PARABOLA = "parabola"
    HYPERBOLA = "hyperbola"
    TEXT = "text"
    TRIANGLE_EQUILATERAL = "triangle_equilateral"
    TRIANGLE_ISOSCELES = "triangle_isosceles"
    TRIANGLE_RIGHT = "triangle_right"
    TRIANGLE_OBTUSE = "triangle_obtuse"
    TRIANGLE_CONGRUENT = "triangle_congruent"
    TRIANGLE_SIMILAR = "triangle_similar"
    TRIANGLE_SHARYGIN = "triangle_sharygin"
    PARALLELOGRAM = "parallelogram"
    TRAPEZOID_ISOSCELES = "trapezoid_isosceles"
    TRAPEZOID = "trapezoid"
    ANGLE = "angle"
    ANGLE_ADJACENT = "angle_adjacent"
    ANGLE_VERTICAL = "angle_vertical"
    ANGLE_TRANSVERSAL = "angle_transversal"
    FORMULA = "formula"
    GRAPH_LINEAR = "graph_linear"
    GRAPH_QUADRATIC = "graph_quadratic"
    GRAPH_SIN = "graph_sin"
    GRAPH_COS = "graph_cos"
    GRAPH_TAN = "graph_tan"
    GRAPH_LOG = "graph_log"
    GRAPH_EXP = "graph_exp"
    GRAPH_SQRT = "graph_sqrt"
    # Правильные многоугольники
    REGULAR_TRIANGLE = "regular_triangle"
    SQUARE = "square"
    REGULAR_PENTAGON = "regular_pentagon"
    REGULAR_HEXAGON = "regular_hexagon"
    # Платоновы тела
    TETRAHEDRON = "tetrahedron"
    CUBE = "cube"
    OCTAHEDRON = "octahedron"
    DODECAHEDRON = "dodecahedron"
    ICOSAHEDRON = "icosahedron"
    # 3D тела
    SOLIDS_3D = "solids_3d"  # родительская кнопка
    PARALLELEPIPED = "parallelepiped"
    SPHERE = "sphere"
    CYLINDER = "cylinder"
    CONE = "cone"
    PYRAMID = "pyramid"
    PRISM = "prism"
    TRUNCATED_CONE = "truncated_cone"
    TRUNCATED_PYRAMID = "truncated_pyramid"
    # Тригонометрия
    TRIGONOMETRIC_CIRCLE = "trigonometric_circle"
    UNIT_CIRCLE = "unit_circle"
    TRIG_CIRCLE_FULL = "trig_circle_full"
    # Четырёхугольники
    QUADRILATERALS = "quadrilaterals"  # родительская кнопка
    RHOMBUS = "rhombus"
    QUADRILATERAL_IRREGULAR = "quadrilateral_irregular"
    CIRCUMSCRIBED_QUADRILATERAL = "circumscribed_quadrilateral"
    # Фракталы
    FRACTALS = "fractals"  # родительская кнопка
    # Геометрические фракталы
    FRACTAL_KOCH = "fractal_koch"
    FRACTAL_SIERPINSKI_TRIANGLE = "fractal_sierpinski_triangle"
    FRACTAL_SIERPINSKI_CARPET = "fractal_sierpinski_carpet"
    FRACTAL_PYTHAGOREAN_TREE = "fractal_pythagorean_tree"
    FRACTAL_CANTOR_SET = "fractal_cantor_set"
    # Алгебраические фракталы
    FRACTAL_MANDELBROT = "fractal_mandelbrot"
    FRACTAL_JULIA = "fractal_julia"
    FRACTAL_NEWTON = "fractal_newton"
