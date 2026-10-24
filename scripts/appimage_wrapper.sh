#!/usr/bin/env bash
# Wrapper для graphics_editor AppImage
# Устанавливает переменные окружения ДО запуска приложения

# Fix for AppImage GIO/GVFS incompatibility (g_task_set_static_name undefined symbol)
# GIO модули загружаются на уровне C, env vars должны быть установлены ДО запуска
export GIO_USE_VFS=local
export GIO_EXTRA_MODULES=""

# Fix для Qt — всегда используем X11/XCB, никогда Wayland
export QT_QPA_PLATFORM=xcb
export QT_QPA_PLATFORMTHEME=qt5ct

# Отключаем OpenGL-интеграцию Qt/XCB
export QT_XCB_GL_INTEGRATION=none

# Отключаем XCB recycle
export QT_XCB_DISABLE_RECYCLE=1

# Отключаем XKB recycle
export QT_XKB_DISABLE_RECYCLE=1

# Запускаем приложение
exec "$APPDIR/usr/bin/graphics_editor" "$@"
