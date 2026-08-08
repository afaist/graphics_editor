"""QUndoCommand-подклассы для операций с фигурами."""

from __future__ import annotations

from typing import List, Set, TYPE_CHECKING

from PySide6.QtGui import QUndoCommand

if TYPE_CHECKING:
    from shapes.base_shape import BaseShape


class AddShapeCommand(QUndoCommand):
    """Команда добавления фигуры."""

    def __init__(
        self,
        manager: "ShapeManager",
        shape: BaseShape,
        parent: QUndoCommand | None = None,
    ):
        super().__init__(f"Add {shape.shape_type.value}", parent)
        self._manager = manager
        self._shape = shape
        self._added_id: int | None = None

    def undo(self) -> None:
        if self._added_id is not None:
            self._manager.remove_shapes({self._added_id})

    def redo(self) -> None:
        # Генерируем ID
        shape = self._shape
        if shape.id in self._manager._shapes:
            shape.id = self._manager._next_id
            self._manager._next_id += 1
        else:
            shape.id = self._manager._next_id
            self._manager._next_id += 1

        self._manager._shapes[shape.id] = shape
        self._manager.shape_added.emit(shape)
        self._manager.shapes_changed.emit()
        self._added_id = shape.id


class RemoveShapesCommand(QUndoCommand):
    """Команда удаления фигур."""

    def __init__(
        self,
        manager: "ShapeManager",
        ids: Set[int],
        parent: QUndoCommand | None = None,
    ):
        super().__init__("Delete shapes", parent)
        self._manager = manager
        self._ids = set(ids)
        self._removed_shapes: List[BaseShape] = []
        self._removed_dicts: List[dict] = []

    def _import_shape(self, data: dict) -> BaseShape:
        import importlib
        from shapes import point_shape, line_shape, rectangle_shape, ellipse_shape
        from shapes import polygon_shape, polyline_shape

        factory = {
            "point": point_shape.PointShape.from_dict,
            "line": line_shape.LineShape.from_dict,
            "rectangle": rectangle_shape.RectangleShape.from_dict,
            "ellipse": ellipse_shape.EllipseShape.from_dict,
            "polygon": polygon_shape.PolygonShape.from_dict,
            "polyline": polyline_shape.PolylineShape.from_dict,
        }
        shape_type = data.get("type")
        if not shape_type or not isinstance(shape_type, str):
            raise ValueError(f"Unknown shape type: {shape_type}")
        cls = factory.get(shape_type)
        if cls is None:
            raise ValueError(f"Unknown shape type: {shape_type}")
        shape = cls(data)
        self._manager._shapes[shape.id] = shape
        return shape

    def undo(self) -> None:
        # Восстанавливаем удалённые фигуры
        for d in self._removed_dicts:
            shape = self._import_shape(d)
            self._manager.shape_added.emit(shape)
        self._manager._selected_ids = set(s.id for s in self._removed_shapes)
        self._manager.shapes_changed.emit()

    def redo(self) -> None:
        # Сохраняем данные перед удалением
        ids_to_remove = set(self._ids)
        self._removed_shapes = [
            self._manager._shapes[i] for i in ids_to_remove if i in self._manager._shapes
        ]
        self._removed_dicts = [s.to_dict() for s in self._removed_shapes]

        for sid in ids_to_remove:
            if sid in self._manager._shapes:
                del self._manager._shapes[sid]
        self._manager._selected_ids -= ids_to_remove
        self._manager.shape_removed.emit(self._removed_shapes)
        self._manager.shapes_changed.emit()


