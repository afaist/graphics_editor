"""3D-фигуры: куб, параллелепипед, сфера, цилиндр, конус, пирамида, призма, усечённые тела."""

from __future__ import annotations

import math
from typing import Any

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QPainter, QPen

from .base_shape import BaseShape, HandleType, ShapeType


class ParallelepipedShape(BaseShape):
    """Прямоугольный параллелепипед — 3D-2D проекция."""

    def __init__(
        self,
        size: float,
        aspect: tuple[float, float, float],
        center: tuple[float, float],
        pen_color: tuple[int, int, int],
        pen_width: float,
        brush_color: tuple[int, int, int] | None,
        selected: bool,
    ):
        """
        size — базовый размер.
        aspect — пропорции (ширина, высота, глубина) относительно size.
        """
        self._size = size
        self._aspect = aspect
        self._center_x = center[0]
        self._center_y = center[1]
        self._vertices: list[QPointF] = []
        super().__init__(pen_color, pen_width, brush_color, selected)
        self._project()

    def _project(self) -> None:
        """Проецирует 3D-вершины на 2D-плоскость."""
        w, h, d = self._aspect
        scale = self._size / 2
        cos_a, sin_a = math.cos(math.radians(30)), math.sin(math.radians(30))
        cos_b, sin_b = math.cos(math.radians(-35)), math.sin(math.radians(-35))

        vertices_3d = [
            (-w, -h, -d),
            (w, -h, -d),
            (w, h, -d),
            (-w, h, -d),
            (-w, -h, d),
            (w, -h, d),
            (w, h, d),
            (-w, h, d),
        ]
        self._vertices = []
        for vx, vy, vz in vertices_3d:
            y1 = vy * cos_a - vz * sin_a
            z1 = vy * sin_a + vz * cos_a
            x2 = vx * cos_b + z1 * sin_b
            self._vertices.append(
                QPointF(self._center_x + x2 * scale * 0.6, self._center_y - y1 * scale * 0.7)
            )

    def _get_shape_type(self) -> ShapeType:
        return ShapeType.PARALLELEPIPED  # type: ignore[attr-defined]

    def _get_edges(self) -> list[tuple[int, int]]:
        return [
            (0, 1),
            (1, 2),
            (2, 3),
            (3, 0),
            (4, 5),
            (5, 6),
            (6, 7),
            (7, 4),
            (0, 4),
            (1, 5),
            (2, 6),
            (3, 7),
        ]

    def _draw_shape_content(self, painter: QPainter) -> None:
        painter.setBrush(Qt.BrushStyle.NoBrush)
        edges = self._get_edges()
        for i, j in edges:
            if i < len(self._vertices) and j < len(self._vertices):
                painter.drawLine(self._vertices[i], self._vertices[j])

    def move(self, dx: float, dy: float) -> None:
        self._center_x += dx
        self._center_y += dy
        self._project()

    def scale(self, factor: float, center: QPointF | None = None) -> None:
        self._size *= factor
        self._size = max(1.0, self._size)
        self._project()

    def bounding_rect(self) -> QRectF:
        if not self._vertices:
            return QRectF()
        xs = [v.x() for v in self._vertices]
        ys = [v.y() for v in self._vertices]
        pad = 10
        return QRectF(
            min(xs) - pad,
            min(ys) - pad,
            max(xs) - min(xs) + pad * 2,
            max(ys) - min(ys) + pad * 2,
        )

    def _handle_positions(self) -> list[tuple[float, float]]:
        return [(v.x(), v.y()) for v in self._vertices]

    def apply_handle_transform(
        self,
        handle: HandleType,
        point: QPointF,
        mouse_pos: QPointF,
        shift_pressed: bool = False,
        vertex_index: int = -1,
    ) -> None:
        if handle == HandleType.MOVE:
            dx = mouse_pos.x() - point.x()
            dy = mouse_pos.y() - point.y()
            self.move(dx, dy)
            return
        idx = handle.value - 2
        if 0 <= idx < len(self._vertices):
            self._vertices[idx].setX(mouse_pos.x())
            self._vertices[idx].setY(mouse_pos.y())

    def get_position_data(self) -> dict[str, Any]:
        return {
            "size": self._size,
            "aspect": self._aspect,
            "center": (self._center_x, self._center_y),
        }

    def restore_position_data(self, data: dict[str, Any]) -> None:
        self._size = data["size"]
        self._aspect = data["aspect"]
        self._center_x, self._center_y = data["center"]
        self._project()

    def to_dict(self) -> dict[str, Any]:
        d = super().to_dict()
        d["size"] = self._size
        d["aspect"] = self._aspect
        d["center_x"] = self._center_x
        d["center_y"] = self._center_y
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BaseShape:
        obj = cls(
            size=data["size"],
            aspect=tuple(data["aspect"]),
            center=(data["center_x"], data["center_y"]),
            pen_color=data["pen_color"],
            pen_width=data.get("pen_width", 2.0),
            brush_color=data.get("brush_color"),
            selected=data.get("selected", False),
        )
        obj.id = data["id"]
        obj._rotation = data.get("rotation", 0.0)
        return obj


