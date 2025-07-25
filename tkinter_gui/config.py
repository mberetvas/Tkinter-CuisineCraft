"""
CuisineCraft Configuration Module
Centralizes all key settings for consistent, maintainable project-wide configuration management.
Loads settings from a .env file if present.
"""

import os
from typing import Final
from dotenv import load_dotenv

# Load environment variables from .env file in project root
BASE_DIR: Final[str] = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
load_dotenv(os.path.join(BASE_DIR, '.env'))

# Database file location (relative to project root)
DB_FILENAME: Final[str] = os.getenv("DB_FILENAME", "CuisineCraft.db")
# Determine the absolute path to the database file, ensuring compatibility and validation
db_env_path = os.getenv("DB_PATH")
if db_env_path:
    DB_PATH: Final[str] = os.path.abspath(os.path.expanduser(db_env_path))
else:
    DB_PATH: Final[str] = os.path.join(BASE_DIR, DB_FILENAME)

# Log file location
LOG_FILENAME: Final[str] = os.getenv("LOG_FILENAME", "CuisineCraft.log")
LOG_PATH: Final[str] = os.path.join(BASE_DIR, LOG_FILENAME)

# Default export directory for menus and shopping lists
EXPORT_DIR: Final[str] = os.path.join(BASE_DIR, os.getenv("EXPORT_DIR", "exports"))

# Supported languages for UI (comma-separated in .env)
SUPPORTED_LANGUAGES: Final[list[str]] = os.getenv("SUPPORTED_LANGUAGES", "en,nl").split(",")

# Debug mode flag
DEBUG: Final[bool] = os.getenv("DEBUG", "False").lower() in ("1", "true", "yes")

LOGGER_LEVEL: Final[str] = os.getenv("LOGGER_LEVEL", "INFO")

# Default CSV delimiter
CSV_DELIMITER: Final[str] = os.getenv("CSV_DELIMITER", ",")

# Date format for exports
EXPORT_DATE_FORMAT: Final[str] = os.getenv("EXPORT_DATE_FORMAT", "%Y-%m-%d")

# Ensure export directory exists
os.makedirs(EXPORT_DIR, exist_ok=True)

