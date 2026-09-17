"""Тесты для Settings — дефолтные значения, to_dict/from_dict, save/load."""

import pytest

from settings.settings import Settings


class TestSettingsDefaults:
    def test_grid_visible(self):
        s = Settings()
        assert s.grid_visible is True

    def test_grid_spacing(self):
        s = Settings()
        assert s.grid_spacing == 20

    def test_grid_minor_spacing(self):
        s = Settings()
        assert s.grid_minor_spacing == 5

    def test_grid_color_minor(self):
        s = Settings()
        assert s.grid_color_minor == "#E8E8E8"

    def test_grid_color_major(self):
        s = Settings()
        assert s.grid_color_major == "#CCCCCC"

    def test_canvas_background(self):
        s = Settings()
        assert s.canvas_background == "#FFFFFF"

    def test_selection_color(self):
        s = Settings()
        assert s.selection_color == "#0078FF"

    def test_snap_to_grid(self):
        s = Settings()
        assert s.snap_to_grid is False

    def test_snap_tolerance(self):
        s = Settings()
        assert s.snap_tolerance == 5.0

    def test_default_pen_width(self):
        s = Settings()
        assert s.default_pen_width == 2.0

    def test_default_pen_color(self):
        s = Settings()
        assert s.default_pen_color == (0, 0, 0)

    def test_default_brush_color(self):
        s = Settings()
        assert s.default_brush_color is None


class TestSettingsToDict:
    def test_to_dict_contains_all_keys(self):
        s = Settings()
        d = s.to_dict()
        expected_keys = [
            "grid_visible",
            "grid_spacing",
            "grid_minor_spacing",
            "grid_color_minor",
            "grid_color_major",
            "canvas_background",
            "selection_color",
            "snap_to_grid",
            "snap_tolerance",
            "default_pen_width",
            "default_pen_color",
            "default_brush_color",
        ]
        for key in expected_keys:
            assert key in d

    def test_to_dict_values_match(self):
        s = Settings()
        d = s.to_dict()
        assert d["grid_spacing"] == 20
        assert d["snap_to_grid"] is False
        assert d["default_pen_width"] == 2.0


class TestSettingsFromDict:
    def test_from_dict_restores_values(self):
        data = {
            "grid_visible": False,
            "grid_spacing": 30,
            "snap_to_grid": True,
            "snap_tolerance": 10.0,
            "default_pen_color": (255, 0, 0),
        }
        s = Settings.from_dict(data)
        assert s.grid_visible is False
        assert s.grid_spacing == 30
        assert s.snap_to_grid is True
        assert s.snap_tolerance == 10.0
        assert s.default_pen_color == (255, 0, 0)

    def test_from_dict_ignores_unknown_keys(self):
        data = {
            "grid_spacing": 40,
            "unknown_key": "ignored",
        }
        s = Settings.from_dict(data)
        assert s.grid_spacing == 40
        assert not hasattr(s, "unknown_key")

    def test_from_dict_empty(self):
        s = Settings.from_dict({})
        assert s.grid_spacing == 20  # дефолт


class TestSettingsSaveLoad:
    def test_save_and_load(self, temp_json_file):
        s = Settings()
        s.grid_spacing = 50
        s.snap_to_grid = True
        s.save(temp_json_file)

        s2 = Settings()
        s2.load(temp_json_file)
        assert s2.grid_spacing == 50
        assert s2.snap_to_grid is True

    def test_load_nonexistent_file(self, temp_json_file):
        s = Settings()
        s.load(temp_json_file)  # файл не существует — не должно вызвать ошибку
        assert s.grid_spacing == 20  # дефолт

    def test_save_load_roundtrip(self, temp_json_file):
        s = Settings()
        s.grid_spacing = 100
        s.grid_minor_spacing = 25
        s.canvas_background = "#000000"
        s.selection_color = "#FF0000"
        s.snap_tolerance = 15.0
        s.default_pen_width = 5.0
        s.default_pen_color = (255, 255, 255)
        s.default_brush_color = (128, 128, 128)

        s.save(temp_json_file)

        s2 = Settings()
        s2.load(temp_json_file)
        assert s2.grid_spacing == 100
        assert s2.grid_minor_spacing == 25
        assert s2.canvas_background == "#000000"
        assert s2.selection_color == "#FF0000"
        assert s2.snap_tolerance == 15.0
        assert s2.default_pen_width == 5.0
        assert s2.default_pen_color == [255, 255, 255]
        assert s2.default_brush_color == [128, 128, 128]

    def test_save_invalid_path(self):
        s = Settings()
        with pytest.raises(RuntimeError):
            s.save("/nonexistent/directory/settings.json")

    def test_load_invalid_json(self, temp_json_file):
        with open(temp_json_file, "w") as f:
            f.write("not valid json {{{")
        s = Settings()
        s.load(temp_json_file)  # должно вывести предупреждение, но не упасть
        assert s.grid_spacing == 20  # дефолт
