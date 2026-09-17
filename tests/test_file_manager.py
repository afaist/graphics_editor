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


class TestAngleRoundtrip:
    """Тесты roundtrip для фигуры «Угол»."""

    def test_save_load_angle(self, temp_gproj_file):
        from shapes.angle_shape import AngleShape

        sm1 = ShapeManager()
        a = AngleShape(vertex=(50, 100), side_a=150, side_b=100, angle_deg=90,
                       pen_color=(255, 128, 64), pen_width=3.0)
        sm1.add_shape(a)

        FileManager.save_project(sm1, temp_gproj_file)

        sm2 = ShapeManager()
        FileManager.load_json(sm2, temp_gproj_file)

        assert sm2.count == 1
        loaded = sm2.shapes[0]
        assert type(loaded).__name__ == "AngleShape"
        assert abs(loaded.vertex.x() - 50) < 0.01
        assert abs(loaded.vertex.y() - 100) < 0.01
        assert loaded.side_a == 150
        assert loaded.side_b == 100
        assert loaded.angle_deg == 90
        assert loaded.pen_color.red() == 255
        assert loaded.pen_color.green() == 128
        assert loaded.pen_color.blue() == 64
        assert loaded.pen_width == 3.0

    def test_load_angle_mixed_project(self, temp_gproj_file):
        from shapes.angle_shape import AngleShape
        from shapes.point_shape import PointShape
        from shapes.arc_shape import ArcShape

        sm1 = ShapeManager()
        sm1.add_shape(PointShape(10, 20, radius=3))
        sm1.add_shape(AngleShape(vertex=(0, 0), side_a=100, side_b=80, angle_deg=45))
        sm1.add_shape(ArcShape(cx=50, cy=50, radius=30, start_angle=0, end_angle=180))

        FileManager.save_project(sm1, temp_gproj_file)

        sm2 = ShapeManager()
        FileManager.load_json(sm2, temp_gproj_file)

        assert sm2.count == 3
        types = [type(s).__name__ for s in sm2.shapes]
        assert "PointShape" in types
        assert "AngleShape" in types
        assert "ArcShape" in types


class TestArcRoundtrip:
    """Тесты roundtrip для фигуры «Дуга»."""

    def test_save_load_arc(self, temp_gproj_file):
        from shapes.arc_shape import ArcShape

        sm1 = ShapeManager()
        arc = ArcShape(cx=100, cy=200, radius=50, start_angle=30, end_angle=150,
                       pen_color=(0, 128, 255), pen_width=2.5)
        sm1.add_shape(arc)

        FileManager.save_project(sm1, temp_gproj_file)

        sm2 = ShapeManager()
        FileManager.load_json(sm2, temp_gproj_file)

        assert sm2.count == 1
        loaded = sm2.shapes[0]
        assert type(loaded).__name__ == "ArcShape"
        assert loaded.cx == 100
        assert loaded.cy == 200
        assert loaded.radius == 50
        assert loaded.start_angle == 30
        assert loaded.end_angle == 150
        assert loaded.pen_color.red() == 0
        assert loaded.pen_color.green() == 128
        assert loaded.pen_color.blue() == 255
        assert loaded.pen_width == 2.5

    def test_arc_validation_on_load(self, temp_gproj_file):
        """Невалидная дуга должна быть пропущена при загрузке."""
        sm = ShapeManager()
        with open(temp_gproj_file, "w") as f:
            json.dump({
                "version": "1.0",
                "shapes": [
                    {
                        "type": "arc",
                        "cx": 100,
                        "cy": 100,
                        # radius отсутствует — невалидно
                        "start_angle": 0,
                        "end_angle": 90,
                        "pen_color": [0, 0, 0],
                        "pen_width": 2.0,
                    }
                ],
            }, f)

        FileManager.load_json(sm, temp_gproj_file)
        assert sm.count == 0

    def test_arc_negative_radius_skipped(self, temp_gproj_file):
        """Дуга с отрицательным радиусом должна быть пропущена."""
        sm = ShapeManager()
        with open(temp_gproj_file, "w") as f:
            json.dump({
                "version": "1.0",
                "shapes": [
                    {
                        "type": "arc",
                        "cx": 100,
                        "cy": 100,
                        "radius": -50,
                        "start_angle": 0,
                        "end_angle": 90,
                        "pen_color": [0, 0, 0],
                        "pen_width": 2.0,
                    }
                ],
            }, f)

        FileManager.load_json(sm, temp_gproj_file)
        assert sm.count == 0


