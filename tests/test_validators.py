"""Тесты для валидаторов — file_size, project_data, shape_data."""

import os
import tempfile

import pytest

from fileio.validators import (
    MAX_FILE_SIZE,
    MAX_SHAPES,
    MAX_VERTICES,
    SHAPE_REQUIRED_FIELDS,
    ValidationError,
    validate_file_size,
    validate_project_data,
    validate_shape_data,
)


class TestConstants:
    def test_max_file_size(self):
        assert MAX_FILE_SIZE == 10 * 1024 * 1024

    def test_max_shapes(self):
        assert MAX_SHAPES == 10_000

    def test_max_vertices(self):
        assert MAX_VERTICES == 5_000

    def test_shape_required_fields_has_point(self):
        assert "point" in SHAPE_REQUIRED_FIELDS
        assert "x" in SHAPE_REQUIRED_FIELDS["point"]
        assert "y" in SHAPE_REQUIRED_FIELDS["point"]

    def test_shape_required_fields_has_rectangle(self):
        assert "rectangle" in SHAPE_REQUIRED_FIELDS
        assert "x" in SHAPE_REQUIRED_FIELDS["rectangle"]
        assert "width" in SHAPE_REQUIRED_FIELDS["rectangle"]


class TestValidateFileSize:
    def test_normal_file(self, temp_json_file):
        with open(temp_json_file, "w") as f:
            f.write("test")
        result = validate_file_size(temp_json_file)
        assert result is None

    def test_empty_file(self, temp_json_file):
        with open(temp_json_file, "w"):
            pass
        result = validate_file_size(temp_json_file)
        assert result is not None
        assert "пустой" in result.lower() or "empty" in result.lower()

    def test_nonexistent_file(self):
        result = validate_file_size("/nonexistent/file.txt")
        assert result is not None
        assert (
            "невозможно" in result.lower()
            or "cannot" in result.lower()
            or "error" in result.lower()
        )

    def test_large_file(self):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"x" * (MAX_FILE_SIZE + 1))
            f.flush()
            path = f.name

        try:
            result = validate_file_size(path)
            assert result is not None
            assert (
                "большой" in result.lower()
                or "big" in result.lower()
                or "too large" in result.lower()
            )
        finally:
            os.unlink(path)


class TestValidateProjectData:
    def test_valid_project_data(self):
        data = {"version": "1.0", "shapes": []}
        warnings = validate_project_data(data)
        assert warnings == []

    def test_missing_version(self):
        data = {"shapes": []}
        warnings = validate_project_data(data)
        assert len(warnings) > 0
        assert "version" in warnings[0].lower() or "version" in warnings[0]

    def test_version_not_string(self):
        data = {"version": 123, "shapes": []}
        warnings = validate_project_data(data)
        assert len(warnings) > 0

    def test_missing_shapes(self):
        data = {"version": "1.0"}
        with pytest.raises(ValidationError, match="shapes"):
            validate_project_data(data)

    def test_shapes_not_list(self):
        data = {"version": "1.0", "shapes": "not_a_list"}
        with pytest.raises(ValidationError, match="массивом"):
            validate_project_data(data)

    def test_too_many_shapes(self):
        data = {"version": "1.0", "shapes": [{} for _ in range(MAX_SHAPES + 1)]}
        with pytest.raises(ValidationError, match="Слишком много"):
            validate_project_data(data)

    def test_valid_project_with_shapes(self):
        data = {
            "version": "1.0",
            "shapes": [
                {"type": "point", "x": 0, "y": 0, "pen_color": [0, 0, 0], "pen_width": 2},
            ],
        }
        warnings = validate_project_data(data)
        assert warnings == []


