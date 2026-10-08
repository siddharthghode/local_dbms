"""
Logging configuration for local_dbms.

Writes to logs/dbms.log (rotating, 5 MB × 3 backups) and to stderr
at WARNING level so the terminal stays clean during normal use.

IMPORTANT: Never pass passwords, tokens, or secrets to any logger call.
"""
import logging
import logging.handlers
import os

from db.config import LOG_DIR


def setup_logging(level: int = logging.DEBUG) -> None:
    os.makedirs(LOG_DIR, exist_ok=True)
    log_file = os.path.join(LOG_DIR, "dbms.log")

    fmt = logging.Formatter(
        "%(asctime)s %(levelname)-8s %(name)s — %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(fmt)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(fmt)

    root = logging.getLogger()
    root.setLevel(level)
    root.addHandler(file_handler)
    root.addHandler(console_handler)
