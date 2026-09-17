"""Валидация данных фигур при загрузке из JSON."""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional, Set

# Карта обязательных полей для каждого типа фигуры
SHAPE_REQUIRED_FIELDS: Dict[str, List[str]] = {
    "point": ["x", "y", "pen_color", "pen_width"],
    "line": ["x1", "y1", "x2", "y2", "pen_color", "pen_width"],
    "ray": ["x1", "y1", "x2", "y2", "pen_color", "pen_width"],
    "infinite_line": ["x1", "y1", "x2", "y2", "pen_color", "pen_width"],
    "rectangle": ["x", "y", "width", "height", "pen_color", "pen_width"],
    "ellipse": ["x", "y", "width", "height", "pen_color", "pen_width"],
    "polygon": ["vertices", "pen_color", "pen_width"],
    "polyline": ["vertices", "pen_color", "pen_width"],
    # Новые типы (могут отсутствовать, если ещё не реализованы)
    "arc": ["x", "y", "width", "height", "start_angle", "sweep_angle", "pen_color", "pen_width"],
    "text": ["x", "y", "text", "pen_color", "pen_width"],
    # Треугольники
    "triangle_equilateral": ["vertices", "pen_color", "pen_width", "triangle_type"],
    "triangle_isosceles": ["vertices", "pen_color", "pen_width", "triangle_type"],
    "triangle_right": ["vertices", "pen_color", "pen_width", "triangle_type"],
    "triangle_obtuse": ["vertices", "pen_color", "pen_width", "triangle_type"],
    # Параллелограмм
    "parallelogram": ["vertices", "pen_color", "pen_width"],
    # Трапеции
    "trapezoid_isosceles": ["vertices", "pen_color", "pen_width", "trapezoid_type"],
    "trapezoid": ["vertices", "pen_color", "pen_width", "trapezoid_type"],
    # Угол
    "angle": ["vertex", "side_a", "side_b", "angle_deg", "pen_color", "pen_width"],
}

# Максимально допустимый размер файла проекта (10 МБ)
MAX_FILE_SIZE = 10 * 1024 * 1024

# Максимально допустимое количество фигур в проекте (защита от переполнения)
MAX_SHAPES = 10_000

# Максимальное количество вершин для полигона/ломаной
MAX_VERTICES = 5_000


class ValidationError(Exception):
    """Ошибка валидации данных фигуры."""

    def __init__(self, message: str, shape_index: int = -1):
        self.shape_index = shape_index
        full_message = message
        if shape_index >= 0:
            full_message = f"[Фигура #{shape_index}] {message}"
        super().__init__(full_message)
        self.message = full_message


def validate_file_size(filepath: str) -> Optional[str]:
    """
    Проверить размер файла перед загрузкой.

    Args:
        filepath: путь к файлу

    Returns:
        предупреждение при превышении лимита или None
    """
    try:
        size = os.path.getsize(filepath)
        if size > MAX_FILE_SIZE:
            return (
                f"Файл слишком большой: {size} байт "
                f"(максимум: {MAX_FILE_SIZE} байт, ~{MAX_FILE_SIZE // 1024 // 1024} МБ)"
            )
        if size == 0:
            return "Файл пустой"
    except OSError as e:
        return f"Невозможно проверить размер файла: {e}"
    return None


def validate_project_data(data: Dict[str, Any]) -> List[str]:
    """
    Валидировать корневые данные проекта.

    Args:
        data: корневой словарь проекта из JSON

    Returns:
        список предупреждений (пустой при отсутствии проблем)

    Raises:
        ValidationError: при критических ошибках
    """
    warnings: List[str] = []

    # Проверка версии
    if "version" not in data:
        warnings.append("Отсутствует поле 'version' — предполагается формат 1.0")
    else:
        version = data["version"]
        if not isinstance(version, str):
            warnings.append("Поле 'version' должно быть строкой")

    # Проверка наличия фигур
    if "shapes" not in data:
        raise ValidationError("Отсутствует обязательное поле 'shapes'")

    shapes = data["shapes"]
    if not isinstance(shapes, list):
        raise ValidationError("Поле 'shapes' должно быть массивом")

    # Проверка количества фигур
    if len(shapes) > MAX_SHAPES:
        raise ValidationError(
            f"Слишком много фигур: {len(shapes)} (максимум: {MAX_SHAPES})"
        )

    return warnings