class TestValidateShapeData:
    def test_valid_point(self):
        data = {"type": "point", "x": 10, "y": 20, "pen_color": [0, 0, 0], "pen_width": 2.0}
        result = validate_shape_data(data)
        assert result is None

    def test_missing_type(self):
        data = {"x": 10, "y": 20}
        result = validate_shape_data(data)
        assert result is not None
        assert "type" in result.lower() or "type" in result

    def test_unknown_type(self):
        data = {"type": "unknown_type"}
        result = validate_shape_data(data)
        assert result is not None
        assert "неизвестн" in result.lower() or "unknown" in result.lower()

    def test_missing_required_fields(self):
        data = {"type": "point", "x": 10}
        result = validate_shape_data(data)
        assert result is not None
        assert "отсутст" in result.lower() or "missing" in result.lower()

    def test_invalid_pen_color_not_list(self):
        data = {"type": "point", "x": 0, "y": 0, "pen_color": "red", "pen_width": 2.0}
        result = validate_shape_data(data)
        assert result is not None

    def test_invalid_pen_color_wrong_length(self):
        data = {"type": "point", "x": 0, "y": 0, "pen_color": [255, 0], "pen_width": 2.0}
        result = validate_shape_data(data)
        assert result is not None

    def test_invalid_pen_color_out_of_range(self):
        data = {"type": "point", "x": 0, "y": 0, "pen_color": [256, 0, 0], "pen_width": 2.0}
        result = validate_shape_data(data)
        assert result is not None

    def test_invalid_pen_width_too_small(self):
        data = {"type": "point", "x": 0, "y": 0, "pen_color": [0, 0, 0], "pen_width": 0.1}
        result = validate_shape_data(data)
        assert result is not None

    def test_valid_polygon(self):
        data = {
            "type": "polygon",
            "vertices": [{"x": 0, "y": 0}, {"x": 100, "y": 0}, {"x": 50, "y": 100}],
            "pen_color": [0, 0, 0],
            "pen_width": 2.0,
        }
        result = validate_shape_data(data)
        assert result is None

    def test_polygon_too_many_vertices(self):
        data = {
            "type": "polygon",
            "vertices": [{"x": 0, "y": 0} for _ in range(MAX_VERTICES + 1)],
            "pen_color": [0, 0, 0],
            "pen_width": 2.0,
        }
        result = validate_shape_data(data)
        assert result is not None
        assert "Слишком много" in result

    def test_polygon_too_few_vertices(self):
        data = {
            "type": "polygon",
            "vertices": [{"x": 0, "y": 0}],
            "pen_color": [0, 0, 0],
            "pen_width": 2.0,
        }
        result = validate_shape_data(data)
        assert result is not None
        assert "Минимум" in result

    def test_polygon_vertices_not_list(self):
        data = {
            "type": "polygon",
            "vertices": "not_a_list",
            "pen_color": [0, 0, 0],
            "pen_width": 2.0,
        }
        result = validate_shape_data(data)
        assert result is not None

    def test_polygon_vertex_missing_coords(self):
        data = {
            "type": "polygon",
            "vertices": [{"x": 0}, {"x": 100, "y": 0}],
            "pen_color": [0, 0, 0],
            "pen_width": 2.0,
        }
        result = validate_shape_data(data)
        assert result is not None

    def test_invalid_numeric_field(self):
        data = {
            "type": "point",
            "x": "not_a_number",
            "y": 0,
            "pen_color": [0, 0, 0],
            "pen_width": 2.0,
        }
        result = validate_shape_data(data)
        assert result is not None

    def test_nan_field(self):
        data = {
            "type": "point",
            "x": float("nan"),
            "y": 0,
            "pen_color": [0, 0, 0],
            "pen_width": 2.0,
        }
        result = validate_shape_data(data)
        assert result is not None
        assert "NaN" in result

    def test_valid_brush_color(self):
        data = {
            "type": "point",
            "x": 0,
            "y": 0,
            "pen_color": [0, 0, 0],
            "pen_width": 2.0,
            "brush_color": [255, 128, 0],
        }
        result = validate_shape_data(data)
        assert result is None

    def test_invalid_brush_color(self):
        data = {
            "type": "point",
            "x": 0,
            "y": 0,
            "pen_color": [0, 0, 0],
            "pen_width": 2.0,
            "brush_color": [256, 0, 0],
        }
        result = validate_shape_data(data)
        assert result is not None

    def test_null_brush_color_allowed(self):
        data = {
            "type": "point",
            "x": 0,
            "y": 0,
            "pen_color": [0, 0, 0],
            "pen_width": 2.0,
            "brush_color": None,
        }
        result = validate_shape_data(data)
        assert result is None


