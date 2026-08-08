"""ShapeManager — управление коллекцией фигур, выделение, группировка, undo/redo."""

from __future__ import annotations

import copy
from typing import Dict, List, Optional, Set, TYPE_CHECKING, Union

from PySide6.QtCore import QPointF, Signal
from PySide6.QtCore import QObject
from PySide6.QtGui import QUndoStack

from shapes.base_shape import BaseShape

if TYPE_CHECKING:
    from shapes.base_shape import BaseShape


class ShapeManager(QObject):
    """Управление набором фигур на холсте."""

    # Сигналы
    shapes_changed = Signal()
    selection_changed = Signal()
    shape_added = Signal(object)
    shape_removed = Signal(object)

    def __init__(self):
        super().__init__()
        self._shapes: Dict[int, BaseShape] = {}
        self._selected_ids: Set[int] = set()
        # Стандартный QUndoStack
        self._undo_stack = QUndoStack(self)
        self._clipboard: Optional[List[dict]] = None
        self._next_id = 0

    # ------------------------------------------------------------------
    # Свойства
    # ------------------------------------------------------------------

    @property
    def shapes(self) -> List[BaseShape]:
        return list(self._shapes.values())

    @property
    def selected_shapes(self) -> List[BaseShape]:
        return [s for s in self._shapes.values() if s.id in self._selected_ids]

    @property
    def selected_ids(self) -> Set[int]:
        return set(self._selected_ids)

    @property
    def undo_stack(self) -> QUndoStack:
        return self._undo_stack

    @undo_stack.setter
    def undo_stack(self, stack: QUndoStack) -> None:
        if hasattr(stack, 'push'):
            self._undo_stack = stack
        else:
            raise ValueError("Stack must have 'push' method")

    @property
    def count(self) -> int:
        return len(self._shapes)

    # ------------------------------------------------------------------
    # Добавление / удаление
    # ------------------------------------------------------------------

    def add_shape(self, shape: BaseShape) -> None:
        shape.id = self._next_id
        self._next_id += 1
        self._shapes[shape.id] = shape
        self.shape_added.emit(shape)
        self.shapes_changed.emit()

    def remove_shapes(self, ids: Set[int]) -> None:
        removed = [self._shapes.pop(i) for i in ids if i in self._shapes]
        self._selected_ids -= ids
        self.shape_removed.emit(removed)
        self.shapes_changed.emit()

    def remove_all(self) -> None:
        self._shapes.clear()
        self._selected_ids.clear()
        self.shapes_changed.emit()
        self.selection_changed.emit()

    # ------------------------------------------------------------------
    # Выделение
    # ------------------------------------------------------------------

    def select_shape(self, shape_id: int, additive: bool = False) -> None:
        if additive:
            self._selected_ids.add(shape_id)
        else:
            self._selected_ids = {shape_id}
        self.selection_changed.emit()

    def select_none(self) -> None:
        for s in self._shapes.values():
            s.selected = False
        self._selected_ids.clear()
        self.selection_changed.emit()

    def select_all(self) -> None:
        self._selected_ids = set(self._shapes.keys())
        for s in self._shapes.values():
            s.selected = True
        self.selection_changed.emit()

    def toggle_selection(self, shape_id: int) -> None:
        if shape_id in self._selected_ids:
            self._selected_ids.discard(shape_id)
            self._shapes[shape_id].selected = False
        else:
            self._selected_ids.add(shape_id)
            self._shapes[shape_id].selected = True
        self.selection_changed.emit()

    def select_by_rect(self, rect) -> Set[int]:
        """Выделить все фигуры, пересекающиеся с rect (QRectF)."""
        new_selection: Set[int] = set()
        for sid, shape in self._shapes.items():
            if shape.bounding_rect().intersects(rect):
                new_selection.add(sid)
                shape.selected = True
        self._selected_ids = new_selection
        self.selection_changed.emit()
        return new_selection

    # ------------------------------------------------------------------
    # Поиск фигуры под точкой
    # ------------------------------------------------------------------

    def hit_test(self, point: QPointF, tolerance: float = 5.0) -> Optional[BaseShape]:
        """Найти фигуру под точкой (спереди назад — последние сверху)."""
        for shape in reversed(self._shapes.values()):
            if shape.contains_point(point):
                return shape
        return None

    # ------------------------------------------------------------------
    # Перемещение выделенных
    # ------------------------------------------------------------------

    def move_selected(self, dx: float, dy: float) -> None:
        if not self._selected_ids:
            return
        for sid in self._selected_ids:
            if sid in self._shapes:
                self._shapes[sid].move(dx, dy)
        self.shapes_changed.emit()

    # ------------------------------------------------------------------
    # Удаление (Delete)
    # ------------------------------------------------------------------

    def delete_selected(self) -> None:
        if not self._selected_ids:
            return
        ids = set(self._selected_ids)
        self.remove_shapes(ids)

    def cut_selected(self) -> None:
        """Вырезать выделенные фигуры (копирует в буфер и удаляет)."""
        self.copy_selected()
        self.delete_selected()

    # ------------------------------------------------------------------
    # Копирование / вставка
    # ------------------------------------------------------------------

    def copy_selected(self) -> None:
        self._clipboard = [s.to_dict() for s in self.selected_shapes]

    def paste_from_clipboard(
        self, offset: QPointF = QPointF(20, 20)
    ) -> List[BaseShape]:
        if not self._clipboard:
            return []
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
        pasted: List[BaseShape] = []
        for data in self._clipboard:
            shape_type = data.get("type")
            if not shape_type or not isinstance(shape_type, str):
                continue
            cls = factory.get(shape_type)
            if cls is None:
                continue
            shape = cls(data)
            # смещаем
            if shape_type == "point":
                shape._x += offset.x()
                shape._y += offset.y()
            elif shape_type == "line":
                shape._x1 += offset.x()
                shape._y1 += offset.y()
                shape._x2 += offset.x()
                shape._y2 += offset.y()
            elif shape_type in ("rectangle", "ellipse"):
                shape._x += offset.x()
                shape._y += offset.y()
            elif shape_type in ("polygon", "polyline"):
                for v in shape._vertices:
                    v.setX(v.x() + offset.x())
                    v.setY(v.y() + offset.y())
            self.add_shape(shape)
            pasted.append(shape)
        return pasted

    # ------------------------------------------------------------------
    # Группировка (метка group)
    # ------------------------------------------------------------------

    def group_selected(self, group_id: int) -> None:
        for sid in self._selected_ids:
            if sid in self._shapes:
                self._shapes[sid]._group_id = group_id

    def ungroup_selected(self) -> None:
        for sid in self._selected_ids:
            if sid in self._shapes:
                self._shapes[sid]._group_id = None

    # ------------------------------------------------------------------
    # Undo-обёртки — используют стандартные QUndoCommand
    # ------------------------------------------------------------------

    def add_shape_undo(self, shape: BaseShape) -> None:
        """Добавить фигуру с возможностью undo через QUndoStack."""
        from manager.undo_commands import AddShapeCommand

        cmd = AddShapeCommand(self, shape)
        self._undo_stack.push(cmd)

    def delete_selected_undo(self) -> None:
        """Удалить выделенные с undo через QUndoStack."""
        from manager.undo_commands import RemoveShapesCommand

        ids = set(self._selected_ids)
        if not ids:
            return
        cmd = RemoveShapesCommand(self, ids)
        self._undo_stack.push(cmd)

    def move_selected_undo(self, dx: float, dy: float) -> None:
        """Переместить выделенные с undo через QUndoStack."""
        from manager.undo_commands import MoveShapesCommand

        if not self._selected_ids:
            return
        cmd = MoveShapesCommand(self, set(self._selected_ids), dx, dy)
        self._undo_stack.push(cmd)

    def change_properties_undo(self, new_props: dict) -> None:
        """Изменить свойства выделенных с undo через QUndoStack."""
        from manager.undo_commands import ChangePropertiesCommand

        if not self._selected_ids:
            return
        cmd = ChangePropertiesCommand(self, set(self._selected_ids), new_props)
        self._undo_stack.push(cmd)

    # ------------------------------------------------------------------
    # Свойства
    # ------------------------------------------------------------------

    def get_selected_properties(self) -> Optional[dict]:
        if not self._selected_ids:
            return None
        # берём свойства первой выделенной фигуры
        sid = next(iter(self._selected_ids))
        if sid not in self._shapes:
            return None
        s = self._shapes[sid]
        return {
            "pen_color": (s.pen_color.red(), s.pen_color.green(), s.pen_color.blue()),
            "pen_width": s.pen_width,
            "brush_color": (
                (s.brush_color.red(), s.brush_color.green(), s.brush_color.blue())
                if s.brush_color
                else None
            ),
            "rotation": s.rotation,
        }

    def set_selected_properties(self, props: dict) -> None:
        """Изменить свойства (без undo)."""
        for sid in self._selected_ids:
            if sid in self._shapes:
                s = self._shapes[sid]
                if "pen_color" in props:
                    s.pen_color = props["pen_color"]
                if "pen_width" in props:
                    s.pen_width = props["pen_width"]
                if "brush_color" in props:
                    s.brush_color = props["brush_color"]
                if "rotation" in props:
                    s.rotation = props["rotation"]
        self.shapes_changed.emit()
