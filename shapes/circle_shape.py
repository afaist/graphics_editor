"""Фигура: Окружность."""

from __future__ import annotations

import math
from typing import Any

from PySide6.QtCore import QPointF, QRectF
from PySide6.QtGui import QPainter

from .base_shape import BaseShape, HandleType, ShapeType


class CircleShape(BaseShape):
    """Окружность, заданная центром и радиусом."""

    def __init__(
        self,
        cx: float,
        cy: float,
        radius: float,
        pen_color: tuple[int, int, int] = (0, 0, 0),
        pen_width: float = 2.0,
        brush_color: tuple[int, int, int] | None = None,
        selected: bool = False,
        show_radius: bool = True,
        radius_type: int = 0,  # 0=radius, 1=diameter
        tangent_type: int = 0,  # 0=none, 1=single, 2=double
        show_chord: bool = False,
        tangent_angle: float = 0.0,  # angle for single tangent (radians)
        tangent_point: tuple[float, float] | None = None,  # external point for double tangent
    ):
        super().__init__(pen_color, pen_width, brush_color, selected)
        self._cx = cx
        self._cy = cy
        self._radius = radius
        self._show_radius = show_radius
        self._radius_type = radius_type
        self._tangent_type = tangent_type
        self._show_chord = show_chord
        self._tangent_angle = tangent_angle
        self._tangent_point = tangent_point

    def set_size(self, width: float, height: float) -> None:
        """Задать радиус окружности по ширине и высоте bounding rect.

        Радиус вычисляется как половина максимального размера.
        """
        self._radius = max(width, height) / 2

    def _get_shape_type(self) -> ShapeType:
        """Возвращает тип фигуры — CIRCLE."""
        return ShapeType.CIRCLE

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

    # ------------------------------------------------------------------
    # Свойства дополнительных элементов
    # ------------------------------------------------------------------

    @property
    def show_radius(self) -> bool:
        return self._show_radius

    @show_radius.setter
    def show_radius(self, value: bool) -> None:
        self._show_radius = value

    @property
    def radius_type(self) -> int:
        return self._radius_type

    @radius_type.setter
    def radius_type(self, value: int) -> None:
        self._radius_type = value

    @property
    def tangent_type(self) -> int:
        return self._tangent_type

    @tangent_type.setter
    def tangent_type(self, value: int) -> None:
        self._tangent_type = value

    @property
    def show_chord(self) -> bool:
        return self._show_chord

    @show_chord.setter
    def show_chord(self, value: bool) -> None:
        self._show_chord = value

    @property
    def tangent_angle(self) -> float:
        return self._tangent_angle

    @tangent_angle.setter
    def tangent_angle(self, value: float) -> None:
        self._tangent_angle = value

    @property
    def tangent_point(self) -> tuple[float, float] | None:
        return self._tangent_point

    @tangent_point.setter
    def tangent_point(self, value: tuple[float, float] | None) -> None:
        self._tangent_point = value

    # ------------------------------------------------------------------
    # Свойства для панели
    # ------------------------------------------------------------------

    def get_properties(self) -> dict[str, Any]:
        """Вернуть свойства фигуры в виде словаря для панели свойств."""
        props = super().get_properties()
        # Храним радиус напрямую — width/height вычисляются из него
        props["_radius"] = self._radius
        props["_show_radius"] = self._show_radius
        props["_radius_type"] = self._radius_type
        props["_tangent_type"] = self._tangent_type
        props["_show_chord"] = self._show_chord
        props["_tangent_angle"] = self._tangent_angle
        props["_tangent_point"] = self._tangent_point
        return props

    def apply_properties(self, properties: dict[str, Any]) -> None:
        """Применить свойства из панели свойств."""
        super().apply_properties(properties)
        if properties is None:
            return
        if "_radius" in properties:
            r = properties["_radius"]
            if r > 0.1:
                self.radius = r
                self._render_dirty = True
        if "_show_radius" in properties:
            self._show_radius = properties["_show_radius"]
            self._render_dirty = True
        if "_radius_type" in properties:
            self._radius_type = properties["_radius_type"]
            self._render_dirty = True
        if "_tangent_type" in properties:
            self._tangent_type = properties["_tangent_type"]
            self._render_dirty = True
        if "_show_chord" in properties:
            self._show_chord = properties["_show_chord"]
            self._render_dirty = True
        if "_tangent_angle" in properties:
            self._tangent_angle = properties["_tangent_angle"]
            self._render_dirty = True
        if "_tangent_point" in properties:
            self._tangent_point = properties["_tangent_point"]
            self._render_dirty = True

    # ------------------------------------------------------------------
    # Абстрактные методы
    # ------------------------------------------------------------------

    def _rotation_center(self) -> tuple[float, float]:
        """Возвращает центр поворота — центр окружности."""
        return (self._cx, self._cy)

    def _draw_shape_content(self, painter: QPainter) -> None:
        """Рисует окружность и дополнительные элементы."""
        from PySide6.QtGui import QBrush, QColor, QFont, QPen

        if self._radius > 0.05:
            # Основная окружность
            painter.drawEllipse(
                QPointF(self._cx, self._cy),
                self._radius,
                self._radius,
            )

            # Центр окружности
            center_pen = QPen(QColor(100, 100, 100), 1)
            painter.setPen(center_pen)
            painter.setBrush(QBrush(QColor(100, 100, 100)))
            painter.drawEllipse(QPointF(self._cx, self._cy), 2, 2)

            font = QFont()
            font.setFamily("Arial")
            font.setPointSizeF(9)
            painter.setFont(font)

            # Радиус/диаметр
            if self._show_radius:
                radius_text = (
                    f"R={self._radius:.0f}"
                    if self._radius_type == 0
                    else f"D={2 * self._radius:.0f}"
                )
                # Рисуем линию радиуса и текст
                radius_pen = QPen(QColor(0, 100, 200), 1)
                painter.setPen(radius_pen)
                end_x = self._cx + self._radius * 0.7
                end_y = self._cy - self._radius * 0.7
                painter.drawLine(int(self._cx), int(self._cy), int(end_x), int(end_y))
                painter.setPen(QColor(0, 100, 200))
                painter.drawText(int(end_x) + 5, int(end_y) - 5, radius_text)

            # Касательная
            if self._tangent_type == 1:
                # Одна касательная — перпендикулярна радиусу в точке на окружности
                tx = self._cx + self._radius * math.cos(self._tangent_angle)
                ty = self._cy + self._radius * math.sin(self._tangent_angle)
                # Направляющий вектор касательной (перпендикулярно радиусу)
                tx_dir = -math.sin(self._tangent_angle)
                ty_dir = math.cos(self._tangent_angle)
                tangent_len = self._radius * 2
                p1x = tx - tx_dir * tangent_len
                p1y = ty - ty_dir * tangent_len
                p2x = tx + tx_dir * tangent_len
                p2y = ty + ty_dir * tangent_len
                tangent_pen = QPen(QColor(200, 0, 0), 1)
                painter.setPen(tangent_pen)
                painter.drawLine(int(p1x), int(p1y), int(p2x), int(p2y))
                # Точка касания
                painter.setBrush(QBrush(QColor(200, 0, 0)))
                painter.drawEllipse(QPointF(tx, ty), 3, 3)

            elif self._tangent_type == 2:
                # Две касательные из внешней точки
                if self._tangent_point:
                    ex, ey = self._tangent_point
                    # Вектор от центра до внешней точки
                    dx = ex - self._cx
                    dy = ey - self._cy
                    dist = math.hypot(dx, dy)
                    if dist > self._radius:
                        # Угол между центром-внешняя_точка и радиусом до точки касания
                        angle_to_point = math.atan2(dy, dx)
                        cos_alpha = self._radius / dist
                        # Две точки касания
                        for sign in [1, -1]:
                            tangent_angle = angle_to_point + sign * math.acos(cos_alpha)
                            tx = self._cx + self._radius * math.cos(tangent_angle)
                            ty = self._cy + self._radius * math.sin(tangent_angle)
                            # Линия от внешней точки до точки касания
                            tangent_pen = QPen(QColor(200, 0, 0), 1)
                            painter.setPen(tangent_pen)
                            painter.drawLine(int(ex), int(ey), int(tx), int(ty))
                            # Точка касания
                            painter.setBrush(QBrush(QColor(200, 0, 0)))
                            painter.drawEllipse(QPointF(tx, ty), 3, 3)
                        # Внешняя точка
                        painter.setBrush(QBrush(QColor(255, 100, 0)))
                        painter.drawEllipse(QPointF(ex, ey), 4, 4)

            # Хорда
            if self._show_chord:
                # Хорда — соединяет две точки на окружности (симметрично по горизонтали)
                chord_angle = math.pi / 4
                p1x = self._cx + self._radius * math.cos(chord_angle)
                p1y = self._cy + self._radius * math.sin(chord_angle)
                p2x = self._cx + self._radius * math.cos(-chord_angle)
                p2y = self._cy + self._radius * math.sin(-chord_angle)
                chord_pen = QPen(QColor(0, 150, 0), 1)
                painter.setPen(chord_pen)
                painter.drawLine(int(p1x), int(p1y), int(p2x), int(p2y))
                # Точки на окружности
                painter.setBrush(QBrush(QColor(0, 150, 0)))
                painter.drawEllipse(QPointF(p1x, p1y), 3, 3)
                painter.drawEllipse(QPointF(p2x, p2y), 3, 3)
        else:
            painter.drawPoint(QPointF(self._cx, self._cy))

    def contains_point(self, point: QPointF) -> bool:
        dx = point.x() - self._cx
        dy = point.y() - self._cy
        return dx * dx + dy * dy <= self._radius * self._radius

    def move(self, dx: float, dy: float) -> None:
        self._cx += dx
        self._cy += dy

    def scale(self, factor: float, center: QPointF | None = None) -> None:
        self._radius *= factor
        if self._radius < 0.1:
            self._radius = 0.1

    def bounding_rect(self) -> QRectF:
        pad = self._compute_bounding_padding(self.pen_width)
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
        """4 маркера: центр + 3 точки на окружности (0°, 90°, 180°)."""
        r = self._radius
        return [
            (self._cx, self._cy),  # центр
            (self._cx + r, self._cy),  # право
            (self._cx, self._cy - r),  # верх
            (self._cx - r, self._cy),  # лево
        ]

    def apply_handle_transform(
        self,
        handle: HandleType,
        point: QPointF,
        mouse_pos: QPointF,
        shift_pressed: bool = False,
        vertex_index: int = -1,
    ) -> None:
        if handle == HandleType.TOP_LEFT:
            # Центр — перемещение
            dx = mouse_pos.x() - point.x()
            dy = mouse_pos.y() - point.y()
            self._cx += dx
            self._cy += dy
        elif handle == HandleType.BOTTOM_RIGHT:
            # Правая точка — изменение радиуса
            dx = mouse_pos.x() - self._cx
            dy = mouse_pos.y() - self._cy
            self._radius = (dx * dx + dy * dy) ** 0.5
            if self._radius < 0.1:
                self._radius = 0.1
        elif handle == HandleType.TOP_CENTER:
            # Верхняя точка — изменение радиуса
            dy = self._cy - mouse_pos.y()
            self._radius = abs(dy)
            if self._radius < 0.1:
                self._radius = 0.1
        elif handle == HandleType.LEFT_CENTER:
            # Левая точка — изменение радиуса
            dx = self._cx - mouse_pos.x()
            self._radius = abs(dx)
            if self._radius < 0.1:
                self._radius = 0.1

    # ------------------------------------------------------------------
    # Позиция для undo
    # ------------------------------------------------------------------

    def get_position_data(self) -> dict:
        return {
            "cx": self._cx,
            "cy": self._cy,
            "radius": self._radius,
        }

    def restore_position_data(self, data: dict) -> None:
        self._cx = data["cx"]
        self._cy = data["cy"]
        self._radius = data["radius"]

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
                "show_radius": self._show_radius,
                "radius_type": self._radius_type,
                "tangent_type": self._tangent_type,
                "show_chord": self._show_chord,
                "tangent_angle": self._tangent_angle,
                "tangent_point": self._tangent_point,
            }
        )
        return d

    @classmethod
    def from_dict(cls, data: dict) -> CircleShape:
        obj = cls(
            cx=data["cx"],
            cy=data["cy"],
            radius=data["radius"],
            pen_color=data["pen_color"],
            brush_color=data.get("brush_color"),
            pen_width=data.get("pen_width", 2.0),
            show_radius=data.get("show_radius", True),
            radius_type=data.get("radius_type", 0),
            tangent_type=data.get("tangent_type", 0),
            show_chord=data.get("show_chord", False),
            tangent_angle=data.get("tangent_angle", 0.0),
            tangent_point=data.get("tangent_point"),
        )
        obj._selected = data.get("selected", False)
        obj._rotation = data.get("rotation", 0.0)
        return obj
