"""Тесты для UndoCommands — redo/undo для всех команд."""

import pytest

from manager.shape_manager import ShapeManager
from manager.undo_commands import (
    AddShapeCommand,
    ChangePropertiesCommand,
    DuplicateShapesCommand,
    GroupCommand,
    MoveShapesCommand,
    RemoveShapesCommand,
    UngroupCommand,
)
from shapes.rectangle_shape import RectangleShape


@pytest.fixture
def manager():
    sm = ShapeManager()
    return sm


@pytest.fixture
def rectangle(manager):
    r = RectangleShape(0, 0, 100, 50)
    manager.add_shape(r)
    return r


# ------------------------------------------------------------------
# AddShapeCommand
# ------------------------------------------------------------------


class TestAddShapeCommand:
    def test_redo_adds_shape(self, manager):
        r = RectangleShape(10, 20, 80, 40)
        cmd = AddShapeCommand(manager, r)
        cmd.redo()
        assert manager.count == 1
        assert manager.shapes[0].x == 10

    def test_undo_removes_shape(self, manager):
        r = RectangleShape(10, 20, 80, 40)
        cmd = AddShapeCommand(manager, r)
        cmd.redo()
        assert manager.count == 1
        cmd.undo()
        assert manager.count == 0

    def test_redo_with_already_added(self, manager):
        r = RectangleShape(10, 20, 80, 40)
        manager.add_shape(r)
        # add_shape уже пушит AddShapeCommand с already_added=True
        assert manager.count == 1


# ------------------------------------------------------------------
# RemoveShapesCommand
# ------------------------------------------------------------------


class TestRemoveShapesCommand:
    def test_redo_removes_shapes(self, manager, rectangle):
        cmd = RemoveShapesCommand(manager, {rectangle.id})
        cmd.redo()
        assert manager.count == 0

    def test_undo_restores_shapes(self, manager, rectangle):
        cmd = RemoveShapesCommand(manager, {rectangle.id})
        cmd.redo()
        assert manager.count == 0
        cmd.undo()
        assert manager.count == 1
        assert manager.shapes[0].x == 0

    def test_remove_nonexistent(self, manager):
        cmd = RemoveShapesCommand(manager, {999})
        cmd.redo()  # не должно вызвать ошибку
        assert manager.count == 0


# ------------------------------------------------------------------
# MoveShapesCommand
# ------------------------------------------------------------------


class TestMoveShapesCommand:
    def test_redo_moves_shapes(self, manager, rectangle):
        cmd = MoveShapesCommand(manager, {rectangle.id}, 10, 20)
        cmd.redo()
        assert rectangle.x == 10
        assert rectangle.y == 20

    def test_undo_restores_positions(self, manager, rectangle):
        cmd = MoveShapesCommand(manager, {rectangle.id}, 10, 20)
        cmd.redo()
        assert rectangle.x == 10
        cmd.undo()
        assert rectangle.x == 0

    def test_move_nonexistent(self, manager):
        cmd = MoveShapesCommand(manager, {999}, 10, 20)
        cmd.redo()  # не должно вызвать ошибку


# ------------------------------------------------------------------
# ChangePropertiesCommand
# ------------------------------------------------------------------


class TestChangePropertiesCommand:
    def test_redo_changes_properties(self, manager, rectangle):
        cmd = ChangePropertiesCommand(
            manager, {rectangle.id}, {"pen_color": (255, 0, 0), "pen_width": 5.0}
        )
        cmd.redo()
        assert rectangle.pen_color.red() == 255
        assert rectangle.pen_width == 5.0

    def test_undo_restores_properties(self, manager, rectangle):
        original_color = (
            rectangle.pen_color.red(),
            rectangle.pen_color.green(),
            rectangle.pen_color.blue(),
        )
        cmd = ChangePropertiesCommand(manager, {rectangle.id}, {"pen_color": (255, 0, 0)})
        cmd.redo()
        assert rectangle.pen_color.red() == 255
        cmd.undo()
        assert rectangle.pen_color.red() == original_color[0]

    def test_change_rotation(self, manager, rectangle):
        cmd = ChangePropertiesCommand(manager, {rectangle.id}, {"rotation": 90.0})
        cmd.redo()
        assert rectangle.rotation == 90.0
        cmd.undo()
        assert rectangle.rotation == 0.0


