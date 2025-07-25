# Decision Log

This file records architectural and implementation decisions using a list format.
2025-07-25 12:12:43 - Log of updates made.

*

## Decision

*

## Rationale 

*

## Implementation Details

2025-07-25 12:13:42 - Initial architectural decisions documented.

## Decision

* Use of `tkinter` for GUI and `sqlite3` for storage.
* Modular structure: separate files for database, GUI, models, utilities, and theming.
* Use of dataclasses for data modeling.
* Integration of OCR (pytesseract) for receipt scanning.
* Environment configuration via `.env` and `dotenv`.

## Rationale 

* `tkinter` is included with Python and enables cross-platform GUIs.
* `sqlite3` provides lightweight, file-based storage.
* Modular code improves maintainability and extensibility.
* Dataclasses simplify data handling and validation.
* OCR integration automates ingredient price updates.

## Implementation Details

* All core logic is in [`tkinter_gui/`](tkinter_gui/) subdirectory.
* Database handler manages all SQL operations and uses context managers.
* GUI is multi-tabbed, modern themed, and supports keyboard shortcuts.
* Utilities handle parsing, exporting, and file operations.
*
[2025-07-25 12:17:53] - Decided to add a new `week_menu` table to the database for persistent storage of custom week menus.  
## Decision  
A new table will be created with columns: id (PK), day (TEXT), recipe_id (INT), created_at (TIMESTAMP).  
## Rationale  
This allows users to save and reload their custom week menus, improving usability and persistence.  
## Implementation Details  
On "Save Menu", the current week menu assignments will be stored in this table. On load, the latest menu can be retrieved and displayed.
[2025-07-25 12:36:25] - Resolved "no such table: WeekMenu" error.
## Resolution
The `create_tables` method in `tkinter_gui/db.py` was refactored to consolidate all `CREATE TABLE IF NOT EXISTS` statements into a single `try` block. This ensures that all necessary tables, including `WeekMenu`, are reliably created upon database connection, preventing premature queries to non-existent tables.
[2025-07-25 12:50:39] - Decided to add the `requests` library as a dependency for HTML fetching in the new Import Recipe tab. This enables robust and maintainable web scraping for supported recipe sites.
[2025-07-25 12:51:14] - Decided to restrict recipe import to a whitelist of supported domains, starting with 15gram.be. This ensures only recipes with implemented parsers can be imported, improving reliability and user experience.
[2025-07-25 12:51:24] - Decided to provide user feedback for recipe import via both an inline label and messageboxes, ensuring users are clearly informed of success or failure. This matches the UX pattern used elsewhere in the app.