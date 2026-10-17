"""WYSIWYG-диалог ввода математических формул (LaTeX)."""

from __future__ import annotations

import base64
import io

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QGroupBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ui.shape_dialogs import ShapeParamDialog


class FormulaEditorDialog(ShapeParamDialog):
    """Диалог ввода математической формулы с WYSIWYG-панелью символов."""

    def __init__(self, parent=None, initial_latex: str = ""):
        super().__init__(parent, "Математическая формула")
        self.setMinimumWidth(500)
        self.setMinimumHeight(600)

        self._latex_text = initial_latex
        self._preview_label: QLabel | None = None
        self._latex_input: QLineEdit | None = None
        self._debounce_timer: QTimer | None = None

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Настраивает интерфейс диалога."""
        main_layout = QVBoxLayout(self)
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
        symbols_layout.addWidget(self._create_greek_letters_group())
        symbols_layout.addWidget(self._create_superscripts_group())
        symbols_layout.addWidget(self._create_fractions_group())
        symbols_layout.addWidget(self._create_roots_group())
        symbols_layout.addWidget(self._create_functions_group())
        symbols_layout.addWidget(self._create_operators_group())
        symbols_layout.addWidget(self._create_brackets_group())

        symbols_layout.addStretch()
        scroll.setWidget(symbols_widget)
        main_layout.addWidget(scroll)

        # --- Подсказка ---
        hint = QLabel("💡 Подсказка: можно вводить LaTeX вручную или использовать кнопки выше")
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
            ("x²", r"x^2"),
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
        row_layout = QVBoxLayout()

        if title:
            label = QLabel(title)
            label.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
            label.setStyleSheet("color: #333;")
            row_layout.addWidget(label)

        row_buttons = QWidget()
        btn_layout = QVBoxLayout()
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(4)

        # Разбиваем на строки по 6 кнопок
        row_size = 6
        for i in range(0, len(items), row_size):
            row = items[i : i + row_size]
            h_layout = QVBoxLayout()
            h_layout.setContentsMargins(0, 0, 0, 0)
            h_layout.setSpacing(4)

            for display, latex in row:
                btn = QPushButton(f"{display}")
                btn.setFixedSize(60, 30)
                btn.setFont(QFont("Segoe UI", 9))
                btn.clicked.connect(lambda checked, l=latex: self._insert_latex(l))
                h_layout.addWidget(btn)

            btn_layout.addLayout(h_layout)

        row_buttons.setLayout(btn_layout)
        row_layout.addWidget(row_buttons)

        row_widget.setLayout(row_layout)
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

        # Пробуем рендерить через matplotlib
        try:
            from matplotlib.figure import Figure
            from matplotlib.mathtext import MathTextParser

            dpi = 150
            fig = Figure(figsize=(4, 1), dpi=dpi)
            parser = MathTextParser("agg")

            bitmap = parser.parse(latex, dpi=dpi, fontsize=16, wrap_with="$")
            if hasattr(bitmap, "convert"):
                rgba = bitmap.convert("RGBA")
                width, height = rgba.size
                # Конвертируем PIL Image в HTML с base64
                buf = io.BytesIO()
                rgba.save(buf, format="PNG")
                buf.seek(0)
                img_data = base64.b64encode(buf.read()).decode()
                html = f'<img src="data:image/png;base64,{img_data}" />'
                self._preview_label.setText(html)
                self._preview_label.setStyleSheet(
                    "QLabel { background-color: white; border-radius: 4px; padding: 4px; }"
                )
            else:
                self._preview_label.setText("Ошибка рендеринга")
                self._preview_label.setStyleSheet(
                    "QLabel { background-color: #fff3f3; border-radius: 4px; padding: 8px; color: #c00; }"
                )
            fig.clf()

        except ImportError:
            self._preview_label.setText("matplotlib не установлен")
            self._preview_label.setStyleSheet(
                "QLabel { background-color: #fff8e1; border-radius: 4px; padding: 8px; color: #f57c00; }"
            )
        except Exception:
            self._preview_label.setText("Некорректный LaTeX")
            self._preview_label.setStyleSheet(
                "QLabel { background-color: #fff3f3; border-radius: 4px; padding: 8px; color: #c00; }"
            )

    def get_latex(self) -> str:
        """Возвращает введённую LaTeX-строку."""
        if self._latex_input:
            return self._latex_input.text()
        return ""