class SphereShape(BaseShape):
    """Шар / сфера — изображается как круг с меридианами и штриховкой."""

    def __init__(
        self,
        radius: float,
        center: tuple[float, float],
        pen_color: tuple[int, int, int],
        pen_width: float,
        brush_color: tuple[int, int, int] | None,
        selected: bool,
    ):
        self._radius = radius
        self._cx = center[0]
        self._cy = center[1]
        super().__init__(pen_color, pen_width, brush_color, selected)

    def _get_shape_type(self) -> ShapeType:
        return ShapeType.SPHERE  # type: ignore[attr-defined]

    def _draw_shape_content(self, painter: QPainter) -> None:
        r = self._radius

        # Основа — круг
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPointF(self._cx, self._cy), r, r)

        # Меридианы (вертикальные эллипсы)
        meridian_color = QColor(
            self._pen_color.red(), self._pen_color.green(), self._pen_color.blue(), 160
        )
        meridian_pen = QPen(meridian_color, max(self.pen_width * 0.6, 1.0))
        painter.setPen(meridian_pen)
        painter.drawEllipse(
            QPointF(self._cx, self._cy),
            r * 0.35,
            r,
        )
        painter.drawEllipse(
            QPointF(self._cx, self._cy),
            r,
            r * 0.35,
        )

        # Параллели (горизонтальные эллипсы)
        painter.drawEllipse(
            QPointF(self._cx, self._cy),
            r,
            r * 0.35,
        )

        # Тень — полукруг справа-сверху (светотень)
        if self._brush_color:
            shadow = QColor(
                self._brush_color.red(), self._brush_color.green(), self._brush_color.blue(), 100
            )
            painter.setBrush(QBrush(shadow))
            painter.setPen(Qt.PenStyle.NoPen)
            # Верхний левый сектор затемнён
            rect = QRectF(self._cx - r, self._cy - r, r, r)
            painter.drawEllipse(rect)

    def move(self, dx: float, dy: float) -> None:
        self._cx += dx
        self._cy += dy

    def scale(self, factor: float, center: QPointF | None = None) -> None:
        self._radius *= factor
        self._radius = max(1.0, self._radius)

    def bounding_rect(self) -> QRectF:
        r = self._radius + 5
        return QRectF(self._cx - r, self._cy - r, r * 2, r * 2)

    def _handle_positions(self) -> list[tuple[float, float]]:
        r = self._radius
        return [
            (self._cx - r, self._cy),
            (self._cx + r, self._cy),
            (self._cx, self._cy - r),
            (self._cx, self._cy + r),
        ]

    def apply_handle_transform(
        self,
        handle: HandleType,
        point: QPointF,
        mouse_pos: QPointF,
        shift_pressed: bool = False,
        vertex_index: int = -1,
    ) -> None:
        if handle == HandleType.MOVE:
            dx = mouse_pos.x() - point.x()
            dy = mouse_pos.y() - point.y()
            self.move(dx, dy)
            return
        if handle == HandleType.BOTTOM_RIGHT:
            dx = mouse_pos.x() - point.x()
            dy = mouse_pos.y() - point.y()
            self._radius += max(dx, dy) * 0.5
            self._radius = max(1.0, self._radius)
        elif handle == HandleType.TOP_LEFT:
            dx = point.x() - mouse_pos.x()
            dy = point.y() - mouse_pos.y()
            self._radius += max(dx, dy) * 0.5
            self._radius = max(1.0, self._radius)

    def get_position_data(self) -> dict[str, Any]:
        return {"radius": self._radius, "center": (self._cx, self._cy)}

    def restore_position_data(self, data: dict[str, Any]) -> None:
        self._radius = data["radius"]
        self._cx, self._cy = data["center"]

    def to_dict(self) -> dict[str, Any]:
        d = super().to_dict()
        d["radius"] = self._radius
        d["center_x"] = self._cx
        d["center_y"] = self._cy
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BaseShape:
        obj = cls(
            radius=data["radius"],
            center=(data["center_x"], data["center_y"]),
            pen_color=data["pen_color"],
            pen_width=data.get("pen_width", 2.0),
            brush_color=data.get("brush_color"),
            selected=data.get("selected", False),
        )
        obj.id = data["id"]
        obj._rotation = data.get("rotation", 0.0)
        return obj


