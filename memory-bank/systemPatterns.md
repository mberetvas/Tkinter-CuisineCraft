# System Patterns *Optional*

This file documents recurring patterns and standards used in the project.
It is optional, but recommended to be updated as the project evolves.
2025-07-25 12:12:47 - Log of updates made.

*

## Coding Patterns

*   

## Architectural Patterns

*   

## Testing Patterns
2025-07-25 12:13:36 - Initial documentation of system patterns.

## Coding Patterns

* Use of Python dataclasses for models ([`Recipe`](tkinter_gui/models.py:9), [`Ingredient`](tkinter_gui/models.py:20), [`ReceiptItem`](tkinter_gui/models.py:30))
* Modular separation: database handler, GUI, models, utilities, theme.
* Logging for error tracking and debugging.

## Architectural Patterns

* MVC-like separation: GUI (View/Controller), database handler (Model/Controller), models (Data).
* Use of context managers for database connections ([`DatabaseHandler`](tkinter_gui/db.py:19)).
* Environment variable configuration via `.env` and `dotenv`.

## Testing Patterns

* Manual workflow validation via GUI.
* Export and import functions for menu and ingredient data.
* To-do: Add automated tests for parsing and export utilities.

*