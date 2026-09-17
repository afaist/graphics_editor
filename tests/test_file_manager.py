"""Тесты для FileManager — save/load JSON, roundtrip, утилиты."""

import json
import os
import tempfile
import pytest
from fileio.file_manager import FileManager
from manager.shape_manager import ShapeManager
from shapes.rectangle_shape import RectangleShape
from shapes.point_shape import PointShape


class TestFileManagerCreation:
    def test_initial_state(self):
        fm = FileManager()
        assert fm.has_current_file is False
        assert fm.current_filepath is None


class TestEnsureGprojExtension:
    def test_adds_extension(self):
        result = FileManager._ensure_gproj_extension("project")
        assert result == "project.gproj"

    def test_no_duplicate_extension(self):
        result = FileManager._ensure_gproj_extension("project.gproj")
        assert result == "project.gproj"

    def test_case_insensitive(self):
        # Метод проверяет расширение case-insensitive, но не меняет регистр имени файла
        result = FileManager._ensure_gproj_extension("project.GPROJ")
        # Уже имеет .GPROJ → расширение не добавляется, регистр сохраняется
        assert result == "project.GPROJ"

    def test_case_insensitive_lower(self):
        result = FileManager._ensure_gproj_extension("project.Gproj")
        assert result == "project.Gproj"

    def test_with_path(self):
        result = FileManager._ensure_gproj_extension("/path/to/project")
        assert result == "/path/to/project.gproj"


class TestSaveJson:
    def test_save_json_empty(self, temp_gproj_file):
        sm = ShapeManager()
        result = FileManager.save_json(sm, temp_gproj_file)
        assert result is True
        with open(temp_gproj_file) as f:
            data = json.load(f)
        assert data["version"] == "1.0"
        assert data["shapes"] == []

    def test_save_json_with_shapes(self, temp_gproj_file):
        sm = ShapeManager()
        r = RectangleShape(10, 20, 100, 50)
        r.id = 0
        sm._shapes[0] = r
        sm._next_id = 1
        result = FileManager.save_json(sm, temp_gproj_file)
        assert result is True
        with open(temp_gproj_file) as f:
            data = json.load(f)
        assert len(data["shapes"]) == 1
        assert data["shapes"][0]["x"] == 10

    def test_save_json_invalid_path(self):
        sm = ShapeManager()
        result = FileManager.save_json(sm, "/nonexistent/dir/file.gproj")
        assert result is False


class TestLoadJson:
    def test_load_json_empty(self, temp_gproj_file):
        with open(temp_gproj_file, "w") as f:
            json.dump({"version": "1.0", "shapes": []}, f)
        sm = ShapeManager()
        result = FileManager.load_json(sm, temp_gproj_file)
        assert result is True
        assert sm.count == 0

    def test_load_json_with_shapes(self, temp_gproj_file):
        with open(temp_gproj_file, "w") as f:
            json.dump({
                "version": "1.0",
                "shapes": [
                    {
                        "id": 0,
                        "type": "rectangle",
                        "pen_color": [255, 0, 0],
                        "pen_width": 2.0,
                        "brush_color": [0, 255, 0],
                        "rotation": 0.0,
                        "group_id": None,
                        "selected": False,
                        "x": 10,
                        "y": 20,
                        "width": 100,
                        "height": 50,
                    }
                ],
            }, f)
        sm = ShapeManager()
        result = FileManager.load_json(sm, temp_gproj_file)
        assert result is True
        assert sm.count == 1
        assert sm.shapes[0].x == 10
        assert sm.shapes[0].width == 100

    def test_load_json_invalid_file(self, temp_gproj_file):
        with open(temp_gproj_file, "w") as f:
            f.write("not json")
        sm = ShapeManager()
        result = FileManager.load_json(sm, temp_gproj_file)
        assert result is False

    def test_load_json_missing_shapes(self, temp_gproj_file):
        with open(temp_gproj_file, "w") as f:
            json.dump({"version": "1.0"}, f)
        sm = ShapeManager()
        result = FileManager.load_json(sm, temp_gproj_file)
        assert result is False

    def test_load_json_clears_existing(self, temp_gproj_file):
        sm = ShapeManager()
        sm.add_shape(RectangleShape(0, 0, 100, 50))
        assert sm.count == 1

        with open(temp_gproj_file, "w") as f:
            json.dump({"version": "1.0", "shapes": []}, f)
        FileManager.load_json(sm, temp_gproj_file)
        assert sm.count == 0


