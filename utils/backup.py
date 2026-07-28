import os
import subprocess
from datetime import datetime

from db.config import DB_CONFIG
from utils.display import success, error, info


BACKUP_DIR = "backups"


def backup_db():
    try:
        os.makedirs(BACKUP_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{BACKUP_DIR}/{DB_CONFIG['dbname']}_{timestamp}.sql"

        env = os.environ.copy()
        env["PGPASSWORD"] = DB_CONFIG["password"]

        result = subprocess.run(
            [
                "pg_dump",
                "-h", DB_CONFIG["host"],
                "-p", str(DB_CONFIG["port"]),
                "-U", DB_CONFIG["user"],
                "-d", DB_CONFIG["dbname"],
                "-f", filename,
            ],
            env=env,
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            success(f"\n✓ Backup successful!")
            info(f"  Saved → {filename}")
        else:
            error(f"\n✗ Backup failed:\n{result.stderr}")

    except FileNotFoundError:
        error("\n✗ pg_dump not found. Ensure PostgreSQL client tools are installed.")
    except Exception as e:
        error(f"\n✗ Error: {e}")