class TestAngleValidation:
    """Тесты валидации фигуры «Угол»."""

    def _valid_angle(self):
        return {
            "type": "angle",
            "vertex": {"x": 100, "y": 200},
            "side_a": 150,
            "side_b": 100,
            "angle_deg": 90,
            "pen_color": [0, 0, 0],
            "pen_width": 2.0,
        }

    def test_angle_in_required_fields(self):
        assert "angle" in SHAPE_REQUIRED_FIELDS
        for field in ("vertex", "side_a", "side_b", "angle_deg", "pen_color", "pen_width"):
            assert field in SHAPE_REQUIRED_FIELDS["angle"]

    def test_valid_angle(self):
        result = validate_shape_data(self._valid_angle())
        assert result is None

    def test_angle_missing_type(self):
        data = {"vertex": {"x": 0, "y": 0}, "side_a": 100, "side_b": 100}
        result = validate_shape_data(data)
        assert result is not None
        assert "type" in result.lower() or "type" in result

    def test_angle_missing_vertex(self):
        data = self._valid_angle()
        del data["vertex"]
        result = validate_shape_data(data)
        assert result is not None
        assert "vertex" in result.lower() or "отсутст" in result.lower()

    def test_angle_vertex_not_dict(self):
        data = self._valid_angle()
        data["vertex"] = "not_a_dict"
        result = validate_shape_data(data)
        assert result is not None
        assert "vertex" in result.lower()

    def test_angle_vertex_missing_x(self):
        data = self._valid_angle()
        data["vertex"] = {"y": 100}
        result = validate_shape_data(data)
        assert result is not None
        assert "vertex" in result.lower()

    def test_angle_vertex_x_not_number(self):
        data = self._valid_angle()
        data["vertex"]["x"] = "not_a_number"
        result = validate_shape_data(data)
        assert result is not None
        assert "vertex" in result.lower()

    def test_angle_missing_side_a(self):
        data = self._valid_angle()
        del data["side_a"]
        result = validate_shape_data(data)
        assert result is not None
        assert "side_a" in result.lower()

    def test_angle_side_a_negative(self):
        data = self._valid_angle()
        data["side_a"] = -10
        result = validate_shape_data(data)
        assert result is not None
        assert "side_a" in result.lower()

    def test_angle_side_a_zero(self):
        data = self._valid_angle()
        data["side_a"] = 0
        result = validate_shape_data(data)
        assert result is not None
        assert "side_a" in result.lower()

    def test_angle_side_a_not_number(self):
        data = self._valid_angle()
        data["side_a"] = "large"
        result = validate_shape_data(data)
        assert result is not None
        assert "side_a" in result.lower()

    def test_angle_missing_side_b(self):
        data = self._valid_angle()
        del data["side_b"]
        result = validate_shape_data(data)
        assert result is not None

    def test_angle_side_b_negative(self):
        data = self._valid_angle()
        data["side_b"] = -50
        result = validate_shape_data(data)
        assert result is not None
        assert "side_b" in result.lower()

    def test_angle_missing_angle_deg(self):
        data = self._valid_angle()
        del data["angle_deg"]
        result = validate_shape_data(data)
        assert result is not None

    def test_angle_angle_deg_zero(self):
        data = self._valid_angle()
        data["angle_deg"] = 0
        result = validate_shape_data(data)
        assert result is not None

    def test_angle_angle_deg_too_large(self):
        data = self._valid_angle()
        data["angle_deg"] = 400
        result = validate_shape_data(data)
        assert result is not None

    def test_angle_angle_deg_not_number(self):
        data = self._valid_angle()
        data["angle_deg"] = "big"
        result = validate_shape_data(data)
        assert result is not None

    def test_angle_negative_vertex(self):
        data = self._valid_angle()
        data["vertex"] = {"x": -100, "y": -50}
        result = validate_shape_data(data)
        assert result is None

    def test_angle_minimal_valid(self):
        data = {
            "type": "angle",
            "vertex": {"x": 0, "y": 0},
            "side_a": 0.1,
            "side_b": 0.1,
            "angle_deg": 0.1,
            "pen_color": [255, 128, 64],
            "pen_width": 0.5,
        }
        result = validate_shape_data(data)
        assert result is None


