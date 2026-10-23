"""PyInstaller hook для matplotlib — включает data files (шрифты, конфиги)."""

from PyInstaller.utils.hooks import collect_data_files

# Собрать все data files matplotlib
# collect_data_files возвращает (datas, binaries) в старых версиях
# и только datas в новых версиях PyInstaller
_result = collect_data_files("matplotlib")
if isinstance(_result, tuple) and len(_result) == 2:
    datas, binaries = _result
else:
    datas = _result
