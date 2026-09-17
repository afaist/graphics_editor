# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller hook для PySide6.
Собирает все данные Qt и подмодули PySide6.
"""

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Собираем все data-файлы PySide6 (стиль, переводы, Qt плагины и т.д.)
datas = collect_data_files('PySide6')

# Собираем все подмодули PySide6
hiddenimports = collect_submodules('PySide6')
