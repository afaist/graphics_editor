"""
PyInstaller hook для исключения libglib из бандла.

PySide6 бандлит старую libglib-2.0.so, которая конфликтует с
системными GIO модулями на свежих дистрибутивах (ABI mismatch).
Этот hook удаляет libglib из бандла, чтобы AppImage использовал
системную libglib.
"""


def hook(hook_api):
    # Удаляем libglib из бинарных файлов
    hook_api.excludes.append("glib")
    hook_api.excludes.append("gi.repository.GLib")
