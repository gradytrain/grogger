"""Custom logging utility for structured, timestamped script logging."""

import logging
import os
from datetime import datetime
from pathlib import Path


class Grogger:
    """A custom logger class that provides structured, timestamped logging functionality.

    Also includes automatic log file management and environment-aware path configuration.
    This class wraps Python's built-in `logging` module to provide a simplified
    interface for logging messages to timestamped log files, with support for both
    local development and CI/CD environments.

    Attributes:
        END_LOG_NO_ERROR (str): Standard message logged upon successful termination.
        END_LOG_ERROR (str): Standard message logged upon error termination.
        script_name (str): Name of the script using the logger.
        now (datetime): Current datetime with local timezone information.
        timestamp (str): Formatted timestamp string used in log file naming (MM-DD-YYYY-HHMM).
        project_path (Path): Current working directory path.
        log_name (str): Generated log file name combining script name and timestamp.
        log_path (str): Full path to the log file, environment-dependent.
        logger (logging.Logger): Underlying Python logger instance.

    Args:
        script_name (str): The name of the script or module using the logger.
            Used for log file naming and logger identification.
        log_level (int, optional): The logging level threshold. Defaults to `logging.INFO`.
            Accepts standard `logging` module levels (e.g., DEBUG, INFO, WARNING, ERROR).

    Methods:
        log(message): Logs an informational message.
        log_error(message): Logs an error message and raises an Exception.
        stop_success(): Logs a successful termination message.

    Notes:
        - In CI/CD environments (detected via the `CI` environment variable),
          log files are created in the current working directory.
        - In local environments, log files are stored in a `logs/` subdirectory
          within the current working directory, which is created if it does not exist.
        - Log entries follow the format: `timestamp - name - level - message`.

    Example:
        >>> logger = Grogger(script_name="my_script", log_level=logging.DEBUG)
        >>> logger.log("Processing started")
        >>> logger.stop_success()

    """

    END_LOG_NO_ERROR = "Logging stopped, Reason: exit code 0"
    END_LOG_ERROR = "Logging stopped, Reason: Error"

    def __init__(self, script_name: str, log_level: int = logging.INFO) -> None:
        """Initialize the custom logger.

        Args:
            script_name (str): The name of the script or module using the logger.
            log_level (int, optional): The logging level threshold. Defaults to `logging.INFO`.

        """
        # Initialize the logger with the script name, log level, and timestamp for log file naming
        self.script_name = script_name
        self.now = datetime.now(
            tz=datetime.now().astimezone().tzinfo
        )  # get local timezone
        self.timestamp = self.now.strftime("%m-%d-%Y-%H%M")

        # path determination
        self.project_path = Path.cwd()  # get script run directory
        self.log_name = f"{self.script_name}-runtime-logs-{self.timestamp}.log"

        if os.getenv("CI"):
            self.log_path = self.log_name
        else:
            log_dir = Path(self.project_path / "logs")
            if not Path.exists(log_dir):
                Path.mkdir(log_dir, parents=True)
            self.log_path = Path(log_dir / self.log_name)

        # Configure logging: file handler for persistent logs, stream handler for the terminal
        self.logger = logging.getLogger(self.script_name)
        self.logger.setLevel(log_level)
        self.logger.propagate = False

        if not self.logger.handlers:  # avoid duplicate handlers across instances
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )

            file_handler = logging.FileHandler(self.log_path)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(formatter)
            self.logger.addHandler(stream_handler)

        self.logger.info("Logging Start for %s", self.script_name)

    def log(self, message: str) -> None:
        """Log an informational message.

        Args:
            message (str): Message to log.

        """
        self.logger.info(message)

    def log_error(self, message: str) -> None:
        """Log an error message and raise an exception.

        Args:
            message (str): Error message to log.

        """
        self.logger.error(message)
        self.logger.info(self.END_LOG_ERROR)
        raise Exception(message)  # noqa: TRY002

    def stop_success(self) -> None:
        """Log a successful termination message."""
        self.logger.info(self.END_LOG_NO_ERROR)
