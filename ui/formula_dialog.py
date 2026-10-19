"""WYSIWYG-диалог ввода математических формул (LaTeX)."""

from __future__ import annotations

import base64
import io

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from ui.shape_dialogs import ShapeParamDialog


class FormulaEditorDialog(ShapeParamDialog):
    """Диалог ввода математической формулы с WYSIWYG-панелью символов."""

    def __init__(self, parent=None, initial_latex: str = "", settings=None):
        super().__init__(parent, "Математическая формула")
        self.setMinimumWidth(500)
        self.setMinimumHeight(600)

        self._latex_text = initial_latex
        self._settings = settings
        self._preview_label: QLabel | None = None
        self._latex_input: QLineEdit | None = None
        self._font_combo: QComboBox | None = None
        self._font_size_spin: QSpinBox | None = None
        self._debounce_timer: QTimer | None = None

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Настраивает интерфейс диалога."""
        main_layout = self._main_layout
        main_layout.setSpacing(10)

        # --- Поле ввода LaTeX ---
        input_group = QGroupBox("LaTeX-код")
        input_layout = QVBoxLayout()

        self._latex_input = QLineEdit(self._latex_text)
        self._latex_input.setPlaceholderText(r"\frac{a}{b} + \sqrt{x}")
        self._latex_input.setFont(QFont("Consolas", 10))
        self._latex_input.textChanged.connect(self._on_latex_changed)
        input_layout.addWidget(self._latex_input)

        input_group.setLayout(input_layout)
        main_layout.addWidget(input_group)

        # --- Параметры шрифта ---
        font_group = QGroupBox("Шрифт формулы")
        font_layout = QHBoxLayout()

        self._font_combo = QComboBox()
        self._font_combo.addItems(
            [
                "Segoe UI",
                "DejaVu Sans",
                "Arial",
                "Times New Roman",
                "Courier New",
                "Cambria Math",
            ]
        )
        self._font_combo.setEditable(False)
        self._font_combo.setFont(QFont("Segoe UI", 9))
        font_layout.addWidget(QLabel("Шрифт:"))
        font_layout.addWidget(self._font_combo)

        self._font_size_spin = QSpinBox()
        self._font_size_spin.setRange(6, 200)
        self._font_size_spin.setValue(16)
        self._font_size_spin.setSuffix(" px")
        self._font_size_spin.setFont(QFont("Segoe UI", 9))
        font_layout.addWidget(QLabel("Размер:"))
        font_layout.addWidget(self._font_size_spin)

        font_group.setLayout(font_layout)
        main_layout.addWidget(font_group)

        # --- Превью ---
        preview_group = QGroupBox("Превью")
        preview_layout = QVBoxLayout()

        self._preview_label = QLabel("Введите формулу для превью")
        self._preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._preview_label.setFont(QFont("Segoe UI", 14))
        self._preview_label.setMinimumHeight(60)
        self._preview_label.setStyleSheet(
            "QLabel { background-color: #f5f5f5; border-radius: 4px; padding: 8px; }"
        )
        preview_layout.addWidget(self._preview_label)

        preview_group.setLayout(preview_layout)
        main_layout.addWidget(preview_group)

        # --- Панель символов (с прокруткой) ---
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMaximumHeight(350)

        symbols_widget = QWidget()
        symbols_layout = QVBoxLayout(symbols_widget)
        symbols_layout.setSpacing(6)

        # Группы символов
        symbols_layout.addWidget(self._create_operators_group())
        symbols_layout.addWidget(self._create_brackets_group())
        symbols_layout.addWidget(self._create_superscripts_group())
        symbols_layout.addWidget(self._create_greek_letters_group())
        symbols_layout.addWidget(self._create_fractions_group())
        symbols_layout.addWidget(self._create_roots_group())
        symbols_layout.addWidget(self._create_functions_group())

        symbols_layout.addStretch()
        scroll.setWidget(symbols_widget)
        main_layout.addWidget(scroll)

        # --- Подсказка ---
        hint = QLabel("💡 Подсказка: можно вводить LaTeX вручную или использовать кнопки")
        hint.setFont(QFont("Segoe UI", 8))
        hint.setStyleSheet("color: #666;")
        main_layout.addWidget(hint)

        main_layout.addStretch()

    # ------------------------------------------------------------------
    # Группы символов
    # ------------------------------------------------------------------

    def _create_greek_letters_group(self) -> QGroupBox:
        """Группа греческих букв."""
        group = QGroupBox("Греческие буквы")
        layout = QVBoxLayout()

        # Строчные
        lower = [
            ("α", r"\alpha"),
            ("β", r"\beta"),
            ("γ", r"\gamma"),
            ("δ", r"\delta"),
            ("ε", r"\epsilon"),
            ("ζ", r"\zeta"),
            ("η", r"\eta"),
            ("θ", r"\theta"),
            ("ι", r"\iota"),
            ("κ", r"\kappa"),
            ("λ", r"\lambda"),
            ("μ", r"\mu"),
        ]
        layout.addWidget(self._make_button_row("Строчные", lower))

        # Прописные
        upper = [
            ("Γ", r"\Gamma"),
            ("Δ", r"\Delta"),
            ("Θ", r"\Theta"),
            ("Λ", r"\Lambda"),
            ("Ξ", r"\Xi"),
            ("Π", r"\Pi"),
            ("Σ", r"\Sigma"),
            ("Υ", r"\Upsilon"),
            ("Φ", r"\Phi"),
            ("Ψ", r"\Psi"),
            ("Ω", r"\Omega"),
        ]
        layout.addWidget(self._make_button_row("Прописные", upper))

        group.setLayout(layout)
        return group

    def _create_superscripts_group(self) -> QGroupBox:
        """Группа степеней и индексов."""
        group = QGroupBox("Степени и индексы")
        layout = QVBoxLayout()

        items = [
            ("x", r"x"),
            ("x²", r"x^2"),
            ("ax²+...", r"a\cdot x^2+b\cdot x+c"),
            ("x³", r"x^3"),
            ("xⁿ", r"x^n"),
            ("xₙ", r"x_n"),
            ("x₁₂", r"x_{12}"),
            ("aᵀ", r"a^T"),
            ("a⁻¹", r"a^{-1}"),
            ("∞", r"\infty"),
        ]
        layout.addWidget(self._make_button_row("", items))

        group.setLayout(layout)
        return group

    def _create_fractions_group(self) -> QGroupBox:
        """Группа дробей."""
        group = QGroupBox("Дроби")
        layout = QVBoxLayout()

        items = [
            ("a/b", r"\frac{a}{b}"),
            ("x²/y", r"\frac{x^2}{y}"),
            ("√a/b", r"\frac{\sqrt{a}}{b}"),
            ("(a+b)/c", r"\frac{(a+b)}{c}"),
        ]
        layout.addWidget(self._make_button_row("", items))

        group.setLayout(layout)
        return group

    def _create_roots_group(self) -> QGroupBox:
        """Группа корней."""
        group = QGroupBox("Корни")
        layout = QVBoxLayout()

        items = [
            ("√x", r"\sqrt{x}"),
            ("∛x", r"\sqrt[3]{x}"),
            ("ⁿ√x", r"\sqrt[n]{x}"),
            ("√(a+b)", r"\sqrt{a+b}"),
        ]
        layout.addWidget(self._make_button_row("", items))

        group.setLayout(layout)
        return group

    def _create_functions_group(self) -> QGroupBox:
        """Группа функций."""
        group = QGroupBox("Функции")
        layout = QVBoxLayout()

        items = [
            ("sin", r"\sin"),
            ("cos", r"\cos"),
            ("tan", r"\tan"),
            ("log", r"\log"),
            ("ln", r"\ln"),
            ("exp", r"\exp"),
            ("lim", r"\lim"),
            ("max", r"\max"),
            ("min", r"\min"),
            ("sup", r"\sup"),
            ("inf", r"\inf"),
            ("det", r"\det"),
        ]
        layout.addWidget(self._make_button_row("", items))

        group.setLayout(layout)
        return group

    def _create_operators_group(self) -> QGroupBox:
        """Группа операторов и символов."""
        group = QGroupBox("Операторы")
        layout = QVBoxLayout()

        items = [
            ("+", r"+"),
            ("−", r"-"),
            ("×", r"\times"),
            ("÷", r"\div"),
            ("·", r"\cdot"),
            ("=", r"="),
            ("≠", r"\neq"),
            ("≈", r"\approx"),
            ("<", r"<"),
            (">", r">"),
            ("≤", r"\leq"),
            ("≥", r"\geq"),
            ("±", r"\pm"),
            ("∑", r"\sum"),
            ("∏", r"\prod"),
            ("∫", r"\int"),
            ("∂", r"\partial"),
            ("∇", r"\nabla"),
            ("∈", r"\in"),
            ("∉", r"\notin"),
            ("⊂", r"\subset"),
            ("⊃", r"\supset"),
            ("∪", r"\cup"),
            ("∩", r"\cap"),
            ("∀", r"\forall"),
            ("∃", r"\exists"),
            ("¬", r"\neg"),
            ("∧", r"\land"),
            ("∨", r"\lor"),
            ("→", r"\rightarrow"),
            ("↔", r"\leftrightarrow"),
            ("⇒", r"\Rightarrow"),
            ("↦", r"\mapsto"),
            ("…", r"\ldots"),
            ("⋯", r"\cdots"),
            ("ℝ", r"\mathbb{R}"),
            ("ℤ", r"\mathbb{Z}"),
            ("ℚ", r"\mathbb{Q}"),
            ("ℂ", r"\mathbb{C}"),
        ]
        layout.addWidget(self._make_button_row("", items))

        group.setLayout(layout)
        return group

    def _create_brackets_group(self) -> QGroupBox:
        """Группа скобок."""
        group = QGroupBox("Скобки")
        layout = QVBoxLayout()

        items = [
            ("( )", r"\left( \right)"),
            ("[ ]", r"\left[ \right]"),
            ("{ }", r"\left\{ \right}"),
            ("| |", r"\left| \right|"),
            ("⟨ ⟩", r"\left\langle \right\rangle"),
        ]
        layout.addWidget(self._make_button_row("", items))

        group.setLayout(layout)
        return group

    def _make_button_row(self, title: str, items: list[tuple[str, str]]) -> QWidget:
        """Создаёт строку кнопок с заданными символами."""
        row_widget = QWidget()
        main_layout = QVBoxLayout(row_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(2)

        if title:
            label = QLabel(title)
            label.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
            label.setStyleSheet("color: #333;")
            main_layout.addWidget(label)

        # Разбиваем на строки по 6 кнопок
        row_size = 6
        for i in range(0, len(items), row_size):
            row = items[i : i + row_size]
            h_layout = QHBoxLayout()
            h_layout.setContentsMargins(0, 0, 0, 0)
            h_layout.setSpacing(4)

            for display, latex in row:
                btn = QPushButton(f"{display}")
                btn.setFixedSize(70, 30)
                btn.setStyleSheet("padding: 4px")
                btn.setFont(QFont("Segoe UI", 8))
                btn.clicked.connect(lambda checked, l=latex: self._insert_latex(l))
                h_layout.addWidget(btn)

            main_layout.addLayout(h_layout)

        return row_widget

    # ------------------------------------------------------------------
    # Взаимодействие
    # ------------------------------------------------------------------

    def _insert_latex(self, latex: str) -> None:
        """Вставляет LaTeX-код в позицию курсора."""
        if self._latex_input is None:
            return
        cursor = self._latex_input.cursorPosition()
        text = self._latex_input.text()
        before = text[:cursor]
        after = text[cursor:]
        self._latex_input.setText(before + latex + after)
        self._latex_input.setCursorPosition(cursor + len(latex))
        self._schedule_preview_update()

    def _on_latex_changed(self) -> None:
        """Вызывается при изменении текста LaTeX."""
        self._schedule_preview_update()

    def _schedule_preview_update(self) -> None:
        """Планирует обновление превью с debounce."""
        if self._debounce_timer is not None:
            self._debounce_timer.stop()
        self._debounce_timer = QTimer()
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.timeout.connect(self._update_preview)
        self._debounce_timer.start(200)

    def _update_preview(self) -> None:
        """Обновляет превью формулы."""
        if self._preview_label is None:
            return
        latex = self._latex_input.text() if self._latex_input else ""
        if not latex.strip():
            self._preview_label.setText("Введите формулу для превью")
            self._preview_label.setStyleSheet(
                "QLabel { background-color: #f5f5f5; border-radius: 4px; padding: 8px; color: #999; }"
            )
            return

        # Определяем шрифт для превью
        assert self._font_combo is not None
        assert self._font_size_spin is not None
        font_family = self._font_combo.currentText()
        font_size = self._font_size_spin.value()

        # Пробуем рендерить через matplotlib
        try:
            from matplotlib.font_manager import FontProperties
            from matplotlib.mathtext import MathTextParser

            dpi = 150
            fp = FontProperties(family=font_family, size=font_size)
            parser = MathTextParser("agg")

            parsed = parser.parse(f"${latex}$", dpi=dpi, prop=fp)
            arr = parsed.image

            import numpy as np

            arr = np.array(arr)
            if arr.ndim == 2:
                h, w = arr.shape
                rgba = np.zeros((h, w, 4), dtype=np.uint8)
                rgba[:, :, 0] = 0
                rgba[:, :, 1] = 0
                rgba[:, :, 2] = 0
                rgba[:, :, 3] = arr
            else:
                rgba = arr
            h, w = rgba.shape[:2]
            # Конвертируем numpy array в PIL Image для base64
            try:
                from PIL import Image

                pil_img = Image.fromarray(rgba, "RGBA")
                buf = io.BytesIO()
                pil_img.save(buf, format="PNG")
                buf.seek(0)
                img_data = base64.b64encode(buf.read()).decode()
                html = f'<img src="data:image/png;base64,{img_data}" />'
                self._preview_label.setText(html)
                self._preview_label.setStyleSheet(
                    "QLabel { background-color: white; border-radius: 4px; padding: 4px; }"
                )
            except ImportError:
                self._preview_label.setText("Ошибка рендеринга превью")
                self._preview_label.setStyleSheet(
                    "QLabel { background-color: #fff3f3; border-radius: 4px; padding: 8px; color: #c00; }"
                )

        except ImportError:
            self._preview_label.setText("matplotlib не установлен")
            self._preview_label.setStyleSheet(
                "QLabel { background-color: #fff8e1; border-radius: 4px; padding: 8px; color: #f57c00; }"
            )
        except Exception as e:
            print(f"[FormulaDialog] render error: {type(e).__name__}: {e}")
            import traceback

            traceback.print_exc()
            self._preview_label.setText("Некорректный LaTeX")
            self._preview_label.setStyleSheet(
                "QLabel { background-color: #fff3f3; border-radius: 4px; padding: 8px; color: #c00; }"
            )

    def get_latex(self) -> str:
        """Возвращает введённую LaTeX-строку."""
        if self._latex_input:
            return self._latex_input.text()
        return ""

    def get_params(self) -> dict:
        """Возвращает параметры формулы."""
        assert self._font_combo is not None
        assert self._font_size_spin is not None
        return {
            "latex": self.get_latex(),
            "font_family": self._font_combo.currentText(),
            "font_size": self._font_size_spin.value(),
        }
