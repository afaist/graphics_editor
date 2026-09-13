"""Единая фабрика фигур — глобальная регистрация и создание по типу."""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional

from shapes.base_shape import BaseShape


class ShapeRegistry:
    """Глобальная реестр фабрик фигур — единственная точка создания фигур по типу."""

    _factories: Dict[str, Callable[[Dict[str, Any]], BaseShape]] = {}

    @classmethod
    def register(
        cls, shape_type: str, from_dict_fn: Callable[[Dict[str, Any]], BaseShape]
    ) -> None:
        """Зарегистрировать фабрику для типа фигуры."""
        cls._factories[shape_type] = from_dict_fn

    @classmethod
    def get_factory(
        cls, shape_type: str
    ) -> Optional[Callable[[Dict[str, Any]], BaseShape]]:
        """Получить фабрику по типу фигуры."""
        return cls._factories.get(shape_type)

    @classmethod
    def create(cls, shape_type: str, data: Dict[str, Any]) -> Optional[BaseShape]:
        """Создать фигуру по типу и данным."""
        factory = cls._factories.get(shape_type)
        if factory is None:
            return None
        return factory(data)

    @classmethod
    def register_all(cls) -> None:
        """Зарегистрировать все встроенные фигуры."""
        from shapes.point_shape import PointShape
        from shapes.line_shape import LineShape
        from shapes.rectangle_shape import RectangleShape
        from shapes.ellipse_shape import EllipseShape
        from shapes.polygon_shape import PolygonShape
        from shapes.polyline_shape import PolylineShape
        from shapes.arc_shape import ArcShape
        from shapes.text_shape import TextShape
        from shapes.bezier_shape import BezierShape

        cls._factories = {
            "point": PointShape.from_dict,
            "line": LineShape.from_dict,
            "ray": LineShape.from_dict,
            "infinite_line": LineShape.from_dict,
            "rectangle": RectangleShape.from_dict,
            "ellipse": EllipseShape.from_dict,
            "polygon": PolygonShape.from_dict,
            "polyline": PolylineShape.from_dict,
            "arc": ArcShape.from_dict,
            "text": TextShape.from_dict,
            "bezier": BezierShape.from_dict,
        }

    @classmethod
    def clear(cls) -> None:
        """Очистить реестр (для тестов)."""
        cls._factories.clear()

    # ------------------------------------------------------------------
    # Кэшированные ссылки на классы фигур
    # ------------------------------------------------------------------

    _shape_classes: Dict[str, type] = {}

    @classmethod
    def _cache_shape_classes(cls) -> None:
        """Кэшировать ссылки на классы фигур при первом обращении."""
        if not cls._shape_classes:
            from shapes.point_shape import PointShape
            from shapes.line_shape import LineShape
            from shapes.rectangle_shape import RectangleShape
            from shapes.ellipse_shape import EllipseShape
            from shapes.polygon_shape import PolygonShape
            from shapes.polyline_shape import PolylineShape
            from shapes.arc_shape import ArcShape
            from shapes.text_shape import TextShape
            from shapes.bezier_shape import BezierShape

            cls._shape_classes = {
                "point": PointShape,
                "line": LineShape,
                "rectangle": RectangleShape,
                "ellipse": EllipseShape,
                "polygon": PolygonShape,
                "polyline": PolylineShape,
                "arc": ArcShape,
                "text": TextShape,
                "bezier": BezierShape,
            }

    @classmethod
    def get_shape_class(cls, shape_type: str) -> Optional[type]:
        """Получить класс фигуры по типу (для isinstance)."""
        cls._cache_shape_classes()
        return cls._shape_classes.get(shape_type)
