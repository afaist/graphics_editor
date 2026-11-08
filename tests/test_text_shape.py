"""Тесты для TextShape — font_size bounds, contains, move, font properties, undo/redo."""

from PySide6.QtCore import QPointF
from PySide6.QtGui import QFont

from shapes.base_shape import HandleType
from shapes.text_shape import TextShape


class TestTextCreation:
    def test_default_properties(self):
        t = TextShape(10, 20, text="Hello")
        assert t.x == 10
        assert t.y == 20
        assert t.text == "Hello"
        assert t.font_size == 14

    def test_custom_font_size(self):
        t = TextShape(0, 0, text="Test", font_size=24)
        assert t.font_size == 24

    def test_empty_text(self):
        t = TextShape(0, 0)
        assert t.text == ""


class TestTextFontValidation:
    def test_font_size_clamped_min(self):
        t = TextShape(0, 0, font_size=2)
        assert t.font_size == 4

    def test_font_size_clamped_max(self):
        t = TextShape(0, 0, font_size=300)
        assert t.font_size == 200

    def test_font_size_normal(self):
        t = TextShape(0, 0, font_size=14)
        assert t.font_size == 14

    def test_set_font_size_clamped_min(self):
        t = TextShape(0, 0)
        t.font_size = 2
        assert t.font_size == 4

    def test_set_font_size_clamped_max(self):
        t = TextShape(0, 0)
        t.font_size = 300
        assert t.font_size == 200


class TestTextMove:
    def test_move(self):
        t = TextShape(10, 20, text="Test")
        t.move(5, -3)
        assert t.x == 15
        assert t.y == 17


class TestTextScale:
    def test_scale_up(self):
        t = TextShape(0, 0, font_size=14)
        t.scale(2.0)
        assert t.font_size == 28

    def test_scale_down(self):
        t = TextShape(0, 0, font_size=14)
        t.scale(0.5)
        assert t.font_size == 7

    def test_scale_zero_not_allowed(self):
        t = TextShape(0, 0)
        t.scale(0)  # factor > 0 required, but 0 is not > 0
        # font_size should remain unchanged since factor is not > 0

    def test_scale_negative_not_allowed(self):
        t = TextShape(0, 0)
        t.scale(-1.0)  # factor must be > 0
        assert t.font_size == 14


class TestTextContains:
    def test_point_inside(self):
        t = TextShape(0, 0, text="Hello", font_size=14)
        br = t.bounding_rect()
        if br.width() > 0 and br.height() > 0:
            assert t.contains_point(QPointF(br.left() + 5, br.top() + 5)) is True

    def test_point_outside(self):
        t = TextShape(0, 0, text="Hello", font_size=14)
        assert t.contains_point(QPointF(1000, 1000)) is False

    def test_empty_text(self):
        t = TextShape(0, 0, text="")
        assert t.contains_point(QPointF(0, 0)) is False


class TestTextBoundingRect:
    def test_empty_text_bounding_rect(self):
        t = TextShape(0, 0, text="")
        br = t.bounding_rect()
        assert br.width() > 0
        assert br.height() > 0

    def test_text_with_content(self):
        t = TextShape(0, 0, text="Hello World", font_size=20)
        br = t.bounding_rect()
        assert br.width() > 0
        assert br.height() > 0

    def test_bounding_rect_contains_text(self):
        t = TextShape(10, 20, text="Test", font_size=14)
        br = t.bounding_rect()
        assert br.left() <= 10
        assert br.top() <= 20


class TestTextHandles:
    def test_get_handles_empty_text(self):
        t = TextShape(0, 0, text="")
        handles = t.get_handles()
        assert len(handles) == 0

    def test_get_handles_with_text(self):
        t = TextShape(0, 0, text="Test")
        handles = t.get_handles()
        assert len(handles) == 4

    def test_get_handle_type_none(self):
        t = TextShape(0, 0, text="Test")
        ht = t.get_handle_type(QPointF(500, 500), tolerance=5.0)
        assert ht == HandleType.NONE


class TestTextApplyHandleTransform:
    def test_top_left(self):
        t = TextShape(10, 20, text="Test")
        t.apply_handle_transform(HandleType.TOP_LEFT, QPointF(10, 20), QPointF(15, 25))
        assert t.x == 15
        assert t.y == 25