class CylinderShape(BaseShape):
    """Цилиндр — два эллипса (основания) + параллельные линии."""

    def __init__(
        self,
        radius: float,
        height: float,
        center: tuple[float, float],
        pen_color: tuple[int, int, int],
        pen_width: float,
        brush_color: tuple[int, int, int] | None,
        selected: bool,
    ):
        self._radius = radius
        self._height = height
        self._cx = center[0]
        self._cy = center[1]
        super().__init__(pen_color, pen_width, brush_color, selected)

    def _get_shape_type(self) -> ShapeType:
        return ShapeType.CYLINDER  # type: ignore[attr-defined]

    def _draw_shape_content(self, painter: QPainter) -> None:
        r = self._radius
        h = self._height
        top_y = self._cy - h / 2
        bottom_y = self._cy + h / 2
        ellipse_h = r * 0.35

        # Видимая часть боковой поверхности (от нижней грани к верхней)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(self.pen_color, self.pen_width))

        # Задняя часть эллипса (пунктиром)
        back_color = QColor(
            self._pen_color.red(), self._pen_color.green(), self._pen_color.blue(), 120
        )
        back_pen = QPen(back_color, self.pen_width)
        painter.setPen(back_pen)
        painter.drawEllipse(
            QPointF(self._cx, top_y),
            r,
            ellipse_h,
        )

        # Передняя часть эллипса (нижнего основания)
        painter.setPen(QPen(self.pen_color, self.pen_width))
        painter.drawEllipse(
            QPointF(self._cx, bottom_y),
            r,
            ellipse_h,
        )

        # Боковые линии
        painter.drawLine(QPointF(self._cx - r, top_y), QPointF(self._cx - r, bottom_y))
        painter.drawLine(QPointF(self._cx + r, top_y), QPointF(self._cx + r, bottom_y))

        # Верхний эллипс (передняя часть)
        painter.drawArc(
            QRectF(self._cx - r, top_y - ellipse_h, r * 2, ellipse_h * 2),
            180 * 16,
            -180 * 16,
        )

        # Заливка боковой поверхности, если есть brush
        if self._brush_color:
            color = QColor(
                self._brush_color.red(), self._brush_color.green(), self._brush_color.blue(), 60
            )
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(QRectF(self._cx - r, top_y, r * 2, h))

    def move(self, dx: float, dy: float) -> None:
        self._cx += dx
        self._cy += dy

    def scale(self, factor: float, center: QPointF | None = None) -> None:
        self._radius *= factor
        self._height *= factor
        self._radius = max(1.0, self._radius)
        self._height = max(1.0, self._height)

    def bounding_rect(self) -> QRectF:
        r = self._radius + 5
        h = self._height + 5
        return QRectF(self._cx - r, self._cy - h / 2, r * 2, h)

    def _handle_positions(self) -> list[tuple[float, float]]:
        return [
            (self._cx - self._radius, self._cy),
            (self._cx + self._radius, self._cy),
            (self._cx, self._cy - self._height / 2),
            (self._cx, self._cy + self._height / 2),
        ]

    def apply_handle_transform(
        self,
        handle: HandleType,
        point: QPointF,
        mouse_pos: QPointF,
        shift_pressed: bool = False,
        vertex_index: int = -1,
    ) -> None:
        if handle == HandleType.MOVE:
            dx = mouse_pos.x() - point.x()
            dy = mouse_pos.y() - point.y()
            self.move(dx, dy)
            return
        if handle == HandleType.BOTTOM_RIGHT:
            dx = mouse_pos.x() - point.x()
            dy = mouse_pos.y() - point.y()
            self._radius += dx * 0.3
            self._height += dy * 0.3
            self._radius = max(1.0, self._radius)
            self._height = max(1.0, self._height)

    def get_position_data(self) -> dict[str, Any]:
        return {
            "radius": self._radius,
            "height": self._height,
            "center": (self._cx, self._cy),
        }

    def restore_position_data(self, data: dict[str, Any]) -> None:
        self._radius = data["radius"]
        self._height = data["height"]
        self._cx, self._cy = data["center"]

    def to_dict(self) -> dict[str, Any]:
        d = super().to_dict()
        d["radius"] = self._radius
        d["height"] = self._height
        d["center_x"] = self._cx
        d["center_y"] = self._cy
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BaseShape:
        obj = cls(
            radius=data["radius"],
            height=data["height"],
            center=(data["center_x"], data["center_y"]),
            pen_color=data["pen_color"],
            pen_width=data.get("pen_width", 2.0),
            brush_color=data.get("brush_color"),
            selected=data.get("selected", False),
        )
        obj.id = data["id"]
        obj._rotation = data.get("rotation", 0.0)
        return obj


