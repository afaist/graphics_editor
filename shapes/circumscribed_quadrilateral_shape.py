"""Фигура: Описанный (вписанный в окружность) четырёхугольник."""

from __future__ import annotations

import math
import random
from typing import Any

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPen

from .base_shape import BaseShape, HandleType, ShapeType


class CircumscribedQuadrilateralShape(BaseShape):
    """Четырёхугольник, вписанный в окружность.

    Вершины лежат на окружности и могут перемещаться по ней.
    Отображаются подписи вершин A, B, C, D и градусные меры углов.
    """

    def __init__(
        self,
        cx: float,
        cy: float,
        radius: float,
        angles: list[float] | None = None,
        pen_color: tuple[int, int, int] = (0, 0, 0),
        pen_width: float = 2.0,
        brush_color: tuple[int, int, int] | None = None,
        selected: bool = False,
    ):
        super().__init__(pen_color, pen_width, brush_color, selected)
        self._cx = cx
        self._cy = cy
        self._radius = max(radius, 10.0)
        # Углы вершин на окружности (в радианах, от -pi до pi)
        if angles is not None and len(angles) == 4:
            self._angles = list(angles)
        else:
            # Случайное разбиение на 4 части
            self._angles = self._random_angles()
        self._labels = ["A", "B", "C", "D"]

    @staticmethod
    def _random_angles() -> list[float]:
        """Генерирует 4 случайных угла на окружности."""
        pts = [random.uniform(0, 2 * math.pi) for _ in range(4)]
        pts.sort()
        return pts

    def _get_shape_type(self) -> ShapeType:
        return ShapeType.CIRCUMSCRIBED_QUADRILATERAL

    # ------------------------------------------------------------------
    # Свойства
    # ------------------------------------------------------------------

    @property
    def cx(self) -> float:
        return self._cx

    @property
    def cy(self) -> float:
        return self._cy

    @property
    def radius(self) -> float:
        return self._radius

    @radius.setter
    def radius(self, value: float) -> None:
        if value > 0.1:
            self._radius = value
            self._render_dirty = True

    @property
    def angles(self) -> list[float]:
        return list(self._angles)

    @property
    def vertices(self) -> list[QPointF]:
        """Возвращает координаты вершин."""
        return [self._vertex_at_angle(a) for a in self._angles]

    @property
    def interior_angles(self) -> list[float]:
        """Возвращает градусные меры внутренних углов."""
        return self._compute_interior_angles()

    # ------------------------------------------------------------------
    # Геометрия
    # ------------------------------------------------------------------

    def _vertex_at_angle(self, angle: float) -> QPointF:
        """Вычисляет координаты точки на окружности по углу."""
        return QPointF(
            self._cx + self._radius * math.cos(angle),
            self._cy + self._radius * math.sin(angle),
        )

    def _compute_interior_angles(self) -> list[float]:
        """Вычисляет внутренние углы четырёхугольника в градусах."""
        verts = self.vertices
        if len(verts) < 4:
            return [0.0, 0.0, 0.0, 0.0]
        angles = []
        for i in range(4):
            prev_v = verts[(i - 1) % 4]
            curr_v = verts[i]
            next_v = verts[(i + 1) % 4]
            v1 = QPointF(prev_v.x() - curr_v.x(), prev_v.y() - curr_v.y())
            v2 = QPointF(next_v.x() - curr_v.x(), next_v.y() - curr_v.y())
            dot = v1.x() * v2.x() + v1.y() * v2.y()
            mag1 = math.hypot(v1.x(), v1.y())
            mag2 = math.hypot(v2.x(), v2.y())
            if mag1 < 1e-10 or mag2 < 1e-10:
                angles.append(0.0)
            else:
                cos_val = max(-1.0, min(1.0, dot / (mag1 * mag2)))
                angle_rad = math.acos(cos_val)
                angles.append(math.degrees(angle_rad))
        return angles

    # ------------------------------------------------------------------
    # Отрисовка
    # ------------------------------------------------------------------

    def _draw_shape_content(self, painter: QPainter) -> None:
        painter.save()
        try:
            # Окружность — пунктирная (стиль CIRCUMCIRCLE_PEN)
            from tools.drawing_styles import CIRCUMCIRCLE_PEN

            painter.setPen(CIRCUMCIRCLE_PEN)
            painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))
            painter.drawEllipse(
                QPointF(self._cx, self._cy),
                self._radius,
                self._radius,
            )

            # Центр O — точка
            from tools.drawing_styles import CIRCUMCIRCLE_COLOR, CIRCUMCIRCLE_PEN

            painter.setPen(CIRCUMCIRCLE_PEN)
            painter.setBrush(QBrush(CIRCUMCIRCLE_COLOR))
            painter.drawEllipse(QPointF(self._cx, self._cy), 3, 3)

            # Центр O — подпись (увеличенный шрифт)
            font = QFont()
            font.setFamily("Arial")
            font.setPointSizeF(14)
            font.setBold(True)
            painter.setFont(font)
            painter.setPen(CIRCUMCIRCLE_COLOR)
            painter.drawText(int(self._cx) + 6, int(self._cy) + 6, "O")

            # Вершины и стороны
            verts = self.vertices
            if len(verts) >= 4:
                # Стороны
                side_pen = QPen(self.pen_color, self.pen_width)
                painter.setPen(side_pen)
                painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))
                for i in range(4):
                    p1 = verts[i]
                    p2 = verts[(i + 1) % 4]
                    painter.drawLine(p1, p2)

                # Точки вершин
                vertex_pen = QPen(QColor(80, 80, 80), 1)
                painter.setPen(vertex_pen)
                painter.setBrush(QBrush(QColor(255, 255, 255)))
                for v in verts:
                    painter.drawEllipse(v, 3, 3)

                # Подписи вершин A, B, C, D
                font.setPointSizeF(9)
                painter.setFont(font)
                painter.setPen(QColor(50, 50, 50))
                offset = 16
                for i, v in enumerate(verts):
                    dx = v.x() - self._cx
                    dy = v.y() - self._cy
                    dist = math.hypot(dx, dy)
                    if dist < 0.01:
                        continue
                    dx /= dist
                    dy /= dist
                    lx = v.x() + dx * offset
                    ly = v.y() + dy * offset
                    text_rect = QRectF(lx - 10, ly - 10, 20, 20)
                    painter.drawText(
                        text_rect,
                        Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter,
                        self._labels[i],
                    )

                # Градусные меры углов — около каждой вершины
                int_angles = self.interior_angles
                font.setPointSizeF(8)
                painter.setFont(font)
                painter.setPen(QColor(120, 120, 120))
                for i in range(4):
                    curr_v = verts[i]
                    prev_v = verts[(i - 1) % 4]
                    next_v = verts[(i + 1) % 4]

                    # Векторы от текущей вершины к соседним
                    v1 = QPointF(prev_v.x() - curr_v.x(), prev_v.y() - curr_v.y())
                    v2 = QPointF(next_v.x() - curr_v.x(), next_v.y() - curr_v.y())

                    # Биссектриса внутреннего угла — сумма единичных векторов
                    mag1 = math.hypot(v1.x(), v1.y())
                    mag2 = math.hypot(v2.x(), v2.y())
                    if mag1 < 1e-10 or mag2 < 1e-10:
                        continue

                    u1 = QPointF(v1.x() / mag1, v1.y() / mag1)
                    u2 = QPointF(v2.x() / mag2, v2.y() / mag2)
                    bisector = QPointF(u1.x() + u2.x(), u1.y() + u2.y())
                    bisector_mag = math.hypot(bisector.x(), bisector.y())
                    if bisector_mag < 1e-10:
                        continue
                    bisector /= bisector_mag

                    # Смещаем от вершины по биссектрисе
                    offset = 24
                    lx = curr_v.x() + bisector.x() * offset
                    ly = curr_v.y() + bisector.y() * offset

                    angle_text = f"{int_angles[i]:.0f}°"
                    text_rect = QRectF(lx - 15, ly - 8, 30, 16)
                    painter.drawText(
                        text_rect,
                        Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter,
                        angle_text,
                    )
        finally:
            painter.restore()

    # ------------------------------------------------------------------
    # Базовые методы
    # ------------------------------------------------------------------

    def contains_point(self, point: QPointF) -> bool:
        return self.bounding_rect().contains(point)

    def move(self, dx: float, dy: float) -> None:
        self._cx += dx
        self._cy += dy

    def scale(self, factor: float, center: QPointF | None = None) -> None:
        self._radius *= factor
        if self._radius < 0.1:
            self._radius = 0.1

    def bounding_rect(self) -> QRectF:
        pad = self._compute_bounding_padding(self.pen_width) + 20
        r = self._radius
        return self._safe_rect(
            self._cx - r - pad,
            self._cy - r - pad,
            2 * r + pad * 2,
            2 * r + pad * 2,
        )

    # ------------------------------------------------------------------
    # Маркеры (handles)
    # ------------------------------------------------------------------

    def _handle_positions(self) -> list[tuple[float, float]]:
        return [(v.x(), v.y()) for v in self.vertices]

    def get_handles(self) -> list[QPointF]:
        return list(self.vertices)

    def get_handle_type(self, point: QPointF, tolerance: float = 5.0) -> HandleType:
        """Определяет тип маркера по пространственному положению вершины."""
        # Сортируем вершины по углу для определения пространственного порядка
        # TOP_LEFT = самая левая-верхняя, BOTTOM_RIGHT = самая правая-нижняя и т.д.
        if len(self._angles) != 4:
            return HandleType.NONE

        # Находим индексы вершин по их пространственному положению
        # Сортируем: сначала по y (сверху вниз), потом по x (слева направо)
        indexed = [(i, self.vertices[i]) for i in range(4)]

        # Находим верхние и нижние
        top_two = sorted(indexed, key=lambda item: item[1].y())[:2]
        bottom_two = sorted(indexed, key=lambda item: item[1].y())[2:]

        # Верхняя левая и правая
        top_left_idx = sorted(top_two, key=lambda item: item[1].x())[0][0]
        top_right_idx = sorted(top_two, key=lambda item: item[1].x())[1][0]

        # Нижняя левая и правая
        bottom_left_idx = sorted(bottom_two, key=lambda item: item[1].x())[0][0]
        bottom_right_idx = sorted(bottom_two, key=lambda item: item[1].x())[1][0]

        # Ищем ближайшую вершину
        for i, v in enumerate(self.vertices):
            dx = point.x() - v.x()
            dy = point.y() - v.y()
            if math.hypot(dx, dy) <= tolerance:
                if i == top_left_idx:
                    return HandleType.TOP_LEFT
                elif i == top_right_idx:
                    return HandleType.TOP_RIGHT
                elif i == bottom_right_idx:
                    return HandleType.BOTTOM_RIGHT
                elif i == bottom_left_idx:
                    return HandleType.BOTTOM_LEFT
        return HandleType.NONE

    def apply_handle_transform(
        self,
        handle: HandleType,
        point: QPointF,
        mouse_pos: QPointF,
        shift_pressed: bool = False,
        vertex_index: int = -1,
    ) -> None:
        """Перемещает вершину по окружности.

        Args:
            handle: тип маркера (используется для других фигур)
            point: начальная позиция мыши
            mouse_pos: текущая позиция мыши
            shift_pressed: нажата ли клавиша Shift
            vertex_index: индекс вершины (для circumscribed_quadrilateral)
        """
        # Если передан индекс вершины, используем его напрямую
        if vertex_index >= 0 and 0 <= vertex_index < len(self._angles):
            dx = mouse_pos.x() - self._cx
            dy = mouse_pos.y() - self._cy
            new_angle = math.atan2(dy, dx)
            self._angles[vertex_index] = new_angle
            self._render_dirty = True
            return

        # Для остальных фигур используем маркер
        handle_map = [
            HandleType.TOP_LEFT,
            HandleType.TOP_RIGHT,
            HandleType.BOTTOM_RIGHT,
            HandleType.BOTTOM_LEFT,
        ]
        handle_idx = handle_map.index(handle) if handle in handle_map else -1
        if handle_idx < 0:
            return

        # Определяем пространственный индекс для этого handle типа
        indexed = [(i, self.vertices[i]) for i in range(4)]
        top_two = sorted(indexed, key=lambda item: item[1].y())[:2]
        bottom_two = sorted(indexed, key=lambda item: item[1].y())[2:]
        top_left_idx = sorted(top_two, key=lambda item: item[1].x())[0][0]
        top_right_idx = sorted(top_two, key=lambda item: item[1].x())[1][0]
        bottom_left_idx = sorted(bottom_two, key=lambda item: item[1].x())[0][0]
        bottom_right_idx = sorted(bottom_two, key=lambda item: item[1].x())[1][0]

        spatial_to_angle = {
            0: top_left_idx,
            1: top_right_idx,
            2: bottom_right_idx,
            3: bottom_left_idx,
        }

        angle_idx = spatial_to_angle.get(handle_idx)
        if angle_idx is None:
            return

        # Перемещаем вершину по окружности
        dx = mouse_pos.x() - self._cx
        dy = mouse_pos.y() - self._cy
        new_angle = math.atan2(dy, dx)
        self._angles[angle_idx] = new_angle
        self._render_dirty = True

    def _sort_angles(self) -> None:
        """Сортирует углы для правильного порядка вершин A, B, C, D.

        Вершина A — самая левая (минимальный x).
        Остальные — по часовой стрелке (убывание угла в полярных координатах).
        """
        if len(self._angles) != 4:
            return
        # Сортируем углы по возрастанию
        sorted_angles = sorted(self._angles)
        # Находим самую левую вершину (минимальный x = cos(angle) минимальный)
        min_idx = 0
        min_x = math.cos(sorted_angles[0])
        for i in range(1, 4):
            x = math.cos(sorted_angles[i])
            if x < min_x:
                min_x = x
                min_idx = i
        # Начинаем с min_idx, идём по часовой стрелке
        # По часовой стрелке = убывание угла (убывание в полярных координатах)
        # Берём углы от min_idx вниз, затем переходим к большим
        result = [sorted_angles[min_idx]]
        # Углы меньше min_idx (идём по часовой стрелке)
        before = sorted_angles[:min_idx]
        # Углы больше min_idx (идём против часовой, но нам нужно по часовой)
        after = sorted_angles[min_idx + 1 :]
        # По часовой стрелке от min_idx: сначала before (в обратном порядке), then after
        result.extend(reversed(before))
        result.extend(after)
        self._angles = result

    # ------------------------------------------------------------------
    # Свойства для панели
    # ------------------------------------------------------------------

    def get_properties(self) -> dict[str, Any]:
        props = super().get_properties()
        props["_radius"] = self._radius
        return props

    def apply_properties(self, properties: dict[str, Any]) -> None:
        super().apply_properties(properties)
        if properties is None:
            return
        if "_radius" in properties:
            r = properties["_radius"]
            if r > 0.1:
                self._radius = r
                self._render_dirty = True

    # ------------------------------------------------------------------
    # Позиция для undo
    # ------------------------------------------------------------------

    def get_position_data(self) -> dict:
        return {
            "cx": self._cx,
            "cy": self._cy,
            "radius": self._radius,
            "angles": list(self._angles),
        }

    def restore_position_data(self, data: dict) -> None:
        self._cx = data["cx"]
        self._cy = data["cy"]
        self._radius = data["radius"]
        if "angles" in data:
            self._angles = list(data["angles"])

    # ------------------------------------------------------------------
    # Сериализация
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update(
            {
                "cx": self._cx,
                "cy": self._cy,
                "radius": self._radius,
                "angles": self._angles,
            }
        )
        return d

    @classmethod
    def from_dict(cls, data: dict) -> CircumscribedQuadrilateralShape:
        obj = cls(
            cx=data["cx"],
            cy=data["cy"],
            radius=data["radius"],
            angles=data.get("angles"),
            pen_color=data["pen_color"],
            brush_color=data.get("brush_color"),
            pen_width=data.get("pen_width", 2.0),
        )
        obj._selected = data.get("selected", False)
        obj._rotation = data.get("rotation", 0.0)
        return obj
