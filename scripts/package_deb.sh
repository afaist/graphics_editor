#!/usr/bin/env bash
# Скрипт сборки DEB-пакета для graphics_editor
# Usage: ./scripts/package_deb.sh <build_dir> <output_dir> [version]

set -euo pipefail

BUILD_DIR="${1:?Usage: $0 <build_dir> <output_dir> [version]}"
OUTPUT_DIR="${2:?Usage: $0 <build_dir> <output_dir> [version]}"
VERSION="${3:-1.0.0}"
# Убираем префикс 'v', если он есть (v1.0.1 → 1.0.1)
VERSION="${VERSION#v}"

PACKAGE_NAME="graphics-editor"
ARCH="amd64"
PACKAGE_DIR="$(mktemp -d)"
CONTROL_DIR="${PACKAGE_DIR}/DEBIAN"

echo "=== Сборка DEB-пакета ==="
echo "  Build dir : ${BUILD_DIR}"
echo "  Output dir: ${OUTPUT_DIR}"
echo "  Version   : ${VERSION}"
echo "  Arch      : ${ARCH}"

# --- Структура пакета ---
mkdir -p "${CONTROL_DIR}"
mkdir -p "${PACKAGE_DIR}/usr/bin"
mkdir -p "${PACKAGE_DIR}/usr/share/applications"
mkdir -p "${PACKAGE_DIR}/usr/share/icons/hicolor/scalable/apps"
mkdir -p "${PACKAGE_DIR}/usr/share/graphics-editor"

# --- Копируем приложение ---
echo "[1/6] Копируем приложение..."
cp -a "${BUILD_DIR}/graphics_editor" "${PACKAGE_DIR}/usr/share/graphics-editor/"

# Создаём symlink в /usr/bin
ln -sf "/usr/share/graphics-editor/graphics_editor" "${PACKAGE_DIR}/usr/bin/graphics_editor"

# --- Копируем app_settings.json ---
if [ -f "app_settings.json" ]; then
    cp "app_settings.json" "${PACKAGE_DIR}/usr/share/graphics-editor/app_settings.json"
fi

# --- Desktop файл ---
echo "[2/6] Устанавливаем desktop-файл..."
cp "graphics_editor.desktop" "${PACKAGE_DIR}/usr/share/applications/graphics_editor.desktop"

# --- Иконка ---
echo "[3/6] Устанавливаем иконку..."
cp "icons/graphics_editor.svg" "${PACKAGE_DIR}/usr/share/icons/hicolor/scalable/apps/graphics_editor.svg"

# --- Control файл ---
echo "[4/6] Генерируем control-файл..."
cat > "${CONTROL_DIR}/control" <<EOF
Package: ${PACKAGE_NAME}
Version: ${VERSION}
Section: graphics
Priority: optional
Architecture: ${ARCH}
Depends: libc6, libgl1, libegl1, libxcb-cursor0, libxkbcommon0, libdbus-1-3, libfontconfig1, libfreetype6, libx11-6, libxext6, libxrender1, libxi6, libxrandr2, libxfixes3, libxcb1, libxcb-render0, libxcb-shape0, libxcb-shm0, libxcb-randr0, libxcb-image0, libsystemd0
Installed-Size: $(du -sk "${PACKAGE_DIR}/usr/share/graphics-editor" | awk '{print $1}')
Maintainer: Graphics Editor Team <https://github.com/user/graphics_editor>
Description: Векторный графический редактор для создания геометрических фигур
 Графический редактор с поддержкой 15+ типов фигур,
 undo/redo, группировки, экспорта в PNG/SVG,
 настройки сетки и привязки.
EOF

# --- Postinst скрипт ---
echo "[5/6] Генерируем postinst-скрипт..."
cat > "${CONTROL_DIR}/postinst" <<'POSTEOF'
#!/bin/bash
# Обновляем desktop database
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database /usr/share/applications 2>/dev/null || true
fi
# Обновляем иконочный кэш
if command -v update-icon-caches &> /dev/null; then
    update-icon-caches /usr/share/icons/hicolor/ 2>/dev/null || true
fi
exit 0
POSTEOF
chmod 755 "${CONTROL_DIR}/postinst"

# --- Собираем пакет ---
echo "[6/6] Собираем .deb пакет..."
DEB_FILE="${OUTPUT_DIR}/${PACKAGE_NAME}_${VERSION}_${ARCH}.deb"
dpkg-deb --build --root-owner-group "${PACKAGE_DIR}" "${DEB_FILE}"

# --- Чистим ---
rm -rf "${PACKAGE_DIR}"

echo "✅ Готово: ${DEB_FILE}"
echo "   Размер: $(du -h "${DEB_FILE}" | cut -f1)"
