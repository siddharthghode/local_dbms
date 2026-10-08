"""Database statistics service."""
import logging

from db.config import DB_CONFIG
from db.metadata import get_db_size, get_table_stats
from db.transactions import readonly_cursor
from utils.formatters import display_table, error, header, info, muted

logger = logging.getLogger(__name__)


def db_stats() -> None:
    header("DATABASE STATISTICS")
    try:
        with readonly_cursor() as cur:
            stats = get_table_stats(cur)
            db_size = get_db_size(cur, DB_CONFIG["dbname"])

        if not stats:
            info("\nNo tables found.")
            return

        rows = [
            (
                s["table"],
                f"{s['rows']:,}",
                s["total_size"],
                s["table_size"],
                s["index_size"],
                s["columns"],
                s["indexes"],
            )
            for s in stats
        ]
        display_table(
            ["Table", "Rows", "Total Size", "Table Size", "Index Size", "Cols", "Idxs"],
            rows,
        )
        muted(f"\n  Total database size: {db_size}")

    except Exception as e:
        logger.error("db_stats failed: %s", e)
        error(f"\n✗ Error: {e}")
