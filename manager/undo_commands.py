"""QUndoCommand-подклассы для операций с фигурами."""

from __future__ import annotations

from typing import List, Set, TYPE_CHECKING

from PySide6.QtGui import QUndoCommand

from shapes.registry import ShapeRegistry

# Импортируем конкретные классы для использования isinstance
if TYPE_CHECKING:
    from manager.shape_manager import ShapeManager
    from shapes.base_shape import BaseShape
    
from shapes.point_shape import PointShape
from shapes.line_shape import LineShape
from shapes.ellipse_shape import EllipseShape
from shapes.rectangle_shape import RectangleShape
from shapes.polygon_shape import PolygonShape


class AddShapeCommand(QUndoCommand):
    """Команда добавления фигуры."""

    def __init__(
        self,
        manager: "ShapeManager",
        shape: BaseShape,
        already_added: bool = False,
        parent: QUndoCommand | None = None,
    ):
        super().__init__(f"Add {shape.shape_type.value}", parent)
        self._manager = manager
        self._shape = shape
        self._already_added = already_added
        self._added_id: int | None = None

    def undo(self) -> None:
        if self._added_id is not None:
            self._manager._shapes.pop(self._added_id, None)
            self._manager._selected_ids.discard(self._added_id)

    def redo(self) -> None:
        shape = self._shape
        if shape.id < 0:
            shape.id = self._manager._next_id
            self._manager._next_id += 1

        if not self._already_added:
            self._manager._shapes[shape.id] = shape
            self._manager.shape_added.emit(shape)
            self._manager.shapes_changed.emit()
        else:
            self._manager._shapes[shape.id] = shape
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
        ShapeRegistry.register_all()
        shape = ShapeRegistry.create(data.get("type"), data) # type: ignore
        if shape is None:
            raise ValueError(f"Unknown shape type: {data.get('type')}")
        self._manager._shapes[shape.id] = shape
        return shape

    def undo(self) -> None:
        for d in self._removed_dicts:
            shape = self._import_shape(d)
        self._manager._selected_ids = set(s.id for s in self._removed_shapes)
        self._manager.shapes_changed.emit()

    def redo(self) -> None:
        ids_to_remove = set(self._ids)
        self._removed_shapes = [
            self._manager._shapes[i]
            for i in ids_to_remove
            if i in self._manager._shapes
        ]
        self._removed_dicts = [s.to_dict() for s in self._removed_shapes]

        for sid in ids_to_remove:
            if sid in self._manager._shapes:
                del self._manager._shapes[sid]
        self._manager._selected_ids -= ids_to_remove
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
        super().__init__("Move shapes", parent)
        self._manager = manager
        self._ids = ids
        self._dx = dx
        self._dy = dy
        self._old_positions: dict[int, dict] = {}

    def _record_position(self, shape: BaseShape) -> dict:
        """Записать координаты фигуры до перемещения.

        Использование isinstance вместо строковых проверок типа фигуры.
        """
        if isinstance(shape, PointShape):
            return {"x": shape._x, "y": shape._y}
        elif isinstance(shape, LineShape):
            return {"x1": shape._x1, "y1": shape._y1, "x2": shape._x2, "y2": shape._y2}
        elif isinstance(shape, (RectangleShape, EllipseShape)):
            return {"x": shape._x, "y": shape._y}
        elif isinstance(shape, PolygonShape):
            return {"vertices": [(v.x(), v.y()) for v in shape._vertices]}
        return {}

    def _restore_position(self, shape: BaseShape, pos: dict) -> None:
        """Восстановить координаты фигуры.

        Использование isinstance вместо строковых проверок типа фигуры.
        """
        if isinstance(shape, PointShape):
            shape._x = pos["x"]
            shape._y = pos["y"]
        elif isinstance(shape, LineShape):
            shape._x1 = pos["x1"]
            shape._y1 = pos["y1"]
            shape._x2 = pos["x2"]
            shape._y2 = pos["y2"]
        elif isinstance(shape, (RectangleShape, EllipseShape)):
            shape._x = pos["x"]
            shape._y = pos["y"]
        elif isinstance(shape, PolygonShape):
            for i, (vx, vy) in enumerate(pos["vertices"]):
                if i < len(shape._vertices):
                    shape._vertices[i].setX(vx)
                    shape._vertices[i].setY(vy)

    def undo(self) -> None:
        for sid, pos in self._old_positions.items():
            if sid in self._manager._shapes:
                self._restore_position(self._manager._shapes[sid], pos)
        self._manager.shapes_changed.emit()

    def redo(self) -> None:
        self._old_positions = {}
        for sid in self._ids:
            if sid in self._manager._shapes:
                shape = self._manager._shapes[sid]
                self._old_positions[sid] = self._record_position(shape)
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
                # Координаты и размеры для прямоугольных фигур
                if "_x" in props and hasattr(shape, "_x"):
                    shape._x = props["_x"]
                if "_y" in props and hasattr(shape, "_y"):
                    shape._y = props["_y"]
                if "_width" in props and hasattr(shape, "_width"):
                    shape._width = props["_width"]
                if "_height" in props and hasattr(shape, "_height"):
                    shape._height = props["_height"]

        self._manager.shapes_changed.emit()

    def redo(self) -> None:
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
                # Сохраняем координаты и размеры, если они есть
                if hasattr(shape, "_x"):
                    self._old_props[sid]["_x"] = shape._x
                if hasattr(shape, "_y"):
                    self._old_props[sid]["_y"] = shape._y
                if hasattr(shape, "_width"):
                    self._old_props[sid]["_width"] = shape._width
                if hasattr(shape, "_height"):
                    self._old_props[sid]["_height"] = shape._height

                if "pen_color" in self._new_props:
                    shape.pen_color = self._new_props["pen_color"]
                if "pen_width" in self._new_props:
                    shape.pen_width = self._new_props["pen_width"]
                if "brush_color" in self._new_props:
                    shape.brush_color = self._new_props["brush_color"]
                if "rotation" in self._new_props:
                    shape.rotation = self._new_props["rotation"]
                # Применяем координаты и размеры
                if "_x" in self._new_props and hasattr(shape, "_x"):
                    shape._x = self._new_props["_x"]
                if "_y" in self._new_props and hasattr(shape, "_y"):
                    shape._y = self._new_props["_y"]
                if "_width" in self._new_props and hasattr(shape, "_width"):
                    shape._width = self._new_props["_width"]
                if "_height" in self._new_props and hasattr(shape, "_height"):
                    shape._height = self._new_props["_height"]

        self._manager.shapes_changed.emit()


