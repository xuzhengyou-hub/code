from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum
import inspect
import os
import threading
from typing import Any


class LogLevel(IntEnum):
    """Log levels ordered from least to most severe."""

    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    FATAL = 50


@dataclass(slots=True)
class LoggerConfig:
    """Runtime configuration for the logger."""

    level: LogLevel = LogLevel.INFO
    file_path: str | None = None
    use_color: bool = True


class SimpleLogger:
    """Thread-safe singleton logger with console and optional file output."""

    _instance: SimpleLogger | None = None
    _singleton_lock = threading.Lock()

    RESET = "\033[0m"
    COLORS = {
        LogLevel.DEBUG: "\033[37m",  # Gray
        LogLevel.INFO: "\033[32m",  # Green
        LogLevel.WARNING: "\033[33m",  # Yellow
        LogLevel.ERROR: "\033[31m",  # Red
        LogLevel.FATAL: "\033[35m",  # Magenta
    }

    def __new__(cls) -> SimpleLogger:
        if cls._instance is None:
            with cls._singleton_lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self._config = LoggerConfig()
        self._write_lock = threading.Lock()
        self._initialized = True

    def configure(
        self,
        *,
        level: LogLevel | str = LogLevel.INFO,
        file_path: str | None = None,
        use_color: bool = True,
    ) -> None:
        """Configure the logger behavior.

        Args:
            level: Minimum level that will be emitted.
            file_path: Optional destination file for append logging.
            use_color: Whether console output should include ANSI colors.
        """
        resolved_level = self._normalize_level(level)
        self._config = LoggerConfig(level=resolved_level, file_path=file_path, use_color=use_color)

    def debug(self, message: str, *args: Any) -> None:
        """Emit a DEBUG log message."""
        self.log(LogLevel.DEBUG, message, *args)

    def info(self, message: str, *args: Any) -> None:
        """Emit an INFO log message."""
        self.log(LogLevel.INFO, message, *args)

    def warning(self, message: str, *args: Any) -> None:
        """Emit a WARNING log message."""
        self.log(LogLevel.WARNING, message, *args)

    def error(self, message: str, *args: Any) -> None:
        """Emit an ERROR log message."""
        self.log(LogLevel.ERROR, message, *args)

    def fatal(self, message: str, *args: Any) -> None:
        """Emit a FATAL log message."""
        self.log(LogLevel.FATAL, message, *args)

    def log(self, level: LogLevel | str, message: str, *args: Any) -> None:
        """Emit a log entry if the level is enabled.

        Args:
            level: Log level enum or corresponding name.
            message: Message template or plain message.
            args: Optional positional values interpolated using `%` formatting.
        """
        resolved_level = self._normalize_level(level)
        if resolved_level < self._config.level:
            return

        rendered_message = message % args if args else message
        filename, line_number = self._get_caller_info()
        output = self._format_message(resolved_level, filename, line_number, rendered_message)

        with self._write_lock:
            self._write_console(output, resolved_level)
            self._write_file(output)

    def _normalize_level(self, level: LogLevel | str) -> LogLevel:
        if isinstance(level, LogLevel):
            return level
        upper_name = level.strip().upper()
        try:
            return LogLevel[upper_name]
        except KeyError as exc:
            raise ValueError(f"Unsupported log level: {level}") from exc

    def _get_caller_info(self) -> tuple[str, int]:
        frame = inspect.currentframe()
        if frame is None:
            return "unknown", 0

        current_file = os.path.abspath(__file__)
        caller = frame
        while caller:
            code = caller.f_code
            candidate = os.path.abspath(code.co_filename)
            if candidate != current_file:
                return os.path.basename(candidate), caller.f_lineno
            caller = caller.f_back

        return "unknown", 0

    def _format_message(self, level: LogLevel, filename: str, line_number: int, message: str) -> str:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"[{timestamp}] [{level.name}] [{filename}:{line_number}] - {message}"

    def _write_console(self, output: str, level: LogLevel) -> None:
        if self._config.use_color:
            color = self.COLORS[level]
            print(f"{color}{output}{self.RESET}")
        else:
            print(output)

    def _write_file(self, output: str) -> None:
        file_path = self._config.file_path
        if not file_path:
            return

        with open(file_path, "a", encoding="utf-8") as file_obj:
            file_obj.write(output + "\n")


def configure_logger(
    *,
    level: LogLevel | str = LogLevel.INFO,
    file_path: str | None = None,
    use_color: bool = True,
) -> SimpleLogger:
    """Configure and return the global logger instance."""
    logger.configure(level=level, file_path=file_path, use_color=use_color)
    return logger


logger = SimpleLogger()
