"""Тесты системы проверки обновлений (manager/updater.py)."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from manager.updater import (
    Updater,
    _compare_versions,
    _get_asset_name,
)
from ui.update_dialog import UpdateDialog

# ======================================================================
# Тесты: сравнение версий
# ======================================================================


class TestCompareVersions:
    """Тесты функции _compare_versions."""

    def test_equal_versions(self):
        assert _compare_versions("1.0.0", "1.0.0") == 0
        assert _compare_versions("1.0.2", "1.0.2") == 0

    def test_newer_version(self):
        assert _compare_versions("1.0.3", "1.0.2") == 1
        assert _compare_versions("2.0.0", "1.0.2") == 1
        assert _compare_versions("1.1.0", "1.0.2") == 1

    def test_older_version(self):
        assert _compare_versions("1.0.1", "1.0.2") == -1
        assert _compare_versions("1.0.0", "1.0.2") == -1
        assert _compare_versions("0.9.9", "1.0.0") == -1

    def test_different_length(self):
        assert _compare_versions("1.0", "1.0.0") == 0
        assert _compare_versions("1.0.0.1", "1.0.0") == 1
        assert _compare_versions("1.0.0", "1.0.0.1") == -1


# ======================================================================
# Тесты: определение имени asset
# ======================================================================


class TestGetAssetName:
    """Тесты функции _get_asset_name."""

    @patch("platform.system", return_value="Windows")
    def test_windows(self, mock_platform):
        assert _get_asset_name() == "graphics_editor.exe"

    @patch("platform.system", return_value="Linux")
    def test_linux(self, mock_platform):
        assert _get_asset_name() == "graphics_editor"

    @patch("platform.system", return_value="Darwin")
    def test_macos(self, mock_platform):
        assert _get_asset_name() == "graphics_editor.app"


# ======================================================================
# Тесты: Updater.check_for_updates
# ======================================================================


class TestCheckForUpdates:
    """Тесты метода check_for_updates."""

    def _mock_response(self, status: int, data: dict) -> MagicMock:
        """Создать мок HTTP-ответа."""
        mock = MagicMock()
        mock.status = status
        mock.read.return_value = json.dumps(data).encode("utf-8")
        return mock

    def _mock_github_release(
        self,
        version: str = "1.0.3",
        has_assets: bool = True,
        asset_name: str = "graphics_editor",
    ) -> dict:
        """Создать мок ответа GitHub API для релиза."""
        data: dict[str, object] = {
            "tag_name": f"v{version}",
            "published_at": "2026-09-25T10:00:00Z",
            "body": "## Изменения\n\n- Исправление бага\n- Новая фича",
            "assets": [],
        }
        if has_assets:
            data["assets"] = [
                {
                    "name": asset_name,
                    "browser_download_url": f"https://github.com/test/release/{asset_name}",
                }
            ]
        return data

    def test_newer_version_found(self):
        """Новая версия найдена — возвращается UpdateInfo."""
        mock_response = self._mock_response(
            200,
            self._mock_github_release(version="1.0.3"),
        )

        with patch("manager.updater.urlopen", return_value=mock_response):
            updater = Updater()
            result = updater.check_for_updates()

        assert result is not None
        assert result.version == "1.0.3"
        assert result.release_date == "2026-09-25"
        assert "Исправление бага" in result.changelog

    def test_no_newer_version(self):
        """Текущая версия — None."""
        mock_response = self._mock_response(
            200,
            self._mock_github_release(version="1.0.2"),
        )

        with patch("manager.updater.urlopen", return_value=mock_response):
            updater = Updater()
            result = updater.check_for_updates()

        assert result is None

    def test_older_version(self):
        """Старая версия — None."""
        mock_response = self._mock_response(
            200,
            self._mock_github_release(version="1.0.1"),
        )

        with patch("manager.updater.urlopen", return_value=mock_response):
            updater = Updater()
            result = updater.check_for_updates()

        assert result is None

    def test_network_error(self):
        """Сетевая ошибка — None."""
        from urllib.error import URLError

        with patch("manager.updater.urlopen", side_effect=URLError("No network")):
            updater = Updater()
            result = updater.check_for_updates()

        assert result is None

    def test_http_error(self):
        """HTTP 404 — None."""
        mock_response = MagicMock()
        mock_response.status = 404

        with patch("manager.updater.urlopen", return_value=mock_response):
            updater = Updater()
            result = updater.check_for_updates()

        assert result is None

    def test_no_assets(self):
        """Нет assets — None."""
        mock_response = self._mock_response(
            200,
            self._mock_github_release(version="1.0.3", has_assets=False),
        )

        with patch("manager.updater.urlopen", return_value=mock_response):
            updater = Updater()
            result = updater.check_for_updates()

        assert result is None


# ======================================================================
# Тесты: Updater.download_update
# ======================================================================


class TestDownloadUpdate:
    """Тесты метода download_update."""

    def test_download_without_url(self):
        """Скачивание без URL — None."""
        updater = Updater()
        result = updater.download_update()
        assert result is None

    def test_download_success(self, tmp_path: Path):
        """Успешное скачивание."""
        updater = Updater()
        updater._download_url = "https://example.com/update.exe"

        # Мок для urlopen — возвращаем байты
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.headers = {"Content-Length": "100"}
        mock_response.read.side_effect = [b"DATA" * 25, b""]

        progress_calls = []

        def on_progress(percent):
            progress_calls.append(percent)

        with patch("manager.updater.urlopen", return_value=mock_response):
            result = updater.download_update(progress_callback=on_progress)

        assert result is not None
        assert result.exists()
        assert len(progress_calls) > 0
        # Очистка
        updater.cleanup()

    def test_download_failure(self):
        """Ошибка скачивания — None."""
        updater = Updater()
        updater._download_url = "https://example.com/update.exe"

        from urllib.error import URLError

        with patch("manager.updater.urlopen", side_effect=URLError("Error")):
            result = updater.download_update()

        assert result is None


# ======================================================================
# Тесты: Updater.apply_update
# ======================================================================


class TestApplyUpdate:
    """Тесты метода apply_update."""

    def test_apply_without_download(self):
        """Применение без скачанного файла — False."""
        updater = Updater()
        result = updater.apply_update()
        assert result is False

    def test_apply_creates_wrapper(self, tmp_path: Path):
        """Применение создаёт скрипт-обёртку."""
        updater = Updater()
        # Создаём мок скачанного файла
        fake_download = tmp_path / "graphics_editor"
        fake_download.write_bytes(b"fake binary")
        updater._download_path = fake_download

        # apply_update вызывает sys.exit(0) — перехватываем
        with (
            patch("manager.updater.sys.exit"),
            patch("manager.updater.subprocess.Popen") as mock_popen,
            patch("manager.updater.Path.exists", return_value=True),
        ):
            updater.apply_update()
            # apply_update вызывает sys.exit(0), поэтому return не достигнут
            # Но мы проверяем что subprocess.Popen был вызван
            assert mock_popen.called


# ======================================================================
# Тесты: Updater.cleanup
# ======================================================================


class TestCleanup:
    """Тесты метода cleanup."""

    def test_cleanup_removes_temp_files(self, tmp_path: Path):
        """Очистка удаляет временные файлы."""
        updater = Updater()
        fake_download = tmp_path / "graphics_editor"
        fake_download.write_bytes(b"fake")
        updater._download_path = fake_download

        updater.cleanup()

        assert not fake_download.exists()

    def test_cleanup_no_path(self):
        """Очистка без пути — ничего не делает."""
        updater = Updater()
        # Не должно вызвать ошибку
        updater.cleanup()


# ======================================================================
# Тесты: UpdateDialog._format_changelog
# ======================================================================


class TestFormatChangelog:
    """Тесты форматирования changelog в HTML."""

    def test_empty_changelog(self):
        assert UpdateDialog._format_changelog("") == "<i>Нет подробностей</i>"
        assert UpdateDialog._format_changelog(None) == "<i>Нет подробностей</i>"

    def test_simple_list(self):
        text = "- Пункт 1\n- Пункт 2\n- Пункт 3"
        html = UpdateDialog._format_changelog(text)
        assert "<ul>" in html
        assert "<li>Пункт 1</li>" in html
        assert "<li>Пункт 2</li>" in html
        assert "</ul>" in html

    def test_mixed_content(self):
        text = "## Заголовок\n\n- Пункт 1\n\nОбычный текст"
        html = UpdateDialog._format_changelog(text)
        assert "<h3>Заголовок</h3>" in html
        assert "<li>Пункт 1</li>" in html
        assert "<p>Обычный текст</p>" in html

    def test_nested_headers(self):
        text = "### Подзаголовок\n\n- Список"
        html = UpdateDialog._format_changelog(text)
        assert "<h4>Подзаголовок</h4>" in html
        assert "<li>Список</li>" in html

    def test_star_list(self):
        text = "* Звёздочка 1\n* Звёздочка 2"
        html = UpdateDialog._format_changelog(text)
        assert "<li>Звёздочка 1</li>" in html
        assert "<li>Звёздочка 2</li>" in html
