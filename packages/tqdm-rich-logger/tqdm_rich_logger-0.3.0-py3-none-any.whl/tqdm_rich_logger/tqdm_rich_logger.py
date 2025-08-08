import logging
import os
import sys
import threading
from pathlib import Path
from threading import Lock
from typing import Dict

from rich.console import Console
from rich.logging import RichHandler
from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm


class TqdmStream:
    """
    Custom stream that writes logs using tqdm.write to avoid progress bar corruption.
    Used to safely display Rich logs during tqdm progress bars.
    """

    def write(self, msg: str) -> None:
        """
        Write message using tqdm.write, preserving progress bar display.

        Args:
            msg: The message to write to the stream.
        """
        if msg.strip():
            tqdm.write(msg, end="")

    def flush(self) -> None:
        """
        Flush stderr to ensure all buffered outputs are written out.
        """
        try:
            sys.stderr.flush()
        except Exception:
            pass

    def read(self, n: int = -1) -> str:
        return ""

    def isatty(self) -> bool:
        return sys.stderr.isatty()

    def close(self) -> None:
        pass


class TqdmRichHandler(RichHandler):
    """
    RichHandler that writes logs through tqdm-safe stream.
    Prevents log formatting from breaking tqdm progress bars.
    """

    def __init__(self, *args, **kwargs) -> None:
        console = Console(file=TqdmStream(), force_terminal=True)
        super().__init__(*args, console=console, **kwargs)


class Logger:
    """
    Singleton-style logger with Rich console support and tqdm-safe output.
    Also writes logs to file and can catch uncaught exceptions from main/threaded code.
    """

    _instances: Dict[str, "Logger"] = {}
    _lock: Lock = Lock()

    def __new__(
        cls,
        log_dir: str = "logs",
        filename: str = "app.log",
        level: int = logging.INFO,
    ) -> "Logger":
        """
        Ensures only one logger instance exists per (log_dir, filename).

        Args:
            log_dir: Directory where the log file is stored.
            filename: Name of the log file.
            level: Logging level for console output.

        Returns:
            A singleton logger instance for the given filename.
        """
        key = os.path.join(log_dir, filename)
        with cls._lock:
            if key not in cls._instances:
                instance = super().__new__(cls)
                instance._initialized = False
                cls._instances[key] = instance
                return instance
            return cls._instances[key]

    def __init__(
        self,
        log_dir: str = "logs",
        filename: str = "app.log",
        level: int = logging.INFO,
        file_level: int = logging.DEBUG,
    ) -> None:
        """
        Initializes the logger if not already initialized.

        Args:
            log_dir: Directory to store log files.
            filename: Log file name.
            level: Console log level.
            file_level: File log level.
        """
        if hasattr(self, "_initialized"):
            return

        self.name: str = filename
        self.logger: logging.Logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.DEBUG)
        self.logger.propagate = False

        if not self.logger.handlers:
            Path(log_dir).mkdir(parents=True, exist_ok=True)

            # Console handler with rich formatting
            rich_handler = TqdmRichHandler(
                rich_tracebacks=True,
                show_path=False,
                markup=True,
            )
            rich_handler.setLevel(level)

            # File handler with timestamped log messages
            file_handler = logging.FileHandler(
                os.path.join(log_dir, filename), encoding="utf-8"
            )
            file_handler.setLevel(file_level)
            file_handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s | %(levelname)s | %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",
                )
            )

            self.logger.addHandler(rich_handler)
            self.logger.addHandler(file_handler)

        self._initialized: bool = True

    def info(self, msg: str) -> None:
        """Logs an informational message."""
        self.logger.info(msg)

    def warning(self, msg: str) -> None:
        """Logs a warning message."""
        self.logger.warning(msg)

    def error(self, msg: str) -> None:
        """Logs an error message."""
        self.logger.error(msg)

    def debug(self, msg: str) -> None:
        """Logs a debug message."""
        self.logger.debug(msg)

    def critical(self, msg: str) -> None:
        """Logs a critical error message."""
        self.logger.critical(msg)

    def exception(self, msg: str) -> None:
        """
        Logs an exception with traceback.
        Should be used inside an exception handler.
        """
        self.logger.exception(msg)

    def tqdm_safe(self):
        """
        Returns a context manager for logging inside tqdm loops.
        Ensures logs do not interfere with progress bars.

        Example:
            with logger.tqdm_safe():
                ...
        """
        return logging_redirect_tqdm(loggers=[self.logger])

    def get_logger(self) -> logging.Logger:
        """
        Returns the internal `logging.Logger` instance for advanced usage.

        Returns:
            The configured logger object.
        """
        return self.logger

    def catch_all_exceptions(self) -> None:
        """
        Installs global exception hooks to log uncaught exceptions,
        including in background threads.
        """

        def handle_exception(exc_type, exc_value, exc_traceback) -> None:
            if not issubclass(exc_type, KeyboardInterrupt):
                self.logger.error(
                    "Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback)
                )

        def handle_thread_exception(args) -> None:
            self.logger.error(
                "Uncaught thread exception",
                exc_info=(args.exc_type, args.exc_value, args.exc_traceback),
            )

        sys.excepthook = handle_exception
        threading.excepthook = handle_thread_exception
