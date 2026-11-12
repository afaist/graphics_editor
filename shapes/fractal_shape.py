"""Фрактальные фигуры."""

from __future__ import annotations

import math
from typing import Any

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPen, QPolygonF

from .base_shape import BaseShape, HandleType, ShapeType


class VectorFractalShape(BaseShape):
    """Векторный фрактал (Кох, Серпинский, Кантор, дерево Пифагора)."""

    def __init__(
        self,
        segments: list[list[tuple[float, float]]] | None = None,
        pen_color: tuple[int, int, int] = (0, 0, 0),
        pen_width: float = 1.5,
        brush_color: tuple[int, int, int] | None = None,
        selected: bool = False,
        fractal_type: str = "fractal",
        rects: list[tuple[float, float, float, float]] | None = None,
        squares: list[list[tuple[float, float]]] | None = None,
        colored_segments: list[tuple[float, float, float, float, int, int, int]] | None = None,
        title: str = "",
    ):
        self._fractal_type = fractal_type
        self._segments = segments if segments is not None else []
        self._rects = rects if rects is not None else []
        self._squares = squares if squares is not None else []
        self._colored_segments = colored_segments if colored_segments is not None else []
        self._title = title
        super().__init__(pen_color, pen_width, brush_color, selected)

    def _get_shape_type(self) -> ShapeType:
        return ShapeType(self._fractal_type)

    def _rotation_center(self) -> tuple[float, float] | None:
        if not self._segments:
            return None
        all_points = [QPointF(p[0], p[1]) for seg in self._segments for p in seg]
        return self._center_of_vertices(all_points)

    def _draw_shape_content(self, painter: QPainter) -> None:
        from PySide6.QtGui import QFont

        fractal_pen = QPen(self.pen_color, self.pen_width)
        painter.setPen(fractal_pen)

        # Рисуем заголовок НАД фракталом
        if self._title:
            title_font = QFont("Segoe UI", 14, QFont.Weight.Bold)
            painter.setFont(title_font)
            painter.setPen(QPen(self.pen_color, 1))
            br = self.bounding_rect()
            # Рисуем в верхней полосе bounding_rect (28px высоты)
            title_rect = QRectF(br.left(), br.top(), br.width(), 28)
            painter.drawText(
                title_rect,
                Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignHCenter,
                self._title,
            )

        # Рисуем закрашенные прямоугольники (ковёр Серпинского)
        if self._rects and self.brush_color:
            painter.setBrush(self.brush_color)
            for x, y, w, h in self._rects:
                painter.drawRect(int(x), int(y), int(w), int(h))

        # Рисуем закрашенные квадраты (дерево Пифагора)
        if self._squares and self.brush_color:
            painter.setBrush(self.brush_color)
            for square in self._squares:
                points = [QPointF(p[0], p[1]) for p in square]
                polygon = QPolygonF(points)
                painter.drawPolygon(polygon)

        # Рисуем цветные линии (множество Кантора)
        if self._colored_segments:
            for x1, y1, x2, y2, r, g, b in self._colored_segments:
                color_pen = QPen(QColor(r, g, b), self.pen_width)
                painter.setPen(color_pen)
                painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

        # Рисуем линии (кох и другие линейные фракталы)
        if self._fractal_type not in (
            "fractal_pythagorean_tree",
            "fractal_cantor_set",
        ):
            painter.setBrush(Qt.BrushStyle.NoBrush)
            for segment in self._segments:
                if len(segment) < 2:
                    continue
                points = [QPointF(p[0], p[1]) for p in segment]
                for i in range(len(points) - 1):
                    painter.drawLine(points[i], points[i + 1])

    def contains_point(self, point: QPointF) -> bool:
        return self.bounding_rect().contains(point)

    def move(self, dx: float, dy: float) -> None:
        new_segments: list[list[tuple[float, float]]] = []
        for segment in self._segments:
            new_seg = [(p[0] + dx, p[1] + dy) for p in segment]
            new_segments.append(new_seg)
        self._segments = new_segments

    def scale(self, factor: float, center: QPointF | None = None) -> None:
        if center is None:
            rot_center = self._rotation_center()
            if rot_center is not None:
                center = QPointF(*rot_center)
            else:
                center = QPointF(0, 0)
        new_segments: list[list[tuple[float, float]]] = []
        for segment in self._segments:
            new_seg = [
                (
                    center.x() + (p[0] - center.x()) * factor,
                    center.y() + (p[1] - center.y()) * factor,
                )
                for p in segment
            ]
            new_segments.append(new_seg)
        self._segments = new_segments

    def rotate(self, angle: float, center: QPointF | None = None) -> None:
        if not self._rotation_center():
            return
        if center is None:
            rot_center = self._rotation_center()
            if rot_center is None:
                return
            cx, cy = rot_center
            center = QPointF(cx, cy)
        rad = math.radians(angle)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        new_segments: list[list[tuple[float, float]]] = []
        for segment in self._segments:
            new_seg = [
                (
                    center.x() + (p[0] - center.x()) * cos_a - (p[1] - center.y()) * sin_a,
                    center.y() + (p[0] - center.x()) * sin_a + (p[1] - center.y()) * cos_a,
                )
                for p in segment
            ]
            new_segments.append(new_seg)
        self._segments = new_segments

    def bounding_rect(self) -> QRectF:
        all_points: list[tuple[float, float]] = []
        for seg in self._segments:
            all_points.extend(seg)
        for x, y, w, h in self._rects:
            all_points.extend([(x, y), (x + w, y), (x + w, y + h), (x, y + h)])
        for square in self._squares:
            all_points.extend(square)
        for x1, y1, x2, y2, *_ in self._colored_segments:
            all_points.extend([(x1, y1), (x2, y2)])
        if not all_points:
            return QRectF()
        xs = [p[0] for p in all_points]
        ys = [p[1] for p in all_points]
        pad = max(self.pen_width / 2 + 2, 4)
        # Добавляем место для заголовка сверху
        title_offset = 28 if self._title else 0
        return self._safe_rect(
            min(xs) - pad,
            min(ys) - pad - title_offset,
            max(xs) - min(xs) + 2 * pad,
            max(ys) - min(ys) + 2 * pad + title_offset,
        )

    def get_handles(self) -> list[QPointF]:
        return []

    def get_handle_type(self, point: QPointF, tolerance: float = 5.0) -> HandleType:
        return HandleType.NONE

    def apply_handle_transform(
        self,
        handle: HandleType,
        point: QPointF,
        mouse_pos: QPointF,
        shift_pressed: bool = False,
        vertex_index: int = -1,
    ) -> None:
        pass

    def _handle_positions(self) -> list[tuple[float, float]]:
        return []

    def get_properties(self) -> dict[str, Any]:
        d = super().get_properties()
        d["_fractal_type"] = self._fractal_type
        return d

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update(
            {
                "segments": self._segments,
                "rects": self._rects,
                "squares": self._squares,
                "colored_segments": self._colored_segments,
                "title": self._title,
                "fractal_type": self._fractal_type,
            }
        )
        return d

    @classmethod
    def from_dict(cls, data: dict) -> VectorFractalShape:
        obj = cls(
            segments=data.get("segments", []),
            pen_color=data["pen_color"],
            brush_color=data.get("brush_color"),
            pen_width=data.get("pen_width", 1.5),
            fractal_type=data.get("fractal_type", "fractal"),
            rects=data.get("rects", []),
            squares=data.get("squares", []),
            colored_segments=data.get("colored_segments", []),
            title=data.get("title", ""),
        )
        obj._selected = data.get("selected", False)
        obj._rotation = data.get("rotation", 0.0)
        return obj


