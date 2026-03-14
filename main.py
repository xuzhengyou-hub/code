from simple_log import LogLevel, configure_logger, logger


def run_demo() -> None:
    """Showcase all supported log levels with console and file output."""
    configure_logger(level=LogLevel.DEBUG, file_path="app.log", use_color=True)

    logger.debug("Debug details: user_id=%s", 1001)
    logger.info("Service started on port %s", 8000)
    logger.warning("Cache is near capacity: %s%%", 85)
    logger.error("Failed to fetch resource: id=%s", "A-42")
    logger.fatal("System halted due to unrecoverable error")


if __name__ == "__main__":
    run_demo()