class TestAngleValidationOnLoad:
    """Тесты валидации угла при загрузке файла."""

    def test_angle_missing_vertex_skipped(self, temp_gproj_file):
        sm = ShapeManager()
        with open(temp_gproj_file, "w") as f:
            json.dump({
                "version": "1.0",
                "shapes": [
                    {
                        "type": "angle",
                        # vertex отсутствует
                        "side_a": 100,
                        "side_b": 80,
                        "angle_deg": 90,
                        "pen_color": [0, 0, 0],
                        "pen_width": 2.0,
                    }
                ],
            }, f)

        FileManager.load_json(sm, temp_gproj_file)
        assert sm.count == 0

    def test_angle_negative_side_skipped(self, temp_gproj_file):
        sm = ShapeManager()
        with open(temp_gproj_file, "w") as f:
            json.dump({
                "version": "1.0",
                "shapes": [
                    {
                        "type": "angle",
                        "vertex": {"x": 0, "y": 0},
                        "side_a": -100,
                        "side_b": 80,
                        "angle_deg": 90,
                        "pen_color": [0, 0, 0],
                        "pen_width": 2.0,
                    }
                ],
            }, f)

        FileManager.load_json(sm, temp_gproj_file)
        assert sm.count == 0

    def test_angle_angle_deg_out_of_range_skipped(self, temp_gproj_file):
        sm = ShapeManager()
        with open(temp_gproj_file, "w") as f:
            json.dump({
                "version": "1.0",
                "shapes": [
                    {
                        "type": "angle",
                        "vertex": {"x": 0, "y": 0},
                        "side_a": 100,
                        "side_b": 80,
                        "angle_deg": 400,
                        "pen_color": [0, 0, 0],
                        "pen_width": 2.0,
                    }
                ],
            }, f)

        FileManager.load_json(sm, temp_gproj_file)
        assert sm.count == 0

    def test_angle_valid_vertex_string_coords_skipped(self, temp_gproj_file):
        sm = ShapeManager()
        with open(temp_gproj_file, "w") as f:
            json.dump({
                "version": "1.0",
                "shapes": [
                    {
                        "type": "angle",
                        "vertex": {"x": "not_a_number", "y": 0},
                        "side_a": 100,
                        "side_b": 80,
                        "angle_deg": 90,
                        "pen_color": [0, 0, 0],
                        "pen_width": 2.0,
                    }
                ],
            }, f)

        FileManager.load_json(sm, temp_gproj_file)
        assert sm.count == 0


class TestMixedProjectRoundtrip:
    """Тесты roundtrip для проекта с разными типами фигур."""

    def test_save_load_all_shapes(self, temp_gproj_file):
        from shapes.angle_shape import AngleShape
        from shapes.arc_shape import ArcShape
        from shapes.line_shape import LineShape
        from shapes.base_shape import ShapeType

        sm1 = ShapeManager()
        sm1.add_shape(PointShape(10, 20, radius=5.0, pen_color=(255, 0, 0)))
        sm1.add_shape(RectangleShape(0, 0, 100, 50, pen_color=(0, 255, 0)))
        sm1.add_shape(LineShape(0, 0, 100, 100, shape_type=ShapeType.LINE))
        sm1.add_shape(ArcShape(cx=50, cy=50, radius=30, start_angle=0, end_angle=180))
        sm1.add_shape(AngleShape(vertex=(0, 0), side_a=120, side_b=80, angle_deg=60))

        FileManager.save_project(sm1, temp_gproj_file)

        sm2 = ShapeManager()
        FileManager.load_json(sm2, temp_gproj_file)

        assert sm2.count == 5
        types = {type(s).__name__ for s in sm2.shapes}
        assert types == {"PointShape", "RectangleShape", "LineShape", "ArcShape", "AngleShape"}

    def test_load_project_with_invalid_shape_skipped(self, temp_gproj_file):
        """Невалидная фигура пропускается, остальные загружаются."""
        sm = ShapeManager()
        with open(temp_gproj_file, "w") as f:
            json.dump({
                "version": "1.0",
                "shapes": [
                    {
                        "id": 0,
                        "type": "point",
                        "x": 10, "y": 20,
                        "pen_color": [0, 0, 0], "pen_width": 2.0,
                    },
                    {
                        "id": 1,
                        "type": "angle",
                        "vertex": {"x": 0, "y": 0},
                        "side_a": -100,  # невалидно
                        "side_b": 80,
                        "angle_deg": 90,
                        "pen_color": [0, 0, 0],
                        "pen_width": 2.0,
                    },
                    {
                        "id": 2,
                        "type": "rectangle",
                        "x": 0, "y": 0, "width": 100, "height": 50,
                        "pen_color": [255, 0, 0], "pen_width": 2.0,
                    },
                ],
            }, f)

        sm = ShapeManager()
        FileManager.load_json(sm, temp_gproj_file)
        # Точка и прямоугольник загружены, угол пропущен
        assert sm.count == 2
        types = {type(s).__name__ for s in sm.shapes}
        assert types == {"PointShape", "RectangleShape"}
