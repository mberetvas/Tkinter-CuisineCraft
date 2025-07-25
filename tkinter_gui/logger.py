"""
Asynchronous, project-wide logger for CuisineCraft.
Provides non-blocking logging with configurable log levels and multiple output destinations.
"""

import logging
from logging.handlers import QueueHandler, QueueListener
from queue import Queue
from typing import Optional, List, Callable
import sys
from .config import LOG_PATH, LOGGER_LEVEL

class AsyncLogger:
    """
    Asynchronous logger supporting console and file outputs.
    """
    def __init__(self, name: str = "CuisineCraft", log_file: Optional[str] = None, level: int = logging.INFO):
        self.queue: Queue = Queue(-1)
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.handlers.clear()
        self.handlers: List[logging.Handler] = []

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        ))
        self.handlers.append(console_handler)

        # File handler (if specified)
        if log_file:
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setFormatter(logging.Formatter(
                "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
            ))
            self.handlers.append(file_handler)

        self.queue_handler = QueueHandler(self.queue)
        self.logger.addHandler(self.queue_handler)
        self.listener = QueueListener(self.queue, *self.handlers, respect_handler_level=True)
        self.listener.start()

        # Mapping from string level to logger method for dynamic selection
        self.level_method_map: dict[str, Callable[[str], None]] = {
            "debug": self.logger.debug,
            "info": self.logger.info,
            "warning": self.logger.warning,
            "error": self.logger.error,
            "critical": self.logger.critical,
        }

    def set_level(self, level: int) -> None:
        """Set the logging level for the logger."""
        self.logger.setLevel(level)
        for handler in self.handlers:
            handler.setLevel(level)

    def get_logger(self) -> logging.Logger:
        """Get the underlying logger instance."""
        return self.logger

    def log(self, message: str, level: Optional[str] = None) -> None:
        """
        Log a message using the method corresponding to the given or configured log level.
        If level is not provided, uses LOGGER_LEVEL from config.
        """
        log_level = (level or LOGGER_LEVEL or "info").lower()
        log_method = self.level_method_map.get(log_level, self.logger.info)
        log_method(message)

    def stop(self) -> None:
        """Stop the queue listener and clean up handlers."""
        self.listener.stop()
        for handler in self.handlers:
            handler.close()

# Singleton instance for project-wide use
async_logger = AsyncLogger(log_file=LOG_PATH, level=logging.INFO)
logger = async_logger.get_logger()
