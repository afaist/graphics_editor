"""Инструменты для генерации фракталов."""

from __future__ import annotations

import math


def generate_koch_segment(
    x1: float, y1: float, x2: float, y2: float, depth: int = 4
) -> list[tuple[float, float]]:
    """Генерирует снежинку Коха из одного отрезка.

    Args:
        x1, y1: начало отрезка
        x2, y2: конец отрезка
        depth: глубина рекурсии

    Returns:
        список точек ломаной Коха
    """
    if depth == 0:
        return [(x1, y1), (x2, y2)]

    # Трети отрезка
    ax, ay = x1 + (x2 - x1) / 3, y1 + (y2 - y1) / 3
    bx, by = x1 + 2 * (x2 - x1) / 3, y1 + 2 * (y2 - y1) / 3

    # Вершина равностороннего треугольника
    mx, my = (ax + bx) / 2, (ay + by) / 2
    dx, dy = bx - ax, by - ay
    px, py = mx - dy * math.sqrt(3) / 2, my + dx * math.sqrt(3) / 2

    # Рекурсивно для четырёх подотрезков
    points: list[tuple[float, float]] = []
    points.extend(generate_koch_segment(x1, y1, ax, ay, depth - 1)[:-1])
    points.extend(generate_koch_segment(ax, ay, px, py, depth - 1)[:-1])
    points.extend(generate_koch_segment(px, py, bx, by, depth - 1)[:-1])
    points.extend(generate_koch_segment(bx, by, x2, y2, depth - 1))
    return points


def generate_koch_snowflake(
    cx: float, cy: float, radius: float, depth: int = 4
) -> list[list[tuple[float, float]]]:
    """Генерирует снежинку Коха из треугольника.

    Args:
        cx, cy: центр
        radius: радиус описанной окружности
        depth: глубина рекурсии

    Returns:
        список ломаных (по одной на сторону)
    """
    angles = [0.0, 2 * math.pi / 3, 4 * math.pi / 3]
    vertices = [(cx + radius * math.cos(a), cy + radius * math.sin(a)) for a in angles]

    segments = []
    for i in range(3):
        x1, y1 = vertices[i]
        x2, y2 = vertices[(i + 1) % 3]
        points = generate_koch_segment(x1, y1, x2, y2, depth)
        segments.append(points)

    return segments


def generate_sierpinski_triangle(
    x1: float, y1: float, x2: float, y2: float, x3: float, y3: float, depth: int = 5
) -> list[list[tuple[float, float]]]:
    """Генерирует треугольник Серпинского.

    Args:
        x1, y1, x2, y2, x3, y3: вершины исходного треугольника
        depth: глубина рекурсии

    Returns:
        список треугольников (каждый — список из 3 точек)
    """
    if depth == 0:
        return [[(x1, y1), (x2, y2), (x3, y3)]]

    # Середины сторон
    mx1, my1 = (x1 + x2) / 2, (y1 + y2) / 2
    mx2, my2 = (x2 + x3) / 2, (y2 + y3) / 2
    mx3, my3 = (x1 + x3) / 2, (y1 + y3) / 2

    # Три подтреугольника
    triangles = []
    triangles.extend(generate_sierpinski_triangle(x1, y1, mx1, my1, mx3, my3, depth - 1))
    triangles.extend(generate_sierpinski_triangle(mx1, my1, x2, y2, mx2, my2, depth - 1))
    triangles.extend(generate_sierpinski_triangle(mx3, my3, mx2, my2, x3, y3, depth - 1))
    return triangles


def generate_sierpinski_carpet(
    x: float, y: float, size: float, depth: int = 4
) -> list[tuple[float, float, float, float]]:
    """Генерирует ковёр Серпинского.

    Args:
        x, y: левый верхний угол
        size: размер квадрата
        depth: глубина рекурсии

    Returns:
        список пустых квадратов (x, y, width, height)
    """
    if depth == 0:
        return []

    sub_size = size / 3
    carpets = []

    # 8 подквадратов (пропускаем центральный)
    for i in range(3):
        for j in range(3):
            if i == 1 and j == 1:
                continue  # пропускаем центр
            carpets.extend(
                generate_sierpinski_carpet(x + j * sub_size, y + i * sub_size, sub_size, depth - 1)
            )

    return carpets


def generate_pythagorean_tree(
    x: float, y: float, angle: float, size: float, depth: int = 7
) -> list[list[tuple[float, float]]]:
    """Генерирует дерево Пифагора.

    Args:
        x, y: основание ствола
        angle: угол наклона (радианы)
        size: размер базового квадрата
        depth: глубина рекурсии

    Returns:
        список отрезков (каждый — пара точек)
    """
    segments: list[list[tuple[float, float]]] = []

    def _draw_tree(x: float, y: float, angle: float, size: float, d: int) -> None:
        if d == 0 or size < 0.5:
            return

        # Верхняя сторона квадрата
        x2 = x + size * math.cos(angle)
        y2 = y + size * math.sin(angle)
        x3 = x2 - size * math.sin(angle)
        y3 = y2 + size * math.cos(angle)
        x4 = x - size * math.sin(angle)
        y4 = y + size * math.cos(angle)

        # Квадрат как 4 отрезка
        segments.append([(x, y), (x2, y2)])
        segments.append([(x2, y2), (x3, y3)])
        segments.append([(x3, y3), (x4, y4)])
        segments.append([(x4, y4), (x, y)])

        # Два дочерних квадрата
        new_size = size / math.sqrt(2)
        _draw_tree(x2, y2, angle - math.pi / 4, new_size, d - 1)
        _draw_tree(x4, y4, angle + math.pi / 4, new_size, d - 1)

    _draw_tree(x, y, angle, size, depth)
    return segments