class ConeShape(BaseShape):
    """Конус — эллипс основания + вершина."""

    def __init__(
        self,
        radius: float,
        height: float,
        center: tuple[float, float],
        pen_color: tuple[int, int, int],
        pen_width: float,
        brush_color: tuple[int, int, int] | None,
        selected: bool,
    ):
        self._radius = radius
        self._height = height
        self._cx = center[0]
        self._cy = center[1]
        super().__init__(pen_color, pen_width, brush_color, selected)

    def _get_shape_type(self) -> ShapeType:
        return ShapeType.CONE  # type: ignore[attr-defined]

    def _draw_shape_content(self, painter: QPainter) -> None:
        r = self._radius
        h = self._height
        apex_y = self._cy - h / 2
        base_y = self._cy + h / 2
        ellipse_h = r * 0.35

        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(self.pen_color, self.pen_width))

        # Боковые линии к вершине
        painter.drawLine(QPointF(self._cx - r, base_y), QPointF(self._cx, apex_y))
        painter.drawLine(QPointF(self._cx + r, base_y), QPointF(self._cx, apex_y))

        # Нижнее основание (эллипс) — передняя часть
        painter.drawArc(
            QRectF(self._cx - r, base_y - ellipse_h, r * 2, ellipse_h * 2),
            0 * 16,
            -180 * 16,
        )

        # Задняя часть эллипса (пунктиром)
        back_color = QColor(
            self._pen_color.red(), self._pen_color.green(), self._pen_color.blue(), 120
        )
        back_pen = QPen(back_color, self.pen_width)
        painter.setPen(back_pen)
        painter.drawArc(
            QRectF(self._cx - r, base_y - ellipse_h, r * 2, ellipse_h * 2),
            180 * 16,
            -180 * 16,
        )

        # Заливка боковой поверхности
        if self._brush_color:
            color = QColor(
                self._brush_color.red(), self._brush_color.green(), self._brush_color.blue(), 60
            )
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.PenStyle.NoPen)
            # Треугольник боковой поверхности
            from PySide6.QtGui import QPolygonF

            poly = QPolygonF(
                [
                    QPointF(self._cx - r, base_y),
                    QPointF(self._cx + r, base_y),
                    QPointF(self._cx, apex_y),
                ]
            )
            painter.drawPolygon(poly)

    def move(self, dx: float, dy: float) -> None:
        self._cx += dx
        self._cy += dy

    def scale(self, factor: float, center: QPointF | None = None) -> None:
        self._radius *= factor
        self._height *= factor
        self._radius = max(1.0, self._radius)
        self._height = max(1.0, self._height)

    def bounding_rect(self) -> QRectF:
        r = self._radius + 5
        h = self._height + 5
        return QRectF(self._cx - r, self._cy - h / 2, r * 2, h)

    def _handle_positions(self) -> list[tuple[float, float]]:
        return [
            (self._cx - self._radius, self._cy + self._height / 2),
            (self._cx + self._radius, self._cy + self._height / 2),
            (self._cx, self._cy - self._height / 2),
        ]

    def apply_handle_transform(
        self,
        handle: HandleType,
        point: QPointF,
        mouse_pos: QPointF,
        shift_pressed: bool = False,
        vertex_index: int = -1,
    ) -> None:
        if handle == HandleType.MOVE:
            dx = mouse_pos.x() - point.x()
            dy = mouse_pos.y() - point.y()
            self.move(dx, dy)
            return
        if handle == HandleType.BOTTOM_RIGHT:
            dx = mouse_pos.x() - point.x()
            dy = mouse_pos.y() - point.y()
            self._radius += dx * 0.3
            self._height += dy * 0.3
            self._radius = max(1.0, self._radius)
            self._height = max(1.0, self._height)

    def get_position_data(self) -> dict[str, Any]:
        return {
            "radius": self._radius,
            "height": self._height,
            "center": (self._cx, self._cy),
        }

    def restore_position_data(self, data: dict[str, Any]) -> None:
        self._radius = data["radius"]
        self._height = data["height"]
        self._cx, self._cy = data["center"]

    def to_dict(self) -> dict[str, Any]:
        d = super().to_dict()
        d["radius"] = self._radius
        d["height"] = self._height
        d["center_x"] = self._cx
        d["center_y"] = self._cy
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BaseShape:
        obj = cls(
            radius=data["radius"],
            height=data["height"],
            center=(data["center_x"], data["center_y"]),
            pen_color=data["pen_color"],
            pen_width=data.get("pen_width", 2.0),
            brush_color=data.get("brush_color"),
            selected=data.get("selected", False),
        )
        obj.id = data["id"]
        obj._rotation = data.get("rotation", 0.0)
        return obj


