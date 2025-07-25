# Copilot Instructions for CuisineCraft

## Project Architecture
- **Main GUI**: Located in `tkinter_gui/main.py`, launches the application and manages the main event loop.
- **Core Modules**: 
  - `db.py`: Handles all SQLite database interactions (recipes, ingredients, menus).
  - `models.py`: Defines data models for recipes and ingredients.
  - `layout.py`, `theme.py`, `constants.py`: Manage GUI layout, theming, and shared constants.
  - `events.py`, `helpers.py`, `utils.py`: Contain event handlers, utility functions, and helper logic for the GUI.
- **Widgets**: Custom Tkinter widgets are in `tkinter_gui/widgets/` (e.g., `ingredient_entry.py`, `modern_entry.py`).
- **SQL Files**: SQL queries for advanced operations are stored as `.sql` files in `tkinter_gui/`.
- **Database**: The SQLite database file is `CuisineCraft.db` (duplicated in root and `tkinter_gui/`).

## Developer Workflows
- **Run the App**: `python -m tkinter_gui.main` (preferred) or `python tkinter_gui/main.py` from the project root.
- **Install Dependencies**: `pip install -r tkinter_gui/requirements.txt` (or use Poetry if configured).
- **Database**: Schema is managed via code and `.sql` files. No migrations framework; update SQL or code directly.
- **Testing**: No formal test suite; manual testing via the GUI is standard.
- **Debugging**: Use print statements or Python debuggers in `main.py` or relevant modules.

## Project Conventions
- **Recipe & Ingredient Entry**: GUI expects comma-separated values for ingredients (amount, unit, ingredient, [price, store, date]). Only the first three are mandatory.
- **Data Flow**: User actions in the GUI trigger event handlers, which update the database and refresh the UI.
- **Exports**: Menus and shopping lists can be exported as text or CSV via GUI actions.
- **Language**: Some UI elements and comments may be in Dutch (e.g., tab names like "Recepten Lijst").

## Integration & Patterns
- **External Libraries**: Uses `pandas`, `requests`, `beautifulsoup4`, `lxml` for data handling and web scraping.
- **No REST API**: All logic is local; no networked services.
- **No ORM**: Direct SQL queries via `sqlite3`.
- **GUI Structure**: Tabs for recipe list, menu generation, adding recipes, and ingredient management.

## Key Files
- `tkinter_gui/main.py`: App entry point
- `tkinter_gui/db.py`: Database logic
- `tkinter_gui/layout.py`, `theme.py`: GUI structure and theming
- `tkinter_gui/widgets/`: Custom widgets
- `tkinter_gui/requirements.txt`: Python dependencies

## Examples
- To add a recipe: Use the "Add recipes" tab, fill entries, and click "Add to database".
- To add ingredients: Use the "Add ingredients to recipe" tab, enter comma-separated values, and submit.
- To generate a weekly menu: Use the "weekmenu generator" tab.

---
For more, see `project-description.md` and `tkinter_gui/README.md`.
