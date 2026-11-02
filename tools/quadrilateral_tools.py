"""Инструменты для построения дополнительных элементов четырёхугольников."""

from __future__ import annotations

import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen

# ====================================================================
# Вспомогательные математические функции
# ====================================================================


def _project_point_to_line(point: QPointF, line_start: QPointF, line_end: QPointF) -> QPointF:
    """Проекция точки на прямую, проходящую через line_start и line_end."""
    dx = line_end.x() - line_start.x()
    dy = line_end.y() - line_start.y()
    length_sq = dx * dx + dy * dy
    if length_sq < 1e-10:
        return line_start
    t = ((point.x() - line_start.x()) * dx + (point.y() - line_start.y()) * dy) / length_sq
    return QPointF(line_start.x() + t * dx, line_start.y() + t * dy)


def _bisector_direction(v_prev: QPointF, v_current: QPointF, v_next: QPointF) -> QPointF:
    """Направление биссектрисы угла v_current (между v_current-v_prev и v_current-v_next)."""
    d1 = QPointF(v_prev.x() - v_current.x(), v_prev.y() - v_current.y())
    d2 = QPointF(v_next.x() - v_current.x(), v_next.y() - v_current.y())
    len1 = math.sqrt(d1.x() * d1.x() + d1.y() * d1.y())
    len2 = math.sqrt(d2.x() * d2.x() + d2.y() * d2.y())
    if len1 < 1e-10 or len2 < 1e-10:
        return QPointF(0, 0)
    u1 = QPointF(d1.x() / len1, d1.y() / len1)
    u2 = QPointF(d2.x() / len2, d2.y() / len2)
    bisect = QPointF(u1.x() + u2.x(), u1.y() + u2.y())
    blen = math.sqrt(bisect.x() * bisect.x() + bisect.y() * bisect.y())
    if blen < 1e-10:
        return QPointF(0, 0)
    return QPointF(bisect.x() / blen, bisect.y() / blen)


def _angle_at_vertex(v_prev: QPointF, v_current: QPointF, v_next: QPointF) -> float:
    """Угол в градусах в вершине v_current между сторонами v_prev-v_current и v_next-v_current."""
    d1 = QPointF(v_prev.x() - v_current.x(), v_prev.y() - v_current.y())
    d2 = QPointF(v_next.x() - v_current.x(), v_next.y() - v_current.y())
    dot = d1.x() * d2.x() + d1.y() * d2.y()
    cross = d1.x() * d2.y() - d1.y() * d2.x()
    angle = math.degrees(math.atan2(abs(cross), dot))
    return angle


def _circumcircle_from_three_points(
    p1: QPointF, p2: QPointF, p3: QPointF
) -> tuple[QPointF | None, float | None]:
    """Центр и радиус окружности, проходящей через 3 точки."""
    mx1, my1 = (p1.x() + p2.x()) / 2.0, (p1.y() + p2.y()) / 2.0
    mx2, my2 = (p2.x() + p3.x()) / 2.0, (p2.y() + p3.y()) / 2.0
    dx1, dy1 = p2.x() - p1.x(), p2.y() - p1.y()
    dx2, dy2 = p3.x() - p2.x(), p3.y() - p2.y()
    det = dx1 * dy2 - dy1 * dx2
    if abs(det) < 1e-10:
        return None, None
    t = ((mx2 - mx1) * dy2 - (my2 - my1) * dx2) / det
    center = QPointF(mx1 + t * dx1, my1 + t * dy1)
    radius = center.distanceToPoint(p1)
    return center, radius


def _get_vertices(shape) -> list[QPointF]:
    """Получить список вершин из фигуры."""
    if hasattr(shape, "_vertices") and shape._vertices:
        return shape._vertices
    return []


# ====================================================================
# Основные методы рисования
# ====================================================================


def draw_diagonals(painter: QPainter, shape) -> None:
    """Рисует диагонали четырёхугольника (пунктир, darkGray)."""
    vertices = _get_vertices(shape)
    if len(vertices) < 4:
        return

    painter.save()
    try:
        pen = QPen(QColor(Qt.GlobalColor.darkGray), 1.0, Qt.PenStyle.DashLine)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawLine(vertices[0], vertices[2])
        painter.drawLine(vertices[1], vertices[3])
    finally:
        painter.restore()


def draw_heights(painter: QPainter, shape, vertex_index: int | None = None) -> None:
    """Рисует высоты четырёхугольника (пунктир, blue).

    Если vertex_index не указан — рисует все 4 высоты.
    Высота из вершины V_i = перпендикуляр из V_i на противоположную сторону.
    """
    vertices = _get_vertices(shape)
    if len(vertices) < 4:
        return

    painter.save()
    try:
        pen = QPen(QColor(Qt.GlobalColor.blue), 1.0, Qt.PenStyle.DashLine)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        opposite_edges = [
            ((2, 3), (1, 2)),  # из A: на CD и BC
            ((3, 0), (2, 3)),  # из B: на DA и CD
            ((0, 1), (3, 0)),  # из C: на AB и DA
            ((1, 2), (0, 1)),  # из D: на BC и AB
        ]

        if vertex_index is not None:
            if 0 <= vertex_index < 4:
                edges = opposite_edges[vertex_index]
                for e_start, e_end in edges:
                    foot = _project_point_to_line(
                        vertices[vertex_index],
                        vertices[e_start],
                        vertices[e_end],
                    )
                    painter.drawLine(vertices[vertex_index], foot)
        else:
            # Из всех вершин — по одной высоте на противоположную сторону
            # A -> CD, B -> DA, C -> AB, D -> BC
            pairs = [
                (0, 3, 0),  # A -> CD
                (1, 0, 1),  # B -> DA
                (2, 1, 2),  # C -> AB
                (3, 2, 3),  # D -> BC
            ]
            for vi, e_start, e_end in pairs:
                foot = _project_point_to_line(vertices[vi], vertices[e_start], vertices[e_end])
                painter.drawLine(vertices[vi], foot)
    finally:
        painter.restore()


