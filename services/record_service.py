"""Record CRUD service with pagination, filtering, and sorting."""
import logging
import time
from typing import Any

from db.config import PAGE_SIZE
from db.metadata import get_column_names, quote_ident
from db.transactions import readonly_cursor, transaction
from utils.formatters import (
    display_page,
    display_table,
    error,
    fmt_duration,
    header,
    info,
    muted,
    success,
    warn,
)
from utils.helpers import get_editable_columns, select_table
from utils.validators import safe_identifier

logger = logging.getLogger(__name__)


def insert_record() -> None:
    header("INSERT RECORD")
    try:
        with readonly_cursor() as cur:
            table_name = select_table(cur)
            if not table_name:
                return
            columns = get_column_names(cur, table_name)

        if not columns:
            error("\n✗ Table does not exist.")
            return

        editable = get_editable_columns(columns)
        info("\n========== ENTER RECORD ==========\n")
        values = [input(f"  {col}: ").strip() for col in editable]

        placeholders = ", ".join(["%s"] * len(values))
        cols_sql = ", ".join(quote_ident(c) for c in editable)

        with transaction() as (_, cur):
            cur.execute(
                f"INSERT INTO {quote_ident(table_name)} ({cols_sql}) VALUES ({placeholders});",
                values,
            )
        logger.info("Inserted 1 record into '%s'.", table_name)
        success("\n✓ Record inserted successfully!")

    except Exception as e:
        logger.error("insert_record failed: %s", e)
        error(f"\n✗ Error: {e}")