# ------------------------------------------------------------------
# DuplicateShapesCommand
# ------------------------------------------------------------------


class TestDuplicateShapesCommand:
    def test_redo_duplicates(self, manager, rectangle):
        cmd = DuplicateShapesCommand(manager, {rectangle.id}, (20, 20))
        cmd.redo()
        assert manager.count == 2

    def test_undo_removes_duplicates(self, manager, rectangle):
        cmd = DuplicateShapesCommand(manager, {rectangle.id}, (20, 20))
        cmd.redo()
        assert manager.count == 2
        cmd.undo()
        assert manager.count == 1

    def test_duplicate_offset(self, manager, rectangle):
        cmd = DuplicateShapesCommand(manager, {rectangle.id}, (50, 30))
        cmd.redo()
        shapes = manager.shapes
        assert len(shapes) == 2
        # Одна из фигур должна быть смещена
        shifted = [s for s in shapes if s.x != 0 or s.y != 0]
        assert len(shifted) == 1


# ------------------------------------------------------------------
# GroupCommand
# ------------------------------------------------------------------


class TestGroupCommand:
    def test_redo_groups(self, manager, rectangle):
        cmd = GroupCommand(manager, {rectangle.id}, 42)
        cmd.redo()
        assert rectangle.group_id == 42

    def test_undo_ungroups(self, manager, rectangle):
        cmd = GroupCommand(manager, {rectangle.id}, 42)
        cmd.redo()
        assert rectangle.group_id == 42
        cmd.undo()
        assert rectangle.group_id is None

    def test_redo_groups_preserves_old_group_id(self, manager, rectangle):
        rectangle.group_id = 10
        cmd = GroupCommand(manager, {rectangle.id}, 42)
        cmd.redo()
        assert rectangle.group_id == 42
        cmd.undo()
        assert rectangle.group_id == 10


# ------------------------------------------------------------------
# UngroupCommand
# ------------------------------------------------------------------


class TestUngroupCommand:
    def test_redo_ungroups(self, manager, rectangle):
        rectangle.group_id = 42
        cmd = UngroupCommand(manager, {rectangle.id})
        cmd.redo()
        assert rectangle.group_id is None

    def test_undo_restores_group(self, manager, rectangle):
        rectangle.group_id = 42
        cmd = UngroupCommand(manager, {rectangle.id})
        cmd.redo()
        assert rectangle.group_id is None
        cmd.undo()
        assert rectangle.group_id == 42


# ------------------------------------------------------------------
# Интеграционные тесты с QUndoStack
# ------------------------------------------------------------------


class TestUndoStackIntegration:
    def test_stack_undo_redo_add(self, manager):
        r = RectangleShape(10, 20, 80, 40)
        cmd = AddShapeCommand(manager, r)
        manager.undo_stack.push(cmd)
        assert manager.count == 1
        manager.undo_stack.undo()
        assert manager.count == 0
        manager.undo_stack.redo()
        assert manager.count == 1

    def test_stack_multiple_operations(self, manager):
        r1 = RectangleShape(0, 0, 100, 50)
        r2 = RectangleShape(100, 0, 100, 50)
        cmd1 = AddShapeCommand(manager, r1)
        cmd2 = AddShapeCommand(manager, r2)
        manager.undo_stack.push(cmd1)
        manager.undo_stack.push(cmd2)
        assert manager.count == 2
        manager.undo_stack.undo()  # undo cmd2
        assert manager.count == 1
        manager.undo_stack.undo()  # undo cmd1
        assert manager.count == 0
        manager.undo_stack.redo()  # redo cmd1
        assert manager.count == 1
        manager.undo_stack.redo()  # redo cmd2
        assert manager.count == 2

    def test_stack_cannot_undo_empty(self, manager):
        manager.undo_stack.undo()  # не должно вызвать ошибку

    def test_stack_cannot_redo_at_beginning(self, manager):
        manager.undo_stack.redo()  # не должно вызвать ошибку
