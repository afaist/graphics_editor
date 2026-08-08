"""Главное окно графического редактора."""

from __future__ import annotations
from typing import Optional

# PySide6 импорты
from PySide6.QtCore import Qt, QPointF, QRectF, Signal, QEvent
from PySide6.QtGui import (
    QAction,
    QColor,
    QKeySequence,
    QPainter,
    QPen,
    QWheelEvent,
    QUndoStack
)
from PySide6.QtWidgets import (
    QGraphicsView,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSplitter,
    QGraphicsScene,
    QStatusBar,
    QToolBar,
    QLabel,
    QFileDialog,
    QMessageBox,
    QDockWidget,
    QGroupBox,
    QComboBox,
    QPushButton,
    QUndoView,
    QCheckBox,
)
# Импорты модулей приложения
from shapes.base_shape import BaseShape, HandleType, ShapeType
from shapes.point_shape import PointShape
from shapes.line_shape import LineShape  # Import added
from shapes.rectangle_shape import RectangleShape
from shapes.ellipse_shape import EllipseShape
from shapes.polygon_shape import PolygonShape
from shapes.polyline_shape import PolylineShape  # Import added

from manager.shape_manager import ShapeManager
from canvas.graphics_canvas import GraphicsCanvas
from tools.tool_manager import ToolManager, ToolType as ToolTypeEnum
from fileio.file_manager import FileManager
from settings.settings import Settings
from ui.property_panel import PropertyPanel
from ui.scene_items import ShapeSceneItem


