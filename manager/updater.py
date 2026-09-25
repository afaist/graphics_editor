"""Система проверки и установки обновлений через GitHub Releases."""

from __future__ import annotations

import json
import platform
import subprocess
import sys
import tempfile
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING
from urllib.error import URLError
from urllib.request import urlopen

if TYPE_CHECKING:
    from PySide6.QtCore import QObject

# ====================================================================
# Константы
# ====================================================================

GITHUB_API = "https://api.github.com/repos/afaist/graphics_editor/releases/latest"
LOCAL_VERSION = "1.0.2"

# ====================================================================
# Структуры данных
# ====================================================================


@dataclass(frozen=True)
class UpdateInfo:
    """Информация об обновлении."""

    version: str
    release_date: str
    download_url: str
    changelog: str
    is_newer: bool = True


# ====================================================================
# Утилиты сравнения версий
# ====================================================================


def _compare_versions(v1: str, v2: str) -> int:
    """Сравнить две строки версий.

    Возвращает:
        -1 если v1 < v2
         0 если v1 == v2
         1 если v1 > v2
    """
    parts1 = [int(x) for x in v1.split(".")]
    parts2 = [int(x) for x in v2.split(".")]

    # Дополнить нулями до одинаковой длины
    max_len = max(len(parts1), len(parts2))
    parts1.extend([0] * (max_len - len(parts1)))
    parts2.extend([0] * (max_len - len(parts2)))

    for a, b in zip(parts1, parts2):
        if a < b:
            return -1
        if a > b:
            return 1
    return 0


# ====================================================================
# Определение имени asset по платформе
# ====================================================================


def _get_asset_name() -> str:
    """Вернуть имя файла обновления для текущей платформы."""
    system = platform.system()
    if system == "Windows":
        return "graphics_editor.exe"
    elif system == "Linux":
        return "graphics_editor"
    elif system == "Darwin":
        return "graphics_editor.app"
    else:
        return "graphics_editor"


# ====================================================================
# Ядро системы обновлений
# ====================================================================


class Updater:
    """Проверка и установка обновлений через GitHub API."""

    def __init__(self, parent: QObject | None = None) -> None:
        self._parent = parent
        self._download_url: str | None = None
        self._download_path: Path | None = None

    # ------------------------------------------------------------------
    # Проверка обновлений
    # ------------------------------------------------------------------

    def check_for_updates(self) -> UpdateInfo | None:
        """Проверить GitHub API на наличие нового обновления.

        Возвращает UpdateInfo если найдено обновление, None если обновлений нет
        или произошла ошибка сети.
        """
        try:
            request = urlopen(GITHUB_API, timeout=10)
            if request.status != 200:
                return None

            data = json.loads(request.read().decode("utf-8"))
        except (URLError, TimeoutError, json.JSONDecodeError, OSError):
            # Сетевая ошибка — молча пропускаем
            return None

        # Извлекаем данные из GitHub API
        remote_version = data.get("tag_name", "").lstrip("v")
        if not remote_version:
            return None

        # Сравниваем версии
        cmp = _compare_versions(remote_version, LOCAL_VERSION)
        if cmp <= 0:
            # Нет новой версии
            return None

        # Ищем asset для текущей платформы
        asset_name = _get_asset_name()
        assets = data.get("assets", [])
        download_url = None
        for asset in assets:
            if asset.get("name") == asset_name:
                download_url = asset.get("browser_download_url")
                break

        if not download_url:
            # Asset не найден для этой платформы — пробуем первый доступный
            if assets:
                download_url = assets[0].get("browser_download_url")
            else:
                return None

        # Формируем changelog
        body = data.get("body", "")
        release_date = data.get("published_at", "")[:10] if data.get("published_at") else ""

        return UpdateInfo(
            version=remote_version,
            release_date=release_date,
            download_url=download_url,
            changelog=body,
            is_newer=True,
        )

    # ------------------------------------------------------------------
    # Скачивание обновления
    # ------------------------------------------------------------------

    def download_update(
        self,
        progress_callback: Callable[[float], None] | None = None,
    ) -> Path | None:
        """Скачать файл обновления.

        Args:
            progress_callback: callback(percent: float) -> None

        Возвращает путь к скачанному файлу или None при ошибке.
        """
        if not self._download_url:
            return None

        try:
            # Создаём временный файл
            tmp_dir = tempfile.mkdtemp(prefix="graphics_editor_update_")
            asset_name = _get_asset_name()
            tmp_path = Path(tmp_dir) / asset_name

            request = urlopen(self._download_url, timeout=60)
            total_size = int(request.headers.get("Content-Length", 0))
            downloaded = 0

            with open(tmp_path, "wb") as f:
                chunk_size = 8192
                while True:
                    chunk = request.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)

                    if total_size > 0 and progress_callback:
                        percent = (downloaded / total_size) * 100
                        progress_callback(percent)

            self._download_path = tmp_path
            return tmp_path

        except (URLError, TimeoutError, OSError):
            # Ошибка скачивания — очищаем временные файлы
            if tmp_path and tmp_path.exists():
                tmp_path.unlink()
            return None

    # ------------------------------------------------------------------
    # Применение обновления
    # ------------------------------------------------------------------

    def apply_update(self) -> bool:
        """Заменить текущий binary и перезапустить приложение.

        Возвращает True если успешно, False при ошибке.
        """
        if not self._download_path or not self._download_path.exists():
            return False

        try:
            # Определяем путь к текущему executable
            current_exe = Path(sys.executable)

            # Создаём скрипт-обёртку для замены и перезапуска
            wrapper = self._create_wrapper(current_exe)
            if wrapper is None:
                return False

            # Запускаем обёртку в фоне
            subprocess.Popen(
                [sys.executable, str(wrapper)],
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
            )

            # Завершаем текущий процесс
            if self._parent:
                self._parent.close()
            sys.exit(0)

        except Exception:
            return False

    def _create_wrapper(self, current_exe: Path) -> Path | None:
        """Создать скрипт-обёртку для замены binary и перезапуска."""
        wrapper_code = f"""
import os
import shutil
import sys
import time

current_exe = {str(current_exe)!r}
new_exe = {str(self._download_path)!r}
target_exe = {str(current_exe)!r}

try:
    # Небольшая задержка чтобы основной процесс закрылся
    time.sleep(1)

    # Копируем новый файл на место старого
    if os.path.exists(target_exe):
        os.replace(target_exe, target_exe + ".old")
    shutil.copy2(new_exe, target_exe)

    # Удаляем старый файл
    if os.path.exists(target_exe + ".old"):
        os.unlink(target_exe + ".old")

    # Перезапускаем приложение
    os.execv(target_exe, [target_exe] + sys.argv[1:])

except Exception as e:
    print(f"Ошибка обновления: {{e}}", file=sys.stderr)
    sys.exit(1)
"""
        tmp_dir = tempfile.mkdtemp(prefix="graphics_editor_update_")
        wrapper_path = Path(tmp_dir) / "update_wrapper.py"
        wrapper_path.write_text(wrapper_code, encoding="utf-8")
        return wrapper_path

    # ------------------------------------------------------------------
    # Очистка
    # ------------------------------------------------------------------

    def cleanup(self) -> None:
        """Очистить временные файлы."""
        if self._download_path and self._download_path.exists():
            try:
                self._download_path.unlink()
            except OSError:
                pass
            # Удаляем родительскую директорию
            try:
                self._download_path.parent.rmdir()
            except OSError:
                pass
