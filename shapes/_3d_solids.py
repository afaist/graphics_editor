"""3D-фигуры: куб, параллелепипед, сфера, цилиндр, конус, пирамида, призма, усечённые тела."""

from __future__ import annotations

import math
from typing import Any

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QPainter, QPen, QPolygonF

from .base_shape import BaseShape, HandleType, ShapeType


class ParallelepipedShape(BaseShape):
    """Прямоугольный параллелепипед — 3D-2D проекция с гранями."""

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
        self._size = size
        self._aspect = aspect
        self._center_x = center[0]
        self._center_y = center[1]
        self._vertices: list[QPointF] = []
        self._labels: list[str] = []
        super().__init__(pen_color, pen_width, brush_color, selected)
        self._project()

    def _project(self) -> None:
        """Проецирует 3D-вершины на 2D-плоскость (как PlatonicSolidShape)."""
        w, h, d = self._aspect
        scale = self._size / 2
        cos_x, sin_x = math.cos(math.radians(30)), math.sin(math.radians(30))
        cos_y, sin_y = math.cos(math.radians(-45)), math.sin(math.radians(-45))

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
        for v3d in vertices_3d:
            x, y, z = v3d
            y1 = y * cos_x - z * sin_x
            z1 = y * sin_x + z * cos_x
            x2 = x * cos_y + z1 * sin_y
            self._vertices.append(
                QPointF(self._center_x + x2 * scale, self._center_y - y1 * scale)
            )
        self._labels = [chr(ord("A") + i) for i in range(len(self._vertices))]

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

    def _get_faces(self) -> list[list[int]]:
        return [
            [0, 1, 2, 3],  # задняя
            [4, 5, 6, 7],  # передняя
            [0, 1, 5, 4],  # нижняя
            [2, 3, 7, 6],  # верхняя
            [0, 3, 7, 4],  # левая
            [1, 2, 6, 5],  # правая
        ]

    def _draw_shape_content(self, painter: QPainter) -> None:
        # Рисуем закрашенные грани с затенением
        self._draw_faces(painter)

        # Рисуем рёбра поверх
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(self.pen_color, self.pen_width))
        for i, j in self._get_edges():
            if i < len(self._vertices) and j < len(self._vertices):
                painter.drawLine(self._vertices[i], self._vertices[j])

        # Метки вершин
        self._draw_labels(painter)

    def _draw_faces(self, painter: QPainter) -> None:
        """Закрашивает видимые грани с затенением."""
        faces = self._get_faces()
        if not faces:
            return

        # Вершины в 3D для вычисления глубины
        w, h, d = self._aspect
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

        # Сортируем грани от дальних к ближним
        face_depths = []
        for face in faces:
            z_sum = sum(vertices_3d[i][2] for i in face) / len(face)
            face_depths.append((z_sum, face))
        face_depths.sort(key=lambda x: x[0])

        for _, face in face_depths:
            cz3 = sum(vertices_3d[i][2] for i in face) / len(face)
            if cz3 > 0:
                brightness = 0.4 + 0.4 * cz3 / max(d, 0.01)
                brightness = max(0.4, min(0.8, brightness))
                color = QColor(int(180 * brightness), int(180 * brightness), int(200 * brightness))
                painter.setBrush(QBrush(color))

                poly_points = [self._vertices[idx] for idx in face if idx < len(self._vertices)]
                if len(poly_points) >= 3:
                    painter.drawPolygon(QPolygonF(poly_points))

    def _draw_labels(self, painter: QPainter) -> None:
        """Рисует метки вершин."""
        if not self._vertices:
            return
        painter.setPen(QPen(self.pen_color, 1))
        cx = sum(v.x() for v in self._vertices) / len(self._vertices)
        cy = sum(v.y() for v in self._vertices) / len(self._vertices)
        for i, v in enumerate(self._vertices):
            dx, dy = v.x() - cx, v.y() - cy
            dist = math.sqrt(dx * dx + dy * dy)
            if dist > 0:
                lx = v.x() + (dx / dist) * 12
                ly = v.y() + (dy / dist) * 12
            else:
                lx, ly = v.x(), v.y()
            painter.drawText(int(lx - 5), int(ly + 5), self._labels[i])

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
        pad = self._size / 2 + 20
        return QRectF(
            min(xs) - pad,
            min(ys) - pad,
            max(xs) - min(xs) + pad * 2,
            max(ys) - min(ys) + pad * 2,
        )

    def contains_point(self, point: QPointF) -> bool:
        return self.bounding_rect().contains(point)

    def _handle_positions(self) -> list[tuple[float, float]]:
        return [(v.x(), v.y()) for v in self._vertices]

    def _rotation_center(self) -> tuple[float, float] | None:
        return self._center_of_vertices(self._vertices)

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
        painter.drawEllipse(QPointF(self._cx, self._cy), r * 0.35, r)
        painter.drawEllipse(QPointF(self._cx, self._cy), r, r * 0.35)

        # Параллели (горизонтальные эллипсы)
        painter.drawEllipse(QPointF(self._cx, self._cy), r, r * 0.35)

        # Тень — полукруг справа-сверху (светотень)
        if self._brush_color:
            shadow = QColor(
                self._brush_color.red(),
                self._brush_color.green(),
                self._brush_color.blue(),
                100,
            )
            painter.setBrush(QBrush(shadow))
            painter.setPen(Qt.PenStyle.NoPen)
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

    def contains_point(self, point: QPointF) -> bool:
        return self.bounding_rect().contains(point)

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

        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(self.pen_color, self.pen_width))

        # Задняя часть верхнего эллипса (пунктиром)
        back_color = QColor(
            self._pen_color.red(),
            self._pen_color.green(),
            self._pen_color.blue(),
            120,
        )
        back_pen = QPen(back_color, self.pen_width)
        painter.setPen(back_pen)
        painter.drawEllipse(QPointF(self._cx, top_y), r, ellipse_h)

        # Передняя часть нижнего эллипса
        painter.setPen(QPen(self.pen_color, self.pen_width))
        painter.drawEllipse(QPointF(self._cx, bottom_y), r, ellipse_h)

        # Боковые линии
        painter.drawLine(QPointF(self._cx - r, top_y), QPointF(self._cx - r, bottom_y))
        painter.drawLine(QPointF(self._cx + r, top_y), QPointF(self._cx + r, bottom_y))

        # Верхний эллипс (передняя часть)
        painter.drawArc(
            QRectF(self._cx - r, top_y - ellipse_h, r * 2, ellipse_h * 2),
            180 * 16,
            -180 * 16,
        )

        # Заливка боковой поверхности
        if self._brush_color:
            color = QColor(
                self._brush_color.red(),
                self._brush_color.green(),
                self._brush_color.blue(),
                60,
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

    def contains_point(self, point: QPointF) -> bool:
        return self.bounding_rect().contains(point)

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
            self._pen_color.red(),
            self._pen_color.green(),
            self._pen_color.blue(),
            120,
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
                self._brush_color.red(),
                self._brush_color.green(),
                self._brush_color.blue(),
                60,
            )
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.PenStyle.NoPen)
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

    def contains_point(self, point: QPointF) -> bool:
        return self.bounding_rect().contains(point)

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
        self._labels: list[str] = []
        super().__init__(pen_color, pen_width, brush_color, selected)
        self._project()

    def _project(self) -> None:
        """Проецирует основание (квадрат в перспективе) + вершину."""
        scale = self._size / 2
        cos_x, sin_x = math.cos(math.radians(30)), math.sin(math.radians(30))
        cos_y, sin_y = math.cos(math.radians(-45)), math.sin(math.radians(-45))

        # Единичные вершины (масштабирование в проекции)
        aspect_h = self._height / self._size
        vertices_3d = [
            (-1, -aspect_h, -1),
            (1, -aspect_h, -1),
            (1, -aspect_h, 1),
            (-1, -aspect_h, 1),
            (0, aspect_h, 0),
        ]

        self._vertices = []
        for v3d in vertices_3d:
            x, y, z = v3d
            y1 = y * cos_x - z * sin_x
            z1 = y * sin_x + z * cos_x
            x2 = x * cos_y + z1 * sin_y
            self._vertices.append(QPointF(self._cx + x2 * scale, self._cy - y1 * scale))
        self._labels = [chr(ord("A") + i) for i in range(len(self._vertices))]

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

    def _get_faces(self) -> list[list[int]]:
        return [
            [0, 1, 4],  # передняя грань
            [1, 2, 4],  # правая грань
            [2, 3, 4],  # задняя грань
            [3, 0, 4],  # левая грань
            [0, 1, 2, 3],  # основание
        ]

    def _draw_shape_content(self, painter: QPainter) -> None:
        # Рисуем закрашенные грани с затенением
        self._draw_faces(painter)

        # Рисуем рёбра поверх
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(self.pen_color, self.pen_width))
        for i, j in self._get_edges():
            if i < len(self._vertices) and j < len(self._vertices):
                painter.drawLine(self._vertices[i], self._vertices[j])

        # Метки вершин
        self._draw_labels(painter)

    def _draw_faces(self, painter: QPainter) -> None:
        """Закрашивает видимые грани с затенением."""
        faces = self._get_faces()
        if not faces:
            return

        s = self._size / 2
        h = self._height / 2
        vertices_3d = [
            (-s, -h, -s),
            (s, -h, -s),
            (s, -h, s),
            (-s, -h, s),
            (0, h, 0),
        ]

        face_depths = []
        for face in faces:
            z_sum = sum(vertices_3d[i][2] for i in face) / len(face)
            face_depths.append((z_sum, face))
        face_depths.sort(key=lambda x: x[0])

        for _, face in face_depths:
            cz3 = sum(vertices_3d[i][2] for i in face) / len(face)
            if cz3 > 0:
                brightness = 0.4 + 0.4 * cz3 / max(s, 0.01)
                brightness = max(0.4, min(0.8, brightness))
                color = QColor(int(180 * brightness), int(180 * brightness), int(200 * brightness))
                painter.setBrush(QBrush(color))

                poly_points = [self._vertices[idx] for idx in face if idx < len(self._vertices)]
                if len(poly_points) >= 3:
                    painter.drawPolygon(QPolygonF(poly_points))

    def _draw_labels(self, painter: QPainter) -> None:
        """Рисует метки вершин."""
        if not self._vertices:
            return
        painter.setPen(QPen(self.pen_color, 1))
        cx = sum(v.x() for v in self._vertices) / len(self._vertices)
        cy = sum(v.y() for v in self._vertices) / len(self._vertices)
        for i, v in enumerate(self._vertices):
            dx, dy = v.x() - cx, v.y() - cy
            dist = math.sqrt(dx * dx + dy * dy)
            if dist > 0:
                lx = v.x() + (dx / dist) * 12
                ly = v.y() + (dy / dist) * 12
            else:
                lx, ly = v.x(), v.y()
            painter.drawText(int(lx - 5), int(ly + 5), self._labels[i])

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
        pad = self._size / 2 + 20
        return QRectF(
            min(xs) - pad,
            min(ys) - pad,
            max(xs) - min(xs) + pad * 2,
            max(ys) - min(ys) + pad * 2,
        )

    def contains_point(self, point: QPointF) -> bool:
        return self.bounding_rect().contains(point)

    def _handle_positions(self) -> list[tuple[float, float]]:
        return [(v.x(), v.y()) for v in self._vertices]

    def _rotation_center(self) -> tuple[float, float] | None:
        return self._center_of_vertices(self._vertices)

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
        self._labels: list[str] = []
        super().__init__(pen_color, pen_width, brush_color, selected)
        self._project()

    def _project(self) -> None:
        """Проецирует треугольную призму."""
        scale = self._size / 2
        aspect_h = self._height / self._size
        cos_x, sin_x = math.cos(math.radians(30)), math.sin(math.radians(30))
        cos_y, sin_y = math.cos(math.radians(-45)), math.sin(math.radians(-45))

        # Единичные координаты (масштабирование в проекции)
        angles = [math.radians(270), math.radians(270 + 120), math.radians(270 + 240)]
        bottom = []
        for a in angles:
            x = math.cos(a)
            z = math.sin(a)
            y1 = -aspect_h * cos_x - z * sin_x
            z1 = -aspect_h * sin_x + z * cos_x
            x2 = x * cos_y + z1 * sin_y
            bottom.append(QPointF(self._cx + x2 * scale, self._cy - y1 * scale))

        # Верхний треугольник
        top = []
        for a in angles:
            x = math.cos(a)
            z = math.sin(a)
            y1 = aspect_h * cos_x - z * sin_x
            z1 = aspect_h * sin_x + z * cos_x
            x2 = x * cos_y + z1 * sin_y
            top.append(QPointF(self._cx + x2 * scale, self._cy - y1 * scale))

        self._vertices = bottom + top
        self._labels = [chr(ord("A") + i) for i in range(len(self._vertices))]

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

    def _get_faces(self) -> list[list[int]]:
        return [
            [0, 1, 4, 3],  # передняя боковая
            [1, 2, 5, 4],  # правая боковая
            [2, 0, 3, 5],  # левая боковая
            [0, 1, 2],  # нижнее основание
            [3, 4, 5],  # верхнее основание
        ]

    def _draw_shape_content(self, painter: QPainter) -> None:
        self._draw_faces(painter)

        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(self.pen_color, self.pen_width))
        for i, j in self._get_edges():
            if i < len(self._vertices) and j < len(self._vertices):
                painter.drawLine(self._vertices[i], self._vertices[j])

        self._draw_labels(painter)

    def _draw_faces(self, painter: QPainter) -> None:
        """Закрашивает видимые грани с затенением."""
        faces = self._get_faces()
        if not faces:
            return

        s = self._size / 2
        h = self._height / 2

        angles = [math.radians(270), math.radians(270 + 120), math.radians(270 + 240)]
        vertices_3d = []
        for a in angles:
            x = s * math.cos(a)
            z = s * math.sin(a)
            vertices_3d.append((x, -h, z))
        for a in angles:
            x = s * math.cos(a)
            z = s * math.sin(a)
            vertices_3d.append((x, h, z))

        face_depths = []
        for face in faces:
            z_sum = sum(vertices_3d[i][2] for i in face) / len(face)
            face_depths.append((z_sum, face))
        face_depths.sort(key=lambda x: x[0])

        for _, face in face_depths:
            cz3 = sum(vertices_3d[i][2] for i in face) / len(face)
            if cz3 > 0:
                brightness = 0.4 + 0.4 * cz3 / max(s, 0.01)
                brightness = max(0.4, min(0.8, brightness))
                color = QColor(int(180 * brightness), int(180 * brightness), int(200 * brightness))
                painter.setBrush(QBrush(color))

                poly_points = [self._vertices[idx] for idx in face if idx < len(self._vertices)]
                if len(poly_points) >= 3:
                    painter.drawPolygon(QPolygonF(poly_points))

    def _draw_labels(self, painter: QPainter) -> None:
        """Рисует метки вершин."""
        if not self._vertices:
            return
        painter.setPen(QPen(self.pen_color, 1))
        cx = sum(v.x() for v in self._vertices) / len(self._vertices)
        cy = sum(v.y() for v in self._vertices) / len(self._vertices)
        for i, v in enumerate(self._vertices):
            dx, dy = v.x() - cx, v.y() - cy
            dist = math.sqrt(dx * dx + dy * dy)
            if dist > 0:
                lx = v.x() + (dx / dist) * 12
                ly = v.y() + (dy / dist) * 12
            else:
                lx, ly = v.x(), v.y()
            painter.drawText(int(lx - 5), int(ly + 5), self._labels[i])

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
        pad = self._size / 2 + 20
        return QRectF(
            min(xs) - pad,
            min(ys) - pad,
            max(xs) - min(xs) + pad * 2,
            max(ys) - min(ys) + pad * 2,
        )

    def contains_point(self, point: QPointF) -> bool:
        return self.bounding_rect().contains(point)

    def _handle_positions(self) -> list[tuple[float, float]]:
        return [(v.x(), v.y()) for v in self._vertices]

    def _rotation_center(self) -> tuple[float, float] | None:
        return self._center_of_vertices(self._vertices)

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
            self._pen_color.red(),
            self._pen_color.green(),
            self._pen_color.blue(),
            120,
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
                self._brush_color.red(),
                self._brush_color.green(),
                self._brush_color.blue(),
                60,
            )
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.PenStyle.NoPen)
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

    def contains_point(self, point: QPointF) -> bool:
        return self.bounding_rect().contains(point)

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
        self._labels: list[str] = []
        super().__init__(pen_color, pen_width, brush_color, selected)
        self._project()

    def _project(self) -> None:
        """Проецирует усечённую пирамиду."""
        scale = self._bottom_size / 2
        aspect_h = self._height / self._bottom_size
        aspect_top = self._top_size / self._bottom_size
        cos_x, sin_x = math.cos(math.radians(30)), math.sin(math.radians(30))
        cos_y, sin_y = math.cos(math.radians(-45)), math.sin(math.radians(-45))

        # Единичные координаты (масштабирование в проекции)
        bottom_3d = [
            (-1, -aspect_h, -1),
            (1, -aspect_h, -1),
            (1, -aspect_h, 1),
            (-1, -aspect_h, 1),
        ]
        top_3d = [
            (-aspect_top, aspect_h, -aspect_top),
            (aspect_top, aspect_h, -aspect_top),
            (aspect_top, aspect_h, aspect_top),
            (-aspect_top, aspect_h, aspect_top),
        ]

        self._vertices = []
        scale = self._bottom_size / 2
        for v3d in bottom_3d:
            x, y, z = v3d
            y1 = y * cos_x - z * sin_x
            z1 = y * sin_x + z * cos_x
            x2 = x * cos_y + z1 * sin_y
            self._vertices.append(QPointF(self._cx + x2 * scale, self._cy - y1 * scale))
        for v3d in top_3d:
            x, y, z = v3d
            y1 = y * cos_x - z * sin_x
            z1 = y * sin_x + z * cos_x
            x2 = x * cos_y + z1 * sin_y
            self._vertices.append(QPointF(self._cx + x2 * scale, self._cy - y1 * scale))
        self._labels = [chr(ord("A") + i) for i in range(len(self._vertices))]

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

    def _get_faces(self) -> list[list[int]]:
        return [
            [0, 1, 5, 4],  # передняя боковая
            [1, 2, 6, 5],  # правая боковая
            [2, 3, 7, 6],  # задняя боковая
            [3, 0, 4, 7],  # левая боковая
            [0, 1, 2, 3],  # нижнее основание
            [4, 5, 6, 7],  # верхнее основание
        ]

    def _draw_shape_content(self, painter: QPainter) -> None:
        self._draw_faces(painter)

        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(self.pen_color, self.pen_width))
        for i, j in self._get_edges():
            if i < len(self._vertices) and j < len(self._vertices):
                painter.drawLine(self._vertices[i], self._vertices[j])

        self._draw_labels(painter)

    def _draw_faces(self, painter: QPainter) -> None:
        """Закрашивает видимые грани с затенением."""
        faces = self._get_faces()
        if not faces:
            return

        bs = self._bottom_size / 2
        ts = self._top_size / 2
        h = self._height / 2

        vertices_3d = [
            (-bs, -h, -bs),
            (bs, -h, -bs),
            (bs, -h, bs),
            (-bs, -h, bs),
            (-ts, h, -ts),
            (ts, h, -ts),
            (ts, h, ts),
            (-ts, h, ts),
        ]

        face_depths = []
        for face in faces:
            z_sum = sum(vertices_3d[i][2] for i in face) / len(face)
            face_depths.append((z_sum, face))
        face_depths.sort(key=lambda x: x[0])

        for _, face in face_depths:
            cz3 = sum(vertices_3d[i][2] for i in face) / len(face)
            if cz3 > 0:
                brightness = 0.4 + 0.4 * cz3 / max(bs, 0.01)
                brightness = max(0.4, min(0.8, brightness))
                color = QColor(int(180 * brightness), int(180 * brightness), int(200 * brightness))
                painter.setBrush(QBrush(color))

                poly_points = [self._vertices[idx] for idx in face if idx < len(self._vertices)]
                if len(poly_points) >= 3:
                    painter.drawPolygon(QPolygonF(poly_points))

    def _draw_labels(self, painter: QPainter) -> None:
        """Рисует метки вершин."""
        if not self._vertices:
            return
        painter.setPen(QPen(self.pen_color, 1))
        cx = sum(v.x() for v in self._vertices) / len(self._vertices)
        cy = sum(v.y() for v in self._vertices) / len(self._vertices)
        for i, v in enumerate(self._vertices):
            dx, dy = v.x() - cx, v.y() - cy
            dist = math.sqrt(dx * dx + dy * dy)
            if dist > 0:
                lx = v.x() + (dx / dist) * 12
                ly = v.y() + (dy / dist) * 12
            else:
                lx, ly = v.x(), v.y()
            painter.drawText(int(lx - 5), int(ly + 5), self._labels[i])

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
        pad = self._bottom_size / 2 + 20
        return QRectF(
            min(xs) - pad,
            min(ys) - pad,
            max(xs) - min(xs) + pad * 2,
            max(ys) - min(ys) + pad * 2,
        )

    def contains_point(self, point: QPointF) -> bool:
        return self.bounding_rect().contains(point)

    def _handle_positions(self) -> list[tuple[float, float]]:
        return [(v.x(), v.y()) for v in self._vertices]

    def _rotation_center(self) -> tuple[float, float] | None:
        return self._center_of_vertices(self._vertices)

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
