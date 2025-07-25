# Product Context

This file provides a high-level overview of the project and the expected product that will be created. Initially it is based upon projectBrief.md (if provided) and all other available project-related information in the working directory. This file is intended to be updated as the project evolves, and should be used to inform all other modes of the project's goals and context.
2025-07-25 12:12:28 - Log of updates made will be appended as footnotes to the end of this file.

*

## Project Goal

*   

## Key Features

*   

## Overall Architecture

*   
2025-07-25 12:13:24 - Updated with project goal, key features, and architecture overview.

## Project Goal

* Provide a modern, user-friendly system for managing recipes, ingredients, and weekly meal planning with export and receipt scanning capabilities.

## Key Features

* Add, view, and manage recipes and ingredients.
* Generate a random weekly menu from stored recipes.
* Export weekly menu and shopping list to text or CSV.
* Scan and parse receipts using OCR to update ingredient prices.
* Modern, multi-tab GUI with search, filtering, and keyboard shortcuts.

## Overall Architecture

* Python application using `tkinter` for GUI and `sqlite3` for persistent storage.
* Modular codebase: [`db.py`](tkinter_gui/db.py:1) for database, [`gui.py`](tkinter_gui/gui.py:1) for UI, [`models.py`](tkinter_gui/models.py:1) for data models, [`utils.py`](tkinter_gui/utils.py:1) for helpers, [`theme.py`](tkinter_gui/theme.py:1) for UI styling.
* Follows MVC-like separation: GUI interacts with database via handler, models define data, utilities handle parsing/export.
* Extensible with widgets and theming for modern UX.
[2025-07-25 13:11:30] - Adopted modular GUI architecture: split gui.py into layout, events, ocr_utils, importers, helpers, constants, and widgets/. This enables clearer separation of concerns and easier future maintenance.