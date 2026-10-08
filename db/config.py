import os

from dotenv import load_dotenv

load_dotenv()


def _require(key: str) -> str:
    val = os.getenv(key)
    if not val:
        raise OSError(f"Missing required environment variable: {key}")
    return val


DB_CONFIG: dict = {
    "host":     os.getenv("DB_HOST", "localhost"),
    "dbname":   _require("DB_NAME"),
    "user":     _require("DB_USER"),
    "password": _require("DB_PASSWORD"),
    "port":     int(os.getenv("DB_PORT", "5432")),
}

POOL_MIN_SIZE: int = int(os.getenv("POOL_MIN_SIZE", "1"))
POOL_MAX_SIZE: int = int(os.getenv("POOL_MAX_SIZE", "5"))

PAGE_SIZE: int = int(os.getenv("PAGE_SIZE", "20"))

EXPORT_DIR: str = os.getenv("EXPORT_DIR", "exports")
IMPORT_DIR: str = os.getenv("IMPORT_DIR", "imports")
BACKUP_DIR: str = os.getenv("BACKUP_DIR", "backups")
LOG_DIR:    str = os.getenv("LOG_DIR",    "logs")
