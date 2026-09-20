"""Тесты для MainWindow._show_settings и UIManager — меню «Настройки»."""


class TestMainWindowShowSettings:
    def test_show_settings_method_exists(self):
        """Проверка что метод _show_settings существует в MainWindow."""
        from ui.main_window import MainWindow

        assert hasattr(MainWindow, "_show_settings")
        assert callable(getattr(MainWindow, "_show_settings"))

    def test_show_settings_imports_settings_dialog(self):
        """Проверка что _show_settings импортирует SettingsDialog."""
        import inspect

        from ui.main_window import MainWindow

        source = inspect.getsource(MainWindow._show_settings)
        assert "SettingsDialog" in source

    def test_show_settings_calls_dlg_exec(self):
        """Проверка что _show_settings вызывает dlg.exec()."""
        import inspect

        from ui.main_window import MainWindow

        source = inspect.getsource(MainWindow._show_settings)
        assert "dlg.exec()" in source


class TestUIManagerSettingsMenu:
    def test_settings_menu_in_create_menu(self):
        """Проверка что UIManager.create_menu добавляет меню «Настройки»."""
        import inspect

        from ui.window_ui import UIManager

        source = inspect.getsource(UIManager.create_menu)
        assert "Настройки" in source
        assert "Параметры по умолчанию" in source

    def test_settings_menu_action_connects_to_show_settings(self):
        """Проверка что пункт меню подключён к mw._show_settings."""
        import inspect

        from ui.window_ui import UIManager

        source = inspect.getsource(UIManager.create_menu)
        assert "_show_settings" in source


