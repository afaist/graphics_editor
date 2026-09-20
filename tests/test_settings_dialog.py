"""Тесты для SettingsDialog — диалог настроек по умолчанию для новых фигур."""

import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QDoubleSpinBox,
    QPushButton,
    QWidget,
)

from settings.settings import Settings
from ui.settings_dialog import SettingsDialog

# ------------------------------------------------------------------
# _ColorButton — тесты без создания виджета
# QColorDialog крашится в offscreen-режиме
# ------------------------------------------------------------------


class TestColorButtonLogic:
    def test_color_button_class_exists(self):
        from ui.settings_dialog import _ColorButton

        assert _ColorButton is not None

    def test_color_button_has_signal(self):
        from ui.settings_dialog import _ColorButton

        assert hasattr(_ColorButton, "color_changed")

    def test_color_button_has_get_color(self):
        from ui.settings_dialog import _ColorButton

        assert hasattr(_ColorButton, "get_color")

    def test_color_button_has_set_color(self):
        from ui.settings_dialog import _ColorButton

        assert hasattr(_ColorButton, "set_color")

    def test_color_button_has_pick_method(self):
        from ui.settings_dialog import _ColorButton

        assert hasattr(_ColorButton, "_pick")


# ------------------------------------------------------------------
# Вспомогательный mock-виджет для MainWindow
# ------------------------------------------------------------------


class _MockMainWindow(QWidget):
    """Минимальный QWidget-обёртка для тестирования SettingsDialog._on_ok."""

    def __init__(self, settings: Settings):
        super().__init__(None)
        self._settings = settings


# ------------------------------------------------------------------
# SettingsDialog — инициализация
# ------------------------------------------------------------------


class TestSettingsDialogInit:
    def test_dialog_is_modal(self, qapp):
        dlg = SettingsDialog()
        assert dlg.windowModality() == Qt.WindowModality.ApplicationModal

    def test_dialog_has_correct_title(self, qapp):
        dlg = SettingsDialog()
        assert dlg.windowTitle() == "Настройки"

    def test_dialog_has_ok_button(self, qapp):
        dlg = SettingsDialog()
        buttons = dlg.findChildren(QPushButton)
        names = [b.text() for b in buttons]
        assert "OK" in names

    def test_dialog_has_cancel_button(self, qapp):
        dlg = SettingsDialog()
        buttons = dlg.findChildren(QPushButton)
        names = [b.text() for b in buttons]
        assert "Отмена" in names

    def test_dialog_has_reset_button(self, qapp):
        dlg = SettingsDialog()
        buttons = dlg.findChildren(QPushButton)
        names = [b.text() for b in buttons]
        assert "Сброс" in names

    def test_dialog_has_pen_width_spinbox(self, qapp):
        dlg = SettingsDialog()
        spinboxes = dlg.findChildren(QDoubleSpinBox)
        assert len(spinboxes) >= 1

    def test_dialog_has_no_brush_checkbox(self, qapp):
        dlg = SettingsDialog()
        checkboxes = dlg.findChildren(QCheckBox)
        has_no_brush = any(cb.text() == "Нет" for cb in checkboxes)
        assert has_no_brush is True


# ------------------------------------------------------------------
# SettingsDialog — set_defaults
# ------------------------------------------------------------------


class TestSettingsDialogSetDefaults:
    def test_set_defaults_pen_color(self, qapp):
        dlg = SettingsDialog()
        dlg.set_defaults((255, 0, 0), None, 2.0)
        assert dlg._pen_color == (255, 0, 0)

    def test_set_defaults_brush_color(self, qapp):
        dlg = SettingsDialog()
        dlg.set_defaults((0, 0, 0), (128, 128, 128), 2.0)
        assert dlg._brush_color == (128, 128, 128)
        assert dlg._no_brush is False

    def test_set_defaults_no_brush(self, qapp):
        dlg = SettingsDialog()
        dlg.set_defaults((0, 0, 0), None, 2.0)
        assert dlg._brush_color is None
        assert dlg._no_brush is True

    def test_set_defaults_pen_width(self, qapp):
        dlg = SettingsDialog()
        dlg.set_defaults((0, 0, 0), None, 5.5)
        assert dlg._pen_width == 5.5

    def test_set_defaults_applies_to_widgets(self, qapp):
        dlg = SettingsDialog()
        dlg.set_defaults((200, 100, 50), (255, 255, 0), 3.0)
        assert dlg._spin_pen_width.value() == 3.0
        assert dlg._chk_no_brush.isChecked() is False