class PyramidShape(BaseShape):
    """Четырёхугольная пирамида — основание + вершина."""

    def __init__(
        self,
        size: float,
        height: float,
        center: tuple[float, float],
        pen_color: tuple[int, int, int],
        pen_width: float,
        brush_color: tuple[int, int, int] | None,
        selected: bool,
    ):
        self._size = size
        self._height = height
        self._cx = center[0]
        self._cy = center[1]
        self._vertices: list[QPointF] = []
        super().__init__(pen_color, pen_width, brush_color, selected)
        self._project()

    def _project(self) -> None:
        """Проецирует основание (квадрат в перспективе) + вершину."""
        s = self._size / 2
        h = self._height / 2
        cos_a, sin_a = math.cos(math.radians(30)), math.sin(math.radians(30))

        # Основание — квадрат в изометрической проекции
        vertices_3d = [
            (-s, 0, -s),  # A
            (s, 0, -s),  # B
            (s, 0, s),  # C
            (-s, 0, s),  # D
            (0, h, 0),  # Apex
        ]

        self._vertices = []
        for vx, vy, vz in vertices_3d:
            y1 = vy * cos_a - vz * sin_a
            x2 = vx * cos_a + vz * sin_a
            self._vertices.append(QPointF(self._cx + x2 * 0.7, self._cy - y1 * 0.6))

    def _get_shape_type(self) -> ShapeType:
        return ShapeType.PYRAMID  # type: ignore[attr-defined]

    def _get_edges(self) -> list[tuple[int, int]]:
        return [
            (0, 1),
            (1, 2),
            (2, 3),
            (3, 0),  # основание
            (0, 4),
            (1, 4),
            (2, 4),
            (3, 4),  # рёбра к вершине
        ]

    def _draw_shape_content(self, painter: QPainter) -> None:
        edges = self._get_edges()
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(self.pen_color, self.pen_width))

        for i, j in edges:
            if i < len(self._vertices) and j < len(self._vertices):
                painter.drawLine(self._vertices[i], self._vertices[j])

        # Подписи вершин
        labels = ["A", "B", "C", "D", "S"]
        font = painter.font()
        font.setPointSizeF(9)
        painter.setFont(font)
        painter.setPen(QColor(50, 50, 50))

        for i, v in enumerate(self._vertices):
            dx, dy = v.x() - self._cx, v.y() - self._cy
            dist = math.sqrt(dx * dx + dy * dy)
            if dist > 0:
                lx = v.x() + (dx / dist) * 12
                ly = v.y() + (dy / dist) * 12
            else:
                lx, ly = v.x(), v.y()
            text_rect = QRectF(lx - 8, ly - 8, 16, 16)
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, labels[i])

    def move(self, dx: float, dy: float) -> None:
        self._cx += dx
        self._cy += dy
        self._project()

    def scale(self, factor: float, center: QPointF | None = None) -> None:
        self._size *= factor
        self._height *= factor
        self._size = max(1.0, self._size)
        self._height = max(1.0, self._height)
        self._project()

    def bounding_rect(self) -> QRectF:
        if not self._vertices:
            return QRectF()
        xs = [v.x() for v in self._vertices]
        ys = [v.y() for v in self._vertices]
        pad = 15
        return QRectF(
            min(xs) - pad,
            min(ys) - pad,
            max(xs) - min(xs) + pad * 2,
            max(ys) - min(ys) + pad * 2,
        )

    def _handle_positions(self) -> list[tuple[float, float]]:
        return [(v.x(), v.y()) for v in self._vertices]

    def apply_handle_transform(
        self,
        handle: HandleType,
        point: QPointF,
        mouse_pos: QPointF,
        shift_pressed: bool = False,
        vertex_index: int = -1,
    ) -> None:
        if handle == HandleType.MOVE:
            dx = mouse_pos.x() - point.x()
            dy = mouse_pos.y() - point.y()
            self.move(dx, dy)
            return
        idx = handle.value - 2
        if 0 <= idx < len(self._vertices):
            self._vertices[idx].setX(mouse_pos.x())
            self._vertices[idx].setY(mouse_pos.y())

    def get_position_data(self) -> dict[str, Any]:
        return {
            "size": self._size,
            "height": self._height,
            "center": (self._cx, self._cy),
        }

    def restore_position_data(self, data: dict[str, Any]) -> None:
        self._size = data["size"]
        self._height = data["height"]
        self._cx, self._cy = data["center"]
        self._project()

    def to_dict(self) -> dict[str, Any]:
        d = super().to_dict()
        d["size"] = self._size
        d["height"] = self._height
        d["center_x"] = self._cx
        d["center_y"] = self._cy
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BaseShape:
        obj = cls(
            size=data["size"],
            height=data["height"],
            center=(data["center_x"], data["center_y"]),
            pen_color=data["pen_color"],
            pen_width=data.get("pen_width", 2.0),
            brush_color=data.get("brush_color"),
            selected=data.get("selected", False),
        )
        obj.id = data["id"]
        obj._rotation = data.get("rotation", 0.0)
        return obj


