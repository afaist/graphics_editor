#!/usr/bin/env bash
# Wrapper для graphics_editor AppImage
# Устанавливает переменные окружения ДО запуска приложения

set -e

# Fix for AppImage GIO/GVFS incompatibility (g_task_set_static_name undefined symbol)
# Очищаем GIO_EXTRA_MODULES — отключает системные GIO модули, которые вызывают segfault
export GIO_EXTRA_MODULES=""
export GIO_USE_VFS=local

# Fix для Qt — всегда используем X11/XCB, никогда Wayland
export QT_QPA_PLATFORM=xcb
export QT_QPA_PLATFORMTHEME=qt5ct

# Запускаем приложение
exec "$APPDIR/usr/bin/graphics_editor" "$@"