class DuplicateShapesCommand(QUndoCommand):
    """Команда дублирования фигур."""

    def __init__(
        self,
        manager: "ShapeManager",
        ids: Set[int],
        offset: "tuple[float, float]" = (20, 20),
        parent: QUndoCommand | None = None,
    ):
        super().__init__("Duplicate shapes", parent)
        self._manager = manager
        self._ids = ids
        self._offset = offset
        self._new_ids: Set[int] = set()
        self._old_dicts: List[dict] = []

    def undo(self) -> None:
        for nid in self._new_ids:
            if nid in self._manager._shapes:
                del self._manager._shapes[nid]
        self._manager._selected_ids -= self._new_ids
        self._manager.shapes_changed.emit()

    def redo(self) -> None:
        for sid in self._ids:
            if sid in self._manager._shapes:
                old_shape = self._manager._shapes[sid]
                self._old_dicts.append(old_shape.to_dict())
                new_shape = old_shape.copy()
                new_shape.offset(self._offset[0], self._offset[1])
                self._manager.add_shape(new_shape)
                self._new_ids.add(new_shape.id)
        self._manager.shapes_changed.emit()


class GroupCommand(QUndoCommand):
    """Команда группировки фигур."""

    def __init__(
        self,
        manager: "ShapeManager",
        ids: Set[int],
        group_id: int,
        parent: QUndoCommand | None = None,
    ):
        super().__init__("Group shapes", parent)
        self._manager = manager
        self._ids = ids
        self._group_id = group_id
        self._old_group_ids: dict[int, int | None] = {}

    def undo(self) -> None:
        for sid, old_gid in self._old_group_ids.items():
            if sid in self._manager._shapes:
                self._manager._shapes[sid].group_id = old_gid
        self._manager.shapes_changed.emit()

    def redo(self) -> None:
        for sid in self._ids:
            if sid in self._manager._shapes:
                shape = self._manager._shapes[sid]
                self._old_group_ids[sid] = shape.group_id
                shape.group_id = self._group_id
        self._manager.shapes_changed.emit()


class UngroupCommand(QUndoCommand):
    """Команда разgrupпировки фигур."""

    def __init__(
        self,
        manager: "ShapeManager",
        ids: Set[int],
        parent: QUndoCommand | None = None,
    ):
        super().__init__("Ungroup shapes", parent)
        self._manager = manager
        self._ids = ids
        self._old_group_ids: dict[int, int | None] = {}

    def undo(self) -> None:
        for sid, old_gid in self._old_group_ids.items():
            if sid in self._manager._shapes:
                self._manager._shapes[sid].group_id = old_gid
        self._manager.shapes_changed.emit()

    def redo(self) -> None:
        for sid in self._ids:
            if sid in self._manager._shapes:
                shape = self._manager._shapes[sid]
                self._old_group_ids[sid] = shape.group_id
                shape.group_id = None
        self._manager.shapes_changed.emit()
