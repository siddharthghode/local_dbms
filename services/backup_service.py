"""Backup and restore service using pg_dump / psql."""
import logging
import os
import subprocess
from datetime import datetime

from db.config import BACKUP_DIR, DB_CONFIG
from utils.formatters import error, header, info, muted, success, warn

logger = logging.getLogger(__name__)


def _pg_env() -> dict:
    env = os.environ.copy()
    env["PGPASSWORD"] = DB_CONFIG["password"]
    return env


def backup_db() -> None:
    header("BACKUP DATABASE")
    try:
        os.makedirs(BACKUP_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(BACKUP_DIR, f"{DB_CONFIG['dbname']}_{timestamp}.sql")

        result = subprocess.run(
            [
                "pg_dump",
                "-h", DB_CONFIG["host"],
                "-p", str(DB_CONFIG["port"]),
                "-U", DB_CONFIG["user"],
                "-d", DB_CONFIG["dbname"],
                "-f", filename,
            ],
            env=_pg_env(),
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            size = os.path.getsize(filename)
            size_str = f"{size / 1024:.1f} KB" if size < 1_048_576 else f"{size / 1_048_576:.1f} MB"
            logger.info("Backup created: %s (%s).", filename, size_str)
            success("\n✓ Backup successful!")
            muted(f"  Saved  : {filename}")
            muted(f"  Size   : {size_str}")
        else:
            logger.error("pg_dump failed: %s", result.stderr)
            error(f"\n✗ Backup failed:\n{result.stderr}")

    except FileNotFoundError:
        error("\n✗ pg_dump not found. Ensure PostgreSQL client tools are installed.")
    except Exception as e:
        logger.error("backup_db failed: %s", e)
        error(f"\n✗ Error: {e}")


def restore_db() -> None:
    """Restore a database from a .sql backup file using psql."""
    header("RESTORE DATABASE")
    warn("\n⚠  WARNING: Restoring will execute SQL against the current database.")
    warn("   Existing data may be overwritten depending on the backup content.")

    backup_files = sorted(
        f for f in os.listdir(BACKUP_DIR) if f.endswith(".sql")
    ) if os.path.isdir(BACKUP_DIR) else []

    if not backup_files:
        error(f"\n✗ No backup files found in '{BACKUP_DIR}/'.")
        return

    info(f"\nAvailable backups in '{BACKUP_DIR}/':\n")
    for i, f in enumerate(backup_files, 1):
        path = os.path.join(BACKUP_DIR, f)
        size = os.path.getsize(path)
        size_str = f"{size / 1024:.1f} KB"
        print(f"  {i}. {f}  ({size_str})")

    try:
        choice = int(input("\nEnter backup number: ").strip())
        backup_file = os.path.join(BACKUP_DIR, backup_files[choice - 1])
    except (ValueError, IndexError):
        error("\n✗ Invalid selection.")
        return

    warn(f"\n  File: {backup_file}")
    confirm = input(
        f"\nType the database name '{DB_CONFIG['dbname']}' to confirm restore: "
    ).strip()
    if confirm != DB_CONFIG["dbname"]:
        info("\nRestore cancelled.")
        return

    result = subprocess.run(
        [
            "psql",
            "-h", DB_CONFIG["host"],
            "-p", str(DB_CONFIG["port"]),
            "-U", DB_CONFIG["user"],
            "-d", DB_CONFIG["dbname"],
            "-f", backup_file,
        ],
        env=_pg_env(),
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        logger.info("Restored database from '%s'.", backup_file)
        success("\n✓ Restore completed successfully!")
    else:
        logger.error("psql restore failed: %s", result.stderr)
        error(f"\n✗ Restore failed:\n{result.stderr}")
