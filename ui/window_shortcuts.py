"""Модуль горячих клавиш (accelerator) графического редактора."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut

if TYPE_CHECKING:
    from ui.main_window import MainWindow


class ShortcutManager:
    """Управление горячими клавишами приложения."""

    def __init__(self, main_window: "MainWindow"):
        self._mw = main_window
        self._shortcuts: list[QShortcut] = []

    # ------------------------------------------------------------------
    # Создание и регистрация горячих клавиш
    # ------------------------------------------------------------------

    def setup_shortcuts(self) -> None:
        """Создание и регистрация всех горячих клавиш приложения."""
        mw = self._mw

        # ---- Файл ----
        self._add(mw, QKeySequence("Ctrl+N"), mw._new_project, "Создать новый проект")
        self._add(mw, QKeySequence("Ctrl+O"), mw._open_project, "Открыть проект")
        self._add(mw, QKeySequence("Ctrl+S"), mw._save_project, "Сохранить проект")
        self._add(
            mw, QKeySequence("Ctrl+Shift+S"), mw._save_project_as, "Сохранить как..."
        )
        self._add(mw, QKeySequence("Ctrl+Shift+P"), mw._export_png, "Экспорт в PNG")
        self._add(mw, QKeySequence("Ctrl+Shift+G"), mw._export_svg, "Экспорт в SVG")
        self._add(mw, QKeySequence("Ctrl+Q"), mw.close, "Выход")

        # ---- Правка ----
        self._add(mw, QKeySequence("Ctrl+Z"), mw._undo, "Отменить")
        self._add(mw, QKeySequence("Ctrl+Shift+Z"), mw._redo, "Повторить")
        self._add(mw, QKeySequence("Ctrl+Y"), mw._redo, "Повторить (альтернатива)")
        self._add(mw, QKeySequence("Ctrl+X"), mw._cut_selected, "Вырезать")
        self._add(mw, QKeySequence("Ctrl+C"), mw._copy_selected, "Копировать")
        self._add(mw, QKeySequence("Ctrl+V"), mw._paste_clipboard, "Вставить")
        self._add(mw, QKeySequence("Delete"), mw._delete_selected, "Удалить")
        self._add(
            mw,
            QKeySequence("Escape"),
            self._on_escape,
            "Снять выделение / отменить рисование",
        )

        # ---- Выделение ----
        self._add(mw, QKeySequence("Ctrl+A"), mw._manager.select_all, "Выделить всё")

        # ---- Вид (масштаб) ----
        if mw._canvas is not None:
            #self._add(mw, QKeySequence("Ctrl+="), mw._canvas.zoom_in, "Приблизить")
            self._add(mw, QKeySequence("Ctrl-="), mw._canvas.zoom_out, "Отдалить")
            self._add(
                mw, QKeySequence("Ctrl0="), mw._canvas.reset_zoom, "Сбросить масштаб"
            )
            self._add(mw, QKeySequence("Ctrl++"), mw._canvas.zoom_in, "Приблизить (+)")

        # ---- Инструменты (горячие клавиши для переключения инструментов) ----
        self._add_tool_shortcut(mw, "V", "select", mw._set_tool)
        self._add_tool_shortcut(mw, "P", "point", mw._set_tool)
        self._add_tool_shortcut(mw, "L", "line", mw._set_tool)
        self._add_tool_shortcut(mw, "R", "ray", mw._set_tool)
        self._add_tool_shortcut(mw, "I", "infinite_line", mw._set_tool)
        self._add_tool_shortcut(mw, "Q", "rectangle", mw._set_tool)
        self._add_tool_shortcut(mw, "E", "ellipse", mw._set_tool)
        self._add_tool_shortcut(mw, "A", "arc", mw._set_tool)
        self._add_tool_shortcut(mw, "G", "polygon", mw._set_tool)
        self._add_tool_shortcut(mw, "Y", "polyline", mw._set_tool)
        self._add_tool_shortcut(mw, "T", "text", mw._set_tool)
        self._add_tool_shortcut(mw, "8", "triangle_equilateral", mw._set_tool)
        self._add_tool_shortcut(mw, "9", "parallelogram", mw._set_tool)
        self._add_tool_shortcut(mw, "0", "trapezoid_isosceles", mw._set_tool)

    def _add(
        self,
        mw: "MainWindow",
        key_sequence: QKeySequence,
        slot,
        description: str = "",
    ) -> None:
        """Создать QShortcut и подключить к слоту."""
        shortcut = QShortcut(key_sequence, mw)
        shortcut.activated.connect(slot)
        shortcut.setContext(Qt.ShortcutContext.ApplicationShortcut)
        if description:
            shortcut.setObjectName(description)
        self._shortcuts.append(shortcut)

    def _add_tool_shortcut(
        self,
        mw: "MainWindow",
        key: str,
        tool_value: str,
        slot,
    ) -> None:
        """Создать горячую клавишу для переключения инструмента по одиночной букве."""
        shortcut = QShortcut(QKeySequence(key), mw)
        from tools.tool_manager import ToolType

        tool_type = ToolType(tool_value)
        shortcut.activated.connect(lambda _checked=False, t=tool_type: slot(t))
        shortcut.setContext(Qt.ShortcutContext.ApplicationShortcut)
        shortcut.setObjectName(tool_value)
        self._shortcuts.append(shortcut)

    # ------------------------------------------------------------------
    # Обработчик Escape
    # ------------------------------------------------------------------

    def _on_escape(self) -> None:
        """Обработчик Escape: снять выделение / отменить рисование."""
        mw = self._mw
        from tools.tool_manager import ToolType

        # Если рисуем — отменяем
        if mw._is_drawing:
            mw._is_drawing = False
            if mw._event_manager:
                mw._event_manager.clear_temp_shape()
                mw._tool_manager.reset_current_shape()
            return

        # Если выбран инструмент кроме выделения — переключаем на выделение
        if mw._tool_manager.current_tool != ToolType.SELECT:
            mw._set_tool(ToolType.SELECT)
            return

        # Иначе снимаем выделение
        mw._manager.select_none()

    # ------------------------------------------------------------------
    # Очистка
    # ------------------------------------------------------------------

    def cleanup(self) -> None:
        """Удаление всех горячих клавиш."""
        for shortcut in self._shortcuts:
            shortcut.deleteLater()
        self._shortcuts.clear()
