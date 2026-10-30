"""Фигура: Платоново тело (3D-2D проекция)."""

import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QPen, QPolygonF

from .base_shape import BaseShape, HandleType, ShapeType


class PlatonicSolidShape(BaseShape):
    def __init__(self, solid_type, size, center, pen_color, pen_width, brush_color, selected):
        self._solid_type = solid_type
        self._size = size
        self._center_x = center[0] if center else 0.0
        self._center_y = center[1] if center else 0.0
        self._vertices_3d = self._get_vertices_3d()
        self._edges = self._get_edges()
        self._vertices: list[QPointF] = []
        self._labels: list[str] = []
        self._num_vertices = 0
        super().__init__(pen_color, pen_width, brush_color, selected)
        self._project()

    def _get_vertices_3d(self):
        phi = (1 + math.sqrt(5)) / 2
        solids = {
            "tetrahedron": [(1, 1, 1), (1, -1, -1), (-1, 1, -1), (-1, -1, 1)],
            "cube": [
                (-1, -1, -1),
                (1, -1, -1),
                (1, 1, -1),
                (-1, 1, -1),
                (-1, -1, 1),
                (1, -1, 1),
                (1, 1, 1),
                (-1, 1, 1),
            ],
            "octahedron": [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)],
            "dodecahedron": [
                (1, 1, 1),
                (1, 1, -1),
                (1, -1, 1),
                (1, -1, -1),
                (-1, 1, 1),
                (-1, 1, -1),
                (-1, -1, 1),
                (-1, -1, -1),
                (0, phi, 1 / phi),
                (0, phi, -1 / phi),
                (0, -phi, 1 / phi),
                (0, -phi, -1 / phi),
                (phi, 1 / phi, 0),
                (phi, -1 / phi, 0),
                (-phi, 1 / phi, 0),
                (-phi, -1 / phi, 0),
                (1 / phi, 0, phi),
                (1 / phi, 0, -phi),
                (-1 / phi, 0, phi),
                (-1 / phi, 0, -phi),
            ],
            "icosahedron": [
                (0, 1, phi),
                (0, 1, -phi),
                (0, -1, phi),
                (0, -1, -phi),
                (1, phi, 0),
                (1, -phi, 0),
                (-1, phi, 0),
                (-1, -phi, 0),
                (phi, 0, 1),
                (phi, 0, -1),
                (-phi, 0, 1),
                (-phi, 0, -1),
            ],
        }
        return solids[self._solid_type]

    def _get_edges(self):
        edges_map = {
            "tetrahedron": [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)],
            "cube": [
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
            ],
            "octahedron": [
                (0, 2),
                (0, 3),
                (0, 4),
                (0, 5),
                (1, 2),
                (1, 3),
                (1, 4),
                (1, 5),
                (2, 4),
                (2, 5),
                (3, 4),
                (3, 5),
            ],
        }
        if self._solid_type in edges_map:
            return edges_map[self._solid_type]
        # Для додекаэдра и икосаэдра — вычисляем по расстоянию
        return self._compute_edges_dynamic()

    def _compute_edges_dynamic(self):
        """Вычисляем рёбра по расстоянию между вершинами в 3D."""
        edges = []
        # Додекаэдр: рёбра длиной ~1.328, икосаэдр: рёбра длиной 2.0
        if self._solid_type == "dodecahedron":
            min_dist, max_dist = 1.2, 1.5
        else:  # icosahedron
            min_dist, max_dist = 1.8, 2.2

        for i in range(len(self._vertices_3d)):
            for j in range(i + 1, len(self._vertices_3d)):
                dx = self._vertices_3d[i][0] - self._vertices_3d[j][0]
                dy = self._vertices_3d[i][1] - self._vertices_3d[j][1]
                dz = self._vertices_3d[i][2] - self._vertices_3d[j][2]
                dist = math.sqrt(dx * dx + dy * dy + dz * dz)
                if min_dist < dist < max_dist:
                    edges.append((i, j))
        return edges

    def _get_faces(self):
        """Возвращает список граней (списки индексов вершин)."""
        faces_map = {
            "tetrahedron": [
                [0, 1, 2],
                [0, 1, 3],
                [0, 2, 3],
                [1, 2, 3],
            ],
            "cube": [
                [0, 1, 2, 3],
                [4, 5, 6, 7],
                [0, 1, 5, 4],
                [2, 3, 7, 6],
                [0, 3, 7, 4],
                [1, 2, 6, 5],
            ],
            "octahedron": [
                [0, 2, 4],
                [0, 4, 3],
                [0, 3, 5],
                [0, 5, 2],
                [1, 4, 2],
                [1, 3, 4],
                [1, 5, 3],
                [1, 2, 5],
            ],
            "dodecahedron": [
                [0, 1, 2, 3, 4],
                [5, 6, 7, 8, 9],
                [10, 11, 12, 13, 14],
                [15, 16, 17, 18, 19],
                [0, 8, 12, 16, 4],
                [1, 5, 9, 10, 2],
                [3, 11, 15, 19, 7],
                [6, 14, 18, 13, 17],
                [0, 4, 9, 5, 1],
                [2, 10, 11, 3, 7],
                [6, 17, 19, 15, 14],
                [8, 12, 13, 18, 16],
            ],
            "icosahedron": [
                [0, 1, 5],
                [0, 5, 11],
                [0, 11, 9],
                [0, 9, 7],
                [0, 7, 1],
                [2, 1, 7],
                [2, 7, 10],
                [2, 10, 3],
                [2, 3, 4],
                [2, 4, 1],
                [6, 11, 5],
                [6, 5, 1],
                [6, 1, 4],
                [6, 4, 8],
                [6, 8, 11],
                [3, 10, 9],
                [3, 9, 11],
                [3, 11, 8],
                [3, 8, 4],
                [4, 8, 1],
            ],
        }
        if self._solid_type in faces_map:
            return faces_map[self._solid_type]
        return []

    def _project(self):
        cos_x, sin_x = math.cos(math.radians(30)), math.sin(math.radians(30))
        cos_y, sin_y = math.cos(math.radians(-45)), math.sin(math.radians(-45))

        # Масштабный коэффициент для выравнивания размеров фигур
        scale_factor = 1.0
        if self._solid_type == "octahedron":
            scale_factor = 1.7  # Октаэдр меньше остальных, увеличиваем

        scale = self._size / 2 * scale_factor
        self._vertices = []
        for v3d in self._vertices_3d:
            x, y, z = v3d
            y1 = y * cos_x - z * sin_x
            z1 = y * sin_x + z * cos_x
            x2 = x * cos_y + z1 * sin_y
            self._vertices.append(
                QPointF(self._center_x + x2 * scale, self._center_y - y1 * scale)
            )
        self._num_vertices = len(self._vertices)
        self._labels = [chr(ord("A") + i) for i in range(self._num_vertices)]

    def _get_shape_type(self):
        return {
            "tetrahedron": ShapeType.TETRAHEDRON,
            "cube": ShapeType.CUBE,
            "octahedron": ShapeType.OCTAHEDRON,
            "dodecahedron": ShapeType.DODECAHEDRON,
            "icosahedron": ShapeType.ICOSAHEDRON,
        }[self._solid_type]

    def set_end_point(self, x, y):
        pass

    def set_size(self, w, h):
        pass

    def add_vertex(self, x, y):
        pass

    def draw(self, painter):
        painter.save()
        pen = QPen(self.pen_color, self.pen_width)
        painter.setPen(pen)

        # Рисуем закрашенные грани с затенением только для тетраэдра и куба
        if self._solid_type in ("tetrahedron", "cube"):
            self._draw_faces(painter)

        # Рисуем рёбра поверх
        painter.setBrush(Qt.BrushStyle.NoBrush)
        for i, j in self._edges:
            if i < len(self._vertices) and j < len(self._vertices):
                painter.drawLine(self._vertices[i], self._vertices[j])

        # Labels
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
        painter.restore()

    def _draw_faces(self, painter):
        """Закрашивает видимые грани с затенением."""
        faces = self._get_faces()
        if not faces:
            return

        # Вычисляем Z-координату для сортировки граней
        face_depths = []
        for face in faces:
            z_sum = 0
            for idx in face:
                if idx < len(self._vertices_3d):
                    z_sum += self._vertices_3d[idx][2]
            face_depths.append((z_sum / len(face), face))

        # Сортируем от дальних к ближним (painter overpaint)
        face_depths.sort(key=lambda x: x[0])

        for _, face in face_depths:
            # Вычисляем нормаль грани
            if len(face) < 3:
                continue

            # Центр грани в 3D
            cz3 = sum(self._vertices_3d[i][2] for i in face) / len(face)

            # Вектор от центра к камере (0,0,1)
            dot = cz3  # просто Z-компонента для простой проекции

            # Если грань обращена к камере — закрашиваем
            if dot > 0:
                # Яркость зависит от угла (0.4 - 0.8)
                brightness = 0.4 + 0.4 * dot
                color = QColor(int(180 * brightness), int(180 * brightness), int(200 * brightness))
                painter.setBrush(QBrush(color))

                # Строим 2D полигон
                poly_points = []
                for idx in face:
                    if idx < len(self._vertices):
                        poly_points.append(self._vertices[idx])

                if len(poly_points) >= 3:
                    painter.drawPolygon(QPolygonF(poly_points))

    def contains_point(self, point):
        return self.bounding_rect().contains(point)

    def move(self, dx, dy):
        self._center_x += dx
        self._center_y += dy
        self._project()

    def rotate(self, angle, center=None):
        self._rotation = (self._rotation + angle) % 360
        self._project()

    def scale(self, factor, center=None):
        self._size *= factor
        self._size = max(1.0, self._size)
        self._project()

    def bounding_rect(self):
        if not self._vertices:
            return QRectF()
        xs = [v.x() for v in self._vertices]
        ys = [v.y() for v in self._vertices]
        pad = self._size / 2 + 20
        return QRectF(
            min(xs) - pad, min(ys) - pad, max(xs) - min(xs) + pad * 2, max(ys) - min(ys) + pad * 2
        )

    def _handle_positions(self) -> list[tuple[float, float]]:
        return [(v.x(), v.y()) for v in self._vertices]

    def get_handles(self):
        return list(self._vertices)

    def apply_handle_transform(self, handle, point, mouse_pos, shift_pressed=False):
        if handle == HandleType.MOVE:
            dx = mouse_pos.x() - point.x()
            dy = mouse_pos.y() - point.y()
            self.move(dx, dy)
            return
        idx = handle.value - 2
        if 0 <= idx < len(self._vertices):
            self._vertices[idx].setX(mouse_pos.x())
            self._vertices[idx].setY(mouse_pos.y())

    def get_position_data(self):
        return {
            "solid_type": self._solid_type,
            "size": self._size,
            "center": (self._center_x, self._center_y),
        }

    def restore_position_data(self, data):
        self._solid_type = data["solid_type"]
        self._size = data["size"]
        self._center_x, self._center_y = data["center"]
        self._project()

    def get_properties(self):
        d = super().get_properties()
        d["solid_type"] = self._solid_type
        d["size"] = self._size
        return d

    def apply_properties(self, properties):
        super().apply_properties(properties)
        if "solid_type" in properties:
            self._solid_type = properties["solid_type"]
            self._vertices_3d = self._get_vertices_3d()
            self._edges = self._get_edges()
        if "size" in properties:
            self._size = properties["size"]
        if any(k in properties for k in ("solid_type", "size")):
            self._project()

    def to_dict(self):
        d = super().to_dict()
        d["solid_type"] = self._solid_type
        d["size"] = self._size
        d["center_x"] = self._center_x
        d["center_y"] = self._center_y
        return d

    @classmethod
    def from_dict(cls, data):
        obj = cls(
            solid_type=data["solid_type"],
            size=data["size"],
            center=(data["center_x"], data["center_y"]),
            pen_color=data["pen_color"],
            pen_width=data.get("pen_width", 2.0),
            brush_color=data.get("brush_color"),
            selected=data.get("selected", False),
        )
        obj._rotation = data.get("rotation", 0.0)
        obj.id = data["id"]
        obj.group_id = data.get("group_id")
        return obj
