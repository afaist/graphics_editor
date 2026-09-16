"""Конфигурация pytest для тестов с PySide6."""

import pytest
from PySide6.QtWidgets import QApplication


@pytest.fixture(scope="session")
def qapp():
    """Создаёт QApplication один раз за сессию."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture
def temp_dir(tmp_path):
    """Временная директория для тестовых файлов."""
    return tmp_path
