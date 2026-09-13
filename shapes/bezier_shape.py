"""Фигура: Кривая Безье (cubic Bezier)."""

from __future__ import annotations

import math
from typing import List, Optional, Tuple, Dict, Any

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPen, QPainterPath

from .base_shape import BaseShape, HandleType, ShapeType


class BezierShape(BaseShape):
    """Кубическая кривая Безье, заданная 4 контрольными точками.
    
    P0 — начальная точка, P1 и P2 — контрольные точки, P3 — конечная точка.
    """

    def __init__(
        self,
        points: Optional[List[Tuple[float, float]]] = None,
        pen_color: Tuple[int, int, int] = (0, 0, 0),
        pen_width: float = 2.0,
        selected: bool = False,
    ):
        super().__init__(pen_color, pen_width, None, selected)
        if points and len(points) == 4:
            self._points: List[QPointF] = [
                QPointF(p[0], p[1]) if not isinstance(p, QPointF) else p for p in points
            ]
        else:
            self._points: List[QPointF] = [QPointF(0, 0)] * 4

    def _get_shape_type(self) -> ShapeType:
        return ShapeType.BEZIER

    def set_end_point(self, x: float, y: float) -> None:
        if len(self._points) >= 4:
            self._points[3].setX(x)
            self._points[3].setY(y)

    def set_size(self, width: float, height: float) -> None:
        pass

    def add_vertex(self, x: float, y: float) -> None:
        pass

    # ------------------------------------------------------------------
    # Свойства
    # ------------------------------------------------------------------

    @property
    def points(self) -> List[QPointF]:
        return list(self._points)

    @points.setter
    def points(self, pts: List[QPointF]) -> None:
        self._points = list(pts)

    @property
    def p0(self) -> QPointF:
        return self._points[0]

    @property
    def p1(self) -> QPointF:
        return self._points[1]

    @property
    def p2(self) -> QPointF:
        return self._points[2]

    @property
    def p3(self) -> QPointF:
        return self._points[3]

    # ------------------------------------------------------------------
    # Сервисные методы
    # ------------------------------------------------------------------

    @staticmethod
    def _bezier_point(p0: QPointF, p1: QPointF, p2: QPointF, p3: QPointF, t: float) -> QPointF:
        """Вычислить точку на кубической кривой Безье для параметра t."""
        u = 1.0 - t
        tt = u * u
        ttt = tt * u
        t2 = t * t
        t3 = t2 * t

        x = ttt * p0.x() + 3 * tt * t * p1.x() + 3 * u * t2 * p2.x() + t3 * p3.x()
        y = ttt * p0.y() + 3 * tt * t * p1.y() + 3 * u * t2 * p2.y() + t3 * p3.y()
        return QPointF(x, y)

    def _build_path(self, steps: int = 100) -> QPainterPath:
        """Построить QPainterPath кривой Безье."""
        if len(self._points) < 4:
            return QPainterPath()

        path = QPainterPath()
        path.moveTo(self._points[0])

        for i in range(1, steps + 1):
            t = i / steps
            pt = self._bezier_point(
                self._points[0], self._points[1],
                self._points[2], self._points[3], t
            )
            path.lineTo(pt)

        return path

    # ------------------------------------------------------------------
    # Абстрактные методы
    # ------------------------------------------------------------------

    def draw(self, painter: QPainter) -> None:
        painter.save()
        try:
            pen = QPen(self.pen_color, self.pen_width)
            painter.setPen(pen)

            path = self._build_path()
            painter.drawPath(path)

            # Рисуем контрольные точки и линии, если выделена
            if self._selected:
                pen.setColor(QColor(0, 120, 255))
                pen.setWidth(1)
                painter.setPen(pen)

                # Линии контрольного полигона
                painter.drawLine(
                    QPointF(self._points[0]),
                    QPointF(self._points[1])
                )
                painter.drawLine(
                    QPointF(self._points[1]),
                    QPointF(self._points[2])
                )
                painter.drawLine(
                    QPointF(self._points[2]),
                    QPointF(self._points[3])
                )

                # Контрольные точки
                for pt in self._points:
                    painter.drawRect(int(pt.x()) - 4, int(pt.y()) - 4, 8, 8)
        finally:
            painter.restore()

    def contains_point(self, point: QPointF, tolerance: float = 5.0) -> bool:
        """Проверить, находится ли точка близко к кривой."""
        if len(self._points) < 4:
            return False

        # Проверяем расстояние до кривой
        steps = 50
        for i in range(steps + 1):
            t = i / steps
            pt = self._bezier_point(
                self._points[0], self._points[1],
                self._points[2], self._points[3], t
            )
            dx = point.x() - pt.x()
            dy = point.y() - pt.y()
            if dx * dx + dy * dy <= tolerance * tolerance:
                return True

        return False

    def move(self, dx: float, dy: float) -> None:
        for pt in self._points:
            pt.setX(pt.x() + dx)
            pt.setY(pt.y() + dy)

    def rotate(self, angle: float, center: Optional[QPointF] = None) -> None:
        if center is None:
            cx = sum(p.x() for p in self._points) / len(self._points)
            cy = sum(p.y() for p in self._points) / len(self._points)
            center = QPointF(cx, cy)

        rad = math.radians(angle)
        cos_a, sin_a = math.cos(rad), math.sin(rad)

        for pt in self._points:
            dx, dy = pt.x() - center.x(), pt.y() - center.y()
            pt.setX(center.x() + dx * cos_a - dy * sin_a)
            pt.setY(center.y() + dx * sin_a + dy * cos_a)

    def scale(self, factor: float, center: Optional[QPointF] = None) -> None:
        if center is None and self._points:
            cx = sum(p.x() for p in self._points) / len(self._points)
            cy = sum(p.y() for p in self._points) / len(self._points)
            center = QPointF(cx, cy)
        if center is None:
            return

        for pt in self._points:
            pt.setX(center.x() + (pt.x() - center.x()) * factor)
            pt.setY(center.y() + (pt.y() - center.y()) * factor)

    def bounding_rect(self) -> QRectF:
        if not self._points:
            return QRectF(0, 0, 0, 0)

        # Для кубической Безье bounding box — это bounding box контрольного полигона
        xs = [p.x() for p in self._points]
        ys = [p.y() for p in self._points]

        x_min, x_max = min(xs), max(xs)
        y_min, y_max = min(ys), max(ys)

        pad = max(self.pen_width / 2 + 5, 6)
        return self._safe_rect(
            x_min - pad,
            y_min - pad,
            x_max - x_min + pad * 2,
            y_max - y_min + pad * 2,
        )

    def get_handles(self) -> List[QPointF]:
        return list(self._points)

    def get_handle_type(self, point: QPointF, tolerance: float = 5.0) -> HandleType:
        for i, pt in enumerate(self._points):
            dx = point.x() - pt.x()
            dy = point.y() - pt.y()
            if dx * dx + dy * dy <= tolerance * tolerance:
                return HandleType(i + 2)
        return HandleType.NONE

    def apply_handle_transform(
        self, handle: HandleType, point: QPointF, mouse_pos: QPointF
    ) -> None:
        idx = handle.value - 2
        if 0 <= idx < len(self._points):
            self._points[idx].setX(mouse_pos.x())
            self._points[idx].setY(mouse_pos.y())

    # ------------------------------------------------------------------
    # Сериализация
    # ------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d["points"] = [{"x": p.x(), "y": p.y()} for p in self._points]
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BezierShape":
        pts_data = data.get("points", [])
        pts = [(p["x"], p["y"]) for p in pts_data] if pts_data else None

        obj = cls(
            points=pts,
            pen_color=data["pen_color"],
            pen_width=data.get("pen_width", 2.0),
            selected=data.get("selected", False),
        )
        obj._rotation = data.get("rotation", 0.0)
        return obj
