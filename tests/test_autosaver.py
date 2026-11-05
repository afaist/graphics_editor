"""Тесты для Autosaver: schedule_save, _do_save, has_autosave, load_autosave, remove_autosave."""

import json
import os

from PySide6.QtCore import QObject

from manager.autosaver import AutoSaver


class MockFileManager:
    """Mock FileManager для тестов."""

    def __init__(self):
        self.current_filepath = None


class MockManager:
    """Mock ShapeManager для тестов."""

    def __init__(self):
        self.shapes = []
        self.undo_stack = MockUndoStack()

    def remove_all(self):
        self.shapes.clear()


class MockUndoStack:
    """Mock QUndoStack для тестов."""

    def __init__(self):
        self._clean = False

    def setClean(self):
        self._clean = True

    def isClean(self):
        return self._clean


class MockMainWindow(QObject):
    """Mock MainWindow для тестов."""

    def __init__(self, tmpdir):
        super().__init__()
        self._file_manager = MockFileManager()
        self._manager = MockManager()
        self._tmpdir = tmpdir
        self._file_manager.current_filepath = os.path.join(tmpdir, "test.gproj")


class TestAutoSaver:
    """Тесты класса AutoSaver."""

    def test_autosave_path_with_filepath(self, tmp_path):
        mw = MockMainWindow(str(tmp_path))
        autosaver = AutoSaver(mw)
        path = autosaver.autosave_path
        assert path.endswith(AutoSaver.AUTOSAVE_FILENAME)
        assert str(tmp_path) in path

    def test_autosave_path_without_filepath(self, tmp_path):
        mw = MockMainWindow(str(tmp_path))
        mw._file_manager.current_filepath = None
        autosaver = AutoSaver(mw)
        path = autosaver.autosave_path
        # Когда filepath=None, используется _get_app_dir()
        assert path.endswith(AutoSaver.AUTOSAVE_FILENAME)

    def test_schedule_save_marks_dirty(self, tmp_path):
        mw = MockMainWindow(str(tmp_path))
        autosaver = AutoSaver(mw)
        autosaver.schedule_save()
        # _dirty должен быть True
        assert autosaver._dirty is True

    def test_has_autosave_false_when_no_file(self, tmp_path):
        mw = MockMainWindow(str(tmp_path))
        autosaver = AutoSaver(mw)
        assert autosaver.has_autosave() is False

    def test_has_autosave_true_when_file_exists(self, tmp_path):
        mw = MockMainWindow(str(tmp_path))
        autosaver = AutoSaver(mw)
        autosave_file = autosaver.autosave_path
        # Создаём файл
        with open(autosave_file, "w") as f:
            f.write("{}")
        assert autosaver.has_autosave() is True

    def test_remove_autosave(self, tmp_path):
        mw = MockMainWindow(str(tmp_path))
        autosaver = AutoSaver(mw)
        autosave_file = autosaver.autosave_path
        with open(autosave_file, "w") as f:
            f.write("{}")
        assert os.path.isfile(autosave_file)
        autosaver.remove_autosave()
        assert not os.path.isfile(autosave_file)

    def test_remove_autosave_no_file(self, tmp_path):
        mw = MockMainWindow(str(tmp_path))
        autosaver = AutoSaver(mw)
        # Не должно вызвать ошибку
        autosaver.remove_autosave()

    def test_load_autosave_no_file(self, tmp_path):
        mw = MockMainWindow(str(tmp_path))
        autosaver = AutoSaver(mw)
        result = autosaver.load_autosave(mw._manager)
        assert result is False

    def test_load_autosave_valid_file(self, tmp_path):
        mw = MockMainWindow(str(tmp_path))
        autosaver = AutoSaver(mw)
        autosave_file = autosaver.autosave_path
        data = {"shapes": []}
        with open(autosave_file, "w") as f:
            json.dump(data, f)
        result = autosaver.load_autosave(mw._manager)
        assert result is True
        assert mw._manager.undo_stack.isClean()

    def test_load_autosave_invalid_json(self, tmp_path):
        mw = MockMainWindow(str(tmp_path))
        autosaver = AutoSaver(mw)
        autosave_file = autosaver.autosave_path
        with open(autosave_file, "w") as f:
            f.write("not valid json {{{")
        result = autosaver.load_autosave(mw._manager)
        assert result is False

    def test_get_app_dir(self):
        # Статический метод должен возвращать строку
        app_dir = AutoSaver._get_app_dir()
        assert isinstance(app_dir, str)
        assert len(app_dir) > 0

    def test_autosave_path_uses_correct_filename(self, tmp_path):
        mw = MockMainWindow(str(tmp_path))
        autosaver = AutoSaver(mw)
        assert AutoSaver.AUTOSAVE_FILENAME == ".project.autosave.gproj"
        assert autosaver.autosave_path.endswith(AutoSaver.AUTOSAVE_FILENAME)

    def test_autosave_interval(self):
        assert AutoSaver.AUTOSAVE_INTERVAL_MS == 60000

    def test_start_and_stop_timer(self, tmp_path):
        mw = MockMainWindow(str(tmp_path))
        autosaver = AutoSaver(mw)
        autosaver.start()
        assert autosaver._timer.isActive()
        autosaver.stop()
        assert not autosaver._timer.isActive()
