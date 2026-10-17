from __future__ import annotations

import json


class Settings:
    """Глобальные настройки приложения."""

    def __init__(self):
        # сетка
        self.grid_visible: bool = True
        self.grid_spacing: int = 20
        self.grid_minor_spacing: int = 5

        # цвета
        self.grid_color_minor: str = "#E8E8E8"
        self.grid_color_major: str = "#CCCCCC"
        self.canvas_background: str = "#FFFFFF"

        # выделение
        self.selection_color: str = "#0078FF"

        # поведение
        self.snap_to_grid: bool = False
        self.snap_tolerance: float = 5.0

        # размер по умолчанию для новых фигур
        self.default_pen_width: float = 2.0
        self.default_pen_color: tuple = (0, 0, 0)
        self.default_brush_color: tuple | None = None

        # параметры графиков по умолчанию
        self.graph_default_width: int = 300
        self.graph_default_height: int = 200
        self.graph_default_font_size: int = 8
        self.graph_default_x_range: int = 10
        self.graph_default_x_steps: int = 500

        # тема оформления
        self.theme: str = "light"

    def to_dict(self) -> dict:
        return {
            "grid_visible": self.grid_visible,
            "grid_spacing": self.grid_spacing,
            "grid_minor_spacing": self.grid_minor_spacing,
            "grid_color_minor": self.grid_color_minor,
            "grid_color_major": self.grid_color_major,
            "canvas_background": self.canvas_background,
            "selection_color": self.selection_color,
            "snap_to_grid": self.snap_to_grid,
            "snap_tolerance": self.snap_tolerance,
            "default_pen_width": self.default_pen_width,
            "default_pen_color": list(self.default_pen_color)
            if self.default_pen_color
            else self.default_pen_color,
            "default_brush_color": list(self.default_brush_color)
            if self.default_brush_color
            else self.default_brush_color,
            "graph_default_width": self.graph_default_width,
            "graph_default_height": self.graph_default_height,
            "graph_default_font_size": self.graph_default_font_size,
            "graph_default_x_range": self.graph_default_x_range,
            "graph_default_x_steps": self.graph_default_x_steps,
            "theme": self.theme,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Settings:
        s = cls()
        for key, value in data.items():
            if not hasattr(s, key):
                continue
            # Конвертируем list обратно в tuple для цветов
            if key in ("default_pen_color", "default_brush_color") and isinstance(value, list):
                value = tuple(value)
            setattr(s, key, value)
        return s

    def save(self, filename: str = "app_settings.json") -> None:
        """Сохранение настроек в JSON‑файл."""
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise RuntimeError(f"Ошибка сохранения настроек в {filename}: {e}")

    def load(self, filename: str = "app_settings.json") -> None:
        """Загрузка настроек из JSON‑файла."""
        try:
            with open(filename, encoding="utf-8") as f:
                data = json.load(f)
                for key, value in data.items():
                    if hasattr(self, key):
                        setattr(self, key, value)
        except FileNotFoundError:
            # Файл не найден — оставляем настройки по умолчанию
            pass
        except Exception as e:
            print(f"Предупреждение: ошибка загрузки настроек из {filename}: {e}")
