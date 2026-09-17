#!/usr/bin/env python3
"""Запуск unit-тестов графического редактора."""

import os
import sys

import pytest

os.environ["QT_QPA_PLATFORM"] = "offscreen"

project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

if __name__ == "__main__":
    test_dir = os.path.join(project_root, "tests")
    exit_code = pytest.main(["-v", test_dir])
    sys.exit(exit_code)
