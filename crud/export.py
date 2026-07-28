import csv
import os
from datetime import datetime, date

from db import cursor
from utils.helpers import select_table, get_table_columns
from utils.display import success, error, warn, info


EXPORT_DIR = "exports"


def _serialize(value):
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(value, date):
        return str(value)
    return value


def export_csv():
    try:
        table_name = select_table(cursor)
        if not table_name:
            return

        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()

        if not rows:
            warn("\nNo records found. Nothing to export.")
            return

        headers = get_table_columns(cursor, table_name)
        os.makedirs(EXPORT_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{EXPORT_DIR}/{table_name}_{timestamp}.csv"

        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows([[_serialize(v) for v in row] for row in rows])

        success(f"\n✓ Export successful!")
        info(f"  Saved → {filename}")

    except Exception as e:
        error(f"\n✗ Error: {e}")
