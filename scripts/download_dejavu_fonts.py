#!/usr/bin/env python3
"""
Скрипт для загрузки DejaVu шрифтов в assets/fonts/dejavu/.
Используется для подготовки бандла шрифтов для PyInstaller.

Шрифты скачиваются с официального сайта DejaVu:
https://dejavu-fonts.github.io/
"""

import sys
import urllib.request
import zipfile
from pathlib import Path


def download_dejavu_fonts(output_dir: str = "assets/fonts/dejavu"):
    """Скачивает и распаковывает DejaVu шрифты."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Проверяем, есть ли уже шрифты
    ttf_files = list(output_path.glob("*.ttf"))
    if ttf_files:
        print(f"✓ DejaVu шрифты уже существуют в {output_dir} ({len(ttf_files)} файлов)")
        return

    print("Загрузка DejaVu шрифтов...")

    # URL для скачивания DejaVu Sans fonts (TTF version)
    # Используем GitHub release или source archive
    dejavu_version = "2.37"
    archive_url = (
        f"https://github.com/dejavu-fonts/dejavu-fonts/releases/"
        f"download/v{dejavu_version}/dejavu-fonts-ttf-2.37.zip"
    )

    archive_path = Path("dejavu-fonts.zip")

    try:
        # Скачиваем архив
        print(f"Скачивание: {archive_url}")
        urllib.request.urlretrieve(archive_url, archive_path)

        # Распаковываем только TTF шрифты
        with zipfile.ZipFile(archive_path, "r") as zip_ref:
            for file in zip_ref.namelist():
                if file.endswith(".ttf"):
                    # Извлекаем только файлы из директории ttf/
                    if "/ttf/" in file or file.count("/") <= 2:
                        zip_ref.extract(file, output_path)
                        print(f"  Извлечено: {file}")

        archive_path.unlink()
        print(f"✓ Завершено! Сохранено {len(list(output_path.glob('*.ttf')))} файлов")

    except Exception as e:
        print(f"✗ Ошибка загрузки: {e}", file=sys.stderr)
        if archive_path.exists():
            archive_path.unlink()
        sys.exit(1)


if __name__ == "__main__":
    output_dir = sys.argv[1] if len(sys.argv) > 1 else "assets/fonts/dejavu"
    download_dejavu_fonts(output_dir)
