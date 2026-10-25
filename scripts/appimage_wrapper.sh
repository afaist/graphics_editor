#!/usr/bin/env bash
# Wrapper для graphics_editor AppImage
# Минимальный wrapper — только GIO fix (критично для работы)

# Fix for AppImage GIO/GVFS incompatibility
export GIO_USE_VFS=local
export GIO_EXTRA_MODULES=""

# Запускаем приложение
exec "$APPDIR/usr/bin/graphics_editor" "$@"
