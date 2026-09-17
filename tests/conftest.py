"""Конфигурация pytest и общие фикстуры."""

import os
import sys
import tempfile

import pytest

# Убедимся, что QT работает в offscreen-режиме
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

# Добавляем корень проекта в sys.path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


# ------------------------------------------------------------------
# Фикстуры Qt
# ------------------------------------------------------------------


@pytest.fixture(scope="session")
def qapp():
    """Создаёт QApplication один раз на сессию."""
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


# ------------------------------------------------------------------
# Фикстуры фигур
# ------------------------------------------------------------------


@pytest.fixture
def point_shape():
    from shapes.point_shape import PointShape

    return PointShape(x=10.0, y=20.0, radius=3.0)


@pytest.fixture
def rectangle_shape():
    from shapes.rectangle_shape import RectangleShape

    return RectangleShape(x=0.0, y=0.0, width=100.0, height=50.0)


@pytest.fixture
def ellipse_shape():
    from shapes.ellipse_shape import EllipseShape

    return EllipseShape(x=0.0, y=0.0, width=80.0, height=60.0)


@pytest.fixture
def line_shape():
    from shapes.base_shape import ShapeType
    from shapes.line_shape import LineShape

    return LineShape(x1=0.0, y1=0.0, x2=100.0, y2=0.0, shape_type=ShapeType.LINE)


@pytest.fixture
def ray_shape():
    from shapes.base_shape import ShapeType
    from shapes.line_shape import LineShape

    return LineShape(x1=0.0, y1=0.0, x2=100.0, y2=0.0, shape_type=ShapeType.RAY)


@pytest.fixture
def infinite_line_shape():
    from shapes.base_shape import ShapeType
    from shapes.line_shape import LineShape

    return LineShape(x1=0.0, y1=0.0, x2=100.0, y2=100.0, shape_type=ShapeType.INFINITE_LINE)


@pytest.fixture
def polygon_shape():
    from shapes.polygon_shape import PolygonShape

    return PolygonShape(vertices=[(0, 0), (100, 0), (100, 100), (0, 100)])


@pytest.fixture
def polyline_shape():
    from shapes.polyline_shape import PolylineShape

    return PolylineShape(vertices=[(0, 0), (50, 50), (100, 0)])


@pytest.fixture
def arc_shape():
    from shapes.arc_shape import ArcShape

    return ArcShape(cx=0.0, cy=0.0, radius=50.0, start_angle=0.0, end_angle=90.0)


@pytest.fixture
def text_shape():
    from shapes.text_shape import TextShape

    return TextShape(x=10.0, y=20.0, text="Hello", font_size=14)


# ------------------------------------------------------------------
# Фикстуры утилит
# ------------------------------------------------------------------


@pytest.fixture
def temp_json_file():
    """Создаёт временный JSON-файл и удаляет его после теста."""
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
    f.close()
    yield f.name
    try:
        os.unlink(f.name)
    except OSError:
        pass


@pytest.fixture
def temp_gproj_file():
    """Создаёт временный .gproj-файл и удаляет его после теста."""
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".gproj", delete=False)
    f.close()
    yield f.name
    try:
        os.unlink(f.name)
    except OSError:
        pass
