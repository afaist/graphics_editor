"""Единые стили для вспомогательных линий и элементов фигур.

Все импорты из PySide6 ленивые — чтобы избежать рекурсии shibokensupport.
"""

from __future__ import annotations

# Кэш для перьев
_pens: dict[str, object] = {}


def _get_qt_gui():
    """Ленивый импорт PySide6.QtGui."""
    from PySide6.QtGui import QColor, QPen

    return QColor, QPen


def _get_qt_core():
    """Ленивый импорт PySide6.QtCore."""
    from PySide6.QtCore import Qt

    return Qt


def _get_color(name: str, r: int, g: int, b: int, a: int = 255):
    """Ленивое создание QColor."""
    if name not in _pens:  # reuse _pens as cache for both colors and pens
        QColor, _ = _get_qt_gui()
        _pens[name] = QColor(r, g, b, a)
    return _pens[name]


def _get_pen(name: str, r: int, g: int, b: int, style: int, a: int = 255):
    """Ленивое создание QPen."""
    if name not in _pens:
        QColor, QPen = _get_qt_gui()
        Qt = _get_qt_core()
        color = QColor(r, g, b, a)
        pen = QPen(color, 1.0, Qt.PenStyle(style))
        _pens[name] = pen
    return _pens[name]


def __getattr__(name: str):
    """Ленивая загрузка всех цветов и перьев."""
    # Цвета
    color_map: dict[str, tuple[int, int, int, int]] = {
        "DIAGONAL_COLOR": (0, 0, 255, 150),
        "HEIGHT_COLOR": (4, 4, 255, 255),
        "BISECTOR_COLOR": (0, 128, 0, 255),
        "CIRCUMCIRCLE_COLOR": (139, 0, 139, 255),
        "ANGLE_COLOR": (255, 0, 0, 255),
    }
    if name in color_map:
        r, g, b, a = color_map[name]
        return _get_color(name, r, g, b, a)

    # Перья
    pen_map: dict[str, tuple[int, int, int, int, int]] = {
        "DIAGONAL_PEN": (0, 0, 255, 2, 150),  # r, g, b, style, a
        "HEIGHT_PEN": (4, 4, 255, 2, 255),
        "BISECTOR_PEN": (0, 128, 0, 3, 255),
        "CIRCUMCIRCLE_PEN": (139, 0, 139, 2, 255),
        "ANGLE_PEN": (255, 0, 0, 1, 255),
    }
    if name in pen_map:
        r, g, b, style, a = pen_map[name]
        return _get_pen(name, r, g, b, style, a)

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


# Стили линий для пользователя — числа, не требуют импортов
LINE_STYLES = [
    ("Сплошная", 1),  # Qt.PenStyle.SolidLine
    ("Пунктир", 2),  # Qt.PenStyle.DashLine
    ("Штрихпунктир", 4),  # Qt.PenStyle.DashDotDotLine
    ("Штрих-пунктир", 3),  # Qt.PenStyle.DashDotLine
]
