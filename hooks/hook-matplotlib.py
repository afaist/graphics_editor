"""PyInstaller hook для matplotlib — включает data files (шрифты, конфиги)."""

from PyInstaller.utils.hooks import collect_data_files

# Собрать все data files matplotlib
datas, binaries = collect_data_files("matplotlib")
