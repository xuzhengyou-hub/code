from .simple_log import LogLevel, SimpleLogger, configure_logger, logger

__all__ = ["LogLevel", "SimpleLogger", "configure_logger", "logger"]


def main() -> None:
    """Entry point for the generated console script."""
    logger.info("simple-log is ready.")