class MainWindow(QMainWindow):
    """Главное окно приложения."""

    # Константы размеров
    WINDOW_WIDTH = 1400
    WINDOW_HEIGHT = 900
    DOCK_WIDTH = 250

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Графический редактор")
        self.resize(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)

        # Инициализация компонентов
        self._settings = Settings()
        self._manager = ShapeManager()
        self._tool_manager = ToolManager()
        self._file_manager = FileManager()

        # UI компоненты
        self._scene: Optional[QGraphicsScene] = None
        self._canvas: Optional[GraphicsCanvas] = None
        self._property_panel: Optional[PropertyPanel] = None

        # Временные переменные для рисования
        self._is_drawing = False
        self._is_dragging = False  # Добавлено
        self._is_selecting = False  # Добавлено

        self._last_mouse_pos: Optional[QPointF] = None
        self._selection_rect: Optional[QGraphicsScene] = None
        self._temp_shape_item = None

        # Дополнительные переменные состояния
        self._selection_start_pos: Optional[QPointF] = None
        self._selection_rect_start: Optional[QPointF] = None

        # Инициализация
        self._setup_scene()
        self._setup_ui()
        self._setup_connections()
        self._update_statusbar()

    # ==================================================================
    # Сцена и холст
    # ==================================================================

    def _setup_scene(self):
        """Настройка графической сцены и холста."""
        self._scene = QGraphicsScene(self)
        self._scene.setBackgroundBrush(QColor(self._settings.canvas_background))
        self._canvas = GraphicsCanvas(self._scene, self._manager, self._settings, self)

        # Кастомная отрисовка сетки
        # self._canvas.draw_background = self._draw_grid

    def _draw_grid(self, painter: QPainter, rect: QRectF) -> None:
        """Отрисовка сетки на холсте."""
        if not self._settings.grid_visible:
            return

        painter.save()
        minor_color = QColor(self._settings.grid_color_minor)
        major_color = QColor(self._settings.grid_color_major)
        minor_sp = self._settings.grid_minor_spacing
        major_sp = self._settings.grid_spacing

        left = int(rect.left())
        top = int(rect.top())

        # Отрисовка мелких линий
        pen_minor = QPen(minor_color, 0.5)
        painter.setPen(pen_minor)
        self._draw_grid_lines(painter, left, top, rect, minor_sp)

        # Отрисовка крупных линий
        pen_major = QPen(major_color, 1.0)
        painter.setPen(pen_major)
        self._draw_grid_lines(painter, left, top, rect, major_sp)

        painter.restore()

    def _draw_grid_lines(
        self, painter: QPainter, left: int, top: int, rect: QRectF, spacing: int
    ) -> None:
        """Вспомогательный метод для отрисовки линий сетки."""
        # Вертикальные линии
        x = (left // spacing) * spacing
        while x < rect.right():
            painter.drawLine(int(x), int(rect.top()), int(x), int(rect.bottom()))
            x += spacing

        # Горизонтальные линии
        y = (top // spacing) * spacing
        while y < rect.bottom():
            painter.drawLine(int(rect.left()), int(y), int(rect.right()), int(y))
            y += spacing

    # ==================================================================
    # UI настройка
    # ==================================================================

    def _setup_ui(self):
        """Настройка пользовательского интерфейса."""
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Левая панель инструментов
        left_panel = self._create_toolbar_panel()
        splitter.addWidget(left_panel)

        # Холст
        if self._canvas is not None:
            splitter.addWidget(self._canvas)

        # Правая панель свойств
        self._create_property_panel(splitter)

        splitter.setStretchFactor(1, 1)  # Холст растягивается
        main_layout.addWidget(splitter)

        self._create_menu()
        self._create_statusbar()

    def _create_property_panel(self, splitter: QSplitter) -> None:
        """Создание панели свойств."""
        self._property_panel = PropertyPanel()
        right_dock = QDockWidget("Свойства", self)
        right_dock.setWidget(self._property_panel)
        right_dock.setFixedWidth(self.DOCK_WIDTH)
        splitter.addWidget(right_dock)

    def _create_toolbar_panel(self) -> QWidget:
        """Создание панели инструментов."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(4)

        # Группы инструментов
        layout.addWidget(self._create_tools_group())
        layout.addWidget(self._create_operations_group())
        layout.addWidget(self._create_view_group())

        layout.addStretch()
        return panel

    def _create_tools_group(self) -> QGroupBox:
        """Группа инструментов рисования."""
        group = QGroupBox("Инструменты")
        layout = QVBoxLayout()
        group.setLayout(layout)

        tools = [
            ("Выделение", "V", ToolTypeEnum.SELECT),
            ("Точка", "P", ToolTypeEnum.POINT),
            ("Отрезок", "L", ToolTypeEnum.LINE),
            ("Луч", "R", ToolTypeEnum.RAY),
            ("Прямая", "I", ToolTypeEnum.INFINITE_LINE),
            ("Прямоугольник", "Q", ToolTypeEnum.RECTANGLE),
            ("Эллипс", "E", ToolTypeEnum.ELLIPSE),
            ("Многоугольник", "G", ToolTypeEnum.POLYGON),
            ("Ломаная", "Y", ToolTypeEnum.POLYLINE),
        ]

        for name, shortcut, tool_type in tools:
            btn = self._add_tool_button(layout, name, shortcut, tool_type)
            # Сохраняем ссылку на кнопку в атрибуте объекта
            setattr(self, f"_btn_{tool_type.value.lower()}", btn)

        layout.addStretch()
        return group

    def _create_operations_group(self) -> QGroupBox:
        """Группа операций с фигурами."""
        group = QGroupBox("Операции")
        layout = QVBoxLayout()
        group.setLayout(layout)

        operations = [
            ("Удалить", self._delete_selected),
            ("Копировать", self._copy_selected),
            ("Вставить", self._paste_clipboard),
        ]

        for name, callback in operations:
            self._add_button(layout, name, callback)

        return group

    def _create_view_group(self) -> QGroupBox:
        """Группа настроек вида."""
        group = QGroupBox("Вид")
        layout = QVBoxLayout()
        group.setLayout(layout)

        view_actions = [
            ("Приблизить", self._canvas.zoom_in if self._canvas else None),
            ("Отдалить", self._canvas.zoom_out if self._canvas else None),
            ("Сбросить масштаб", self._canvas.reset_zoom if self._canvas else None),
        ]

        for name, callback in view_actions:
            self._add_button(layout, name, callback)

        # Чекбоксы
        self._chk_grid = self._add_checkbox(
            layout, "Сетка", self._settings.grid_visible, self._toggle_grid
        )
        self._chk_snap = self._add_checkbox(
            layout,
            "Привязка к сетке",
            self._settings.snap_to_grid,
            self._toggle_snap,
        )

        return group

    def _add_tool_button(
        self, layout: QVBoxLayout, name: str, shortcut: str, tool_type: ToolTypeEnum
    ) -> QPushButton:
        """Создание кнопки инструмента с автоматической настройкой."""
        btn = QPushButton(f"{name} ({shortcut})")
        btn.setCheckable(True)
        btn.setObjectName(str(tool_type.value))
        btn.clicked.connect(lambda checked, t=tool_type: self._set_tool(t))
        layout.addWidget(btn)
        return btn

    def _add_button(self, layout: QVBoxLayout, name: str, callback) -> QPushButton:
        """Создание обычной кнопки."""
        btn = QPushButton(name)
        if callback:
            btn.clicked.connect(callback)
        layout.addWidget(btn)
        return btn

    def _add_checkbox(
        self, layout: QVBoxLayout, name: str, checked: bool, callback
    ) -> QCheckBox:
        """Создание чекбокса."""
        cb = QCheckBox(name)
        cb.setChecked(checked)
        cb.stateChanged.connect(callback)
        layout.addWidget(cb)
        return cb

    # ==================================================================
    # Меню и статусбар
    # ==================================================================

    def _create_menu(self):
        """Создание главного меню."""
        menubar = self.menuBar()

        # Файл
        file_menu = menubar.addMenu("Файл")
        file_actions = [
            ("Новый", "Ctrl+N", self._new_project),
            ("Открыть...", "Ctrl+O", self._open_project),
            ("Сохранить", "Ctrl+S", self._save_project),
            ("Сохранить как...", "Ctrl+Shift+S", self._save_project_as),
            None,  # Сепаратор
            ("Экспорт в PNG...", "Ctrl+Shift+P", self._export_png),
            ("Экспорт в SVG...", "Ctrl+Shift+G", self._export_svg),
            None,  # Сепаратор
            ("Выход", "Ctrl+Q", self.close),
        ]
        self._add_menu_actions(file_menu, file_actions)

        # Правка
        edit_menu = menubar.addMenu("Правка")
        edit_actions = [
            ("Отменить", "Ctrl+Z", self._undo),
            ("Повторить", "Ctrl+Y", self._redo),
            None,
            ("Вырезать", "Ctrl+X", self._cut_selected),
            ("Копировать", "Ctrl+C", self._copy_selected),
            ("Вставить", "Ctrl+V", self._paste_clipboard),
            None,
            ("Удалить", "Delete", self._delete_selected),
            ("Выделить всё", "Ctrl+A", self._manager.select_all),
        ]
        self._add_menu_actions(edit_menu, edit_actions)

        # Вид
        view_menu = menubar.addMenu("Вид")
        if self._canvas is not None:
            view_actions = [
                ("Приблизить", "Ctrl+=", self._canvas.zoom_in),
                ("Отдалить", "Ctrl+-", self._canvas.zoom_out),
                ("Сбросить масштаб", "Ctrl+0", self._canvas.reset_zoom),
                None,
                ("Сетка", None, self._toggle_grid),
            ]
            self._add_menu_actions(view_menu, view_actions)

    def _add_menu_actions(self, menu, actions: list) -> None:
        """Вспомогательный метод для добавления действий в меню."""
        for action_data in actions:
            if action_data is None:  # Сепаратор
                menu.addSeparator()
                continue

            name, shortcut, callback = action_data
            action = QAction(name, self)
            if shortcut:
                action.setShortcut(shortcut)
            action.triggered.connect(callback)
            menu.addAction(action)

            # Для чекбоксов в меню
            if name == "Сетка":
                action.setCheckable(True)
                action.setChecked(self._settings.grid_visible)

    def _create_statusbar(self):
        """Создание статусбара."""
        self._status = self.statusBar()
        self._status_label = QLabel("Готово")
        self._coords_label = QLabel("X: 0  Y: 0")
        self._zoom_label = QLabel("Масштаб: 100%")

        self._status.addPermanentWidget(self._coords_label)
        self._status.addPermanentWidget(self._zoom_label)
        self._status.addWidget(self._status_label)

    # ==================================================================
    # Соединения сигналов
    # ==================================================================
    # ... existing code ...

    def _setup_connections(self):
        """Настройка соединений сигналов."""
        if not hasattr(self._manager.shapes_changed, "connect"):
            raise AttributeError(
                "shapes_changed signal is not properly initialized in ShapeManager"
            )

        # Get canvas once to satisfy type checker
        canvas = self._canvas
        if canvas is None:
            raise AttributeError("Canvas is not initialized")

        # Get property panel once to satisfy type checker
        property_panel = self._property_panel
        if property_panel is None:
            raise AttributeError("Property panel is not initialized")

        connections = [
            (self._manager.shapes_changed, self._on_shapes_changed),
            (self._manager.selection_changed, self._on_selection_changed),
            (self._tool_manager.tool_changed, self._on_tool_changed),
            (canvas.mouse_position_changed, self._on_mouse_position_changed),
            (canvas.zoom_changed, self._on_zoom_changed),
            (property_panel.properties_changed, self._on_properties_changed),
            # Подключаем события мыши
            (canvas.mouse_pressed, self._on_canvas_mouse_press),
            (canvas.mouse_moved, self._on_canvas_mouse_move),
            (canvas.mouse_released, self._on_canvas_mouse_release),
        ]

        for signal, slot in connections:
            signal.connect(slot)

        # Привязка к сцене
        if canvas:
            canvas.viewport().installEventFilter(self)

    # ==================================================================
    # Инструменты и обработка событий
    # ==================================================================

    def _set_tool(self, tool_type: ToolTypeEnum):
        """Установка текущего инструмента."""
        self._tool_manager.current_tool = tool_type

        # Обновление состояния кнопок
        for tool in ToolTypeEnum:
            btn_attr = f"_btn_{tool.value.lower()}"
            if hasattr(self, btn_attr):
                btn = getattr(self, btn_attr)
                btn.setChecked(tool_type.value == self._tool_manager.current_tool.value)

        # Переключение режима перетаскивания холста:
        # SELECT - разрешаем панорамирование (ScrollHandDrag),
        # рисование - отключаем (NoDrag), чтобы не мешало рисованию.
        if tool_type == ToolTypeEnum.SELECT:
            if self._canvas:
                self._canvas.set_drag_mode(QGraphicsView.DragMode.ScrollHandDrag)
        else:
            if self._canvas:
                self._canvas.set_drag_mode(QGraphicsView.DragMode.NoDrag)

    def _on_shapes_changed(self):
        """Обработчик изменения списка фигур — ��ерерисовываем всю сцену."""
        self._sync_scene_with_manager()
        self._update_statusbar()

    def _sync_scene_with_manager(self):
        """Синхронизация QGraphicsScene с фигурами в ShapeManager."""
        if self._scene is None:
            return
        # Удаляем все старые ShapeSceneItem со сцены
        items_to_remove = [
            item for item in self._scene.items() if isinstance(item, ShapeSceneItem)
        ]
        for item in items_to_remove:
            self._scene.removeItem(item)
        # Добавляем ShapeSceneItem для каждой фигуры
        for shape in self._manager.shapes:
            scene_item = ShapeSceneItem(shape)
            scene_item.setZValue(0)  # базовый Z-уровень
            self._scene.addItem(scene_item)

    def _on_selection_changed(self):
        """Обработчик изменения выделения."""
        selected_count = len(self._manager.selected_shapes)
        if selected_count == 0:
            self._status_label.setText("Готово")
        else:
            self._status_label.setText(f"Выбрано фигур: {selected_count}")

    def _on_tool_changed(self, tool_type: ToolTypeEnum):
        """Обработчик смены инструмента."""
        # Итерируем по экземплярам Enum, а не по строковым значениям
        for tool in list(ToolTypeEnum):
            btn_attr = f"_btn_{tool.value}"  # Используем .value для формирования имени атрибута
            if hasattr(self, btn_attr):
                btn = getattr(self, btn_attr)
                # Сравниваем экземпляры Enum напрямую — это надёжнее
                btn.setChecked(tool == tool_type)

    def _on_mouse_position_changed(self, x: float, y: float):
        """Обновление координат курсора в статусбаре."""
        self._coords_label.setText(f"X: {x:.1f}  Y: {y:.1f}")

    def _on_zoom_changed(self, zoom_factor: float):
        """Обновление масштаба в статусбаре."""
        percentage = int(zoom_factor * 100)
        self._zoom_label.setText(f"Масштаб: {percentage}%")

    # ==================================================================
    # Обработка событий
    # ==================================================================

    def eventFilter(self, obj, event):
        """Фильтр событий для обработки мыши на холсте."""
        if (
            self._canvas is not None
            and obj == self._canvas.viewport()
            and event.type() == QEvent.Type.Wheel
        ):
            wheel_event = event
            if wheel_event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                # Масштабирование при зажатом Ctrl
                if wheel_event.angleDelta().y() > 0:
                    self._canvas.zoom_in()
                else:
                    self._canvas.zoom_out()
                return True
        return super().eventFilter(obj, event)

    # ==================================================================
    # Операции с фигурами
    # ==================================================================

    def _delete_selected(self):
        """Удаление выделенных фигур."""
        self._manager.delete_selected()

    def _copy_selected(self):
        """Копирование выделенных фигур."""
        self._manager.copy_selected()

    def _paste_clipboard(self):
        """Вставка из буфера обмена."""
        self._manager.paste_from_clipboard()

    def _cut_selected(self):
        """Вырезание выделенных фигур."""
        self._manager.cut_selected()

    # ==================================================================
    # Операции с проектом
    # ==================================================================

    def _new_project(self):
        """Создание нового проекта."""
        self._manager.remove_all()
        if self._scene is not None:
            self._scene.clear()
        self._update_statusbar()

    def _open_project(self):
        """Открытие проекта."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Открыть проект", "", "Графические проекты (*.gproj);;Все файлы (*.*)"
        )
        if file_path:
            try:
                self._file_manager.load_project(self._manager, file_path)
                self._update_statusbar()
            except Exception as e:
                QMessageBox.critical(
                    self, "Ошибка", f"Не удалось открыть файл: {str(e)}"
                )

    def _save_project(self):
        """Сохранение проекта."""
        if not self._file_manager.has_current_file:
            self._save_project_as()
        else:
            try:
                if self._file_manager.current_filepath:
                    self._file_manager.save_project(
                        self._manager, self._file_manager.current_filepath
                    )
            except Exception as e:
                QMessageBox.critical(
                    self, "Ошибка", f"Не удалось сохранить файл: {str(e)}"
                )

    def _save_project_as(self):
        """Сохранение проекта как..."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить проект как...",
            "",
            "Графические проекты (*.gproj);;Все файлы (*.*)",
        )
        if file_path:
            try:
                self._file_manager.save_project_as(file_path, self._manager)
            except Exception as e:
                QMessageBox.critical(
                    self, "Ошибка", f"Не удалось сохранить файл: {str(e)}"
                )

    def _export_png(self):
        """Экспорт в PNG."""
        if self._canvas is None:
            QMessageBox.warning(
                self, "Предупреждение", "Нет активного холста для экспорта."
            )
            return
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Экспорт в PNG", "", "PNG изображения (*.png);;Все файлы (*.*)"
        )
        if file_path:
            try:
                self._canvas.export_to_png(file_path)
            except Exception as e:
                QMessageBox.critical(
                    self, "Ошибка", f"Не удалось экспортировать в PNG: {str(e)}"
                )

    def _export_svg(self):
        """Экспорт в SVG."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Экспорт в SVG", "", "SVG изображения (*.svg);;Все файлы (*.*)"
        )
        if file_path:
            if self._canvas is None:
                QMessageBox.warning(self, "Ошибка", "Нет активного холста.")
                return
            try:
                self._canvas.export_to_svg(file_path)
            except Exception as e:
                QMessageBox.critical(
                    self, "Ошибка", f"Не удалось экспортировать в SVG: {str(e)}"
                )

    # ==================================================================
    # Настройки вида
    # ==================================================================

    def _toggle_grid(self, state: int):
        """Переключение видимости сетки."""
        visible = state == Qt.CheckState.Checked.value
        self._settings.grid_visible = visible
        if self._canvas:
            self._canvas.update()

    def _toggle_snap(self, state: int):
        """Переключение привязки к сетке."""
        snap = state == Qt.CheckState.Checked.value
        self._settings.snap_to_grid = snap

    # ==================================================================
    # Вспомогательные методы
    # ==================================================================

    def _update_statusbar(self):
        """Обновление статусбара."""
        shape_count = len(self._manager.shapes)
        self._status_label.setText(f"Фигур: {shape_count}")

    # ==================================================================
    # Обработка рисования на холсте
    # ==================================================================

    def _on_canvas_mouse_press(self, event):
        """Обработка нажатия мыши на холсте."""
        if self._canvas is None:
            return
        pos = self._canvas.mapToScene(event.pos())
        shift_pressed = event.modifiers() & Qt.KeyboardModifier.ShiftModifier

        current_tool = self._tool_manager.current_tool

        # Убедимся, что сбросили старые состояния перед началом
        # self._is_dragging и self._is_selecting должны быть False для инструментов рисования

        if current_tool == ToolTypeEnum.SELECT:
            self._handle_selection_press(pos, shift_pressed)
        else:
            # Сбрасываем состояния выделения перед рисованием
            self._is_dragging = False
            self._is_selecting = False
            print(f"Starting draw with tool {current_tool} at {pos}")
            self._start_drawing(pos, shift_pressed)
            print(f"After start, is_drawing: {self._is_drawing}")

    def _handle_selection_press(self, pos: QPointF, shift_pressed: bool):
        """Обработка выделения фигур."""
        hit_shape = self._manager.hit_test(pos)

        if hit_shape:
            if shift_pressed:
                self._manager.toggle_selection(hit_shape.id)
            else:
                if hit_shape.id not in self._manager.selected_ids:
                    self._manager.select_shape(hit_shape.id)
                # Запоминаем начальную позицию для перемещения
                self._selection_start_pos = pos
                self._is_dragging = False
        else:
            # Начало выделения рамкой
            if not shift_pressed:
                self._manager.select_none()
            self._selection_rect_start = pos
            self._is_selecting = True

    def _start_drawing(self, pos: QPointF, shift_pressed: bool):
        """Начало рисования новой фигуры."""
        self._is_drawing = True
        self._tool_manager.start_shape(pos, self._settings)
        self._update_temp_shape()

    def _on_canvas_mouse_move(self, event):
        """Обработка движения мыши на холсте."""
        if self._canvas is None:
            return
        pos = self._canvas.mapToScene(event.pos())
        self._last_mouse_pos = pos
        shift_pressed = event.modifiers() & Qt.KeyboardModifier.ShiftModifier

        current_tool = self._tool_manager.current_tool

        # Если мы в режиме SELECT и перетаскиваем фигуру
        if current_tool == ToolTypeEnum.SELECT and self._is_dragging:
            self._move_selected_shapes(pos)
        # Если мы рисуем новую фигуру
        elif self._is_drawing and self._tool_manager.temp_shape is not None:
            self._continue_drawing(pos, shift_pressed)
        else:
            # Отладка: если не рисуем и не двигаем, проверяем почему
            # print(f"DEBUG: tool={current_tool}, is_drawing={self._is_drawing}, temp_shape={self._tool_manager.temp_shape is not None}")
            pass

    def _move_selected_shapes(self, current_pos: QPointF):
        """Перемещение выделенных фигур."""
        if self._selection_start_pos is None:
            return
        dx = current_pos.x() - self._selection_start_pos.x()
        dy = current_pos.y() - self._selection_start_pos.y()

        if abs(dx) > 3 or abs(dy) > 3:  # Порог для начала перемещения
            self._is_dragging = True
            self._manager.move_selected(dx, dy)
            self._selection_start_pos = current_pos

    def _continue_drawing(self, pos: QPointF, shift_pressed: bool):
        """Продолжение рисования фигуры."""
        self._tool_manager.update_shape(pos, shift_pressed)
        self._update_temp_shape()

    def _on_canvas_mouse_release(self, event):
        """Обработка отпускания кнопки мыши на холсте."""
        if self._canvas is None:
            return
        pos = self._canvas.mapToScene(event.pos())
        shift_pressed = event.modifiers() & Qt.KeyboardModifier.ShiftModifier

        current_tool = self._tool_manager.current_tool

        if current_tool == ToolTypeEnum.SELECT:
            if self._is_selecting:
                self._finish_selection_rectangle()
            elif self._is_dragging:
                self._is_dragging = False
        else:
            if self._is_drawing:
                self._finish_drawing(pos, shift_pressed)
            # Сбрасываем флаг рисования, даже если finish_drawing его уже сбросил (на всякий случай)
            self._is_drawing = False

    def _finish_selection_rectangle(self):
        """Завершение выделения рамкой."""
        if hasattr(self, "_selection_rect_start") and self._last_mouse_pos:
            if self._selection_rect_start is None:
                return
            start = self._selection_rect_start
            end = self._last_mouse_pos
            selection_rect = QRectF(
                min(start.x(), end.x()),
                min(start.y(), end.y()),
                abs(end.x() - start.x()),
                abs(end.y() - start.y()),
            )

            if selection_rect.width() > 5 or selection_rect.height() > 5:
                self._manager.select_by_rect(selection_rect)

        self._is_selecting = False

    def _finish_drawing(self, pos: QPointF, shift_pressed: bool):
        """Завершение рисования фигуры."""
        current_tool = self._tool_manager.current_tool
        shape = None

        if current_tool in (ToolTypeEnum.POLYGON, ToolTypeEnum.POLYLINE):
            shape = self._tool_manager.finish_current_shape()
        else:
            shape = self._tool_manager.finish_shape(pos)

        if shape is None:
            self._is_drawing = False
            return

        # Добавление фигуры в менеджер
        if isinstance(shape, PointShape):
            # Для точки вызываем публичный метод MainWindow
            self.add_shape(shape)
            self._clear_temp_shape()
        else:
            # Простая проверка на минимальный размер
            br = shape.bounding_rect()
            w = br.width()
            h = br.height()

            # Check for length attribute specifically for shapes that have it
            if isinstance(shape, (LineShape, PolylineShape)):
                # Важно: используем публичный метод add_shape, чтобы обновить сцену
                if shape.length() > 1.0:
                    self.add_shape(shape)  # <--- ИЗМЕНЕНИЕ ЗДЕСЬ
                    self._clear_temp_shape()
            elif w > 1 or h > 1:
                self.add_shape(shape)  # <--- И ЗДЕСЬ
                self._clear_temp_shape()

        self._is_drawing = False

    # ==================================================================
    # Временные фигуры
    # ==================================================================

    def _update_temp_shape(self):
        """Обновление временной фигуры на сцене."""
        self._clear_temp_shape()

        temp_shape = self._tool_manager.temp_shape
        if temp_shape is None:
            return

        if self._scene is None:
            return

        item = ShapeSceneItem(temp_shape)
        item.setZValue(1000)  # Поверх всех фигур
        self._scene.addItem(item)
        self._temp_shape_item = item

    def _clear_temp_shape(self):
        """Очистка временной фигуры."""
        if hasattr(self, "_temp_shape_item") and self._temp_shape_item is not None:
            try:
                if self._scene and self._temp_shape_item.scene() == self._scene:
                    self._scene.removeItem(self._temp_shape_item)
            except RuntimeError:
                # Объект уже удалён — игнорируем
                pass
            finally:
                self._temp_shape_item = None

    # ==================================================================
    # Отмена/повтор
    # ==================================================================

    def _undo(self):
        """Отмена последнего действия."""
        if self._manager.undo_stack.canUndo:
            self._manager.undo_stack.undo()
            self._update_statusbar()

    def _redo(self):
        """Повтор отменённого действия."""
        if self._manager.undo_stack.canRedo:
            self._manager.undo_stack.redo()
            self._update_statusbar()

    # ==================================================================
    # Закрытие приложения
    # ==================================================================

    def closeEvent(self, event):
        """Обработка закрытия окна приложения."""
        # Сохраняем настройки перед закрытием
        try:
            self._settings.save()  # Используем новый метод save()
        except Exception as e:
            QMessageBox.warning(
                self, "Предупреждение", f"Не удалось сохранить настройки: {e}"
            )

        # Спрашиваем подтверждение, если есть несохранённые изменения
        if self._has_unsaved_changes():
            reply = QMessageBox.question(
                self,
                "Подтверждение закрытия",
                "Есть несохранённые изменения. Выйти без сохранения?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.No:
                event.ignore()
                return

        event.accept()

    def _has_unsaved_changes(self) -> bool:
        """Проверка наличия несохранённых изменений."""
        # Здесь должна быть логика проверки изменений
        # Например, сравнение текущего состояния с последним сохранённым
        return False  # Заглушка — замените на реальную реализацию

    # ==================================================================
    # Вспомогательные методы
    # ==================================================================

    def _get_tool_button(self, tool_type: ToolTypeEnum) -> Optional[QPushButton]:
        """Получение кнопки инструмента по типу."""
        btn_attr = f"_btn_{tool_type.value.lower()}"
        return getattr(self, btn_attr, None)

    def _refresh_canvas(self):
        """Принудительное обновление холста."""
        if self._canvas:
            self._canvas.update()

    def _reset_drawing_state(self):
        """Сброс состояния рисования."""
        self._is_drawing = False
        self._last_mouse_pos = None
        self._selection_rect_start = None
        self._selection_start_pos = None
        self._is_dragging = False
        self._is_selecting = False

        # Очищаем временные фигуры
        self._clear_temp_shape()

        # Уведомляем менеджер инструментов о сбросе
        self._tool_manager.reset_current_shape()

    def _update_property_panel(self):
        """Обновление панели свойств для выделенных фигур."""
        if self._property_panel is None:
            return

        selected_shapes = self._manager.selected_shapes
        if selected_shapes:
            # Если выделена одна фигура — показываем её свойства
            if len(selected_shapes) == 1:
                shape = selected_shapes[0]
                # Создаем словарь свойств из объекта фигуры
                props = self._get_shape_properties_dict(shape)
                self._property_panel.set_properties(props)
            else:
                # Если несколько — показываем общие свойства (например, цвет заливки)
                self._property_panel.set_multiple_shapes(selected_shapes)
        else:
            self._property_panel.clear()

    def _get_shape_properties_dict(self, shape: BaseShape) -> dict:
        """Вспомогательный метод для преобразования фигуры в словарь свойств."""
        # Получаем текущие значения из объекта фигуры
        pen_color = shape.pen_color
        if isinstance(pen_color, QColor):
            pen_color = (pen_color.red(), pen_color.green(), pen_color.blue())
        elif not isinstance(pen_color, tuple):
            pen_color = (0, 0, 0)  # fallback

        pen_width = shape.pen_width

        brush_color = shape.brush_color
        if isinstance(brush_color, QColor):
            brush_color = (brush_color.red(), brush_color.green(), brush_color.blue())
        elif brush_color is None:
            brush_color = None
        elif not isinstance(brush_color, tuple):
            brush_color = None  # fallback, если тип некорректный

        rotation = shape.rotation

        return {
            "pen_color": pen_color,
            "pen_width": pen_width,
            "brush_color": brush_color,
            "rotation": rotation,
        }

    # ... existing code ...

    # ==================================================================
    # Обработка изменений свойств фигур
    # ==================================================================

    def _on_properties_changed(self):
        """Обработчик изменения свойств фигуры через панель свойств."""
        selected_shapes = self._manager.selected_shapes
        if not selected_shapes:
            return

        try:
            # Получаем обновлённые свойства из панели
            if self._property_panel is None:
                QMessageBox.warning(self, "Ошибка", "Не активирована property_panel")
                return
            new_properties = self._property_panel.get_updated_properties()

            # Применяем изменения ко всем выделенным фигурам
            for shape in selected_shapes:
                shape.apply_properties(new_properties)

            # Обновляем сцену
            self._refresh_canvas()
            self._update_statusbar()

        except Exception as e:
            QMessageBox.warning(
                self, "Ошибка", f"Не удалось применить свойства: {str(e)}"
            )

    # ==================================================================
    # Вспомогательные методы для работы с координатами
    # ==================================================================

    def _snap_to_grid(self, pos: QPointF) -> QPointF:
        """Привязка координат к сетке, если включена."""
        if self._settings.snap_to_grid and self._settings.grid_spacing > 0:
            spacing = self._settings.grid_spacing
            x = round(pos.x() / spacing) * spacing
            y = round(pos.y() / spacing) * spacing
            return QPointF(x, y)
        return pos

    def _get_snapped_position(self, event) -> QPointF:
        """Получение позиции с учётом привязки к сетке."""
        if self._canvas is None:
            return QPointF(0, 0)
        pos = self._canvas.mapToScene(event.pos())
        return self._snap_to_grid(pos)

    # ==================================================================
    # Методы для работы с undo/redo
    # ==================================================================

    def _setup_undo_redo(self):
        """Настройка стека отмены/повтора."""
        undo_stack = QUndoStack(self)
        self._manager.undo_stack = undo_stack

        # Добавляем панель просмотра истории действий
        undo_view = QUndoView(undo_stack)
        undo_dock = QDockWidget("История действий", self)
        undo_dock.setWidget(undo_view)
        undo_dock.setFixedWidth(200)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, undo_dock)

    # ==================================================================
    # Инициализация дополнительных компонентов
    # ==================================================================

    def _initialize_additional_components(self):
        """Инициализация дополнительных UI‑компонентов."""
        # Настройка панели истории действий
        self._setup_undo_redo()

        # Подключение сигналов менеджера фигур
        self._manager.shapes_changed.connect(self._update_property_panel)
        self._manager.selection_changed.connect(self._update_property_panel)

        # Обновление UI при старте
        self._update_property_panel()
        self._refresh_canvas()

    # ==================================================================
    # Переопределённые методы
    # ==================================================================

    def resizeEvent(self, event):
        """Обработка изменения размера окна."""
        super().resizeEvent(event)
        # При изменении размера окна обновляем отображение
        self._refresh_canvas()

    def showEvent(self, event):
        """Обработка показа окна."""
        super().showEvent(event)
        # При показе окна обновляем статусбар
        self._update_statusbar()

    # ==================================================================
    # Публичные методы для внешнего использования
    # ==================================================================

    def add_shape(self, shape: BaseShape):
        """Публичный метод для добавления фигуры извне."""
        self._manager.add_shape(shape)
        if self._scene:
            self._scene.update()
        self._update_statusbar()

    def clear_all(self):
        """Публичный метод для очистки всего холста."""
        reply = QMessageBox.question(
            self,
            "Подтверждение очистки",
            "Вы уверены, что хотите очистить весь холст?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._new_project()

    def export_to_png(self, file_path: str):
        """Публичный метод для экспорта в PNG."""
        if self._canvas is None:
            QMessageBox.warning(self, "Ошибка", "Нет активного canvas!")
            return
        try:
            self._canvas.export_to_png(file_path)
            QMessageBox.information(self, "Успех", "Файл успешно экспортирован в PNG")
        except Exception as e:
            QMessageBox.critical(
                self, "Ошибка", f"Не удалось экспортировать в PNG: {str(e)}"
            )

    def export_to_svg(self, file_path: str):
        """Публичный метод для экспорта в SVG."""
        if self._canvas is None:
            QMessageBox.warning(self, "Предупреждение", "Нет активного холста")
            return
        try:
            self._canvas.export_to_svg(file_path)
            QMessageBox.information(self, "Успех", "Файл успешно экспортирован в SVG")
        except Exception as e:
            QMessageBox.critical(
                self, "Ошибка", f"Не удалось экспортировать в SVG: {str(e)}"
            )


# ==================================================================
# Вспомогательные функции и константы
# ==================================================================


def create_main_window() -> MainWindow:
    """Фабрика для создания главного окна приложения."""
    return MainWindow()


# Конец файла
