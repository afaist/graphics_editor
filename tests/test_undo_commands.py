"""Тесты для UndoCommands — redo/undo для всех команд."""

import pytest
from PySide6.QtGui import QFont

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
from shapes.text_shape import TextShape


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
    def test_redo_saves_state(self, manager, rectangle):
        """redo() сохраняет текущее состояние фигур."""
        # Фигуры уже перемещены до создания команды
        rectangle.move(10, 20)
        old_pos = rectangle.get_position_data()
        cmd = MoveShapesCommand(
            manager, {rectangle.id}, 10, 20, old_positions={rectangle.id: old_pos}
        )
        cmd.redo()
        assert rectangle.x == 10
        assert rectangle.y == 20

    def test_undo_restores_positions(self, manager, rectangle):
        """undo() возвращает фигуры в старое состояние."""
        old_pos = rectangle.get_position_data()  # x=0, y=0
        rectangle.move(10, 20)
        cmd = MoveShapesCommand(
            manager, {rectangle.id}, 10, 20, old_positions={rectangle.id: old_pos}
        )
        cmd.redo()
        assert rectangle.x == 10
        cmd.undo()
        assert rectangle.x == 0
        assert rectangle.y == 0

    def test_undo_redo_cycle(self, manager, rectangle):
        """После undo→redo фигура должна вернуться в перемещённое состояние."""
        old_pos = rectangle.get_position_data()  # x=0, y=0
        rectangle.move(10, 20)
        cmd = MoveShapesCommand(
            manager, {rectangle.id}, 10, 20, old_positions={rectangle.id: old_pos}
        )
        cmd.redo()
        assert rectangle.x == 10
        assert rectangle.y == 20

        cmd.undo()
        assert rectangle.x == 0
        assert rectangle.y == 0

        cmd.redo()
        assert rectangle.x == 10
        assert rectangle.y == 20

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


# ------------------------------------------------------------------
# TextShape font properties undo/redo
# ------------------------------------------------------------------


@pytest.fixture
def text_shape(manager):
    t = TextShape(0, 0, text="Hello World", font_size=14, font_family="Segoe UI")
    manager.add_shape(t)
    return t


