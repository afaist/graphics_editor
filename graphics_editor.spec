# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Определяем данные для включения (конфигурационные файлы проекта)
project_datas = [
    ('app_settings.json', '.'),
    ('fonts', 'fonts'),
    ('icons', 'icons'),
]

# Собираем все данные matplotlib
try:
    from PyInstaller.utils.hooks import collect_data_files
    matplotlib_datas = collect_data_files('matplotlib')
    project_datas.extend(matplotlib_datas)
except ImportError:
    pass  # collect_data_files может отсутствовать в старых версиях PyInstaller

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=project_datas,
    hiddenimports=[
        'PySide6',
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'PySide6.QtSvg',
        'PySide6.QtXml',
        # matplotlib для формул и графиков
        'matplotlib',
        'matplotlib.figure',
        'matplotlib.pyplot',
        'matplotlib.backends.backend_agg',
        'matplotlib.font_manager',
        'matplotlib.mathtext',
        'matplotlib.axes',
        'matplotlib.axis',
        'matplotlib.colorbar',
        'matplotlib.collections',
        'matplotlib.container',
        'matplotlib.dates',
        'matplotlib.image',
        'matplotlib.legend',
        'matplotlib.lines',
        'matplotlib.patches',
        'matplotlib.path',
        'matplotlib.projections',
        'matplotlib.spines',
        'matplotlib.streamplot',
        'matplotlib.table',
        'matplotlib.text',
        'matplotlib.transforms',
        'matplotlib._api',
        'matplotlib._layout',
        'matplotlib._tight',
        'matplotlib.backend_bases',
        'matplotlib.backends.backend_pdf',
        'matplotlib.backends.backend_svg',
        'matplotlib.category',
        'matplotlib.cm',
        'matplotlib.colors',
        'matplotlib.contour',
        'matplotlib.dates',
        'matplotlib.gridspec',
        'matplotlib.offsetbox',
        'matplotlib.scale',
        'matplotlib.style',
        'matplotlib.testing',
        'matplotlib.widgets',
        # PIL для превью формул/графиков
        'PIL',
        'PIL.Image',
        # numpy (требуется matplotlib)
        'numpy',
        # platformdirs для сохранения настроек
        'platformdirs',
    ],
    hookspath=['hooks'],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'unittest',
        'xml.etree',
        'setuptools',
        'distutils',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='graphics_editor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # UPX повреждает бинарники PySide6, вызывая segfault на Linux
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,       # GUI-приложение, без консоли
    disable_windowed_traceback=True,  # Показывать traceback при ошибке
    argv_emulation=False,
    target_arch='x86_64',
    codesign_identity=None,
    entitlements_file=None,
)

# Для onedir-структуры (папка с exe + зависимости) используется
# шаг Package в CI/CD, так как COLLECT конфликтует с EXE при
# последовательной обработке spec-файла.