class MoveShapesCommand(QUndoCommand):
    """Команда перемещения фигур."""

    def __init__(
        self,
        manager: "ShapeManager",
        ids: Set[int],
        dx: float,
        dy: float,
        parent: QUndoCommand | None = None,
    ):
        super().__init__(f"Move ({dx:.1f}, {dy:.1f})", parent)
        self._manager = manager
        self._ids = ids
        self._dx = dx
        self._dy = dy
        self._old_positions: dict[int, tuple[float, float, float, float]] = {}

    def _get_position(self, shape: BaseShape) -> tuple:
        """Получить координаты фигуры в зависимости от типа."""
        shape_type = shape.shape_type
        if shape_type.value == "point":
            return (shape.x, shape.y, 0.0, 0.0)
        elif shape_type.value == "line":
            return (shape.x1, shape.y1, shape.x2, shape.y2)
        elif shape_type.value in ("rectangle", "ellipse"):
            return (shape.x, shape.y, shape.width, shape.height)
        elif shape_type in (
            __import__("shapes.polygon_shape", fromlist=["PolygonShape"]).PolygonShape,
            __import__("shapes.polyline_shape", fromlist=["PolylineShape"]),
        ):
            return tuple((v.x(), v.y()) for v in shape.vertices)
        return ()

    def undo(self) -> None:
        # Возвращаем старые позиции
        for sid, pos in self._old_positions.items():
            if sid in self._manager._shapes:
                shape = self._manager._shapes[sid]
                shape_type = shape.shape_type
                if shape_type.value == "point":
                    shape.x = pos[0]
                    shape.y = pos[1]
                elif shape_type.value == "line":
                    shape.x1 = pos[0]
                    shape.y1 = pos[1]
                    shape.x2 = pos[2]
                    shape.y2 = pos[3]
                elif shape_type.value in ("rectangle", "ellipse"):
                    shape.x = pos[0]
                    shape.y = pos[1]
                    shape.width = pos[2]
                    shape.height = pos[3]
                elif hasattr(shape, "move"):
                    shape.move(-self._dx, -self._dy)

        self._manager.shapes_changed.emit()

    def redo(self) -> None:
        # Сохраняем текущие позиции и применяем смещение
        self._old_positions = {}
        for sid in self._ids:
            if sid in self._manager._shapes:
                shape = self._manager._shapes[sid]
                self._old_positions[sid] = self._get_position(shape)
                shape.move(self._dx, self._dy)

        self._manager.shapes_changed.emit()


class ChangePropertiesCommand(QUndoCommand):
    """Команда изменения свойств фигур."""

    def __init__(
        self,
        manager: "ShapeManager",
        ids: Set[int],
        new_props: dict,
        parent: QUndoCommand | None = None,
    ):
        super().__init__("Change properties", parent)
        self._manager = manager
        self._ids = ids
        self._new_props = new_props
        self._old_props: dict[int, dict] = {}

    def undo(self) -> None:
        # Возвращаем старые свойства
        for sid, props in self._old_props.items():
            if sid in self._manager._shapes:
                shape = self._manager._shapes[sid]
                if "pen_color" in props:
                    shape.pen_color = props["pen_color"]
                if "pen_width" in props:
                    shape.pen_width = props["pen_width"]
                if "brush_color" in props:
                    shape.brush_color = props["brush_color"]
                if "rotation" in props:
                    shape.rotation = props["rotation"]

        self._manager.shapes_changed.emit()

    def redo(self) -> None:
        # Сохраняем старые свойства и применяем новые
        self._old_props = {}
        for sid in self._ids:
            if sid in self._manager._shapes:
                shape = self._manager._shapes[sid]
                self._old_props[sid] = {
                    "pen_color": shape.pen_color,
                    "pen_width": shape.pen_width,
                    "brush_color": shape.brush_color,
                    "rotation": shape.rotation,
                }
                if "pen_color" in self._new_props:
                    shape.pen_color = self._new_props["pen_color"]
                if "pen_width" in self._new_props:
                    shape.pen_width = self._new_props["pen_width"]
                if "brush_color" in self._new_props:
                    shape.brush_color = self._new_props["brush_color"]
                if "rotation" in self._new_props:
                    shape.rotation = self._new_props["rotation"]

        self._manager.shapes_changed.emit()