def validate_shape_data(
    shape_data: Dict[str, Any], index: int = -1
) -> Optional[str]:
    """
    Валидировать данные конкретной фигуры.

    Args:
        shape_data: словарь данных фигуры
        index: индекс фигуры для информативности

    Returns:
        строка предупреждения при проблеме или None при успехе
    """
    shape_type = shape_data.get("type")

    if not shape_type:
        return f"Отсутствует поле 'type' в фигуре #{index}"

    # Проверяем, известен ли тип фигуры
    if shape_type not in SHAPE_REQUIRED_FIELDS:
        return f"Неизвестный тип фигуры: '{shape_type}' — пропущена валидация"

    # Проверяем обязательные поля
    required = SHAPE_REQUIRED_FIELDS[shape_type]
    missing = [field for field in required if field not in shape_data]

    if missing:
        return (
            f"Отсутствуют обязательные поля: {', '.join(missing)}"
        )

    # Валидация числовых полей
    numeric_fields = ["x", "y", "x1", "y1", "x2", "y2", "width", "height"]
    for field in numeric_fields:
        if field in shape_data:
            val = shape_data[field]
            if not isinstance(val, (int, float)):
                return f"Поле '{field}' должно быть числом, получено: {type(val).__name__}"
            if isinstance(val, float) and (val != val):  # NaN check
                return f"Поле '{field}' содержит NaN"

    # Валидация pen_color
    if "pen_color" in shape_data:
        pc = shape_data["pen_color"]
        if not isinstance(pc, (list, tuple)) or len(pc) != 3:
            return "Поле 'pen_color' должно быть кортежем из 3 чисел"
        for i, c in enumerate(pc):
            if not isinstance(c, int) or not (0 <= c <= 255):
                return f"Компонента цвета pen_color[{i}] должна быть int 0-255"

    # Валидация pen_width
    if "pen_width" in shape_data:
        pw = shape_data["pen_width"]
        if not isinstance(pw, (int, float)) or pw < 0.5:
            return "pen_width должно быть >= 0.5"

    # Валидация vertices для polygon/polyline
    if shape_type in ("polygon", "polyline") and "vertices" in shape_data:
        verts = shape_data["vertices"]
        if not isinstance(verts, list):
            return "Поле 'vertices' должно быть массивом"
        if len(verts) > MAX_VERTICES:
            return (
                f"Слишком много вершин: {len(verts)} (максимум: {MAX_VERTICES})"
            )
        if len(verts) < 2:
            return f"Минимум 2 вершины для {shape_type}, получено: {len(verts)}"
        for vi, v in enumerate(verts):
            if not isinstance(v, dict):
                return f"Вершина [{vi}] должна быть объектом {{x, y}}"
            if "x" not in v or "y" not in v:
                return f"Вершина [{vi}] должна содержать 'x' и 'y'"
            for coord in ("x", "y"):
                if not isinstance(v[coord], (int, float)):
                    return f"Вершина [{vi}].{coord} должно быть числом"

    # Валидация vertex для angle
    if shape_type == "angle" and "vertex" in shape_data:
        vertex = shape_data["vertex"]
        if not isinstance(vertex, dict):
            return "Поле 'vertex' должно быть объектом {x, y}"
        if "x" not in vertex or "y" not in vertex:
            return "Поле 'vertex' должно содержать 'x' и 'y'"
        for coord in ("x", "y"):
            if not isinstance(vertex[coord], (int, float)):
                return f"Поле 'vertex'.{coord} должно быть числом"
        # side_a, side_b должны быть положительными
        for field in ("side_a", "side_b"):
            if field in shape_data:
                val = shape_data[field]
                if not isinstance(val, (int, float)) or val <= 0:
                    return f"Поле '{field}' должно быть положительным числом"
        # angle_deg в диапазоне 0..360
        if "angle_deg" in shape_data:
            val = shape_data["angle_deg"]
            if not isinstance(val, (int, float)):
                return "Поле 'angle_deg' должно быть числом"
            if val <= 0 or val > 360:
                return "Поле 'angle_deg' должно быть в диапазоне 0..360"

    # Валидация brush_color (опциональное поле)
    if "brush_color" in shape_data and shape_data["brush_color"] is not None:
        bc = shape_data["brush_color"]
        if not isinstance(bc, (list, tuple)) or len(bc) != 3:
            return "Поле 'brush_color' должно быть кортежем из 3 чисел или null"
        for i, c in enumerate(bc):
            if not isinstance(c, int) or not (0 <= c <= 255):
                return f"Компонента цвета brush_color[{i}] должна быть int 0-255"

    return None
