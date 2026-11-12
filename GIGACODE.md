# Graphics Editor — Project Guide for AI Agent

## Overview

**Graphics Editor** — a vector graphics editor for geometry education (Russian educational context). Built with Python 3.12 + PySide6 (Qt6 QGraphicsView framework).

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12 |
| GUI | PySide6 (Qt6) / QGraphicsView |
| Graphs | matplotlib |
| Images | Pillow |
| Config | platformdirs |
| Packaging | PyInstaller |
| Linting | Ruff |
| Type checking | Mypy |
| Testing | pytest |

## Project Structure

```
graphics_editor/
├── main.py                    # Entry point
├── pyproject.toml             # Config: ruff, mypy, pytest, isort
├── requirements.txt           # Runtime + dev deps
├── app_settings.json          # Runtime settings (grid, colors, behavior)
├── app_version.py             # Version info
├── logging_config.py          # Logging setup
├── graphics_editor.spec       # PyInstaller spec
│
├── canvas/                    # Graphics canvas (QGraphicsView)
│   └── graphics_canvas.py     # Grid, zoom, pan, export
│
├── fileio/                    # File I/O
│   ├── file_manager.py        # Save/load/export (.gproj, PNG, SVG)
│   └── validators.py          # JSON schema validation
│
├── manager/                   # Business logic managers
│   ├── shape_manager.py       # Shape collection, selection, grouping
│   ├── undo_commands.py       # QUndoCommand implementations
│   ├── autosaver.py           # Auto-save with QTimer
│   └── updater.py             # GitHub update checker
│
├── shapes/                    # Shape classes (38+ types)
│   ├── base_shape.py          # Abstract base class (Template Method)
│   ├── registry.py            # Factory pattern for shape creation
│   ├── platonic_solid_shape.py  # Platonic solids (tetrahedron, cube, etc.)
│   ├── _3d_solids.py          # 3D solids (parallelepiped, sphere, cylinder, etc.)
│   └── [shape]_shape.py       # Individual shape implementations
│
├── tools/                     # Tool system
│   ├── tool_types.py          # ToolType enum (36+ tools)
│   ├── tool_manager.py        # Active tool management
│   ├── drawing_styles.py      # Default pen/brush styles
│   └── quadrilateral_tools.py # Helper drawing functions
│
├── ui/                        # User interface (25+ files)
│   ├── main_window.py         # MainWindow orchestrator
│   ├── window_ui.py           # Menu/toolbar/dock construction
│   ├── window_actions.py      # QAction + property panel
│   ├── window_shortcuts.py    # Hotkeys
│   ├── window_project.py      # New/open/save/export
│   ├── window_events.py       # EventManager (delegator)
│   ├── window_events_mouse.py # Mouse handlers
│   ├── window_events_drawing.py # Shape drawing + temp objects
│   ├── window_events_dialogs.py # Shape parameter dialogs
│   ├── window_canvas.py       # CanvasManager
│   ├── drawing_context.py     # Drawing state context
│   ├── scene_items.py         # QGraphicsItem wrappers for shapes
│   ├── property_panel.py      # Shape properties editor
│   ├── history_panel.py       # Shape history list
│   ├── shape_dialogs.py       # Shape parameter dialogs
│   ├── formula_dialog.py      # LaTeX formula editor
│   ├── graph_dialog.py        # Function graph editor
│   ├── settings_dialog.py     # Default settings dialog
│   ├── export_dialog.py       # Export area selector
│   ├── update_dialog.py       # Update notification
│   ├── help_dialogs.py        # Help/about dialogs
│   ├── theme_manager.py       # Light/dark theme
│   └── common_widgets.py      # Shared UI widgets
│
├── settings/                  # Application settings
│   └── settings.py            # Settings class (JSON persistence)
│
└── tests/                     # Unit tests (42 test files)
    ├── conftest.py            # pytest fixtures
    └── test_*.py              # Test modules
```

## Architecture

**Modular MVC-inspired architecture** with clear separation of concerns:

```
                    ┌─────────────────────┐
                    │     MainWindow       │
                    │   (Orchestrator)     │
                    └─────────┬───────────┘
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
   ┌──────┴──────┐    ┌──────┴──────┐    ┌──────┴──────┐
   │  EventManager│    │ ShapeManager│    │ToolManager  │
   │ (delegates to│    │ (collection,│    │ (active tool│
   │  Mouse/Drawing│    │  selection, │    │  creation)  │
   │   /DialogMgr)│    │  undo/redo) │    │             │
   └──────┬──────┘    └──────┬──────┘    └─────────────┘
          │                   │
   ┌──────┴──────┐    ┌──────┴──────┐
   │GraphicsCanvas│    │  Shape*     │
   │ (QGraphicsView│    │  (Strategy) │
   │  + grid/zoom) │    └──────┬──────┘
   └──────────────┘           │
                              │
                    ┌─────────┴─────────┐
                    │  ShapeRegistry     │
                    │  (Factory pattern) │
                    └───────────────────┘
```

### Key Patterns

