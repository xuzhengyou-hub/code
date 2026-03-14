from __future__ import annotations

import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout

from simple_log import LogLevel, SimpleLogger, configure_logger, logger


class TestSimpleLogger(unittest.TestCase):
    def setUp(self) -> None:
        configure_logger(level=LogLevel.DEBUG, file_path=None, use_color=False)

    def test_singleton_instance(self) -> None:
        self.assertIs(logger, SimpleLogger())

    def test_level_filtering(self) -> None:
        buffer = io.StringIO()
        configure_logger(level=LogLevel.INFO, file_path=None, use_color=False)

        with redirect_stdout(buffer):
            logger.debug("hidden message")
            logger.info("visible message")

        output = buffer.getvalue()
        self.assertNotIn("hidden message", output)
        self.assertIn("visible message", output)

    def test_file_output_append(self) -> None:
        fd, path = tempfile.mkstemp(suffix=".log")
        os.close(fd)

        try:
            configure_logger(level=LogLevel.DEBUG, file_path=path, use_color=False)
            logger.error("write to file")

            with open(path, "r", encoding="utf-8") as file_obj:
                content = file_obj.read()

            self.assertIn("[ERROR]", content)
            self.assertIn("write to file", content)
        finally:
            os.remove(path)

    def test_context_contains_file_and_line(self) -> None:
        buffer = io.StringIO()
        configure_logger(level=LogLevel.DEBUG, file_path=None, use_color=False)

        with redirect_stdout(buffer):
            logger.info("context check")

        output = buffer.getvalue()
        self.assertIn("test_simple_log.py", output)
        self.assertIn("context check", output)


if __name__ == "__main__":
    unittest.main()
