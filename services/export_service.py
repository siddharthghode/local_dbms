"""CSV export service."""
import csv
import logging
import os
import time
from datetime import date, datetime
from decimal import Decimal

from db.config import EXPORT_DIR
from db.metadata import quote_ident
from db.transactions import readonly_cursor
from utils.formatters import error, fmt_duration, header, muted, success, warn
from utils.helpers import get_table_columns, select_table

logger = logging.getLogger(__name__)


def _serialize(value) -> str:
    if value is None:
        return ""
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(value, date):
        return str(value)
    if isinstance(value, Decimal):
        return str(value)
    return value


def export_csv() -> None:
    header("EXPORT CSV")
    try:
        with readonly_cursor() as cur:
            table_name = select_table(cur)
            if not table_name:
                return

            t0 = time.perf_counter()
            cur.execute(f"SELECT * FROM {quote_ident(table_name)}")
            rows = cur.fetchall()
            headers = get_table_columns(cur, table_name)

        if not rows:
            warn("\nNo records found. Nothing to export.")
            return

        os.makedirs(EXPORT_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(EXPORT_DIR, f"{table_name}_{timestamp}.csv")

        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows([[_serialize(v) for v in row] for row in rows])

        elapsed = time.perf_counter() - t0
        logger.info("Exported %d rows from '%s' → %s.", len(rows), table_name, filename)
        success("\n✓ Export successful!")
        muted(f"  Rows     : {len(rows):,}")
        muted(f"  Saved    : {filename}")
        muted(f"  Time     : {fmt_duration(elapsed)}")

    except Exception as e:
        logger.error("export_csv failed: %s", e)
        error(f"\n✗ Error: {e}")
