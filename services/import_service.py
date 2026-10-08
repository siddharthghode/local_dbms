"""CSV import service with validation, preview, and transactional bulk insert."""
import csv
import logging
import os
import time

from db.config import IMPORT_DIR
from db.metadata import quote_ident
from db.transactions import readonly_cursor, transaction
from utils.formatters import display_table, error, fmt_duration, header, info, muted, success, warn
from utils.helpers import get_editable_columns, get_table_columns, select_table

logger = logging.getLogger(__name__)


def import_csv() -> None:
    header("IMPORT CSV")
    try:
        os.makedirs(IMPORT_DIR, exist_ok=True)
        csv_files = sorted(f for f in os.listdir(IMPORT_DIR) if f.endswith(".csv"))

        if csv_files:
            info(f"\nAvailable CSV files in '{IMPORT_DIR}/':\n")
            for i, f in enumerate(csv_files, 1):
                print(f"  {i}. {f}")
            print()
        else:
            info(f"\nPlace CSV files in '{IMPORT_DIR}/' first.\n")

        file_input = input("Enter CSV number or filename: ").strip()

        if file_input.isdigit() and csv_files:
            idx = int(file_input) - 1
            if 0 <= idx < len(csv_files):
                file_path = os.path.join(IMPORT_DIR, csv_files[idx])
            else:
                error("\n✗ Invalid number.")
                return
        else:
            file_path = (
                file_input if os.path.isabs(file_input)
                else os.path.join(IMPORT_DIR, file_input)
            )

        if not os.path.exists(file_path):
            error(f"\n✗ File not found: {file_path}")
            return

        with readonly_cursor() as cur:
            table_name = select_table(cur)
            if not table_name:
                return
            table_columns = get_table_columns(cur, table_name)

        insert_columns = get_editable_columns(table_columns)

        # ── validate headers ───────────────────────────────────────────────────
        with open(file_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames or []
            missing = [c for c in insert_columns if c not in fieldnames]
            if missing:
                error(f"\n✗ CSV is missing columns: {', '.join(missing)}")
                return

            all_rows = list(reader)

        total = len(all_rows)
        info(f"\n  File   : {os.path.basename(file_path)}")
        info(f"  Table  : {table_name}")
        info(f"  Rows   : {total:,}")

        # ── preview ────────────────────────────────────────────────────────────
        preview = all_rows[:5]
        if preview:
            info("\nPreview (first 5 rows):")
            display_table(
                insert_columns,
                [[r.get(c, "") for c in insert_columns] for r in preview],
            )

        if input(f"\nImport all {total:,} rows into '{table_name}'? (y/n): ").lower() != "y":
            warn("\nImport cancelled.")
            return

        # ── bulk insert in a single transaction ────────────────────────────────
        placeholders = ", ".join(["%s"] * len(insert_columns))
        cols_sql = ", ".join(quote_ident(c) for c in insert_columns)
        query = f"INSERT INTO {quote_ident(table_name)} ({cols_sql}) VALUES ({placeholders})"

        inserted = skipped = 0
        t0 = time.perf_counter()

        with transaction() as (_, cur):
            for row in all_rows:
                values = [row.get(c) or None for c in insert_columns]
                try:
                    cur.execute(query, values)
                    inserted += 1
                except Exception as row_err:
                    logger.warning("Skipped row: %s", row_err)
                    skipped += 1

        elapsed = time.perf_counter() - t0
        logger.info(
            "Imported %d rows into '%s' (%d skipped) in %s.",
            inserted, table_name, skipped, fmt_duration(elapsed),
        )
        success("\n✓ Import complete!")
        muted(f"  Inserted : {inserted:,}")
        muted(f"  Skipped  : {skipped:,}")
        muted(f"  Time     : {fmt_duration(elapsed)}")

    except Exception as e:
        logger.error("import_csv failed: %s", e)
        error(f"\n✗ Error: {e}")