class TestSettingsDefaultValues:
    """Проверка что дефолтные значения Settings используются при создании фигур."""

    def test_default_pen_color_is_black(self):
        from settings.settings import Settings

        s = Settings()
        assert s.default_pen_color == (0, 0, 0)

    def test_default_brush_color_is_none(self):
        from settings.settings import Settings

        s = Settings()
        assert s.default_brush_color is None

    def test_default_pen_width_is_2(self):
        from settings.settings import Settings

        s = Settings()
        assert s.default_pen_width == 2.0

    def test_tool_manager_uses_settings_defaults(self, qapp):
        """Проверка что ToolManager создаёт фигуры с параметрами из Settings."""
        from PySide6.QtCore import QPointF
        from PySide6.QtWidgets import QApplication

        from settings.settings import Settings
        from tools.tool_manager import ToolManager, ToolType

        app = QApplication.instance()
        if app is None:
            app = QApplication([])

        settings = Settings()
        settings.default_pen_color = (255, 100, 50)
        settings.default_pen_width = 4.0
        settings.default_brush_color = (100, 200, 100)

        tm = ToolManager()
        tm.current_tool = ToolType.ELLIPSE
        tm.start_shape(QPointF(0, 0), settings)
        tm.update_shape(QPointF(100, 50))
        shape = tm.finish_shape()

        assert shape is not None
        assert shape.pen_color.red() == 255
        assert shape.pen_color.green() == 100
        assert shape.pen_color.blue() == 50
        assert shape.pen_width == 4.0
        assert shape.brush_color is not None
        assert shape.brush_color.red() == 100
        assert shape.brush_color.green() == 200
        assert shape.brush_color.blue() == 100

    def test_tool_manager_no_brush_when_none(self, qapp):
        """Проверка что brush_color=None когда settings.default_brush_color=None."""
        from PySide6.QtCore import QPointF
        from PySide6.QtWidgets import QApplication

        from settings.settings import Settings
        from tools.tool_manager import ToolManager, ToolType

        app = QApplication.instance()
        if app is None:
            app = QApplication([])

        settings = Settings()
        settings.default_pen_color = (0, 0, 0)
        settings.default_brush_color = None

        tm = ToolManager()
        tm.current_tool = ToolType.ELLIPSE
        tm.start_shape(QPointF(0, 0), settings)
        tm.update_shape(QPointF(100, 50))
        shape = tm.finish_shape()

        assert shape is not None
        assert shape.brush_color is None

    def test_tool_manager_line_uses_settings(self, qapp):
        """Проверка что LineShape создаётся с параметрами из Settings."""
        from PySide6.QtCore import QPointF
        from PySide6.QtWidgets import QApplication

        from settings.settings import Settings
        from tools.tool_manager import ToolManager, ToolType

        app = QApplication.instance()
        if app is None:
            app = QApplication([])

        settings = Settings()
        settings.default_pen_color = (128, 64, 192)
        settings.default_pen_width = 3.0

        tm = ToolManager()
        tm.current_tool = ToolType.LINE
        tm.start_shape(QPointF(0, 0), settings)
        tm.update_shape(QPointF(100, 50))
        shape = tm.finish_shape()

        assert shape is not None
        assert shape.pen_color.red() == 128
        assert shape.pen_color.green() == 64
        assert shape.pen_color.blue() == 192
        assert shape.pen_width == 3.0

    def test_tool_manager_ellipse_uses_settings(self, qapp):
        """Проверка что EllipseShape создаётся с параметрами из Settings."""
        from PySide6.QtCore import QPointF
        from PySide6.QtWidgets import QApplication

        from settings.settings import Settings
        from tools.tool_manager import ToolManager, ToolType

        app = QApplication.instance()
        if app is None:
            app = QApplication([])

        settings = Settings()
        settings.default_pen_color = (200, 50, 50)
        settings.default_brush_color = (50, 200, 50)
        settings.default_pen_width = 2.5

        tm = ToolManager()
        tm.current_tool = ToolType.ELLIPSE
        tm.start_shape(QPointF(0, 0), settings)
        tm.update_shape(QPointF(80, 60))
        shape = tm.finish_shape()

        assert shape is not None
        assert shape.pen_color.red() == 200
        assert shape.brush_color is not None
        assert shape.brush_color.green() == 200

    def test_tool_manager_point_uses_settings(self, qapp):
        """Проверка что PointShape создаётся с параметрами из Settings."""
        from PySide6.QtCore import QPointF
        from PySide6.QtWidgets import QApplication

        from settings.settings import Settings
        from tools.tool_manager import ToolManager, ToolType

        app = QApplication.instance()
        if app is None:
            app = QApplication([])

        settings = Settings()
        settings.default_pen_color = (0, 128, 255)
        settings.default_brush_color = (255, 255, 0)
        settings.default_pen_width = 1.5

        tm = ToolManager()
        tm.current_tool = ToolType.POINT
        tm.start_shape(QPointF(50, 50), settings)
        shape = tm.finish_shape()

        assert shape is not None
        assert shape.pen_color.blue() == 255
        assert shape.brush_color is not None
        assert shape.brush_color.blue() == 0

    def test_tool_manager_polygon_uses_settings(self, qapp):
        """Проверка что PolygonShape создаётся с параметрами из Settings."""
        from PySide6.QtCore import QPointF
        from PySide6.QtWidgets import QApplication

        from settings.settings import Settings
        from tools.tool_manager import ToolManager, ToolType

        app = QApplication.instance()
        if app is None:
            app = QApplication([])

        settings = Settings()
        settings.default_pen_color = (100, 100, 100)
        settings.default_brush_color = (200, 150, 100)
        settings.default_pen_width = 3.5

        tm = ToolManager()
        tm.current_tool = ToolType.POLYGON
        tm.start_shape(QPointF(0, 0), settings)
        tm.update_shape(QPointF(100, 0))
        tm.update_shape(QPointF(100, 100))
        shape = tm.finish_polygon()

        assert shape is not None
        assert shape.pen_color.red() == 100
        assert shape.brush_color is not None
        assert shape.pen_width == 3.5


class TestSettingsLoadInMainWindow:
    """Проверка что MainWindow загружает настройки при инициализации."""

    def test_settings_load_called_in_init(self):
        """Проверка что в __init__ MainWindow вызывает settings.load()."""
        import inspect

        from ui.main_window import MainWindow

        source = inspect.getsource(MainWindow.__init__)
        assert "settings.load()" in source or "self._settings.load()" in source