class PrismShape(BaseShape):
    """Трёхугольная призма — два треугольника + боковые рёбра."""

    def __init__(
        self,
        size: float,
        height: float,
        center: tuple[float, float],
        pen_color: tuple[int, int, int],
        pen_width: float,
        brush_color: tuple[int, int, int] | None,
        selected: bool,
    ):
        self._size = size
        self._height = height
        self._cx = center[0]
        self._cy = center[1]
        self._vertices: list[QPointF] = []
        super().__init__(pen_color, pen_width, brush_color, selected)
        self._project()

    def _project(self) -> None:
        """Проецирует треугольную призму."""
        s = self._size / 2
        h = self._height / 2
        cos_a, sin_a = math.cos(math.radians(30)), math.sin(math.radians(30))

        # Нижний треугольник
        angles = [math.radians(270), math.radians(270 + 120), math.radians(270 + 240)]
        bottom = []
        for a in angles:
            x = s * math.cos(a)
            z = s * math.sin(a)
            y1 = 0 * cos_a - z * sin_a
            x2 = x * cos_a + z * sin_a
            bottom.append(QPointF(self._cx + x2 * 0.7, self._cy + h * 0.5 - y1 * 0.5))

        # Верхний треугольник
        top = []
        for a in angles:
            x = s * math.cos(a)
            z = s * math.sin(a)
            y1 = h * cos_a - z * sin_a
            x2 = x * cos_a + z * sin_a
            top.append(QPointF(self._cx + x2 * 0.7, self._cy - h * 0.5 - y1 * 0.5))

        self._vertices = bottom + top

    def _get_shape_type(self) -> ShapeType:
        return ShapeType.PRISM  # type: ignore[attr-defined]

    def _get_edges(self) -> list[tuple[int, int]]:
        return [
            (0, 1),
            (1, 2),
            (2, 0),  # нижний треугольник
            (3, 4),
            (4, 5),
            (5, 3),  # верхний треугольник
            (0, 3),
            (1, 4),
            (2, 5),  # боковые рёбра
        ]

    def _draw_shape_content(self, painter: QPainter) -> None:
        edges = self._get_edges()
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(self.pen_color, self.pen_width))

        for i, j in edges:
            if i < len(self._vertices) and j < len(self._vertices):
                painter.drawLine(self._vertices[i], self._vertices[j])

    def move(self, dx: float, dy: float) -> None:
        self._cx += dx
        self._cy += dy
        self._project()

    def scale(self, factor: float, center: QPointF | None = None) -> None:
        self._size *= factor
        self._height *= factor
        self._size = max(1.0, self._size)
        self._height = max(1.0, self._height)
        self._project()

    def bounding_rect(self) -> QRectF:
        if not self._vertices:
            return QRectF()
        xs = [v.x() for v in self._vertices]
        ys = [v.y() for v in self._vertices]
        pad = 10
        return QRectF(
            min(xs) - pad,
            min(ys) - pad,
            max(xs) - min(xs) + pad * 2,
            max(ys) - min(ys) + pad * 2,
        )

    def _handle_positions(self) -> list[tuple[float, float]]:
        return [(v.x(), v.y()) for v in self._vertices]

    def apply_handle_transform(
        self,
        handle: HandleType,
        point: QPointF,
        mouse_pos: QPointF,
        shift_pressed: bool = False,
        vertex_index: int = -1,
    ) -> None:
        if handle == HandleType.MOVE:
            dx = mouse_pos.x() - point.x()
            dy = mouse_pos.y() - point.y()
            self.move(dx, dy)
            return
        idx = handle.value - 2
        if 0 <= idx < len(self._vertices):
            self._vertices[idx].setX(mouse_pos.x())
            self._vertices[idx].setY(mouse_pos.y())

    def get_position_data(self) -> dict[str, Any]:
        return {
            "size": self._size,
            "height": self._height,
            "center": (self._cx, self._cy),
        }

    def restore_position_data(self, data: dict[str, Any]) -> None:
        self._size = data["size"]
        self._height = data["height"]
        self._cx, self._cy = data["center"]
        self._project()

    def to_dict(self) -> dict[str, Any]:
        d = super().to_dict()
        d["size"] = self._size
        d["height"] = self._height
        d["center_x"] = self._cx
        d["center_y"] = self._cy
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BaseShape:
        obj = cls(
            size=data["size"],
            height=data["height"],
            center=(data["center_x"], data["center_y"]),
            pen_color=data["pen_color"],
            pen_width=data.get("pen_width", 2.0),
            brush_color=data.get("brush_color"),
            selected=data.get("selected", False),
        )
        obj.id = data["id"]
        obj._rotation = data.get("rotation", 0.0)
        return obj


