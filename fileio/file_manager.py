"""FileManager — сохранение, загрузка и экспорт проектов."""


from __future__ import annotations

import json
import math
from typing import Any, Callable, Dict, List, Optional
import os

from PySide6.QtCore import QFile, QIODevice, QPointF, QSize, Qt
from PySide6.QtGui import QImage, QPainter, QPen

from shapes.base_shape import BaseShape
from manager.shape_manager import ShapeManager


class FileManager:
    """Сохранение/загрузка проектов и экспорт."""

    # Сопоставление type -> from_dict
    _shape_factory: Dict[str, Callable] = {}
    def __init__(self):
        self._current_filepath: Optional[str] = None


    @classmethod
    def register_factory(cls, shape_type: str, from_dict_fn):
        cls._shape_factory[shape_type] = from_dict_fn

    @classmethod
    def import_shapes(cls):
        """Импортировать все модули фигур и зарегистрировать фабрики."""
        from shapes.point_shape import PointShape
        from shapes.line_shape import LineShape
        from shapes.rectangle_shape import RectangleShape
        from shapes.ellipse_shape import EllipseShape
        from shapes.polygon_shape import PolygonShape
        from shapes.polyline_shape import PolylineShape

        cls._shape_factory = {
            "point": PointShape.from_dict,
            "line": LineShape.from_dict,
            "rectangle": RectangleShape.from_dict,
            "ellipse": EllipseShape.from_dict,
            "polygon": PolygonShape.from_dict,
            "polyline": PolylineShape.from_dict,
        }

    @property
    def has_current_file(self) -> bool:
        """Проверяет, загружен ли текущий файл проекта."""
        return self._current_filepath is not None

    @property
    def current_filepath(self) -> Optional[str]:
        """Возвращает путь к текущему файлу проекта."""
        return self._current_filepath

    @current_filepath.setter
    def current_filepath(self, filepath: Optional[str]):
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
        except IOError as e:
            print(f"Save error: {e}")
            return False

    # ------------------------------------------------------------------
    # Загрузка из JSON (внутренний метод)
    # ------------------------------------------------------------------

    @classmethod
    def load_json(cls, manager: ShapeManager, filepath: str) -> bool:
        cls.import_shapes()
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            print(f"Load error: {e}")
            return False

        # очищаем текущие фигуры
        manager.remove_all()

        shapes_data = data.get("shapes", [])
        for shape_data in shapes_data:
            shape_type = shape_data.get("type")
            factory = cls._shape_factory.get(shape_type)
            if factory is None:
                print(f"Unknown shape type: {shape_type}")
                continue
            try:
                shape = factory(shape_data)
                manager.add_shape(shape)
            except Exception as e:
                print(f"Error loading shape: {e}")
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
            filepath: путь к файлу проекта (.json)

        Returns:
            bool: True при успешной загрузке, False при ошибке
        """
        return cls.load_json(manager, filepath)

    @classmethod
    def save_project(cls, manager: ShapeManager, filepath: str) -> bool:
        """
        Публичный метод для сохранения проекта.

        Args:
            manager: экземпляр ShapeManager с фигурами
            filepath: путь для сохранения файла (.json)

        Returns:
            bool: True при успешной записи, False при ошибке
        """
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
        if self.save_json(manager, filepath):
            self.current_filepath = filepath
            return True
        return False


    # ------------------------------------------------------------------
    # Экспорт в PNG
    # ------------------------------------------------------------------

    @staticmethod
    def export_png(manager: ShapeManager, filepath: str,
                   width: int = 1920, height: int = 1080) -> bool:
        """
        Экспорт фигур в PNG.
        """
        try:
            from PySide6.QtWidgets import QGraphicsScene
            from PySide6.QtGui import QPainter, QColor, QImage, QImageWriter
            from PySide6.QtCore import QRectF
            
            from ui.scene_items import ShapeSceneItem

            # 1. Создаём сцену с белым фоном
            scene = QGraphicsScene()
            scene.setBackgroundBrush(QColor(0xFFFFFF))

            # 2. Добавляем фигуры на сцену
            for shape in manager.shapes:
                item = ShapeSceneItem(shape)
                item.setZValue(0)
                scene.addItem(item)

            # 3. Получаем границы всех объектов
            rect = scene.itemsBoundingRect()
            
            # Если сцена пуста или bounds are empty, используем заданный размер
            if rect.isEmpty():
                rect = QRectF(0, 0, width, height)
            
            # Добавляем небольшой отступ (padding)
            padding = 10
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
                    raise IOError(f"Failed to save PNG to {filepath}: {writer.errorString()}")
                
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
    # Экспорт в SVG
    # ------------------------------------------------------------------

    @staticmethod
    def export_svg(manager: ShapeManager, filepath: str) -> bool:
        """
        Экспорт фигур в SVG через QSvgGenerator.
        Использует QGraphicsScene для корректного рендеринга трансформаций.
        """
        try:
            from PySide6.QtWidgets import QGraphicsScene
            from PySide6.QtSvg import QSvgGenerator
            from PySide6.QtGui import QPainter, QColor
            from PySide6.QtCore import QRectF

            from ui.scene_items import ShapeSceneItem

            # Создаём сцену с белым фоном
            scene = QGraphicsScene()
            scene.setBackgroundBrush(QColor(0xFFFFFF))

            # Добавляем фигуры на сцену
            for shape in manager.shapes:
                item = ShapeSceneItem(shape)
                item.setZValue(0)
                scene.addItem(item)

            rect = scene.itemsBoundingRect()
            if rect.isEmpty():
                rect = QRectF(0, 0, 1920, 1080)

            padding = 10
            export_rect = rect.adjusted(-padding, -padding, padding, padding)

            generator = QSvgGenerator()
            generator.setFileName(filepath)
            generator.setSize(QSize(int(export_rect.width()), int(export_rect.height())))
            generator.setViewBox(export_rect)
            generator.setTitle("Графический редактор — SVG экспорт")
            generator.setDescription("Экспорт из графического редактора")

            painter = QPainter(generator)
            scene.render(painter, export_rect, rect)
            painter.end()

            return True
        except Exception as e:
            print(f"SVG export error: {e}")
            import traceback
            traceback.print_exc()
            return False


    # ------------------------------------------------------------------    
    # Вспомогательные методы для работы с файлами
    # ------------------------------------------------------------------

    @staticmethod
    def get_supported_formats() -> Dict[str, str]:
        """
        Возвращает словарь поддерживаемых форматов экспорта.

        Returns:
            dict: сопоставление расширения файла и описания формата
        """
        return {
            ".json": "JSON Project File (*.json)",
            ".png": "PNG Image (*.png)",
            ".svg": "SVG Vector Graphic (*.svg)"
        }

    @classmethod
    def is_project_file(cls, filepath: str) -> bool:
        """
        Проверяет, является ли файл проектом (JSON).

        Args:
            filepath: путь к файлу для проверки

        Returns:
            bool: True если файл — проект, False иначе
        """
        if not filepath.lower().endswith('.json'):
            return False

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return 'version' in data and 'shapes' in data
        except (IOError, json.JSONDecodeError):
            return False

    @staticmethod
    def get_file_info(filepath: str) -> Optional[Dict[str, Any]]:
        """
        Получает информацию о файле проекта.

        Args:
            filepath: путь к файлу проекта

        Returns:
            dict или None: информация о проекте или None при ошибке
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {
                    'version': data.get('version', 'unknown'),
            'shape_count': len(data.get('shapes', [])),
            'file_size': os.path.getsize(filepath),
            'modified': os.path.getmtime(filepath)
        }
        except (IOError, json.JSONDecodeError, ImportError) as e:
            print(f"Error reading file info: {e}")
            return None

    # ------------------------------------------------------------------
    # Методы для работы с настройками
    # ------------------------------------------------------------------

    @staticmethod
    def save_settings(settings: Dict, filepath: str) -> bool:
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
        except IOError as e:
            print(f"Settings save error: {e}")
            return False

    @staticmethod
    def load_settings(filepath: str) -> Optional[Dict]:
        """
        Загрузка настроек приложения.

        Args:
            filepath: путь к файлу настроек

        Returns:
            dict или None: загруженные настройки или None при ошибке
        """
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            print(f"Settings load error: {e}")
            return None
