#!/usr/bin/env bash
# Wrapper для graphics_editor AppImage
# Устанавливает переменные окружения ДО запуска приложения

set -e

# Fix for AppImage GIO/GVFS incompatibility
export GIO_USE_VFS=local

# Fix for Qt platform (prefer X11/XCB over Wayland)
if [ -n "$WAYLAND_DISPLAY" ] && [ -n "$DISPLAY" ]; then
    export QT_QPA_PLATFORM=xcb
fi

# Запускаем приложение
exec "$APPDIR/usr/bin/graphics_editor" "$@"
