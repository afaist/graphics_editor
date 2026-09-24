"""E2E-тесты: сценарии использования графического редактора.

Тесты проверяют полный жизненный цикл: создание → выделение → перемещение →
изменение свойств → сохранение → загрузка.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from PySide6.QtCore import QPointF, QRectF

from fileio.file_manager import FileManager
from manager.shape_manager import ShapeManager
from shapes.base_shape import ShapeType
from shapes.line_shape import LineShape
from shapes.point_shape import PointShape
from shapes.rectangle_shape import RectangleShape

# ======================================================================
# Сценарий 1: Создать фигуру → выделить → переместить → удалить
# ======================================================================


class TestCreateSelectMoveDelete:
    """Полный цикл: создать → выделить → переместить → удалить."""

    def test_create_point(self):
        """Создание точки."""
        manager = ShapeManager()
        shape = PointShape(10.0, 20.0)
        manager.add_shape(shape)
        manager.select_shape(shape.id)

        assert shape.id in manager.selected_ids
        assert len(manager.shapes) == 1
        assert manager.count == 1

    def test_create_rectangle(self):
        """Создание прямоугольника."""
        manager = ShapeManager()
        shape = RectangleShape(x=0, y=0, width=100, height=50)
        manager.add_shape(shape)

        assert len(manager.shapes) == 1
        assert shape.width == 100
        assert shape.height == 50

    def test_select_by_rect(self):
        """Выделение по прямоугольнику."""
        manager = ShapeManager()
        s1 = PointShape(10, 10)
        s2 = PointShape(50, 50)
        manager.add_shape(s1)
        manager.add_shape(s2)

        manager.select_none()
        rect = QRectF(0, 0, 100, 100)
        manager.select_by_rect(rect)

        assert s1.id in manager.selected_ids
        assert s2.id in manager.selected_ids

    def test_move_selected(self):
        """Перемещение выделенных фигур."""
        manager = ShapeManager()
        shape = PointShape(0, 0)
        manager.add_shape(shape)
        manager.select_shape(shape.id)

        manager.move_selected(10, 20)

        assert shape._x == 10
        assert shape._y == 20

    def test_delete_selected(self):
        """Удаление выделенных фигур."""
        manager = ShapeManager()
        shape = PointShape(0, 0)
        manager.add_shape(shape)
        manager.select_shape(shape.id)

        manager.delete_selected()

        assert shape.id not in {s.id for s in manager.shapes}
        assert len(manager.shapes) == 0
        assert len(manager.selected_ids) == 0

    def test_full_cycle(self):
        """Полный цикл: создать → выделить → переместить → удалить."""
        manager = ShapeManager()

        # 1. Создать
        rect = RectangleShape(x=0, y=0, width=100, height=50)
        manager.add_shape(rect)
        manager.select_shape(rect.id)
        assert manager.count == 1

        # 2. Выделить (уже сделано выше)
        assert rect.id in manager.selected_ids

        # 3. Переместить
        manager.move_selected(25, 30)
        assert rect._x == 25
        assert rect._y == 30

        # 4. Удалить
        manager.delete_selected()
        assert manager.count == 0
        assert len(manager.selected_ids) == 0


# ======================================================================
# Сценарий 2: Copy → Paste
# ======================================================================


class TestCopyPaste:
    """Тесты копирования и вставки."""

    def test_copy_and_paste(self):
        """Копирование и вставка фигуры."""
        manager = ShapeManager()

        # Создать исходную фигуру
        rect = RectangleShape(x=0, y=0, width=100, height=50)
        manager.add_shape(rect)
        manager.select_shape(rect.id)
        original_id = rect.id

        # Копировать
        manager.copy_selected()

        # Вставить
        manager.paste_from_clipboard()

        # Должно быть 2 фигуры
        assert manager.count == 2

        # ID разные — найти вставленную фигуру
        ids = {s.id for s in manager.shapes}
        assert len(ids) == 2
        # Вставленная фигура имеет новый ID
        new_id = ids - {original_id}
        assert len(new_id) == 1

    def test_paste_with_offset(self):
        """Вставка со смещением."""
        manager = ShapeManager()
        rect = RectangleShape(x=0, y=0, width=100, height=50)
        manager.add_shape(rect)
        manager.select_shape(rect.id)
        original_x = rect._x

        manager.copy_selected()
        manager.paste_from_clipboard(QPointF(50, 50))

        # Найти вставленную фигуру (с новым ID)
        new_shapes = [s for s in manager.shapes if s.id != rect.id]
        assert len(new_shapes) == 1
        assert new_shapes[0]._x == original_x + 50  # type: ignore[attr-defined]


# ======================================================================
# Сценарий 3: Save → Load (сериализация)
# ======================================================================


class TestSaveLoad:
    """Тесты сериализации и десериализации."""

    def test_save_and_load_project(self):
        """Сохранение и загрузка проекта."""
        manager = ShapeManager()
        file_manager = FileManager()

        # Создать фигуры
        rect = RectangleShape(x=10, y=20, width=100, height=50)
        manager.add_shape(rect)
        line = LineShape(0, 0, 200, 100)
        manager.add_shape(line)

        # Сохранить
        with tempfile.NamedTemporaryFile(suffix=".gproj", delete=False) as f:
            path = f.name

        try:
            success = file_manager.save_project(manager, path)
            assert success

            # Загрузить в новый менеджер
            new_manager = ShapeManager()
            loaded = file_manager.load_project(new_manager, path)
            assert loaded

            # Проверить фигуры
            assert new_manager.count == 2

            # Проверить координаты прямоугольника
            loaded_rect = next(s for s in manager.shapes if s.shape_type == ShapeType.RECTANGLE)
            assert loaded_rect._x == 10  # type: ignore[attr-defined]
            assert loaded_rect._y == 20  # type: ignore[attr-defined]
            assert loaded_rect._width == 100  # type: ignore[attr-defined]
            assert loaded_rect._height == 50  # type: ignore[attr-defined]

            # Проверить линию
            loaded_line = next(s for s in manager.shapes if s.shape_type == ShapeType.LINE)
            assert loaded_line._x1 == 0  # type: ignore[attr-defined]
            assert loaded_line._y1 == 0  # type: ignore[attr-defined]
            assert loaded_line._x2 == 200  # type: ignore[attr-defined]
            assert loaded_line._y2 == 100  # type: ignore[attr-defined]
        finally:
            Path(path).unlink(missing_ok=True)

    def test_save_load_empty_project(self):
        """Сохранение и загрузка пустого проекта."""
        manager = ShapeManager()
        file_manager = FileManager()

        with tempfile.NamedTemporaryFile(suffix=".gproj", delete=False) as f:
            path = f.name

        try:
            success = file_manager.save_project(manager, path)
            assert success

            new_manager = ShapeManager()
            loaded = file_manager.load_project(new_manager, path)
            assert loaded
            assert new_manager.count == 0
        finally:
            Path(path).unlink(missing_ok=True)

    def test_save_load_point(self):
        """Сохранение и загрузка точки."""
        manager = ShapeManager()
        file_manager = FileManager()

        point = PointShape(42, 99)
        manager.add_shape(point)

        with tempfile.NamedTemporaryFile(suffix=".gproj", delete=False) as f:
            path = f.name

        try:
            file_manager.save_project(manager, path)

            new_manager = ShapeManager()
            file_manager.load_project(new_manager, path)

            assert new_manager.count == 1
            loaded_point = next(s for s in manager.shapes if s.shape_type == ShapeType.POINT)
            assert loaded_point._x == 42  # type: ignore[attr-defined]
            assert loaded_point._y == 99  # type: ignore[attr-defined]
        finally:
            Path(path).unlink(missing_ok=True)


# ======================================================================
# Сценарий 4: Undo/Redo
# ======================================================================


class TestUndoRedo:
    """Тесты undo/redo."""

    def test_undo_add_shape(self):
        """Undo добавления фигуры."""
        manager = ShapeManager()
        stack = manager.undo_stack

        rect = RectangleShape(x=0, y=0, width=100, height=50)
        manager.add_shape(rect)

        # Должна быть одна команда в стеке
        assert stack.canUndo()

        # Undo
        stack.undo()
        assert manager.count == 0

    def test_redo_add_shape(self):
        """Redo добавления фигуры."""
        manager = ShapeManager()
        stack = manager.undo_stack

        rect = RectangleShape(x=0, y=0, width=100, height=50)
        manager.add_shape(rect)
        stack.undo()

        # Redo
        stack.redo()
        assert manager.count == 1

    def test_multiple_undo_redo(self):
        """Несколько операций undo/redo."""
        manager = ShapeManager()
        stack = manager.undo_stack

        # Добавить 3 фигуры
        for i in range(3):
            rect = RectangleShape(x=i * 10, y=0, width=50, height=50)
            manager.add_shape(rect)

        assert manager.count == 3

        # Undo дважды
        stack.undo()
        stack.undo()
        assert manager.count == 1

        # Redo один раз
        stack.redo()
        assert manager.count == 2
