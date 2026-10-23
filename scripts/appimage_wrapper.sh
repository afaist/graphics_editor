#!/usr/bin/env bash
# Wrapper для graphics_editor AppImage
# Устанавливает переменные окружения ДО запуска приложения

set -e

# Fix for AppImage GIO/GVFS incompatibility (g_task_set_static_name undefined symbol)
# Отключаем GIO модули через symlink на пустой файл
GIO_MODULES_DIR="$APPDIR/usr/lib/gio/modules"
mkdir -p "$GIO_MODULES_DIR"
# Создаём symlink вместо системного модуля, который вызывает ошибку
ln -sf /dev/null "$GIO_MODULES_DIR/libgvfsdbus.so" 2>/dev/null || true

# Также пробуем отключить через env vars
export GIO_USE_VFS=local

# Fix для Qt — всегда используем X11/XCB, никогда Wayland
export QT_QPA_PLATFORM=xcb
export QT_QPA_PLATFORMTHEME=qt5ct

# Запускаем приложение
exec "$APPDIR/usr/bin/graphics_editor" "$@"
