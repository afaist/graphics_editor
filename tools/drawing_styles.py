"""Единые стили для вспомогательных линий и элементов фигур."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPen

# ---------------------------------------------------------------------------
# Диагонали — синий пунктир с прозрачностью
# ---------------------------------------------------------------------------
DIAGONAL_COLOR = QColor(0, 0, 255, 150)
DIAGONAL_PEN = QPen(DIAGONAL_COLOR, 1.0, Qt.PenStyle.DashLine)


# ---------------------------------------------------------------------------
# Высоты — синий пунктир
# ---------------------------------------------------------------------------
HEIGHT_COLOR = QColor(Qt.GlobalColor.blue)
HEIGHT_PEN = QPen(HEIGHT_COLOR, 1.0, Qt.PenStyle.DashLine)


# ---------------------------------------------------------------------------
# Биссектрисы — зелёный штрих-пунктир
# ---------------------------------------------------------------------------
BISECTOR_COLOR = QColor(Qt.GlobalColor.green)
BISECTOR_PEN = QPen(BISECTOR_COLOR, 1.0, Qt.PenStyle.DashDotLine)


# ---------------------------------------------------------------------------
# Описанная окружность — darkMagenta пунктир
# ---------------------------------------------------------------------------
CIRCUMCIRCLE_COLOR = QColor(Qt.GlobalColor.darkMagenta)
CIRCUMCIRCLE_PEN = QPen(CIRCUMCIRCLE_COLOR, 1.0, Qt.PenStyle.DashLine)


# ---------------------------------------------------------------------------
# Углы (дуги и текст) — красный
# ---------------------------------------------------------------------------
ANGLE_COLOR = QColor(Qt.GlobalColor.red)
ANGLE_PEN = QPen(ANGLE_COLOR, 1.0)
