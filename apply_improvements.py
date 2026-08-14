#!/usr/bin/env python3
"""Добавляет _on_history_shape_deleted в main_window.py"""

BASE = '/home/afaist/DopFast/work/Python/graphics_editor'

with open(f'{BASE}/ui/main_window.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Ищем место после _refresh_canvas и добавляем метод
target = '''    def _refresh_canvas(self):
        self._action_manager.refresh_canvas()'''

replacement = '''    def _refresh_canvas(self):
        self._action_manager.refresh_canvas()

    def _on_history_shape_deleted(self, shape_id):
        """Обработчик удаления фигуры из HistoryPanel."""
        self._action_manager.refresh_canvas()
        self._action_manager.update_statusbar()'''

if '_on_history_shape_deleted' not in content:
    content = content.replace(target, replacement)
    print('Добавлен _on_history_shape_deleted')
else:
    print('_on_history_shape_deleted уже существует')

with open(f'{BASE}/ui/main_window.py', 'w', encoding='utf-8') as f:
    f.write(content)

# Проверяем синтаксис
import py_compile
try:
    py_compile.compile(f'{BASE}/ui/main_window.py', doraise=True)
    print('main_window.py: OK')
except py_compile.PyCompileError as e:
    print(f'ERROR: {e}')
    exit(1)