class TruncatedConeShape(BaseShape):
    """Усечённый конус — два эллипса разных размеров + боковые линии."""

    def __init__(
        self,
        bottom_radius: float,
        top_radius: float,
        height: float,
        center: tuple[float, float],
        pen_color: tuple[int, int, int],
        pen_width: float,
        brush_color: tuple[int, int, int] | None,
        selected: bool,
    ):
        self._bottom_radius = bottom_radius
        self._top_radius = top_radius
        self._height = height
        self._cx = center[0]
        self._cy = center[1]
        super().__init__(pen_color, pen_width, brush_color, selected)

    def _get_shape_type(self) -> ShapeType:
        return ShapeType.TRUNCATED_CONE  # type: ignore[attr-defined]

    def _draw_shape_content(self, painter: QPainter) -> None:
        r_bottom = self._bottom_radius
        r_top = self._top_radius
        h = self._height
        top_y = self._cy - h / 2
        bottom_y = self._cy + h / 2
        ellipse_h_bottom = r_bottom * 0.35
        ellipse_h_top = r_top * 0.35

        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(self.pen_color, self.pen_width))

        # Нижний эллипс (передняя часть)
        painter.drawArc(
            QRectF(
                self._cx - r_bottom,
                bottom_y - ellipse_h_bottom,
                r_bottom * 2,
                ellipse_h_bottom * 2,
            ),
            0 * 16,
            -180 * 16,
        )

        # Верхний эллипс (передняя часть)
        painter.drawArc(
            QRectF(self._cx - r_top, top_y - ellipse_h_top, r_top * 2, ellipse_h_top * 2),
            0 * 16,
            -180 * 16,
        )

        # Задние части эллипсов (пунктиром)
        back_color = QColor(
            self._pen_color.red(), self._pen_color.green(), self._pen_color.blue(), 120
        )
        back_pen = QPen(back_color, self.pen_width)
        painter.setPen(back_pen)
        painter.drawArc(
            QRectF(
                self._cx - r_bottom,
                bottom_y - ellipse_h_bottom,
                r_bottom * 2,
                ellipse_h_bottom * 2,
            ),
            180 * 16,
            -180 * 16,
        )
        painter.drawArc(
            QRectF(self._cx - r_top, top_y - ellipse_h_top, r_top * 2, ellipse_h_top * 2),
            180 * 16,
            -180 * 16,
        )

        # Боковые линии
        painter.setPen(QPen(self.pen_color, self.pen_width))
        painter.drawLine(QPointF(self._cx - r_bottom, bottom_y), QPointF(self._cx - r_top, top_y))
        painter.drawLine(QPointF(self._cx + r_bottom, bottom_y), QPointF(self._cx + r_top, top_y))

        # Заливка боковой поверхности
        if self._brush_color:
            color = QColor(
                self._brush_color.red(), self._brush_color.green(), self._brush_color.blue(), 60
            )
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.PenStyle.NoPen)
            from PySide6.QtGui import QPolygonF

            poly = QPolygonF(
                [
                    QPointF(self._cx - r_bottom, bottom_y),
                    QPointF(self._cx + r_bottom, bottom_y),
                    QPointF(self._cx + r_top, top_y),
                    QPointF(self._cx - r_top, top_y),
                ]
            )
            painter.drawPolygon(poly)

    def move(self, dx: float, dy: float) -> None:
        self._cx += dx
        self._cy += dy

    def scale(self, factor: float, center: QPointF | None = None) -> None:
        self._bottom_radius *= factor
        self._top_radius *= factor
        self._height *= factor
        self._bottom_radius = max(1.0, self._bottom_radius)
        self._top_radius = max(1.0, self._top_radius)
        self._height = max(1.0, self._height)

    def bounding_rect(self) -> QRectF:
        r = max(self._bottom_radius, self._top_radius) + 5
        h = self._height + 5
        return QRectF(self._cx - r, self._cy - h / 2, r * 2, h)

    def _handle_positions(self) -> list[tuple[float, float]]:
        return [
            (self._cx - self._bottom_radius, self._cy + self._height / 2),
            (self._cx + self._bottom_radius, self._cy + self._height / 2),
            (self._cx - self._top_radius, self._cy - self._height / 2),
            (self._cx + self._top_radius, self._cy - self._height / 2),
        ]

    def apply_handle_transform(
        self,
        handle: HandleType,
        point: QPointF,
        mouse_pos: QPointF,
        shift_pressed: bool = False,
        vertex_index: int = -1,
    ) -> None:
        if handle == HandleType.MOVE:
            dx = mouse_pos.x() - point.x()
            dy = mouse_pos.y() - point.y()
            self.move(dx, dy)
            return
        if handle == HandleType.BOTTOM_RIGHT:
            dx = mouse_pos.x() - point.x()
            dy = mouse_pos.y() - point.y()
            self._bottom_radius += dx * 0.3
            self._top_radius += dx * 0.2
            self._height += dy * 0.3
            self._bottom_radius = max(1.0, self._bottom_radius)
            self._top_radius = max(1.0, self._top_radius)
            self._height = max(1.0, self._height)

    def get_position_data(self) -> dict[str, Any]:
        return {
            "bottom_radius": self._bottom_radius,
            "top_radius": self._top_radius,
            "height": self._height,
            "center": (self._cx, self._cy),
        }

    def restore_position_data(self, data: dict[str, Any]) -> None:
        self._bottom_radius = data["bottom_radius"]
        self._top_radius = data["top_radius"]
        self._height = data["height"]
        self._cx, self._cy = data["center"]

    def to_dict(self) -> dict[str, Any]:
        d = super().to_dict()
        d["bottom_radius"] = self._bottom_radius
        d["top_radius"] = self._top_radius
        d["height"] = self._height
        d["center_x"] = self._cx
        d["center_y"] = self._cy
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BaseShape:
        obj = cls(
            bottom_radius=data["bottom_radius"],
            top_radius=data["top_radius"],
            height=data["height"],
            center=(data["center_x"], data["center_y"]),
            pen_color=data["pen_color"],
            pen_width=data.get("pen_width", 2.0),
            brush_color=data.get("brush_color"),
            selected=data.get("selected", False),
        )
        obj.id = data["id"]
        obj._rotation = data.get("rotation", 0.0)
        return obj


