"""Управление темами оформления приложения."""

from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication

if TYPE_CHECKING:
    pass


class ThemeName(StrEnum):
    """Названия доступных тем."""

    LIGHT = "light"
    DARK = "dark"
    SYSTEM = "system"


class ThemeManager:
    """Управление темами оформления приложения."""

    THEMES = {
        ThemeName.LIGHT: "Светлая",
        ThemeName.DARK: "Тёмная",
        ThemeName.SYSTEM: "Системная",
    }

    # Цвета для светлой темы
    LIGHT_COLORS = {
        "window_bg": "#F5F5F5",
        "panel_bg": "#FFFFFF",
        "panel_border": "#D0D0D0",
        "text_color": "#000000",
        "text_secondary": "#666666",
        "button_bg": "#FFFFFF",
        "button_hover": "#E8E8E8",
        "button_pressed": "#D0D0D0",
        "selection_color": "#0078FF",
        "grid_minor": "#E8E8E8",
        "grid_major": "#CCCCCC",
        "canvas_bg": "#FFFFFF",
        "statusbar_bg": "#F0F0F0",
        "statusbar_text": "#333333",
        "dock_bg": "#F5F5F5",
        "dock_header": "#B0B0B0",
        "input_bg": "#FFFFFF",
        "input_border": "#CCCCCC",
    }

    # Цвета для тёмной темы
    DARK_COLORS = {
        "window_bg": "#1E1E1E",
        "panel_bg": "#252526",
        "panel_border": "#3E3E42",
        "text_color": "#CCCCCC",
        "text_secondary": "#999999",
        "button_bg": "#3C3C3C",
        "button_hover": "#4D4D4D",
        "button_pressed": "#333333",
        "selection_color": "#0078D4",
        "grid_minor": "#2D2D30",
        "grid_major": "#3E3E42",
        "canvas_bg": "#1E1E1E",
        "statusbar_bg": "#007ACC",
        "statusbar_text": "#FFFFFF",
        "dock_bg": "#252526",
        "dock_header": "#2D2D30",
        "input_bg": "#3C3C3C",
        "input_border": "#555555",
    }

    def __init__(self, app: QApplication):
        self._app = app
        self._current_theme = ThemeName.LIGHT
        self._colors = self.LIGHT_COLORS.copy()

    @property
    def current_theme(self) -> ThemeName:
        return self._current_theme

    @property
    def colors(self) -> dict[str, str]:
        return self._colors.copy()

    def set_theme(self, theme: ThemeName) -> None:
        """Установить тему оформления."""
        self._current_theme = theme
        if theme == ThemeName.LIGHT:
            self._colors = self.LIGHT_COLORS.copy()
        elif theme == ThemeName.DARK:
            self._colors = self.DARK_COLORS.copy()
        else:  # SYSTEM
            # Временно используем светлую, можно расширить
            self._colors = self.LIGHT_COLORS.copy()

        self._apply_palette()
        self._apply_stylesheet()

    def _apply_palette(self) -> None:
        """Применить QPalette для базовых цветов приложения и диалогов."""
        c = self._colors
        palette = QPalette()

        # Активная группа (Active)
        palette.setColor(
            QPalette.ColorGroup.Active, QPalette.ColorRole.Window, QColor(c["window_bg"])
        )
        palette.setColor(
            QPalette.ColorGroup.Active, QPalette.ColorRole.WindowText, QColor(c["text_color"])
        )
        palette.setColor(
            QPalette.ColorGroup.Active, QPalette.ColorRole.Base, QColor(c["panel_bg"])
        )
        palette.setColor(
            QPalette.ColorGroup.Active, QPalette.ColorRole.AlternateBase, QColor(c["button_hover"])
        )
        palette.setColor(
            QPalette.ColorGroup.Active, QPalette.ColorRole.ToolTipBase, QColor(c["panel_bg"])
        )
        palette.setColor(
            QPalette.ColorGroup.Active, QPalette.ColorRole.ToolTipText, QColor(c["text_color"])
        )
        palette.setColor(
            QPalette.ColorGroup.Active,
            QPalette.ColorRole.PlaceholderText,
            QColor(c["text_secondary"]),
        )
        palette.setColor(
            QPalette.ColorGroup.Active, QPalette.ColorRole.Button, QColor(c["button_bg"])
        )
        palette.setColor(
            QPalette.ColorGroup.Active, QPalette.ColorRole.ButtonText, QColor(c["text_color"])
        )
        palette.setColor(
            QPalette.ColorGroup.Active, QPalette.ColorRole.Highlight, QColor(c["selection_color"])
        )
        palette.setColor(
            QPalette.ColorGroup.Active, QPalette.ColorRole.HighlightedText, QColor("#FFFFFF")
        )
        palette.setColor(
            QPalette.ColorGroup.Active, QPalette.ColorRole.Light, QColor(c["panel_border"])
        )
        palette.setColor(
            QPalette.ColorGroup.Active, QPalette.ColorRole.Midlight, QColor(c["panel_border"])
        )
        palette.setColor(
            QPalette.ColorGroup.Active, QPalette.ColorRole.Dark, QColor(c["panel_border"])
        )
        palette.setColor(
            QPalette.ColorGroup.Active, QPalette.ColorRole.Mid, QColor(c["panel_border"])
        )
        palette.setColor(
            QPalette.ColorGroup.Active, QPalette.ColorRole.Text, QColor(c["text_color"])
        )
        palette.setColor(
            QPalette.ColorGroup.Active, QPalette.ColorRole.Link, QColor(c["selection_color"])
        )
        palette.setColor(
            QPalette.ColorGroup.Active, QPalette.ColorRole.WindowText, QColor(c["text_color"])
        )

        # Неактивная группа (Inactive) — дублируем Active
        palette.setColor(
            QPalette.ColorGroup.Inactive, QPalette.ColorRole.Window, QColor(c["window_bg"])
        )
        palette.setColor(
            QPalette.ColorGroup.Inactive, QPalette.ColorRole.WindowText, QColor(c["text_color"])
        )
        palette.setColor(
            QPalette.ColorGroup.Inactive, QPalette.ColorRole.Base, QColor(c["panel_bg"])
        )
        palette.setColor(
            QPalette.ColorGroup.Inactive,
            QPalette.ColorRole.AlternateBase,
            QColor(c["button_hover"]),
        )
        palette.setColor(
            QPalette.ColorGroup.Inactive, QPalette.ColorRole.ToolTipBase, QColor(c["panel_bg"])
        )
        palette.setColor(
            QPalette.ColorGroup.Inactive, QPalette.ColorRole.ToolTipText, QColor(c["text_color"])
        )
        palette.setColor(
            QPalette.ColorGroup.Inactive,
            QPalette.ColorRole.PlaceholderText,
            QColor(c["text_secondary"]),
        )
        palette.setColor(
            QPalette.ColorGroup.Inactive, QPalette.ColorRole.Button, QColor(c["button_bg"])
        )
        palette.setColor(
            QPalette.ColorGroup.Inactive, QPalette.ColorRole.ButtonText, QColor(c["text_color"])
        )
        palette.setColor(
            QPalette.ColorGroup.Inactive,
            QPalette.ColorRole.Highlight,
            QColor(c["selection_color"]),
        )
        palette.setColor(
            QPalette.ColorGroup.Inactive, QPalette.ColorRole.HighlightedText, QColor("#FFFFFF")
        )
        palette.setColor(
            QPalette.ColorGroup.Inactive, QPalette.ColorRole.Light, QColor(c["panel_border"])
        )
        palette.setColor(
            QPalette.ColorGroup.Inactive, QPalette.ColorRole.Midlight, QColor(c["panel_border"])
        )
        palette.setColor(
            QPalette.ColorGroup.Inactive, QPalette.ColorRole.Dark, QColor(c["panel_border"])
        )
        palette.setColor(
            QPalette.ColorGroup.Inactive, QPalette.ColorRole.Mid, QColor(c["panel_border"])
        )
        palette.setColor(
            QPalette.ColorGroup.Inactive, QPalette.ColorRole.Text, QColor(c["text_color"])
        )
        palette.setColor(
            QPalette.ColorGroup.Inactive, QPalette.ColorRole.Link, QColor(c["selection_color"])
        )
        palette.setColor(
            QPalette.ColorGroup.Inactive, QPalette.ColorRole.WindowText, QColor(c["text_color"])
        )

        # Неактивная группа (Disabled) — затемнённый текст
        palette.setColor(
            QPalette.ColorGroup.Disabled,
            QPalette.ColorRole.WindowText,
            QColor(c["text_secondary"]),
        )
        palette.setColor(
            QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(c["text_secondary"])
        )
        palette.setColor(
            QPalette.ColorGroup.Disabled,
            QPalette.ColorRole.ButtonText,
            QColor(c["text_secondary"]),
        )

        # Применяем ко всему приложению (включая все диалоги)
        self._app.setPalette(palette)

    def _apply_stylesheet(self) -> None:
        """Применить QSS-стиль для специфических элементов."""
        c = self._colors

        stylesheet = f"""
            QMainWindow {{
                background-color: {c["window_bg"]};
            }}

            QGroupBox {{
                background-color: {c["panel_bg"]};
                border: 1px solid {c["panel_border"]};
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 12px;
                font-weight: bold;
            }}

            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: {c["text_color"]};
            }}

            QPushButton {{
                background-color: {c["button_bg"]};
                border: 1px solid {c["panel_border"]};
                border-radius: 4px;
                padding: 6px 12px;
                color: {c["text_color"]};
                font-size: 10pt;
            }}

            QPushButton:hover {{
                background-color: {c["button_hover"]};
            }}

            QPushButton:pressed {{
                background-color: {c["button_pressed"]};
            }}

            QPushButton:checked {{
                background-color: {c["selection_color"]};
                color: #FFFFFF;
            }}

            QCheckBox {{
                color: {c["text_color"]};
                spacing: 6px;
            }}

            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
            }}

            QSpinBox, QDoubleSpinBox {{
                background-color: {c["input_bg"]};
                border: 1px solid {c["input_border"]};
                border-radius: 3px;
                padding: 3px;
                color: {c["text_color"]};
            }}

            QMenuBar {{
                background-color: {c["panel_bg"]};
                color: {c["text_color"]};
                border-bottom: 1px solid {c["panel_border"]};
            }}

            QMenuBar::item:selected {{
                background-color: {c["button_hover"]};
            }}

            QMenu {{
                background-color: {c["panel_bg"]};
                color: {c["text_color"]};
                border: 1px solid {c["panel_border"]};
            }}

            QMenu::item:selected {{
                background-color: {c["button_hover"]};
            }}

            QStatusBar {{
                background-color: {c["statusbar_bg"]};
                color: {c["statusbar_text"]};
                border-top: 1px solid {c["panel_border"]};
            }}

            QDockWidget {{
                titlebar-close-icon: none;
                titlebar-normal-icon: none;
                background-color: {c["dock_bg"]};
            }}

            QDockWidget::title {{
                background-color: {c["dock_header"]};
                text-align: left;
                padding: 4px;
                color: {c["text_color"]};
                font-weight: bold;
            }}

            QDockWidget::close-button, QDockWidget::float-button {{
                subcontrol-origin: padding;
                padding: 2px;
                background-color: transparent;
            }}

            QScrollBar:vertical {{
                background-color: {c["panel_bg"]};
                width: 12px;
                border: none;
            }}

            QScrollBar::handle:vertical {{
                background-color: {c["button_bg"]};
                border-radius: 6px;
                min-height: 20px;
            }}

            QScrollBar::handle:vertical:hover {{
                background-color: {c["button_hover"]};
            }}

            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}

            QScrollBar:horizontal {{
                background-color: {c["panel_bg"]};
                height: 12px;
                border: none;
            }}

            QScrollBar::handle:horizontal {{
                background-color: {c["button_bg"]};
                border-radius: 6px;
                min-width: 20px;
            }}

            QScrollBar::handle:horizontal:hover {{
                background-color: {c["button_hover"]};
            }}

            QTabWidget::pane {{
                border: 1px solid {c["panel_border"]};
                border-radius: 4px;
                background-color: {c["panel_bg"]};
                top: -1px;
            }}

            QTabWidget::tab-bar {{
                alignment: left;
            }}

            QTabWidget > QWidget {{
                background-color: {c["panel_bg"]};
            }}

            QTabBar::tab {{
                background-color: {c["dock_header"]};
                color: {c["text_color"]};
                font-weight: bold;
                padding: 6px 12px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                margin-right: 2px;
            }}

            QTabBar::tab:selected {{
                background-color: {c["panel_bg"]};
                border-bottom: 2px solid {c["selection_color"]};
            }}

            QTabBar::tab:!selected {{
                margin-top: 2px;
            }}

            QLabel {{
                color: {c["text_color"]};
            }}

            QComboBox {{
                background-color: {c["input_bg"]};
                border: 1px solid {c["input_border"]};
                border-radius: 3px;
                padding: 3px;
                color: {c["text_color"]};
            }}

            QComboBox::drop-down {{
                border: none;
            }}

            QComboBox::item:selected {{
                background-color: {c["button_hover"]};
            }}

            QListWidget {{
                background-color: {c["panel_bg"]};
                border: 1px solid {c["panel_border"]};
                border-radius: 3px;
                color: {c["text_color"]};
                padding: 4px;
            }}

            QListWidget::item {{
                padding: 4px;
                border-radius: 2px;
            }}

            QListWidget::item:hover {{
                background-color: {c["button_hover"]};
            }}

            QListWidget::item:selected {{
                background-color: {c["selection_color"]};
                color: #FFFFFF;
            }}

            QUndoView {{
                background-color: {c["panel_bg"]};
                color: {c["text_color"]};
                border: none;
            }}

            QUndoView::item {{
                color: {c["text_color"]};
                padding: 2px 4px;
            }}

            QUndoView::item:hover {{
                background-color: {c["button_hover"]};
            }}

            QUndoView::item:selected {{
                background-color: {c["selection_color"]};
                color: #FFFFFF;
            }}

            QToolTip {{
                background-color: {c["panel_bg"]};
                color: {c["text_color"]};
                border: 1px solid {c["panel_border"]};
            }}

            QDialog {{
                background-color: {c["panel_bg"]};
            }}

            QSpinBox, QDoubleSpinBox {{
                selection-background-color: {c["selection_color"]};
            }}
        """

        self._app.setStyleSheet(stylesheet)

    def get_theme_name(self, theme: ThemeName) -> str:
        """Получить русское название темы."""
        return self.THEMES.get(theme, theme.value)

    def get_available_themes(self) -> list[tuple[ThemeName, str]]:
        """Получить список доступных тем с русскими названиями."""
        return [(theme, self.THEMES[theme]) for theme in ThemeName]