class TestArcValidation:
    """Тесты валидации фигуры «Дуга»."""

    def _valid_arc(self):
        return {
            "type": "arc",
            "cx": 100.0,
            "cy": 200.0,
            "radius": 50.0,
            "start_angle": 0.0,
            "end_angle": 90.0,
            "pen_color": [0, 0, 0],
            "pen_width": 2.0,
        }

    def test_arc_in_required_fields(self):
        assert "arc" in SHAPE_REQUIRED_FIELDS
        for field in ("cx", "cy", "radius", "start_angle", "end_angle", "pen_color", "pen_width"):
            assert field in SHAPE_REQUIRED_FIELDS["arc"]

    def test_valid_arc(self):
        result = validate_shape_data(self._valid_arc())
        assert result is None

    def test_arc_missing_type(self):
        data = {"cx": 0, "cy": 0, "radius": 50}
        result = validate_shape_data(data)
        assert result is not None
        assert "type" in result.lower() or "type" in result

    def test_arc_missing_cx(self):
        data = self._valid_arc()
        del data["cx"]
        result = validate_shape_data(data)
        assert result is not None
        assert "cx" in result.lower()

    def test_arc_missing_cy(self):
        data = self._valid_arc()
        del data["cy"]
        result = validate_shape_data(data)
        assert result is not None

    def test_arc_cx_not_number(self):
        data = self._valid_arc()
        data["cx"] = "not_a_number"
        result = validate_shape_data(data)
        assert result is not None

    def test_arc_missing_radius(self):
        data = self._valid_arc()
        del data["radius"]
        result = validate_shape_data(data)
        assert result is not None

    def test_arc_radius_zero(self):
        data = self._valid_arc()
        data["radius"] = 0
        result = validate_shape_data(data)
        assert result is not None

    def test_arc_radius_negative(self):
        data = self._valid_arc()
        data["radius"] = -50
        result = validate_shape_data(data)
        assert result is not None

    def test_arc_radius_not_number(self):
        data = self._valid_arc()
        data["radius"] = "big"
        result = validate_shape_data(data)
        assert result is not None

    def test_arc_missing_start_angle(self):
        data = self._valid_arc()
        del data["start_angle"]
        result = validate_shape_data(data)
        assert result is not None

    def test_arc_start_angle_not_number(self):
        data = self._valid_arc()
        data["start_angle"] = "zero"
        result = validate_shape_data(data)
        assert result is not None

    def test_arc_missing_end_angle(self):
        data = self._valid_arc()
        del data["end_angle"]
        result = validate_shape_data(data)
        assert result is not None

    def test_arc_end_angle_not_number(self):
        data = self._valid_arc()
        data["end_angle"] = "big"
        result = validate_shape_data(data)
        assert result is not None

    def test_arc_negative_coords(self):
        data = self._valid_arc()
        data["cx"] = -100
        data["cy"] = -200
        result = validate_shape_data(data)
        assert result is None

    def test_arc_minimal_valid(self):
        data = {
            "type": "arc",
            "cx": 0,
            "cy": 0,
            "radius": 0.1,
            "start_angle": 0,
            "end_angle": 0.1,
            "pen_color": [0, 0, 0],
            "pen_width": 0.5,
        }
        result = validate_shape_data(data)
        assert result is None