class TruncatedPyramidShape(BaseShape):
    """Усечённая пирамида — два квадрата разных размеров + рёбра."""

    def __init__(
        self,
        bottom_size: float,
        top_size: float,
        height: float,
        center: tuple[float, float],
        pen_color: tuple[int, int, int],
        pen_width: float,
        brush_color: tuple[int, int, int] | None,
        selected: bool,
    ):
        self._bottom_size = bottom_size
        self._top_size = top_size
        self._height = height
        self._cx = center[0]
        self._cy = center[1]
        self._vertices: list[QPointF] = []
        super().__init__(pen_color, pen_width, brush_color, selected)
        self._project()

    def _project(self) -> None:
        """Проецирует усечённую пирамиду."""
        cos_a, sin_a = math.cos(math.radians(30)), math.sin(math.radians(30))

        h = self._height / 2
        bs = self._bottom_size / 2
        ts = self._top_size / 2

        # Нижний квадрат
        bottom_3d = [
            (-bs, 0, -bs),
            (bs, 0, -bs),
            (bs, 0, bs),
            (-bs, 0, bs),
        ]
        # Верхний квадрат
        top_3d = [
            (-ts, h, -ts),
            (ts, h, -ts),
            (ts, h, ts),
            (-ts, h, ts),
        ]

        self._vertices = []
        for vx, vy, vz in bottom_3d:
            y1 = vy * cos_a - vz * sin_a
            x2 = vx * cos_a + vz * sin_a
            self._vertices.append(QPointF(self._cx + x2 * 0.7, self._cy + h * 0.5 - y1 * 0.5))
        for vx, vy, vz in top_3d:
            y1 = vy * cos_a - vz * sin_a
            x2 = vx * cos_a + vz * sin_a
            self._vertices.append(QPointF(self._cx + x2 * 0.7, self._cy - h * 0.5 - y1 * 0.5))

    def _get_shape_type(self) -> ShapeType:
        return ShapeType.TRUNCATED_PYRAMID  # type: ignore[attr-defined]

    def _get_edges(self) -> list[tuple[int, int]]:
        return [
            (0, 1),
            (1, 2),
            (2, 3),
            (3, 0),  # нижний квадрат
            (4, 5),
            (5, 6),
            (6, 7),
            (7, 4),  # верхний квадрат
            (0, 4),
            (1, 5),
            (2, 6),
            (3, 7),  # боковые рёбра
        ]

    def _draw_shape_content(self, painter: QPainter) -> None:
        edges = self._get_edges()
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(self.pen_color, self.pen_width))

        for i, j in edges:
            if i < len(self._vertices) and j < len(self._vertices):
                painter.drawLine(self._vertices[i], self._vertices[j])

    def move(self, dx: float, dy: float) -> None:
        self._cx += dx
        self._cy += dy
        self._project()

    def scale(self, factor: float, center: QPointF | None = None) -> None:
        self._bottom_size *= factor
        self._top_size *= factor
        self._height *= factor
        self._bottom_size = max(1.0, self._bottom_size)
        self._top_size = max(1.0, self._top_size)
        self._height = max(1.0, self._height)
        self._project()

    def bounding_rect(self) -> QRectF:
        if not self._vertices:
            return QRectF()
        xs = [v.x() for v in self._vertices]
        ys = [v.y() for v in self._vertices]
        pad = 10
        return QRectF(
            min(xs) - pad,
            min(ys) - pad,
            max(xs) - min(xs) + pad * 2,
            max(ys) - min(ys) + pad * 2,
        )

    def _handle_positions(self) -> list[tuple[float, float]]:
        return [(v.x(), v.y()) for v in self._vertices]

    def apply_handle_transform(
        self,
        handle: HandleType,
        point: QPointF,
        mouse_pos: QPointF,
        shift_pressed: bool = False,
        vertex_index: int = -1,
    ) -> None:
        if handle == HandleType.MOVE:
            dx = mouse_pos.x() - point.x()
            dy = mouse_pos.y() - point.y()
            self.move(dx, dy)
            return
        idx = handle.value - 2
        if 0 <= idx < len(self._vertices):
            self._vertices[idx].setX(mouse_pos.x())
            self._vertices[idx].setY(mouse_pos.y())

    def get_position_data(self) -> dict[str, Any]:
        return {
            "bottom_size": self._bottom_size,
            "top_size": self._top_size,
            "height": self._height,
            "center": (self._cx, self._cy),
        }

    def restore_position_data(self, data: dict[str, Any]) -> None:
        self._bottom_size = data["bottom_size"]
        self._top_size = data["top_size"]
        self._height = data["height"]
        self._cx, self._cy = data["center"]
        self._project()

    def to_dict(self) -> dict[str, Any]:
        d = super().to_dict()
        d["bottom_size"] = self._bottom_size
        d["top_size"] = self._top_size
        d["height"] = self._height
        d["center_x"] = self._cx
        d["center_y"] = self._cy
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BaseShape:
        obj = cls(
            bottom_size=data["bottom_size"],
            top_size=data["top_size"],
            height=data["height"],
            center=(data["center_x"], data["center_y"]),
            pen_color=data["pen_color"],
            pen_width=data.get("pen_width", 2.0),
            brush_color=data.get("brush_color"),
            selected=data.get("selected", False),
        )
        obj.id = data["id"]
        obj._rotation = data.get("rotation", 0.0)
        return obj