1. **Orchestrator**: `MainWindow` coordinates all submodules, delegates to managers
2. **Delegation**: `EventManager` delegates to `MouseManager`, `DrawingManager`, `DialogManager`
3. **Factory/Registry**: `ShapeRegistry` creates shapes by type string; each shape implements `from_dict()`
4. **Strategy**: Each shape type is a separate class inheriting from `BaseShape`
5. **Template Method**: `BaseShape.draw()` provides skeleton (save/pen/brush/rotation/content/selection/restore), subclasses implement `_draw_shape_content()`
6. **Observer**: Qt signals/slots connect managers to UI
7. **Command**: `QUndoStack` + `QUndoCommand` subclasses for undo/redo

### Data Flow

User input → `GraphicsCanvas` signals → `EventManager` → `ShapeManager` (state change) → signals → UI updates. All mutations go through `QUndoStack`.

## Code Conventions

### Style (enforced by Ruff + isort)

- **Line length**: 99 characters
- **Quotes**: double quotes (`"`)
- **Indentation**: 4 spaces
- **Every file starts with**: `from __future__ import annotations`
- **Import order**: isort-managed — stdlib → third-party → local packages (`shapes`, `ui`, `manager`, `canvas`, `fileio`, `tools`, `settings`)

### Naming

- `snake_case` for functions/variables
- `PascalCase` for classes
- `UPPER_SNAKE_CASE` for constants

### Documentation

- Module-level docstrings: `"""..."""`
- Logging: `get_logger()` pattern via `logging_config.py`
- Error handling: `try/except` with `logger.warning()` for non-fatal errors

### Type Hints

- Used throughout the codebase
- `TYPE_CHECKING` blocks for circular imports

### Enums

- `ShapeType` — 46+ shape types (38+ 2D + 8 3D)
- `HandleType` — 11 resize handle types
- `ToolType` — 45+ tools (36+ 2D + 9 3D)

## Running Commands

| Command | Description |
|---|---|
| `python main.py` | Run application |
| `python run_tests.py` | Run all tests (pytest with offscreen Qt) |
| `pytest tests/ -v` | Direct pytest |
| `ruff check .` | Lint |
| `ruff format .` | Format |
| `ruff check . && ruff format --check .` | CI lint check |
| `mypy .` | Type checking |
| `pre-commit run --all-files` | All pre-commit hooks |
| `pyinstaller graphics_editor.spec` | Build distributable |

## Shape System

### Adding a New Shape

1. Create `shapes/new_shape.py` inheriting from `BaseShape`
2. Implement required methods:
   - `_draw_shape_content()` — rendering logic (Template Method)
   - `from_dict()` — factory classmethod for deserialization
   - Override `get_handle_positions()` if custom resize handles needed
   - Override `shape_type_name` property for display name
3. Register in `shapes/registry.py` — add to `_registry` dict
4. Add to `tools/tool_types.py` — add new `ToolType` enum value
5. Add UI wiring in `ui/window_actions.py` — tool button + action
6. Add tests in `tests/`

### Shape Types (38+)

Points, lines (segment/ray/infinite), rectangles, ellipses, circles, polygons, polylines, arcs, parabolas, hyperbolas, pencil (freehand), text, formulas, function graphs, triangles (equilateral/isosceles/right/obtuse/Sharygin/congruent/similar), parallelograms, trapezoids, angles (single/adjacent/vertical/transversal), regular polygons, Platonic solids, trigonometric circles, rhombuses, quadrilaterals, 3D solids (parallelepiped, sphere, cylinder, cone, pyramid, prism, truncated cone, truncated pyramid).

## UI System

### Adding a New Tool

1. Add `ToolType.YOUR_TOOL` enum value in `tools/tool_types.py`
2. Register action in `ui/window_actions.py` — add `QAction` and connect to tool manager
3. Handle tool behavior in `ui/window_events_drawing.py` — drawing logic
4. Add shortcut in `ui/window_shortcuts.py` if applicable
5. Add button to toolbar in `ui/window_ui.py` if not auto-generated

### Event Flow

`GraphicsCanvas` (mouse/keyboard events) → `EventManager` → `MouseManager` / `DrawingManager` / `DialogManager` → `ShapeManager` → signals → UI updates

## File Format

Project files use `.gproj` extension — JSON-based format with schema validation (`fileio/validators.py`). Supports PNG and SVG export.

## Testing

- 42 test modules covering shapes, managers, file I/O, tools
- Fixtures in `tests/conftest.py`
- Qt runs in offscreen mode for CI
- Run with: `python run_tests.py` or `pytest tests/ -v`
- 1321 tests total

## Configuration

- `app_settings.json` — runtime settings (grid, colors, snap behavior)
- `pyproject.toml` — build/lint/type-check/test config
- `graphics_editor.spec` — PyInstaller packaging config
- `app_version.py` — version string

## Important Notes for AI Agent

- **Always run linting and tests** after making changes: `ruff check . && ruff format . && python run_tests.py`
- **Respect the Template Method pattern** in shapes — only override `_draw_shape_content()`, not `draw()`
- **All shape mutations must go through ShapeManager** to ensure undo/redo works
- **Use `TYPE_CHECKING` blocks** to avoid circular imports
- **Double quotes** for all strings, not single quotes
- **Line length 99** — do not exceed
- **Every new file must start with** `from __future__ import annotations`
- **Logging**: use `get_logger(__name__)` from `logging_config`, not `print()`
- **Qt signals**: emit `shapes_changed`, `selection_changed`, etc. when state changes
- **Theme support**: use `ThemeManager` for colors, don't hardcode color values