def draw_bisectors(painter: QPainter, shape, vertex_indices: list[int] | None = None) -> None:
    """Рисует биссектрисы четырёхугольника (штрих-пунктир, green).

    Биссектриса = линия из вершины, делящая угол пополам.
    Длина биссектрисы: ~60% от меньшей из двух смежных сторон.
    """
    vertices = _get_vertices(shape)
    if len(vertices) < 4:
        return

    painter.save()
    try:
        pen = QPen(QColor(Qt.GlobalColor.green), 1.0, Qt.PenStyle.DashDotLine)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        if vertex_indices is None:
            vertex_indices = [0, 1, 2, 3]

        for vi in vertex_indices:
            if vi < 0 or vi >= 4:
                continue
            v_prev = vertices[(vi - 1) % 4]
            v_curr = vertices[vi]
            v_next = vertices[(vi + 1) % 4]

            bisect_dir = _bisector_direction(v_prev, v_curr, v_next)
            if abs(bisect_dir.x()) < 1e-10 and abs(bisect_dir.y()) < 1e-10:
                continue

            # Длина = 60% от меньшей из двух смежных сторон
            side1 = math.sqrt((v_prev.x() - v_curr.x()) ** 2 + (v_prev.y() - v_curr.y()) ** 2)
            side2 = math.sqrt((v_next.x() - v_curr.x()) ** 2 + (v_next.y() - v_curr.y()) ** 2)
            length = min(side1, side2) * 0.6
            if length < 1.0:
                continue

            end_x = v_curr.x() + bisect_dir.x() * length
            end_y = v_curr.y() + bisect_dir.y() * length
            painter.drawLine(v_curr, QPointF(end_x, end_y))
    finally:
        painter.restore()


def draw_angles(painter: QPainter, shape) -> None:
    """Рисует дуги в вершинах с градусной мерой.

    Радиус дуги: 15 пикселей.
    Текст угла: позиция по биссектрисе на расстоянии 28 пикселей от вершины.
    """
    vertices = _get_vertices(shape)
    if len(vertices) < 4:
        return

    painter.save()
    try:
        arc_pen = QPen(QColor(Qt.GlobalColor.red), 1.0)
        text_font = QFont("Arial", 9)
        painter.setFont(text_font)

        for i in range(4):
            v_prev = vertices[(i - 1) % 4]
            v_curr = vertices[i]
            v_next = vertices[(i + 1) % 4]

            angle_deg = _angle_at_vertex(v_prev, v_curr, v_next)

            # Рисуем дугу
            radius = 15.0
            arc_rect = QRectF(
                v_curr.x() - radius,
                v_curr.y() - radius,
                radius * 2,
                radius * 2,
            )

            # Вычисляем углы для дуги в градусах (Qt: 1/8 градуса, по часовой стрелке)
            angle1 = math.degrees(math.atan2(v_prev.y() - v_curr.y(), v_prev.x() - v_curr.x()))
            angle2 = math.degrees(math.atan2(v_next.y() - v_curr.y(), v_next.x() - v_curr.x()))

            painter.setPen(arc_pen)
            # Рисуем дугу от angle1 до angle2
            # Qt использует 1/8 градуса и отрицательный угол для против часовой
            painter.drawArc(arc_rect, int(-angle1 * 8), int((angle2 - angle1) * 8))

            # Текст угла
            bisect_dir = _bisector_direction(v_prev, v_curr, v_next)
            text_dist = 28.0
            text_x = v_curr.x() + bisect_dir.x() * text_dist
            text_y = v_curr.y() + bisect_dir.y() * text_dist

            painter.setPen(QColor(Qt.GlobalColor.red))
            text_rect = QRectF(text_x - 15, text_y - 5, 30, 15)
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, f"{angle_deg:.1f}°")
    finally:
        painter.restore()


def draw_circumcircle(painter: QPainter, shape) -> None:
    """Рисует описанную окружность для вписываемых четырёхугольников.

    Центр и радиус — пересечение серединных перпендикуляров двух сторон.
    Стиль: пунктир, darkMagenta.
    """
    vertices = _get_vertices(shape)
    if len(vertices) < 4:
        return

    center, radius = _circumcircle_from_three_points(vertices[0], vertices[1], vertices[2])
    if center is None or radius is None:
        return
    if radius < 1.0:
        return

    painter.save()
    try:
        pen = QPen(QColor(Qt.GlobalColor.darkMagenta), 1.0, Qt.PenStyle.DashLine)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(center, radius, radius)
    finally:
        painter.restore()


def is_cyclic_quadrilateral(shape) -> bool:
    """Проверяет, является ли четырёхугольник вписываемым.

    Вписываемый: сумма противоположных углов ≈ 180°.
    """
    vertices = _get_vertices(shape)
    if len(vertices) < 4:
        return False

    angles = []
    for i in range(4):
        v_prev = vertices[(i - 1) % 4]
        v_curr = vertices[i]
        v_next = vertices[(i + 1) % 4]
        angles.append(_angle_at_vertex(v_prev, v_curr, v_next))

    # Проверяем: угол0 + угол2 ≈ 180 или угол1 + угол3 ≈ 180
    return abs(angles[0] + angles[2] - 180.0) < 5.0 or abs(angles[1] + angles[3] - 180.0) < 5.0
