"""FileManager — сохранение, загрузка и экспорт проектов."""

from __future__ import annotations

import json
import os
from typing import Any

from PySide6.QtCore import QRectF

from fileio.validators import validate_file_size, validate_project_data, validate_shape_data
from manager.shape_manager import ShapeManager
from shapes.registry import ShapeRegistry


class FileManager:
    """Сохранение/загрузка проектов и экспорт."""

    def __init__(self):
        self._current_filepath: str | None = None

    @property
    def has_current_file(self) -> bool:
        """Проверяет, загружен ли текущий файл проекта."""
        return self._current_filepath is not None

    @property
    def current_filepath(self) -> str | None:
        """Возвращает путь к текущему файлу проекта."""
        return self._current_filepath

    @current_filepath.setter
    def current_filepath(self, filepath: str | None):
        """Устанавливает путь к текущему файлу."""
        self._current_filepath = filepath

    # ------------------------------------------------------------------
    # Сохранение в JSON
    # ------------------------------------------------------------------

    @staticmethod
    def save_json(manager: ShapeManager, filepath: str) -> bool:
        data = {
            "version": "1.0",
            "shapes": [s.to_dict() for s in manager.shapes],
        }
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except OSError as e:
            print(f"Save error: {e}")
            return False

    # ------------------------------------------------------------------
    # Загрузка из JSON (внутренний метод)
    # ------------------------------------------------------------------

    @classmethod
    def load_json(cls, manager: ShapeManager, filepath: str) -> bool:
        """
        Загружает проект из JSON файла.

        Использует ShapeRegistry для создания фигур.
        """
        # Инициализируем реестр фигур
        ShapeRegistry.register_all()

        try:
            with open(filepath, encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            print(f"Load error: {e}")
            return False

        # Валидация размера файла
        size_warning = validate_file_size(filepath)
        if size_warning:
            print(f"File validation warning: {size_warning}")

        # Валидация корневых данных проекта
        try:
            warnings = validate_project_data(data)
            for w in warnings:
                print(f"Warning: {w}")
        except Exception as e:
            print(f"Invalid project file: {e}")
            return False

        # очищаем текущие фигуры
        manager.remove_all()

        shapes_data = data.get("shapes", [])
        loaded_count = 0
        skipped_count = 0

        for idx, shape_data in enumerate(shapes_data):
            # Валидация данных фигуры
            warning = validate_shape_data(shape_data, idx)
            if warning:
                print(f"Skipping shape #{idx}: {warning}")
                skipped_count += 1
                continue

            # Создаем фигуру через единый реестр
            shape_type = shape_data.get("type", "unknown")
            shape = ShapeRegistry.create(shape_type, shape_data)

            if shape is None:
                print(f"Failed to create shape of type {shape_type} from data: {shape_data}")
                skipped_count += 1
                continue

            manager.add_shape(shape)
            loaded_count += 1

        if skipped_count > 0:
            print(f"Loaded {loaded_count} shapes, skipped {skipped_count} invalid")

        return True

    # ------------------------------------------------------------------
    # Публичный метод загрузки проекта
    # ------------------------------------------------------------------

    @classmethod
    def load_project(cls, manager: ShapeManager, filepath: str) -> bool:
        """
        Публичный метод для загрузки проекта.

        Args:
            manager: экземпляр ShapeManager для загрузки фигур
            filepath: путь к файлу проекта (.gproj)

        Returns:
            bool: True при успешной загрузке, False при ошибке
        """
        return cls.load_json(manager, filepath)

    @staticmethod
    def _ensure_gproj_extension(filepath: str) -> str:
        """
        Добавляет расширение .gproj к пути, если его нет.

        Args:
        filepath: исходный путь к файлу

        Returns:
        str: путь с расширением .gproj
        """
        if not filepath.lower().endswith(".gproj"):
            filepath = os.path.splitext(filepath)[0] + ".gproj"
        return filepath

    @classmethod
    def save_project(cls, manager: ShapeManager, filepath: str) -> bool:
        """
        Публичный метод для сохранения проекта.

        Args:
        manager: экземпляр ShapeManager с фигурами
        filepath: путь для сохранения файла (.gproj)

        Returns:
        bool: True при успешной записи, False при ошибке
        """
        filepath = cls._ensure_gproj_extension(filepath)
        return cls.save_json(manager, filepath)

    def save_project_as(self, filepath: str, manager: ShapeManager) -> bool:
        """
        Сохраняет проект по новому пути и обновляет текущий путь.

        Args:
        filepath: новый путь для сохранения
        manager: менеджер фигур

        Returns:
        bool: True при успехе, False при ошибке
        """
        filepath = self._ensure_gproj_extension(filepath)
        if self.save_json(manager, filepath):
            self.current_filepath = filepath
            return True
        return False

    # ------------------------------------------------------------------
    # Экспорт в PNG
    # ------------------------------------------------------------------

    @staticmethod
    def export_png(
        manager: ShapeManager,
        filepath: str,
        region: str = "all_shapes",
        selected_ids: set[int] | None = None,
        viewport_rect: QRectF | None = None,
        width: int = 1920,
        height: int = 1080,
    ) -> bool:
        """
        Экспорт фигур в PNG.

        Args:
            manager: ShapeManager с фигурами
            filepath: путь для сохранения
            region: "all_shapes" | "selected" | "viewport"
            selected_ids: ID выделенных фигур (для region="selected")
            viewport_rect: прямоугольник viewport (для region="viewport")
            width: fallback width для пустой сцены
            height: fallback height для пустой сцены
        """
        try:
            from PySide6.QtGui import QColor, QImage, QImageWriter, QPainter
            from PySide6.QtWidgets import QGraphicsScene

            from ui.scene_items import ShapeSceneItem

            # 1. Создаём сцену с белым фоном
            scene = QGraphicsScene()
            scene.setBackgroundBrush(QColor(0xFFFFFF))

            # 2. Добавляем фигуры на сцену в зависимости от региона
            if region == "selected" and selected_ids:
                for shape in manager.shapes:
                    if shape.id in selected_ids:
                        item = ShapeSceneItem(shape)
                        item.setZValue(0)
                        scene.addItem(item)
            else:
                for shape in manager.shapes:
                    item = ShapeSceneItem(shape)
                    item.setZValue(0)
                    scene.addItem(item)

            # 3. Определяем область рендеринга
            if region == "viewport" and viewport_rect is not None:
                # Видимая область — используем переданный прямоугольник
                rect = viewport_rect
            else:
                # Все фигуры или выделенные — bounding rect
                rect = scene.itemsBoundingRect()

            # Если сцена пуста или bounds are empty, используем заданный размер
            if rect.isEmpty():
                rect = QRectF(0, 0, width, height)

            # Добавляем отступ (padding) — учитываем подписи вершин (~16px) + размер шрифта
            padding = 30
            rect.adjust(-padding, -padding, padding, padding)

            # Вычисляем размеры с гарантией минимум 1px
            img_width = max(int(rect.width()), 1)
            img_height = max(int(rect.height()), 1)

            # Для очень тонких линий/точек обеспечиваем минимальный размер для визуализации
            if img_width < 10:
                img_width = max(int(rect.width() + 20), 10)
            if img_height < 10:
                img_height = max(int(rect.height() + 20), 10)

            # Создаем QImage
            try:
                image = QImage(img_width, img_height, QImage.Format.Format_ARGB32_Premultiplied)
                image.fill(QColor(0xFFFFFF))

                painter = QPainter(image)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)

                # Рендерим сцену
                # Важно: renderMapping масштабирует содержимое scene rect в target rect
                scene.render(painter, QRectF(0, 0, img_width, img_height), rect)
                painter.end()

                # Используем QImageWriter для более надежного сохранения с явным форматом
                writer = QImageWriter(filepath)
                writer.setFormat(b"PNG")  # Явное указание формата в байтах
                writer.setQuality(95)

                if not writer.write(image):
                    raise OSError(f"Failed to save PNG to {filepath}: {writer.errorString()}")

                return True
            except Exception as img_err:
                print(f"QImage creation or rendering error: {img_err}")
                import traceback

                traceback.print_exc()
                return False

        except Exception as e:
            print(f"PNG export error: {e}")
            import traceback

            traceback.print_exc()
            return False

    # ------------------------------------------------------------------
    # Экспорт в SVG (Удален согласно пункту 1.3 плана)
    # ------------------------------------------------------------------
    # Примечание: Метод export_svg удален из FileManager.
    # Экспорт в SVG должен осуществляться через GraphicsCanvas.export_to_svg(),
    # который использует QSvgGenerator для корректного рендеринга с учетом
    # трансформаций и стилей UI.

    # ------------------------------------------------------------------
    # Вспомогательные методы для работы с файлами
    # ------------------------------------------------------------------

    @staticmethod
    def get_supported_formats() -> dict[str, str]:
        """
        Возвращает словарь поддерживаемых форматов экспорта.

        Returns:
            dict: сопоставление расширения файла и описания формата
        """
        return {
            ".gproj": "Графический проект (*.gproj)",
            ".png": "PNG Image (*.png)",
            # ".svg": "SVG Vector Graphic (*.svg)" Удалено, так как экспорт SVG теперь в Canvas
        }

    @classmethod
    def is_project_file(cls, filepath: str) -> bool:
        """
        Проверяет, является ли файл проектом (.gproj).

        Args:
        filepath: путь к файлу для проверки

        Returns:
        bool: True если файл — проект, False иначе
        """
        if not filepath.lower().endswith(".gproj"):
            return False

        try:
            with open(filepath, encoding="utf-8") as f:
                data = json.load(f)
                return "version" in data and "shapes" in data
        except (OSError, json.JSONDecodeError):
            return False

    @staticmethod
    def get_file_info(filepath: str) -> dict[str, Any] | None:
        """
        Получает информацию о файле проекта.

        Args:
            filepath: путь к файлу проекта

        Returns:
            dict или None: информация о проекте или None при ошибке
        """
        try:
            with open(filepath, encoding="utf-8") as f:
                data = json.load(f)
                return {
                    "version": data.get("version", "unknown"),
                    "shape_count": len(data.get("shapes", [])),
                    "file_size": os.path.getsize(filepath),
                    "modified": os.path.getmtime(filepath),
                }
        except (OSError, json.JSONDecodeError, ImportError) as e:
            print(f"Error reading file info: {e}")
            return None

    # ------------------------------------------------------------------
    # Методы для работы с настройками
    # ------------------------------------------------------------------

    @staticmethod
    def save_settings(settings: dict, filepath: str) -> bool:
        """
        Сохранение настроек приложения.

        Args:
            settings: словарь настроек
            filepath: путь для сохранения

        Returns:
            bool: True при успехе, False при ошибке
        """
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            return True
        except OSError as e:
            print(f"Settings save error: {e}")
            return False

    @staticmethod
    def load_settings(filepath: str) -> dict | None:
        """
        Загрузка настроек приложения.

        Args:
            filepath: путь к файлу настроек

        Returns:
            dict или None: загруженные настройки или None при ошибке
        """
        try:
            with open(filepath, encoding="utf-8") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            print(f"Settings load error: {e}")
            return None