def view_records(table_name: str | None = None) -> None:
    """View records with pagination."""
    try:
        with readonly_cursor() as cur:
            if table_name is None:
                table_name = select_table(cur)
                if not table_name:
                    return
            headers = get_column_names(cur, table_name)

        page_size = PAGE_SIZE
        page = 1

        while True:
            offset = (page - 1) * page_size
            with readonly_cursor() as cur:
                cur.execute(f"SELECT COUNT(*) FROM {quote_ident(table_name)}")
                total_rows = cur.fetchone()[0]
                total_pages = max(1, (total_rows + page_size - 1) // page_size)

                cur.execute(
                    f"SELECT * FROM {quote_ident(table_name)} ORDER BY id LIMIT %s OFFSET %s",
                    (page_size, offset),
                )
                rows = cur.fetchall()

            display_page(headers, rows, page, total_pages, total_rows)

            if total_pages <= 1:
                break

            cmd = input("\n> ").strip().lower()
            if cmd in ("exit", "q", ""):
                break
            elif cmd == "next" and page < total_pages:
                page += 1
            elif cmd == "prev" and page > 1:
                page -= 1
            elif cmd == "first":
                page = 1
            elif cmd == "last":
                page = total_pages
            elif cmd.startswith("page "):
                try:
                    p = int(cmd.split()[1])
                    if 1 <= p <= total_pages:
                        page = p
                    else:
                        warn(f"Page must be between 1 and {total_pages}.")
                except (ValueError, IndexError):
                    warn("Usage: page <number>")
            else:
                warn("Commands: next · prev · first · last · page N · exit")

    except Exception as e:
        logger.error("view_records failed: %s", e)
        error(f"Error: {e}")


def search_records() -> None:
    """Case-insensitive search with optional multi-column, filter, sort, pagination."""
    header("SEARCH RECORDS")
    try:
        with readonly_cursor() as cur:
            table_name = select_table(cur)
            if not table_name:
                return
            all_cols = get_column_names(cur, table_name)

        editable = get_editable_columns(all_cols)

        info("\nSearch columns (comma-separated numbers, or 'all'):\n")
        for i, col in enumerate(editable, 1):
            print(f"  {i}. {col}")

        raw = input("\nColumns: ").strip().lower()
        if raw == "all":
            search_cols = editable
        else:
            idxs = [int(x.strip()) - 1 for x in raw.split(",")]
            search_cols = [editable[i] for i in idxs]

        keyword = input("Search keyword: ").strip()

        # Optional sort
        sort_col = input("Sort by column (Enter to skip): ").strip()
        sort_dir = "ASC"
        if sort_col:
            try:
                sort_col = safe_identifier(sort_col)
                if sort_col not in all_cols:
                    warn(f"Column '{sort_col}' not found, skipping sort.")
                    sort_col = ""
                else:
                    sort_dir = input("Direction ASC/DESC [ASC]: ").strip().upper() or "ASC"
                    if sort_dir not in ("ASC", "DESC"):
                        sort_dir = "ASC"
            except ValueError:
                sort_col = ""

        conditions = " OR ".join(
            f"{quote_ident(c)}::text ILIKE %s" for c in search_cols
        )
        params: list[Any] = [f"%{keyword}%" for _ in search_cols]

        order_clause = ""
        if sort_col:
            order_clause = f" ORDER BY {quote_ident(sort_col)} {sort_dir}"

        page_size = PAGE_SIZE
        page = 1

        while True:
            offset = (page - 1) * page_size
            with readonly_cursor() as cur:
                cur.execute(
                    f"SELECT COUNT(*) FROM {quote_ident(table_name)} WHERE {conditions}",
                    params,
                )
                total_rows = cur.fetchone()[0]
                total_pages = max(1, (total_rows + page_size - 1) // page_size)

                t0 = time.perf_counter()
                cur.execute(
                    f"SELECT * FROM {quote_ident(table_name)} WHERE {conditions}"
                    f"{order_clause} LIMIT %s OFFSET %s",
                    params + [page_size, offset],
                )
                rows = cur.fetchall()
                elapsed = time.perf_counter() - t0

            display_page(all_cols, rows, page, total_pages, total_rows)
            muted(f"  Query time: {fmt_duration(elapsed)}")

            if total_pages <= 1:
                break
            cmd = input("\n> ").strip().lower()
            if cmd in ("exit", "q", ""):
                break
            elif cmd == "next" and page < total_pages:
                page += 1
            elif cmd == "prev" and page > 1:
                page -= 1
            elif cmd == "first":
                page = 1
            elif cmd == "last":
                page = total_pages
            elif cmd.startswith("page "):
                try:
                    p = int(cmd.split()[1])
                    if 1 <= p <= total_pages:
                        page = p
                except (ValueError, IndexError):
                    pass

    except (ValueError, IndexError):
        error("\n✗ Invalid selection.")
    except Exception as e:
        logger.error("search_records failed: %s", e)
        error(f"\n✗ Error: {e}")


def update_record() -> None:
    header("UPDATE RECORD")
    try:
        with readonly_cursor() as cur:
            table_name = select_table(cur)
            if not table_name:
                return

        view_records(table_name)
        record_id = input("\nEnter ID to Update: ").strip()

        with readonly_cursor() as cur:
            all_cols = get_column_names(cur, table_name)
            cur.execute(f"SELECT * FROM {quote_ident(table_name)} WHERE id=%s", (record_id,))
            record = cur.fetchone()

        if record is None:
            error("\n✗ Record not found.")
            return

        info("\nCurrent Record:")
        display_table(all_cols, [record])

        editable = get_editable_columns(all_cols)
        info("\nSelect Columns to Update\n")
        for i, col in enumerate(editable, 1):
            print(f"  {i}. {col}")

        choices = input("\nEnter column numbers (comma separated): ")
        selected = [int(x.strip()) for x in choices.split(",")]

        updates: list[str] = []
        values: list[Any] = []
        for choice in selected:
            col = editable[choice - 1]
            values.append(input(f"  New {col}: "))
            updates.append(f"{quote_ident(col)} = %s")

        updates.append("updated_at = CURRENT_TIMESTAMP")
        values.append(record_id)

        with transaction() as (_, cur):
            cur.execute(
                f"UPDATE {quote_ident(table_name)} SET {', '.join(updates)} WHERE id = %s;",
                values,
            )
        logger.info("Updated record id=%s in '%s'.", record_id, table_name)
        success("\n✓ Record updated successfully!")

    except Exception as e:
        logger.error("update_record failed: %s", e)
        error(f"\n✗ Error: {e}")


def delete_record() -> None:
    header("DELETE RECORD")
    try:
        with readonly_cursor() as cur:
            table_name = select_table(cur)
            if not table_name:
                return

        view_records(table_name)
        record_id = input("\nEnter ID to Delete: ").strip()

        with readonly_cursor() as cur:
            all_cols = get_column_names(cur, table_name)
            cur.execute(f"SELECT * FROM {quote_ident(table_name)} WHERE id = %s", (record_id,))
            record = cur.fetchone()

        if record is None:
            error("\n✗ Record not found.")
            return

        info("\nSelected Record:")
        display_table(all_cols, [record])

        if input("\nAre you sure you want to delete? (y/n): ").lower() != "y":
            warn("\nDeletion cancelled.")
            return

        with transaction() as (_, cur):
            cur.execute(f"DELETE FROM {quote_ident(table_name)} WHERE id = %s", (record_id,))
        logger.info("Deleted record id=%s from '%s'.", record_id, table_name)
        success("\n✓ Record deleted successfully!")

    except Exception as e:
        logger.error("delete_record failed: %s", e)
        error(f"\n✗ Error: {e}")
