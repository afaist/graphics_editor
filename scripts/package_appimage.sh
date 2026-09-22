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

# --- Создаём временную структуру AppDir ---
STAGING_DIR="$(mktemp -d)"
mkdir -p "${STAGING_DIR}/usr/bin"
mkdir -p "${STAGING_DIR}/usr/share/applications"
mkdir -p "${STAGING_DIR}/usr/share/icons/hicolor/scalable/apps"

# PyInstaller --onedir создаёт директорию dist/graphics_editor/
# Внутри неё лежит исполняемый файл graphics_editor
PYINSTALLER_DIR="${BUILD_DIR}/${APP_NAME}"

if [ ! -d "${PYINSTALLER_DIR}" ]; then
  echo "❌ Ошибка: директория не найдена: ${PYINSTALLER_DIR}" >&2
  echo "   Проверьте, что PyInstaller собрал приложение:" >&2
  echo "     python -m PyInstaller --onedir --name ${APP_NAME} main.py" >&2
  exit 1
fi

# Копируем всё содержимое PyInstaller-директории в AppDir
cp -a "${PYINSTALLER_DIR}/." "${STAGING_DIR}/usr/bin/"

# Убедимся, что главный бинарь исполняемый
BIN_DST="${STAGING_DIR}/usr/bin/${APP_NAME}"
if [ ! -x "${BIN_DST}" ]; then
  chmod +x "${BIN_DST}"
fi

# Диагностика: убедимся, что это валидный ELF
echo "--- Диагностика исполняемого файла ---"
file "${BIN_DST}"
head -c 4 "${BIN_DST}" | xxd
if ! file "${BIN_DST}" | grep -q "ELF"; then
  echo "❌ Ошибка: файл не является валидным ELF-бинарём (неверный заголовок)" >&2
  exit 1
fi

# Desktop файл
cp "graphics_editor.desktop" "${STAGING_DIR}/usr/share/applications/${APP_NAME}.desktop"

# Иконка
cp "icons/graphics_editor.svg" "${STAGING_DIR}/usr/share/icons/hicolor/scalable/apps/${APP_NAME}.svg"

# (Опционально) Если у тебя есть ресурсы (Python-код, шаблоны, конфиги), положи их сюда:
# mkdir -p "${STAGING_DIR}/opt/graphics_editor"
# cp -r "${BUILD_DIR}/resources/"* "${STAGING_DIR}/opt/graphics_editor/"

# --- Собираем AppImage ---
echo "[3/4] Собираем AppImage..."

LINUXDEPLOY_LIBRARY_PATH="${HOME}/.linuxdeploy/plugins" \
  "${LINUXDEPLOY_BIN}" \
    --appdir "${STAGING_DIR}" \
    -e "${STAGING_DIR}/usr/bin/${APP_NAME}" \
    -d "${STAGING_DIR}/usr/share/applications/${APP_NAME}.desktop" \
    -i "${STAGING_DIR}/usr/share/icons/hicolor/scalable/apps/${APP_NAME}.svg" \
    -o appimage

# --- Копируем результат ---
echo "[4/4] Копируем результат..."
mkdir -p "${OUTPUT_DIR}"

# AppImage может быть с другим именем (из Desktop Entry Name)
APPIMAGE_FOUND=0
for f in "${STAGING_DIR}"/*.AppImage; do
  [ -f "$f" ] || continue
  mv "$f" "${OUTPUT_DIR}/${APP_NAME}-${APPIMAGE_ARCH}.AppImage"
  chmod +x "${OUTPUT_DIR}/${APP_NAME}-${APPIMAGE_ARCH}.AppImage"
  APPIMAGE_FOUND=1
  break
done

if [ "$APPIMAGE_FOUND" -eq 0 ]; then
  echo "❌ Ошибка: AppImage не найден в ${STAGING_DIR}" >&2
  ls -la "${STAGING_DIR}" >&2
  exit 1
fi

# --- Чистим ---
rm -rf "${STAGING_DIR}" "$(dirname "${LINUXDEPLOY_BIN}")" "$(dirname "${LINUXDEPLOY_PLUGIN}")"

echo "✅ Готово: ${OUTPUT_DIR}/${APP_NAME}-${APPIMAGE_ARCH}.AppImage"
echo "   Размер: $(du -h "${OUTPUT_DIR}/${APP_NAME}-${APPIMAGE_ARCH}.AppImage" | cut -f1)"
