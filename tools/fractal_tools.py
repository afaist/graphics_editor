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
    """Генерирует ковёр Серпинского — список заполненных квадратов.

    Args:
        x, y: левый верхний угол
        size: размер квадрата
        depth: глубина рекурсии

    Returns:
        список заполненных квадратов (x, y, width, height)
    """
    if depth == 0:
        return [(x, y, size, size)]

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
    ax: float,
    ay: float,
    bx: float,
    by: float,
    depth: int = 7,
    angle: float = 45.0,
    min_size: float = 1.5,
) -> list[list[tuple[float, float]]]:
    """Генерирует дерево Пифагора — список закрашенных квадратов.

    Алгоритм:
    1. На основании AB достраиваем квадрат (ABCD)
    2. На верхней стороне DC квадрата строим прямоугольный треугольник с вершиной E
    3. Рекурсивно строим деревья на катетах DE и EC

    Args:
        ax, ay: начало основания ветки (нижний левый угол)
        bx, by: конец основания ветки (нижний правый угол)
        depth: глубина рекурсии (уровень). depth=1 → 1 квадрат, depth=3 → 15 квадратов
        angle: угол при основании треугольника в градусах (45 — классическое дерево)
        min_size: минимальная длина основания для отсечения (по умолчанию 1.5 px)

    Returns:
        список квадратов (список из 4 кортежей (x, y))
    """
    # Валидация угла — предотвращаем вырожденные ветви
    angle = max(5.0, min(85.0, angle))

    squares: list[list[tuple[float, float]]] = []

    def _build(ax_pt: float, ay_pt: float, bx_pt: float, by_pt: float, d: int) -> None:
        if d <= 0:
            return

        s = math.hypot(bx_pt - ax_pt, by_pt - ay_pt)
        if s < min_size:
            return

        # Единичный вектор основания и перпендикуляр "вверх"
        ux, uy = (bx_pt - ax_pt) / s, (by_pt - ay_pt) / s
        nx, ny = uy, -ux

        # Вершины квадрата: A, B, C, D (по часовой стрелке)
        # A (нижний левый), B (нижний правый), C (верхний правый), D (верхний левый)
        c_x = bx_pt + nx * s
        c_y = by_pt + ny * s
        d_x = ax_pt + nx * s
        d_y = ay_pt + ny * s

        # Треугольник строится на ВЕРХНЕЙ стороне квадрата (DC)
        # Вектор от D к C — он равен вектору от A к B
        # Вершина E над стороной DC через тригонометрию
        rad = math.radians(angle)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        e_x = d_x + s * cos_a * (cos_a * ux + sin_a * nx)
        e_y = d_y + s * cos_a * (cos_a * uy + sin_a * ny)

        # Добавляем квадрат — большие рисуются первыми, маленькие поверх
        squares.append(
            [
                (ax_pt, ay_pt),
                (bx_pt, by_pt),
                (c_x, c_y),
                (d_x, d_y),
            ]
        )

        # Рекурсивные вызовы — квадраты на катетах DE и EC
        # Левая ветвь: от D к E
        _build(d_x, d_y, e_x, e_y, d - 1)
        # Правая ветвь: от E к C
        _build(e_x, e_y, c_x, c_y, d - 1)

    _build(ax, ay, bx, by, depth)
    return squares

    _build(ax, ay, bx, by, depth)
    return squares


