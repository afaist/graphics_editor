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

        # координатная система
        self.coord_cell_size: int = 20  # размер клетки в пикселях = 1 единица
        self.coord_origin_x: float = 700.0  # центр сцены X
        self.coord_origin_y: float = 450.0  # центр сцены Y
        self.coord_visible: bool = True
        self.coord_axis_color: str = "#000000"
        self.coord_axis_width: float = 2.0
        self.coord_tick_labels: bool = True

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
            "default_pen_color": self.default_pen_color,
            "default_brush_color": self.default_brush_color,
            "coord_cell_size": self.coord_cell_size,
            "coord_origin_x": self.coord_origin_x,
            "coord_origin_y": self.coord_origin_y,
            "coord_visible": self.coord_visible,
            "coord_axis_color": self.coord_axis_color,
            "coord_axis_width": self.coord_axis_width,
            "coord_tick_labels": self.coord_tick_labels,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Settings":
        s = cls()
        for key, value in data.items():
            if hasattr(s, key):
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
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
                for key, value in data.items():
                    if hasattr(self, key):
                        setattr(self, key, value)
        except FileNotFoundError:
            # Файл не найден — оставляем настройки по умолчанию
            pass
        except Exception as e:
            print(f"Предупреждение: ошибка загрузки настроек из {filename}: {e}")