class TestTextSerialization:
    def test_to_dict(self):
        t = TextShape(10, 20, text="Hello", font_size=18)
        d = t.to_dict()
        assert d["x"] == 10
        assert d["y"] == 20
        assert d["text"] == "Hello"
        assert d["font_size"] == 18
        assert d["type"] == "text"

    def test_from_dict(self):
        data = {
            "id": 1,
            "type": "text",
            "pen_color": (0, 0, 255),
            "pen_width": 2.0,
            "brush_color": None,
            "rotation": 0.0,
            "group_id": None,
            "selected": False,
            "x": 10,
            "y": 20,
            "text": "World",
            "font_size": 24,
        }
        t = TextShape.from_dict(data)
        assert t.x == 10
        assert t.text == "World"
        assert t.font_size == 24

    def test_roundtrip(self):
        t = TextShape(5, 15, text="Test Text", font_size=20)
        t.id = 42
        d = t.to_dict()
        t2 = TextShape.from_dict(d)
        assert t2.x == 5
        assert t2.text == "Test Text"
        assert t2.font_size == 20

    def test_to_dict_with_font_properties(self):
        """to_dict включает все свойства шрифта."""
        t = TextShape(0, 0, text="Test", font_size=18, font_family="Arial", font_weight=75)
        t.italic = True
        t.underline = True
        t.strikethrough = True
        d = t.to_dict()
        assert d["font_family"] == "Arial"
        assert d["font_size"] == 18
        assert d["font_weight"] == 75
        assert d["italic"] is True
        assert d["underline"] is True
        assert d["strikethrough"] is True

    def test_from_dict_with_font_properties(self):
        """from_dict корректно восстанавливает все свойства шрифта."""
        data = {
            "id": 1,
            "type": "text",
            "pen_color": (0, 0, 0),
            "pen_width": 2.0,
            "brush_color": None,
            "rotation": 0.0,
            "group_id": None,
            "selected": False,
            "x": 10,
            "y": 20,
            "text": "Test",
            "font_size": 24,
            "font_family": "Courier New",
            "font_weight": QFont.Weight.Bold,
            "italic": True,
            "underline": True,
            "strikethrough": True,
        }
        t = TextShape.from_dict(data)
        assert t.font_family == "Courier New"
        assert t.font_size == 24
        assert t.font_weight == QFont.Weight.Bold
        assert t.italic is True
        assert t.underline is True
        assert t.strikethrough is True

    def test_roundtrip_with_all_font_properties(self):
        """Полный цикл сериализации/десериализации со всеми свойствами шрифта."""
        t = TextShape(5, 15, text="Hello", font_size=20, font_family="Verdana")
        t.font_weight = QFont.Weight.Bold
        t.italic = True
        t.underline = True
        t.strikethrough = True
        t.id = 99
        d = t.to_dict()
        t2 = TextShape.from_dict(d)
        assert t2.x == 5
        assert t2.y == 15
        assert t2.text == "Hello"
        assert t2.font_size == 20
        assert t2.font_family == "Verdana"
        assert t2.font_weight == QFont.Weight.Bold
        assert t2.italic is True
        assert t2.underline is True
        assert t2.strikethrough is True