# ------------------------------------------------------------------
# SettingsDialog — сброс
# ------------------------------------------------------------------


class TestSettingsDialogReset:
    def test_reset_pen_color(self, qapp):
        dlg = SettingsDialog()
        dlg.set_defaults((255, 0, 0), (0, 255, 0), 5.0)
        dlg._on_reset()
        assert dlg._pen_color == (0, 0, 0)

    def test_reset_brush_to_none(self, qapp):
        dlg = SettingsDialog()
        dlg.set_defaults((0, 0, 0), (255, 255, 255), 2.0)
        dlg._on_reset()
        assert dlg._brush_color is None
        assert dlg._no_brush is True

    def test_reset_pen_width(self, qapp):
        dlg = SettingsDialog()
        dlg.set_defaults((0, 0, 0), None, 10.0)
        dlg._on_reset()
        assert dlg._pen_width == 2.0

    def test_reset_spinbox_value(self, qapp):
        dlg = SettingsDialog()
        dlg.set_defaults((0, 0, 0), None, 10.0)
        dlg._on_reset()
        assert dlg._spin_pen_width.value() == 2.0

    def test_reset_no_brush_checkbox(self, qapp):
        dlg = SettingsDialog()
        dlg.set_defaults((0, 0, 0), (255, 0, 0), 2.0)
        dlg._on_reset()
        assert dlg._chk_no_brush.isChecked() is True

    def test_reset_disables_brush_button(self, qapp):
        dlg = SettingsDialog()
        dlg.set_defaults((0, 0, 0), (255, 0, 0), 2.0)
        dlg._on_reset()
        assert dlg._btn_brush_color.isEnabled() is False


# ------------------------------------------------------------------
# SettingsDialog — сохранение настроек
# ------------------------------------------------------------------


class TestSettingsDialogSave:
    def test_on_ok_saves_pen_color(self, qapp, temp_json_file):
        settings = Settings()
        settings.load(temp_json_file)
        mw = _MockMainWindow(settings)

        dlg = SettingsDialog(mw)
        dlg.set_defaults((0, 0, 0), None, 2.0)
        dlg._pen_color = (100, 150, 200)
        dlg._on_ok()

        assert settings.default_pen_color == (100, 150, 200)

    def test_on_ok_saves_pen_width(self, qapp, temp_json_file):
        settings = Settings()
        settings.load(temp_json_file)
        mw = _MockMainWindow(settings)

        dlg = SettingsDialog(mw)
        dlg.set_defaults((0, 0, 0), None, 2.0)
        dlg._spin_pen_width.setValue(7.5)
        dlg._on_ok()

        assert settings.default_pen_width == 7.5

    def test_on_ok_saves_no_brush(self, qapp, temp_json_file):
        settings = Settings()
        settings.load(temp_json_file)
        mw = _MockMainWindow(settings)

        dlg = SettingsDialog(mw)
        dlg.set_defaults((0, 0, 0), (255, 0, 0), 2.0)
        dlg._chk_no_brush.setChecked(True)
        dlg._on_ok()

        assert settings.default_brush_color is None

    def test_on_ok_saves_brush_color(self, qapp, temp_json_file):
        settings = Settings()
        settings.load(temp_json_file)
        mw = _MockMainWindow(settings)

        dlg = SettingsDialog(mw)
        dlg.set_defaults((0, 0, 0), None, 2.0)
        dlg._brush_color = (200, 100, 50)
        dlg._chk_no_brush.setChecked(False)
        dlg._on_ok()

        assert settings.default_brush_color == (200, 100, 50)

    def test_on_ok_persists_to_file(self, qapp, temp_json_file):
        settings = Settings()
        settings.load(temp_json_file)
        mw = _MockMainWindow(settings)

        dlg = SettingsDialog(mw)
        dlg.set_defaults((0, 0, 0), None, 2.0)
        dlg._pen_color = (50, 60, 70)
        dlg._spin_pen_width.setValue(4.0)
        dlg._brush_color = (100, 200, 100)
        dlg._chk_no_brush.setChecked(False)
        dlg._on_ok()

        # _on_ok вызывает settings.save() с дефолтным именем "app_settings.json"
        # Поэтому загружаем из того же файла
        s2 = Settings()
        s2.load("app_settings.json")
        assert s2.default_pen_color == [50, 60, 70]
        assert s2.default_pen_width == 4.0
        assert s2.default_brush_color == [100, 200, 100]

        # Убираем за собой
        try:
            os.unlink("app_settings.json")
        except OSError:
            pass

    def test_on_ok_with_none_parent(self, qapp):
        dlg = SettingsDialog(None)
        dlg.set_defaults((0, 0, 0), None, 2.0)
        dlg._on_ok()

    def test_on_cancel_does_not_save(self, qapp, temp_json_file):
        settings = Settings()
        settings.default_pen_color = (255, 0, 0)
        settings.load(temp_json_file)
        mw = _MockMainWindow(settings)

        dlg = SettingsDialog(mw)
        dlg.set_defaults((255, 0, 0), None, 2.0)
        dlg._pen_color = (0, 255, 0)
        dlg.reject()

        assert settings.default_pen_color == (255, 0, 0)