class TestTextFontPropertiesUndoRedo:
    """Тесты для undo/redo свойств шрифта текстовых фигур."""

    def test_redo_changes_font_size(self, manager, text_shape):
        cmd = ChangePropertiesCommand(manager, {text_shape.id}, {"font_size": 24})
        cmd.redo()
        assert text_shape.font_size == 24

    def test_undo_restores_font_size(self, manager, text_shape):
        original_size = text_shape.font_size  # 14
        cmd = ChangePropertiesCommand(manager, {text_shape.id}, {"font_size": 30})
        cmd.redo()
        assert text_shape.font_size == 30
        cmd.undo()
        assert text_shape.font_size == original_size

    def test_redo_changes_font_family(self, manager, text_shape):
        cmd = ChangePropertiesCommand(manager, {text_shape.id}, {"font_family": "Arial"})
        cmd.redo()
        assert text_shape.font_family == "Arial"

    def test_undo_restores_font_family(self, manager, text_shape):
        original_family = text_shape.font_family  # "Segoe UI"
        cmd = ChangePropertiesCommand(manager, {text_shape.id}, {"font_family": "Courier New"})
        cmd.redo()
        assert text_shape.font_family == "Courier New"
        cmd.undo()
        assert text_shape.font_family == original_family

    def test_redo_changes_font_weight(self, manager, text_shape):
        cmd = ChangePropertiesCommand(manager, {text_shape.id}, {"font_weight": QFont.Weight.Bold})
        cmd.redo()
        assert text_shape.font_weight == QFont.Weight.Bold

    def test_undo_restores_font_weight(self, manager, text_shape):
        original_weight = text_shape.font_weight  # QFont.Weight.Normal
        cmd = ChangePropertiesCommand(manager, {text_shape.id}, {"font_weight": QFont.Weight.Bold})
        cmd.redo()
        assert text_shape.font_weight == QFont.Weight.Bold
        cmd.undo()
        assert text_shape.font_weight == original_weight

    def test_redo_changes_italic(self, manager, text_shape):
        cmd = ChangePropertiesCommand(manager, {text_shape.id}, {"italic": True})
        cmd.redo()
        assert text_shape.italic is True

    def test_undo_restores_italic(self, manager, text_shape):
        original_italic = text_shape.italic  # False
        cmd = ChangePropertiesCommand(manager, {text_shape.id}, {"italic": True})
        cmd.redo()
        assert text_shape.italic is True
        cmd.undo()
        assert text_shape.italic == original_italic

    def test_redo_changes_underline(self, manager, text_shape):
        cmd = ChangePropertiesCommand(manager, {text_shape.id}, {"underline": True})
        cmd.redo()
        assert text_shape.underline is True

    def test_undo_restores_underline(self, manager, text_shape):
        original_underline = text_shape.underline  # False
        cmd = ChangePropertiesCommand(manager, {text_shape.id}, {"underline": True})
        cmd.redo()
        assert text_shape.underline is True
        cmd.undo()
        assert text_shape.underline == original_underline

    def test_redo_changes_strikethrough(self, manager, text_shape):
        cmd = ChangePropertiesCommand(manager, {text_shape.id}, {"strikethrough": True})
        cmd.redo()
        assert text_shape.strikethrough is True

    def test_undo_restores_strikethrough(self, manager, text_shape):
        original_strike = text_shape.strikethrough  # False
        cmd = ChangePropertiesCommand(manager, {text_shape.id}, {"strikethrough": True})
        cmd.redo()
        assert text_shape.strikethrough is True
        cmd.undo()
        assert text_shape.strikethrough == original_strike

    def test_redo_changes_multiple_font_properties(self, manager, text_shape):
        """Проверка что несколько свойств шрифта меняются одновременно."""
        cmd = ChangePropertiesCommand(
            manager,
            {text_shape.id},
            {
                "font_family": "Arial",
                "font_size": 20,
                "font_weight": QFont.Weight.Bold,
                "italic": True,
            },
        )
        cmd.redo()
        assert text_shape.font_family == "Arial"
        assert text_shape.font_size == 20
        assert text_shape.font_weight == QFont.Weight.Bold
        assert text_shape.italic is True

    def test_undo_restores_multiple_font_properties(self, manager, text_shape):
        """Проверка что undo восстанавливает все свойства шрифта."""
        original_family = text_shape.font_family
        original_size = text_shape.font_size
        original_weight = text_shape.font_weight
        original_italic = text_shape.italic

        cmd = ChangePropertiesCommand(
            manager,
            {text_shape.id},
            {
                "font_family": "Verdana",
                "font_size": 30,
                "font_weight": QFont.Weight.Black,
                "italic": True,
            },
        )
        cmd.redo()
        assert text_shape.font_family == "Verdana"
        assert text_shape.font_size == 30
        assert text_shape.font_weight == QFont.Weight.Black
        assert text_shape.italic is True

        cmd.undo()
        assert text_shape.font_family == original_family
        assert text_shape.font_size == original_size
        assert text_shape.font_weight == original_weight
        assert text_shape.italic == original_italic

    def test_redo_changes_all_font_properties(self, manager, text_shape):
        """Проверка что все свойства шрифта (включая underline и strikethrough) меняются."""
        cmd = ChangePropertiesCommand(
            manager,
            {text_shape.id},
            {
                "font_family": "Georgia",
                "font_size": 24,
                "font_weight": QFont.Weight.DemiBold,
                "italic": True,
                "underline": True,
                "strikethrough": True,
            },
        )
        cmd.redo()
        assert text_shape.font_family == "Georgia"
        assert text_shape.font_size == 24
        assert text_shape.font_weight == QFont.Weight.DemiBold
        assert text_shape.italic is True
        assert text_shape.underline is True
        assert text_shape.strikethrough is True

    def test_undo_redo_all_font_properties(self, manager, text_shape):
        """Полный цикл undo/redo для всех свойств шрифта."""
        original_family = text_shape.font_family
        original_size = text_shape.font_size
        original_weight = text_shape.font_weight
        original_italic = text_shape.italic
        original_underline = text_shape.underline
        original_strike = text_shape.strikethrough

        cmd = ChangePropertiesCommand(
            manager,
            {text_shape.id},
            {
                "font_family": "Times New Roman",
                "font_size": 36,
                "font_weight": QFont.Weight.Bold,
                "italic": True,
                "underline": True,
                "strikethrough": True,
            },
        )
        # Redo
        cmd.redo()
        assert text_shape.font_family == "Times New Roman"
        assert text_shape.font_size == 36
        assert text_shape.font_weight == QFont.Weight.Bold
        assert text_shape.italic is True
        assert text_shape.underline is True
        assert text_shape.strikethrough is True

        # Undo
        cmd.undo()
        assert text_shape.font_family == original_family
        assert text_shape.font_size == original_size
        assert text_shape.font_weight == original_weight
        assert text_shape.italic == original_italic
        assert text_shape.underline == original_underline
        assert text_shape.strikethrough == original_strike

        # Redo again
        cmd.redo()
        assert text_shape.font_family == "Times New Roman"
        assert text_shape.font_size == 36
        assert text_shape.font_weight == QFont.Weight.Bold
        assert text_shape.italic is True
        assert text_shape.underline is True
        assert text_shape.strikethrough is True

    def test_undo_with_text_shape_and_rectangle(self, manager, text_shape):
        """Проверка что undo/redo работает корректно когда есть и текст и прямоугольник."""
        rect = RectangleShape(50, 50, 100, 50)
        manager.add_shape(rect)

        cmd = ChangePropertiesCommand(
            manager,
            {text_shape.id, rect.id},
            {"font_size": 20, "pen_width": 5.0},
        )
        cmd.redo()
        assert text_shape.font_size == 20
        assert rect.pen_width == 5.0

        cmd.undo()
        assert text_shape.font_size == 14
        assert rect.pen_width == 2.0

    def test_stack_undo_redo_font_properties(self, manager, text_shape):
        """Интеграционный тест с QUndoStack для свойств шрифта."""
        cmd1 = ChangePropertiesCommand(manager, {text_shape.id}, {"font_size": 18})
        manager.undo_stack.push(cmd1)
        assert text_shape.font_size == 18

        cmd2 = ChangePropertiesCommand(manager, {text_shape.id}, {"font_family": "Arial"})
        manager.undo_stack.push(cmd2)
        assert text_shape.font_family == "Arial"

        # Undo cmd2
        manager.undo_stack.undo()
        assert text_shape.font_family != "Arial"

        # Undo cmd1
        manager.undo_stack.undo()
        assert text_shape.font_size == 14

        # Redo cmd1
        manager.undo_stack.redo()
        assert text_shape.font_size == 18

        # Redo cmd2
        manager.undo_stack.redo()
        assert text_shape.font_family == "Arial"