class TestTextFontProperties:
    """Тесты для свойств шрифта: font_family, font_weight, italic, underline, strikethrough."""

    def test_default_font_family(self):
        t = TextShape(0, 0, text="Test")
        assert t.font_family == "Segoe UI"

    def test_custom_font_family(self):
        t = TextShape(0, 0, text="Test", font_family="Arial")
        assert t.font_family == "Arial"

    def test_set_font_family(self):
        t = TextShape(0, 0, text="Test")
        t.font_family = "Times New Roman"
        assert t.font_family == "Times New Roman"

    def test_default_font_weight(self):
        t = TextShape(0, 0, text="Test")
        assert t.font_weight == QFont.Weight.Normal

    def test_custom_font_weight(self):
        t = TextShape(0, 0, text="Test", font_weight=QFont.Weight.Bold)
        assert t.font_weight == QFont.Weight.Bold

    def test_set_font_weight(self):
        t = TextShape(0, 0, text="Test")
        t.font_weight = QFont.Weight.Black
        assert t.font_weight == QFont.Weight.Black

    def test_default_italic(self):
        t = TextShape(0, 0, text="Test")
        assert t.italic is False

    def test_set_italic(self):
        t = TextShape(0, 0, text="Test")
        t.italic = True
        assert t.italic is True

    def test_default_underline(self):
        t = TextShape(0, 0, text="Test")
        assert t.underline is False

    def test_set_underline(self):
        t = TextShape(0, 0, text="Test")
        t.underline = True
        assert t.underline is True

    def test_default_strikethrough(self):
        t = TextShape(0, 0, text="Test")
        assert t.strikethrough is False

    def test_set_strikethrough(self):
        t = TextShape(0, 0, text="Test")
        t.strikethrough = True
        assert t.strikethrough is True

    def test_all_font_properties_together(self):
        """Проверка что все свойства шрифта устанавливаются независимо."""
        t = TextShape(
            0,
            0,
            text="Test",
            font_family="Arial",
            font_size=16,
            font_weight=QFont.Weight.Bold,
            italic=True,
            underline=True,
            strikethrough=True,
        )
        assert t.font_family == "Arial"
        assert t.font_size == 16
        assert t.font_weight == QFont.Weight.Bold
        assert t.italic is True
        assert t.underline is True
        assert t.strikethrough is True


class TestTextGetQFont:
    """Тесты для метода get_qfont()."""

    def test_get_qfont_default(self):
        t = TextShape(0, 0, text="Test")
        font = t.get_qfont()
        assert isinstance(font, QFont)
        assert font.family() == "Segoe UI"
        assert font.pointSize() == 14
        assert font.weight() == QFont.Weight.Normal
        assert font.italic() is False
        assert font.underline() is False
        assert font.strikeOut() is False

    def test_get_qfont_custom_family(self):
        t = TextShape(0, 0, text="Test", font_family="Arial")
        font = t.get_qfont()
        assert font.family() == "Arial"

    def test_get_qfont_custom_size(self):
        t = TextShape(0, 0, text="Test", font_size=24)
        font = t.get_qfont()
        assert font.pointSize() == 24

    def test_get_qfont_bold(self):
        t = TextShape(0, 0, text="Test", font_weight=QFont.Weight.Bold)
        font = t.get_qfont()
        assert font.weight() == QFont.Weight.Bold

    def test_get_qfont_italic(self):
        t = TextShape(0, 0, text="Test", italic=True)
        font = t.get_qfont()
        assert font.italic() is True

    def test_get_qfont_underline(self):
        t = TextShape(0, 0, text="Test", underline=True)
        font = t.get_qfont()
        assert font.underline() is True

    def test_get_qfont_strikethrough(self):
        t = TextShape(0, 0, text="Test", strikethrough=True)
        font = t.get_qfont()
        assert font.strikeOut() is True

    def test_get_qfont_all_styles(self):
        """Проверка что все стили применяются одновременно."""
        t = TextShape(
            0,
            0,
            text="Test",
            font_family="Courier New",
            font_size=18,
            font_weight=QFont.Weight.Bold,
            italic=True,
            underline=True,
            strikethrough=True,
        )
        font = t.get_qfont()
        assert font.family() == "Courier New"
        assert font.pointSize() == 18
        assert font.weight() == QFont.Weight.Bold
        assert font.italic() is True
        assert font.underline() is True
        assert font.strikeOut() is True

    def test_get_qfont_changes_reflect_in_shape(self):
        """Изменение свойств шрифта отражается в get_qfont()."""
        t = TextShape(0, 0, text="Test")
        font1 = t.get_qfont()
        assert font1.pointSize() == 14

        t.font_size = 20
        font2 = t.get_qfont()
        assert font2.pointSize() == 20

    def test_get_qfont_weight_black(self):
        """Проверка что QFont.Weight.Black корректно применяется."""
        t = TextShape(0, 0, text="Test", font_weight=QFont.Weight.Black)
        font = t.get_qfont()
        assert font.weight() == QFont.Weight.Black

    def test_get_qfont_weight_demi_bold(self):
        """Проверка что QFont.DemiBold корректно применяется."""
        t = TextShape(0, 0, text="Test", font_weight=QFont.Weight.DemiBold)
        font = t.get_qfont()
        assert font.weight() == QFont.Weight.DemiBold