# ------------------------------------------------------------------
# SettingsDialog — чекбокс "Нет" заливки
# ------------------------------------------------------------------


class TestSettingsDialogNoBrushToggle:
    def test_brush_button_enabled_when_brush_color_set(self, qapp):
        dlg = SettingsDialog()
        dlg.set_defaults((0, 0, 0), (255, 0, 0), 2.0)
        assert dlg._btn_brush_color.isEnabled() is True

    def test_brush_button_disabled_when_no_brush(self, qapp):
        dlg = SettingsDialog()
        dlg.set_defaults((0, 0, 0), None, 2.0)
        assert dlg._btn_brush_color.isEnabled() is False

    def test_checking_no_brush_disables_color_button(self, qapp):
        dlg = SettingsDialog()
        dlg.set_defaults((0, 0, 0), (255, 0, 0), 2.0)
        assert dlg._btn_brush_color.isEnabled() is True
        dlg._chk_no_brush.setChecked(True)
        assert dlg._btn_brush_color.isEnabled() is False

    def test_unchecking_no_brush_enables_color_button(self, qapp):
        dlg = SettingsDialog()
        dlg.set_defaults((0, 0, 0), None, 2.0)
        dlg._chk_no_brush.setChecked(False)
        assert dlg._btn_brush_color.isEnabled() is True

    def test_checking_no_brush_clears_brush_color(self, qapp):
        dlg = SettingsDialog()
        dlg.set_defaults((0, 0, 0), (100, 200, 50), 2.0)
        dlg._chk_no_brush.setChecked(True)
        assert dlg._brush_color is None


# ------------------------------------------------------------------
# Интеграция
# ------------------------------------------------------------------


class TestSettingsDialogIntegration:
    def test_full_cycle(self, qapp, temp_json_file):
        settings = Settings()
        settings.default_pen_color = (255, 128, 0)
        settings.default_brush_color = (0, 200, 100)
        settings.default_pen_width = 3.5
        settings.save(temp_json_file)

        settings2 = Settings()
        settings2.load(temp_json_file)
        assert settings2.default_pen_color == [255, 128, 0]
        assert settings2.default_brush_color == [0, 200, 100]
        assert settings2.default_pen_width == 3.5

        mw = _MockMainWindow(settings2)
        dlg = SettingsDialog(mw)
        dlg.set_defaults(
            settings2.default_pen_color,
            settings2.default_brush_color,
            settings2.default_pen_width,
        )
        assert dlg._pen_color == (255, 128, 0)

        dlg._on_reset()
        assert dlg._pen_color == (0, 0, 0)
        assert dlg._brush_color is None
        assert dlg._pen_width == 2.0

        dlg._on_ok()
        assert settings2.default_pen_color == (0, 0, 0)
        assert settings2.default_brush_color is None
        assert settings2.default_pen_width == 2.0
