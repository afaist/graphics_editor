"""Тесты для FormulaShape — создание, сериализация, свойства."""

from PySide6.QtCore import QPointF

from shapes.base_shape import HandleType
from shapes.formula_shape import FormulaShape


class TestFormulaCreation:
    def test_default_properties(self):
        f = FormulaShape(10, 20, latex_text=r"\frac{a}{b}")
        assert f.x == 10
        assert f.y == 20
        assert f.latex == r"\frac{a}{b}"
        assert f.font_size == 16

    def test_custom_font_size(self):
        f = FormulaShape(0, 0, latex_text=r"x^2", font_size=24)
        assert f.font_size == 24

    def test_empty_latex(self):
        f = FormulaShape(0, 0)
        assert f.latex == ""

    def test_shape_type(self):
        f = FormulaShape(0, 0)
        assert f.shape_type.value == "formula"


class TestFormulaFontValidation:
    def test_font_size_clamped_min(self):
        f = FormulaShape(0, 0, font_size=2)
        assert f.font_size == 4

    def test_font_size_clamped_max(self):
        f = FormulaShape(0, 0, font_size=300)
        assert f.font_size == 200

    def test_font_size_normal(self):
        f = FormulaShape(0, 0, font_size=14)
        assert f.font_size == 14

    def test_set_font_size_clamped_min(self):
        f = FormulaShape(0, 0)
        f.font_size = 2
        assert f.font_size == 4

    def test_set_font_size_clamped_max(self):
        f = FormulaShape(0, 0)
        f.font_size = 300
        assert f.font_size == 200


class TestFormulaMove:
    def test_move(self):
        f = FormulaShape(10, 20, latex_text=r"\alpha")
        f.move(5, -3)
        assert f.x == 15
        assert f.y == 17


class TestFormulaScale:
    def test_scale_up(self):
        f = FormulaShape(0, 0, font_size=14)
        f.scale(2.0)
        assert f.font_size == 28

    def test_scale_down(self):
        f = FormulaShape(0, 0, font_size=14)
        f.scale(0.5)
        assert f.font_size == 7

    def test_scale_negative_not_allowed(self):
        f = FormulaShape(0, 0)
        f.scale(-1.0)
        # Negative scale is a no-op for FormulaShape (like TextShape)
        assert f.font_size == 16


class TestFormulaLatexProperty:
    def test_set_latex(self):
        f = FormulaShape(0, 0)
        f.latex = r"\beta"
        assert f.latex == r"\beta"

    def test_set_latex_triggers_render(self):
        f = FormulaShape(0, 0)
        f._render_dirty = False
        f.latex = r"\gamma"
        assert f._render_dirty is True


class TestFormulaContains:
    def test_point_outside(self):
        f = FormulaShape(0, 0, latex_text=r"x")
        assert f.contains_point(QPointF(1000, 1000)) is False

    def test_bounding_rect_valid(self):
        f = FormulaShape(0, 0, latex_text=r"x")
        br = f.bounding_rect()
        assert br.width() > 0
        assert br.height() > 0


class TestFormulaBoundingRect:
    def test_empty_latex_bounding_rect(self):
        f = FormulaShape(0, 0, latex_text="")
        br = f.bounding_rect()
        assert br.width() > 0
        assert br.height() > 0

    def test_bounding_rect_contains_position(self):
        f = FormulaShape(10, 20, latex_text=r"\alpha")
        br = f.bounding_rect()
        assert br.left() <= 10
        assert br.top() <= 20


class TestFormulaHandles:
    def test_get_handles(self):
        f = FormulaShape(0, 0, latex_text=r"x")
        handles = f.get_handles()
        assert len(handles) == 4

    def test_get_handle_type_none(self):
        f = FormulaShape(0, 0, latex_text=r"x")
        ht = f.get_handle_type(QPointF(500, 500), tolerance=5.0)
        assert ht == HandleType.NONE


class TestFormulaApplyHandleTransform:
    def test_top_left(self):
        f = FormulaShape(10, 20, latex_text=r"x")
        f.apply_handle_transform(HandleType.TOP_LEFT, QPointF(10, 20), QPointF(15, 25))
        assert f.x == 15
        assert f.y == 25


class TestFormulaSerialization:
    def test_to_dict(self):
        f = FormulaShape(10, 20, latex_text=r"\frac{a}{b}", font_size=18)
        d = f.to_dict()
        assert d["x"] == 10
        assert d["y"] == 20
        assert d["latex"] == r"\frac{a}{b}"
        assert d["font_size"] == 18
        assert d["type"] == "formula"

    def test_from_dict(self):
        data = {
            "id": 1,
            "type": "formula",
            "pen_color": (0, 0, 255),
            "pen_width": 2.0,
            "brush_color": None,
            "rotation": 0.0,
            "group_id": None,
            "selected": False,
            "x": 10,
            "y": 20,
            "latex": r"\sqrt{x}",
            "font_size": 24,
        }
        f = FormulaShape.from_dict(data)
        assert f.x == 10
        assert f.latex == r"\sqrt{x}"
        assert f.font_size == 24
        # При загрузке render_dirty должен быть True
        assert f._render_dirty is True

    def test_roundtrip(self):
        f = FormulaShape(5, 15, latex_text=r"\int_0^1 x^2 dx", font_size=20)
        f.id = 42
        d = f.to_dict()
        f2 = FormulaShape.from_dict(d)
        assert f2.x == 5
        assert f2.latex == r"\int_0^1 x^2 dx"
        assert f2.font_size == 20