def generate_cantor_set(
    x1: float, y: float, x2: float, depth: int = 6
) -> list[tuple[float, float, float, float]]:
    """Генерирует множество Кантора.

    Args:
        x1, y: левый край и вертикальная позиция
        x2: правый край
        depth: глубина рекурсии

    Returns:
        список отрезков (x, y, width, height)
    """
    if depth == 0:
        return [(x1, y, x2 - x1, 1)]

    width = x2 - x1
    third = width / 3

    segments = []
    segments.extend(generate_cantor_set(x1, y, x1 + third, depth - 1))
    segments.extend(generate_cantor_set(x1 + 2 * third, y, x2, depth - 1))

    return segments


def generate_mandelbrot(
    width: int,
    height: int,
    x_min: float,
    x_max: float,
    y_min: float,
    y_max: float,
    max_iter: int = 256,
) -> tuple[list[list[int]], float, float]:
    """Генерирует множество Мандельброта.

    Args:
        width, height: размер изображения
        x_min, x_max, y_min, y_max: область комплексной плоскости
        max_iter: максимальное число итераций

    Returns:
        (цветовая карта, масштаб по x, масштаб по y)
    """
    try:
        import numpy as np
    except ImportError:
        return [], 1.0, 1.0

    x = np.linspace(x_min, x_max, width)
    y = np.linspace(y_min, y_max, height)
    X, Y = np.meshgrid(x, y)
    C = X + 1j * Y

    Z = np.zeros_like(C, dtype=np.complex128)
    result = np.zeros_like(C, dtype=np.int32)

    for i in range(max_iter):
        mask = np.abs(Z) <= 2
        Z[mask] = Z[mask] ** 2 + C[mask]
        result[np.abs(Z) > 2 & mask] = i

    return result.tolist(), width / (x_max - x_min), height / (y_max - y_min)


def generate_julia(
    width: int,
    height: int,
    x_min: float,
    x_max: float,
    y_min: float,
    y_max: float,
    c_real: float,
    c_imag: float,
    max_iter: int = 256,
) -> tuple[list[list[int]], float, float]:
    """Генерирует множество Жюлиа.

    Args:
        width, height: размер изображения
        x_min, x_max, y_min, y_max: область комплексной плоскости
        c_real, c_imag: комплексное число c
        max_iter: максимальное число итераций

    Returns:
        (цветовая карта, масштаб по x, масштаб по y)
    """
    try:
        import numpy as np
    except ImportError:
        return [], 1.0, 1.0

    x = np.linspace(x_min, x_max, width)
    y = np.linspace(y_min, y_max, height)
    X, Y = np.meshgrid(x, y)
    Z = X + 1j * Y
    C = np.full_like(Z, c_real + 1j * c_imag)

    result = np.zeros_like(Z, dtype=np.int32)

    for i in range(max_iter):
        mask = np.abs(Z) <= 2
        Z[mask] = Z[mask] ** 2 + C[mask]
        result[np.abs(Z) > 2 & mask] = i

    return result.tolist(), width / (x_max - x_min), height / (y_max - y_min)


def generate_newton(
    width: int,
    height: int,
    x_min: float,
    x_max: float,
    y_min: float,
    y_max: float,
    roots: list[complex],
    max_iter: int = 64,
) -> tuple[list[list[int]], float, float]:
    """Генерирует бассейн Ньютона для полинома с заданными корнями.

    Args:
        width, height: размер изображения
        x_min, x_max, y_min, y_max: область комплексной плоскости
        roots: список корней полинома
        max_iter: максимальное число итераций

    Returns:
        (цветовая карта, масштаб по x, масштаб по y)
    """
    try:
        import numpy as np
    except ImportError:
        return [], 1.0, 1.0

    x = np.linspace(x_min, x_max, width)
    y = np.linspace(y_min, y_max, height)
    X, Y = np.meshgrid(x, y)
    Z = X + 1j * Y

    result = np.zeros_like(Z, dtype=np.int32)
    colors = np.zeros_like(Z, dtype=np.int32)

    for i in range(max_iter):
        # f(z) = product(z - root)
        fz = np.ones_like(Z)
        # f'(z) = sum(product(z - root) / (z - root))
        dfz = np.zeros_like(Z)
        for root in roots:
            fz = fz * (Z - root)
            dfz = dfz + fz / (Z - root + 1e-10)

        Z_new = Z - fz / dfz

        # Проверяем сходимость к корням
        for idx, root in enumerate(roots):
            mask = np.abs(Z_new - root) < 1e-6
            result[mask] = i
            colors[mask] = idx

        Z = Z_new

    return result.tolist(), width / (x_max - x_min), height / (y_max - y_min)
