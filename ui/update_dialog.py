"""Диалог обновления приложения."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from manager.updater import UpdateInfo, Updater


class UpdateDialog(QDialog):
    """Диалог обновления: информация о новой версии + прогресс скачивания."""

    # Сигналы
    update_started = Signal()
    update_completed = Signal()

    def __init__(self, update_info: UpdateInfo, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._update_info = update_info
        self._updater = Updater(self)

        self.setWindowTitle("Обновление")
        self.setModal(True)
        self.resize(480, 400)
        self._build_ui()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Заголовок
        title = QLabel("Доступно обновление!")
        title.setFont(QFont("", 14, QFont.Weight.Bold))
        layout.addWidget(title)

        # Информация о версии
        version_label = QLabel(
            f"Версия {self._update_info.version}  ({self._update_info.release_date})"
        )
        layout.addWidget(version_label)

        # Разделитель
        layout.addWidget(QLabel(""))  # spacer

        # Changelog
        changelog_label = QLabel("Изменения:")
        changelog_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(changelog_label)

        self._changelog_text = QTextBrowser()
        self._changelog_text.setHtml(self._format_changelog(self._update_info.changelog))
        self._changelog_text.setMaximumHeight(150)
        layout.addWidget(self._changelog_text)

        # Прогресс-бар (скрыт по умолчанию)
        self._progress_bar = QProgressBar()
        self._progress_bar.setVisible(False)
        layout.addWidget(self._progress_bar)

        # Разделитель
        layout.addWidget(QLabel(""))  # spacer

        # Кнопки
        btn_layout = QVBoxLayout()
        btn_layout.addStretch()

        # Кнопка обновления
        self._btn_update = QPushButton("Обновить и перезапустить")
        self._btn_update.setStyleSheet(
            "QPushButton { background-color: #0078FF; color: white; "
            "font-weight: bold; padding: 8px; }"
        )
        self._btn_update.clicked.connect(self._on_update_clicked)
        btn_layout.addWidget(self._btn_update)

        # Кнопка «Позже»
        btn_later = QPushButton("Позже")
        btn_later.clicked.connect(self.reject)
        btn_layout.addWidget(btn_later)

        layout.addLayout(btn_layout)

    # ------------------------------------------------------------------
    # Обработчики
    # ------------------------------------------------------------------

    def _on_update_clicked(self) -> None:
        """Запустить скачивание и установку обновления."""
        self._btn_update.setEnabled(False)
        self._progress_bar.setVisible(True)
        self._progress_bar.setValue(0)

        # Скачиваем в фоне с обновлением прогресса
        def on_progress(percent: float) -> None:
            self._progress_bar.setValue(int(percent))

        downloaded_path = self._updater.download_update(progress_callback=on_progress)

        if downloaded_path is None:
            QMessageBox.critical(
                self,
                "Ошибка",
                "Не удалось скачать обновление. Проверьте подключение к интернету.",
            )
            self._btn_update.setEnabled(True)
            self._progress_bar.setVisible(False)
            return

        # Применяем обновление
        success = self._updater.apply_update()
        if not success:
            QMessageBox.warning(
                self,
                "Ошибка",
                "Не удалось применить обновление. Попробуйте скачать вручную.",
            )
            self._btn_update.setEnabled(True)
            return

        self.update_completed.emit()

    # ------------------------------------------------------------------
    # Утилиты
    # ------------------------------------------------------------------

    @staticmethod
    def _format_changelog(text: str) -> str:
        """Преобразовать changelog в HTML."""
        if not text:
            return "<i>Нет подробностей</i>"

        # Обрабатываем строки: заголовки, списки, обычный текст
        lines = text.split("\n")
        html_lines = []

        in_list = False
        for line in lines:
            stripped = line.strip()
            if not stripped:
                if in_list:
                    html_lines.append("</ul>")
                    in_list = False
                continue

            # Заголовок уровня 3 (например, "## Изменения")
            if stripped.startswith("## "):
                if in_list:
                    html_lines.append("</ul>")
                    in_list = False
                html_lines.append(f"<h3>{stripped[3:]}</h3>")
            # Заголовок уровня 4
            elif stripped.startswith("### "):
                if in_list:
                    html_lines.append("</ul>")
                    in_list = False
                html_lines.append(f"<h4>{stripped[4:]}</h4>")
            # Пункт списка
            elif stripped.startswith("- ") or stripped.startswith("* "):
                if not in_list:
                    html_lines.append("<ul>")
                    in_list = True
                html_lines.append(f"<li>{stripped[2:]}</li>")
            # Обычная строка
            else:
                if in_list:
                    html_lines.append("</ul>")
                    in_list = False
                html_lines.append(f"<p>{stripped}</p>")

        if in_list:
            html_lines.append("</ul>")

        return "\n".join(html_lines)

    def reject(self) -> None:
        """Закрыть диалог без обновления."""
        self._updater.cleanup()
        super().reject()

    def closeEvent(self, event) -> None:  # type: ignore[override]
        self._updater.cleanup()
        super().closeEvent(event)


class NoUpdateDialog(QDialog):
    """Диалог: обновлений нет."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Обновления")
        self.setModal(True)
        self.resize(360, 120)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        info = QLabel("У вас установлена последняя версия приложения.")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info)

        btn_ok = QPushButton("OK")
        btn_ok.clicked.connect(self.accept)
        layout.addWidget(btn_ok)