class RasterFractalShape(BaseShape):
    """Растровый фрактал (Мандельброт, Жюлиа, Ньютон)."""

    def __init__(
        self,
        data: list[list[int]],
        width: int,
        height: int,
        x_scale: float,
        y_scale: float,
        fractal_type: str = "mandelbrot",
        pen_color: tuple[int, int, int] = (0, 0, 0),
        pen_width: float = 1.0,
        brush_color: tuple[int, int, int] | None = None,
        selected: bool = False,
        title: str = "",
    ):
        self._fractal_type = fractal_type
        self._data = data
        self._width = width
        self._height = height
        self._x_scale = x_scale
        self._y_scale = y_scale
        self._title = title
        super().__init__(pen_color, pen_width, brush_color, selected)
        self._render_dirty = True

    def _get_shape_type(self) -> ShapeType:
        return ShapeType(self._fractal_type)

    def _rotation_center(self) -> tuple[float, float] | None:
        return (self._width / 2, self._height / 2)

    def _draw_shape_content(self, painter: QPainter) -> None:
        from PySide6.QtGui import QFont, QImage, QPixmap

        if not self._data or not self._width or not self._height:
            return

        # Рисуем заголовок НАД фракталом
        if self._title:
            title_font = QFont("Segoe UI", 14, QFont.Weight.Bold)
            painter.setFont(title_font)
            painter.setPen(QPen(self.pen_color, 1))
            br = self.bounding_rect()
            # Рисуем в верхней полосе bounding_rect (28px высоты)
            title_rect = QRectF(br.left(), br.top(), br.width(), 28)
            painter.drawText(
                title_rect,
                Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignHCenter,
                self._title,
            )

        try:
            # Создаём QImage из данных
            img_data = bytearray()
            for row in self._data:
                for val in row:
                    # Градиентная раскраска
                    r = min(255, val * 3)
                    g = min(255, val * 2)
                    b = min(255, val)
                    img_data.extend([b, g, r, 255])  # BGRA

            image = QImage(img_data, self._width, self._height, QImage.Format.Format_ARGB32)
            pixmap = QPixmap.fromImage(image)
            title_offset = 28 if self._title else 0
            painter.drawPixmap(0, title_offset, pixmap)
        except ImportError:
            # numpy не установлен — рисуем заглушку
            painter.setPen(QPen(QColor(200, 0, 0), 2))
            painter.drawText(0, 20, "numpy не установлен")

    def contains_point(self, point: QPointF) -> bool:
        return self.bounding_rect().contains(point)

    def move(self, dx: float, dy: float) -> None:
        self._render_dirty = True

    def scale(self, factor: float, center: QPointF | None = None) -> None:
        self._render_dirty = True

    def rotate(self, angle: float, center: QPointF | None = None) -> None:
        self._render_dirty = True

    def bounding_rect(self) -> QRectF:
        pad = max(self.pen_width / 2 + 2, 4)
        title_offset = 28 if self._title else 0
        return self._safe_rect(
            -pad,
            -pad - title_offset,
            self._width + 2 * pad,
            self._height + 2 * pad + title_offset,
        )

    def get_handles(self) -> list[QPointF]:
        return []

    def get_handle_type(self, point: QPointF, tolerance: float = 5.0) -> HandleType:
        return HandleType.NONE

    def apply_handle_transform(
        self,
        handle: HandleType,
        point: QPointF,
        mouse_pos: QPointF,
        shift_pressed: bool = False,
        vertex_index: int = -1,
    ) -> None:
        pass

    def _handle_positions(self) -> list[tuple[float, float]]:
        return []

    def get_properties(self) -> dict[str, Any]:
        d = super().get_properties()
        d["_fractal_type"] = self._fractal_type
        d["_width"] = self._width
        d["_height"] = self._height
        return d

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update(
            {
                "data": self._data,
                "width": self._width,
                "height": self._height,
                "x_scale": self._x_scale,
                "y_scale": self._y_scale,
                "title": self._title,
                "fractal_type": self._fractal_type,
            }
        )
        return d

    @classmethod
    def from_dict(cls, data: dict) -> RasterFractalShape:
        obj = cls(
            data=data.get("data", []),
            width=data.get("width", 500),
            height=data.get("height", 500),
            x_scale=data.get("x_scale", 1.0),
            y_scale=data.get("y_scale", 1.0),
            fractal_type=data.get("fractal_type", "mandelbrot"),
            pen_color=data["pen_color"],
            brush_color=data.get("brush_color"),
            pen_width=data.get("pen_width", 1.0),
            title=data.get("title", ""),
        )
        obj._selected = data.get("selected", False)
        obj._rotation = data.get("rotation", 0.0)
        return obj
