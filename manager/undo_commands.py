"""QUndoCommand-подклассы для операций с фигурами."""

from __future__ import annotations

from typing import List, Set, TYPE_CHECKING

from PySide6.QtGui import QUndoCommand

if TYPE_CHECKING:
    from shapes.base_shape import BaseShape
    from manager.shape_manager import ShapeManager


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
        # Удаляем фигуру из менеджера.
        # НЕ вызываем shapes_changed.emit() — это делает remove_shapes() извне.
        if self._added_id is not None:
            self._manager._shapes.pop(self._added_id, None)
            self._manager._selected_ids.discard(self._added_id)

    def redo(self) -> None:
        shape = self._shape
        # Присваиваем ID если ещё не присвоен
        if shape.id < 0:
            shape.id = self._manager._next_id
            self._manager._next_id += 1

        if not self._already_added:
            # Фигура ещё не в _shapes (случай add_shape_undo или загрузки из файла).
            # Добавляем и вызываем emit.
            self._manager._shapes[shape.id] = shape
            self._manager.shape_added.emit(shape)
            self._manager.shapes_changed.emit()
        else:
            # Фигура уже добавлена через add_shape(), emit уже вызван.
            # Просто убеждаемся, что фигура в _shapes.
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
        self._manager._selected_ids = set(s.id for s in self._removed_shapes)
        self._manager.shapes_changed.emit()

    def redo(self) -> None:
        # Сохраняем данные перед удалением
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