def generate_cantor_set(
    x1: float, y: float, x2: float, depth: int = 6
) -> tuple[list[tuple[float, float, float, float, float, float]], float]:
    """Генерирует множество Кантора — все уровни, сложенные вертикально.

    Каждый уровень — отрезки на своей высоте y + level * line_spacing.
    Возвращает список кортежей (x1, y1, x2, y2, r, g, b) для отрисовки линиями.

    Args:
        x1, y: левый край и вертикальная позиция уровня 0
        x2: правый край
        depth: глубина рекурсии (показывает уровни 0..depth)

    Returns:
        (список сегментов с цветами, общая высота фрактала)
    """
    segments_with_color: list[tuple[float, float, float, float, float, float]] = []
    line_spacing = max(15.0, (x2 - x1) / 12.0)  # расстояние между уровнями

    def _cantor_segments(sx1: float, sx2: float, d: int, level: int) -> list[tuple[float, float]]:
        """Возвращает отрезки уровня d."""
        if d == 0:
            return [(sx1, sx2)]
        third = (sx2 - sx1) / 3
        return _cantor_segments(sx1, sx1 + third, d - 1, level) + _cantor_segments(
            sx2 - third, sx2, d - 1, level
        )

    for level in range(depth + 1):
        segs = _cantor_segments(x1, x2, level, level)
        y_level = y + level * line_spacing

        # Цвет: от тёмного к светлому (градиент от синего к жёлтому)
        t = level / max(1, depth)
        # Простой градиент: синий → голубой → зелёный → жёлтый
        r = min(255, int(60 + 195 * t))
        g = min(255, int(80 + 140 * t))
        b = min(255, int(220 - 180 * t))

        for sx1, sx2 in segs:
            segments_with_color.append((sx1, y_level, sx2, y_level, r, g, b))

    total_height = (depth + 1) * line_spacing
    return segments_with_color, total_height


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
        escaped = (np.abs(Z) > 2) & mask
        result[escaped] = i

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
        escaped = (np.abs(Z) > 2) & mask
        result[escaped] = i

    return result.tolist(), width / (x_max - x_min), height / (y_max - y_min)


def generate_newton(
    width: int,
    height: int,
    x_min: float = -2.5,
    x_max: float = 2.5,
    y_min: float = -2.5,
    y_max: float = 2.5,
    roots: list[complex] | None = None,
    max_iter: int = 50,
) -> tuple[bytes, int, int, int, int]:
    """Генерирует бассейн Ньютона.

    Алгоритм:
    1. Итеративно применяем метод Ньютона к каждой точке
    2. Запоминаем индекс корня и число итераций для каждой точки
    3. Раскрашиваем: цвет корня × затемнение по числу итераций

    Args:
        width, height: размер изображения
        x_min, x_max, y_min, y_max: область комплексной плоскости
        roots: список корней полинома (по умолчанию z³ - 1 = 0)
        max_iter: максимальное число итераций

    Returns:
        (RGBA данные, width, height, x_scale, y_scale)
    """
    try:
        import numpy as np
    except ImportError:
        return b"", 1, 1, 1.0, 1.0

    if roots is None:
        roots = [
            complex(1, 0),
            complex(-0.5, math.sqrt(3) / 2),
            complex(-0.5, -math.sqrt(3) / 2),
        ]

    roots_arr = np.array(roots, dtype=np.complex128)
    # Цвета корней: красноватый, зеленоватый, синеватый
    root_colors = np.array(
        [
            [230, 70, 60],
            [60, 180, 90],
            [70, 110, 240],
        ],
        dtype=np.float64,
    )

    x = np.linspace(x_min, x_max, width)
    y = np.linspace(y_min, y_max, height)
    X, Y = np.meshgrid(x, y)
    Z = X + 1j * Y

    # root_idx: индекс корня (-1 = не сошлось), steps: число итераций
    root_idx = np.full(Z.shape, -1, dtype=np.int32)
    steps = np.zeros(Z.shape, dtype=np.float64)
    active = np.ones(Z.shape, dtype=bool)

    for i in range(max_iter):
        Z[active] = Z[active] - (Z[active] ** 3 - 1) / (3 * Z[active] ** 2)
        # К какому корню притянуло
        dist = np.abs(Z[:, :, None] - roots_arr[None, None, :])
        near = dist.argmin(axis=2)
        done = dist.min(axis=2) < 1e-6
        just_now = active & done
        root_idx[just_now] = near[just_now]
        steps[just_now] = i
        active &= ~done

    # Раскрашиваем
    out = np.zeros((height, width, 3), dtype=np.uint8)
    for k in range(len(roots)):
        mask = root_idx == k
        t = steps[mask] / max_iter
        factor = 1.0 - 0.75 * np.sqrt(t)  # чем дольше — тем темнее
        out[mask] = (root_colors[k] * factor[:, None]).astype(np.uint8)

    # Не сошлось — почти чёрный
    out[root_idx == -1] = [15, 15, 25]

    # Конвертируем в RGBA
    rgba = bytearray()
    for row in out:
        for r, g, b in row:
            rgba.extend([b, g, r, 255])  # BGRA для QImage

    return bytes(rgba), width, height, width / (x_max - x_min), height / (y_max - y_min)
