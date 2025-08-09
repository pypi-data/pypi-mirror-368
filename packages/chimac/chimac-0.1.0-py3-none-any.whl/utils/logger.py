import logging
import os
import sys
import threading
from logging.handlers import RotatingFileHandler
from pathlib import Path
from threading import Lock
from typing import IO, Dict, cast

from rich.console import Console
from rich.logging import RichHandler
from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm


class TqdmStream:
    """Thread-safe tqdm-compatible stream for Rich logging."""

    _lock = Lock()

    def write(self, msg: str) -> None:
        if msg.strip():
            with self._lock:
                tqdm.write(msg, end="")

    def flush(self) -> None:
        try:
            sys.stdout.flush()
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
    """RichHandler that plays nicely with tqdm progress bars."""

    def __init__(self, *args, **kwargs) -> None:
        console = Console(
            file=cast(IO[str], TqdmStream()), force_terminal=True, markup=True
        )
        super().__init__(*args, console=console, **kwargs)


class Logger:
    """Singleton Rich + tqdm-safe logger with file rotation and global exception handling."""

    _instances: Dict[str, "Logger"] = {}
    _lock: Lock = Lock()

    def __new__(
        cls, log_dir="logs", filename="app.log", level=logging.INFO
    ) -> "Logger":
        key = os.path.abspath(os.path.join(log_dir, filename))
        with cls._lock:
            if key not in cls._instances:
                instance = super().__new__(cls)
                instance._initialized = False
                cls._instances[key] = instance
            return cls._instances[key]

    def __init__(
        self,
        log_dir="logs",
        filename="app.log",
        level=logging.INFO,
        file_level=logging.DEBUG,
        max_bytes=5_000_000,
        backup_count=5,
    ) -> None:
        if self._initialized:
            return

        self.name = filename
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.DEBUG)
        self.logger.propagate = False

        Path(log_dir).mkdir(parents=True, exist_ok=True)

        # Console handler
        rich_handler = TqdmRichHandler(
            rich_tracebacks=True, show_path=False, markup=True
        )
        rich_handler.setLevel(level)

        # Rotating file handler
        file_handler = RotatingFileHandler(
            os.path.join(log_dir, filename),
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        file_handler.setLevel(file_level)
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s | %(levelname)s | %(message)s", "%Y-%m-%d %H:%M:%S"
            )
        )

        self.logger.addHandler(rich_handler)
        self.logger.addHandler(file_handler)

        self._initialized = True

    # Shorthand logging methods
    def info(self, msg):
        self.logger.info(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)

    def debug(self, msg):
        self.logger.debug(msg)

    def critical(self, msg):
        self.logger.critical(msg)

    def exception(self, msg):
        self.logger.exception(msg)

    def success(self, msg: str):
        """Custom green-colored success log."""
        self.logger.info(f"[bold green]✔ {msg}[/bold green]")

    def tqdm_safe(self):
        return logging_redirect_tqdm(loggers=[self.logger])

    def get_logger(self):
        return self.logger

    def catch_all_exceptions(self) -> None:
        def handle_exception(exc_type, exc_value, exc_traceback):
            if not issubclass(exc_type, KeyboardInterrupt):
                self.logger.error(
                    "Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback)
                )

        def handle_thread_exception(args):
            self.logger.error(
                "Uncaught thread exception",
                exc_info=(args.exc_type, args.exc_value, args.exc_traceback),
            )

        sys.excepthook = handle_exception
        threading.excepthook = handle_thread_exception

        # Optional: catch asyncio task exceptions
        try:
            import asyncio

            asyncio.get_event_loop().set_exception_handler(
                lambda loop, ctx: self.logger.error(
                    f"Uncaught async exception: {ctx.get('exception')}"
                )
            )
        except ImportError:
            pass
