#!/usr/bin/env bash
# Скрипт сборки AppImage для graphics_editor
# Usage: ./scripts/package_appimage.sh <build_dir> <output_dir> [version]

set -euo pipefail

BUILD_DIR="${1:?Usage: $0 <build_dir> <output_dir> [version]}"
OUTPUT_DIR="${2:?Usage: $0 <build_dir> <output_dir> [version]}"
VERSION="${3:-1.0.0}"

APP_NAME="graphics_editor"
APPIMAGE_ARCH="x86_64"

echo "=== Сборка AppImage ==="
echo "  Build dir : ${BUILD_DIR}"
echo "  Output dir: ${OUTPUT_DIR}"
echo "  Version   : ${VERSION}"

# --- Скачиваем linuxdeploy и плагин ---
LINUXDEPLOY_URL="https://github.com/linuxdeploy/linuxdeploy/releases/download/continuous/linuxdeploy-${APPIMAGE_ARCH}.AppImage"
LINUXDEPLOY_PLUGIN_URL="https://github.com/linuxdeploy/linuxdeploy-plugin-appimage/releases/download/continuous/linuxdeploy-plugin-appimage-${APPIMAGE_ARCH}.AppImage"

LINUXDEPLOY_BIN="$(mktemp -d)/linuxdeploy.AppImage"
LINUXDEPLOY_PLUGIN="$(mktemp -d)/linuxdeploy-plugin-appimage.AppImage"

echo "[1/4] Скачиваем linuxdeploy..."
curl -fsSL "${LINUXDEPLOY_URL}" -o "${LINUXDEPLOY_BIN}"
chmod +x "${LINUXDEPLOY_BIN}"

echo "[2/4] Скачиваем плагин appimage..."
curl -fsSL "${LINUXDEPLOY_PLUGIN_URL}" -o "${LINUXDEPLOY_PLUGIN}"
chmod +x "${LINUXDEPLOY_PLUGIN}"

# Распаковываем плагин в стандартную директорию linuxdeploy
PLUGIN_EXTRACT="$(mktemp -d)"
( cd "${PLUGIN_EXTRACT}" && "${LINUXDEPLOY_PLUGIN}" --appimage-extract 2>/dev/null ) || true
mkdir -p "${HOME}/.linuxdeploy/plugins"
find "${PLUGIN_EXTRACT}/squashfs-root" -name "libappimage.so" -exec cp {} "${HOME}/.linuxdeploy/plugins/" \; 2>/dev/null || true
rm -rf "${PLUGIN_EXTRACT}"

# --- Создаём временную структуру ---
STAGING_DIR="$(mktemp -d)"
mkdir -p "${STAGING_DIR}/usr/bin"
mkdir -p "${STAGING_DIR}/usr/share/applications"
mkdir -p "${STAGING_DIR}/usr/share/icons/hicolor/scalable/apps"

# Копируем приложение
cp -a "${BUILD_DIR}/${APP_NAME}/" "${STAGING_DIR}/usr/bin/"

# Desktop файл
cp "graphics_editor.desktop" "${STAGING_DIR}/usr/share/applications/${APP_NAME}.desktop"

# Иконка
cp "icons/graphics_editor.svg" "${STAGING_DIR}/usr/share/icons/hicolor/scalable/apps/${APP_NAME}.svg"

# --- Собираем AppImage ---
echo "[3/4] Собираем AppImage..."
APPIMAGE_FILE="${STAGING_DIR}/${APP_NAME}.AppImage"

LINUXDEPLOY_LIBRARY_PATH="${HOME}/.linuxdeploy/plugins" \
"${LINUXDEPLOY_BIN}" \
    --appdir "${STAGING_DIR}" \
    -d "${STAGING_DIR}/usr/share/applications/${APP_NAME}.desktop" \
    -i "${STAGING_DIR}/usr/share/icons/hicolor/scalable/apps/${APP_NAME}.svg" \
    -o appimage

# --- Копируем результат ---
echo "[4/4] Копируем результат..."
mv "${APPIMAGE_FILE}" "${OUTPUT_DIR}/${APP_NAME}-${APPIMAGE_ARCH}.AppImage"
chmod +x "${OUTPUT_DIR}/${APP_NAME}-${APPIMAGE_ARCH}.AppImage"

# --- Чистим ---
rm -rf "${STAGING_DIR}" "$(dirname "${LINUXDEPLOY_BIN}")" "$(dirname "${LINUXDEPLOY_PLUGIN}")"

echo "✅ Готово: ${OUTPUT_DIR}/${APP_NAME}-${APPIMAGE_ARCH}.AppImage"
echo "   Размер: $(du -h "${OUTPUT_DIR}/${APP_NAME}-${APPIMAGE_ARCH}.AppImage" | cut -f1)"