class TestSaveProject:
    def test_save_project(self, temp_gproj_file):
        sm = ShapeManager()
        sm.add_shape(RectangleShape(0, 0, 100, 50))
        result = FileManager.save_project(sm, temp_gproj_file)
        assert result is True
        assert os.path.exists(temp_gproj_file)

    def test_save_project_adds_extension(self, temp_json_file):
        sm = ShapeManager()
        result = FileManager.save_project(sm, temp_json_file)
        assert result is True
        # Файл должен быть сохранён с расширением .gproj
        expected = temp_json_file.rsplit(".", 1)[0] + ".gproj"
        assert os.path.exists(expected)
        os.unlink(expected)


class TestSaveProjectAs:
    def test_save_project_as(self, temp_gproj_file):
        fm = FileManager()
        sm = ShapeManager()
        sm.add_shape(RectangleShape(0, 0, 100, 50))
        result = fm.save_project_as(temp_gproj_file, sm)
        assert result is True
        assert fm.current_filepath == temp_gproj_file

    def test_save_project_as_invalid_path(self):
        fm = FileManager()
        sm = ShapeManager()
        result = fm.save_project_as("/nonexistent/file.gproj", sm)
        assert result is False


class TestIsProjectFile:
    def test_valid_project_file(self, temp_gproj_file):
        with open(temp_gproj_file, "w") as f:
            json.dump({"version": "1.0", "shapes": []}, f)
        assert FileManager.is_project_file(temp_gproj_file) is True

    def test_invalid_project_file(self, temp_gproj_file):
        with open(temp_gproj_file, "w") as f:
            json.dump({"not_valid": True}, f)
        assert FileManager.is_project_file(temp_gproj_file) is False

    def test_not_gproj_extension(self):
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"test")
            f.flush()
            path = f.name
        try:
            assert FileManager.is_project_file(path) is False
        finally:
            os.unlink(path)

    def test_invalid_json(self, temp_gproj_file):
        with open(temp_gproj_file, "w") as f:
            f.write("not json")
        assert FileManager.is_project_file(temp_gproj_file) is False


class TestGetFileInfo:
    def test_get_file_info(self, temp_gproj_file):
        with open(temp_gproj_file, "w") as f:
            json.dump({
                "version": "1.0",
                "shapes": [
                    {"type": "rectangle", "x": 0, "y": 0, "width": 100, "height": 50,
                     "pen_color": [0, 0, 0], "pen_width": 2.0},
                    {"type": "point", "x": 10, "y": 20, "pen_color": [0, 0, 0], "pen_width": 2.0},
                ],
            }, f)
        info = FileManager.get_file_info(temp_gproj_file)
        assert info is not None
        assert info["version"] == "1.0"
        assert info["shape_count"] == 2
        assert info["file_size"] > 0

    def test_get_file_info_invalid(self):
        info = FileManager.get_file_info("/nonexistent/file.gproj")
        assert info is None


class TestGetSupportedFormats:
    def test_returns_dict(self):
        formats = FileManager.get_supported_formats()
        assert isinstance(formats, dict)

    def test_has_gproj(self):
        formats = FileManager.get_supported_formats()
        assert ".gproj" in formats

    def test_has_png(self):
        formats = FileManager.get_supported_formats()
        assert ".png" in formats


class TestRoundtrip:
    def test_save_load_roundtrip(self, temp_gproj_file):
        sm1 = ShapeManager()
        r1 = RectangleShape(10, 20, 100, 50, pen_color=(255, 128, 64))
        r1._rotation = 45.0
        sm1.add_shape(r1)
        p1 = PointShape(50, 50, radius=5.0)
        sm1.add_shape(p1)

        FileManager.save_project(sm1, temp_gproj_file)

        sm2 = ShapeManager()
        FileManager.load_json(sm2, temp_gproj_file)

        assert sm2.count == 2
        shapes_by_type = {}
        for s in sm2.shapes:
            shapes_by_type[type(s).__name__] = s

        assert "RectangleShape" in shapes_by_type
        assert "PointShape" in shapes_by_type
        assert shapes_by_type["RectangleShape"].x == 10
        assert shapes_by_type["PointShape"].radius == 5.0


class TestExportSettings:
    def test_save_settings(self, temp_json_file):
        settings = {"key": "value", "number": 42}
        result = FileManager.save_settings(settings, temp_json_file)
        assert result is True
        with open(temp_json_file) as f:
            loaded = json.load(f)
        assert loaded == settings

    def test_load_settings(self, temp_json_file):
        with open(temp_json_file, "w") as f:
            json.dump({"key": "value"}, f)
        result = FileManager.load_settings(temp_json_file)
        assert result == {"key": "value"}

    def test_load_settings_nonexistent(self):
        result = FileManager.load_settings("/nonexistent/file.json")
        assert result is None
