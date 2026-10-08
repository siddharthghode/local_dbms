"""Index management service."""
import logging

from db.metadata import list_indexes, quote_ident
from db.transactions import readonly_cursor, transaction
from utils.formatters import display_table, error, header, info, muted, success, warn
from utils.helpers import get_editable_columns, get_table_columns, select_table

logger = logging.getLogger(__name__)


def list_all_indexes() -> None:
    header("INDEXES")
    try:
        with readonly_cursor() as cur:
            table_name = select_table(cur)
            if not table_name:
                return
            idxs = list_indexes(cur, table_name)

        if not idxs:
            warn("\nNo indexes found.")
            return

        rows = [
            (
                i["index_name"],
                i["table_name"],
                "✓" if i["is_unique"] else "",
                "✓" if i["is_primary"] else "",
                i["columns"],
            )
            for i in idxs
        ]
        display_table(["Index", "Table", "Unique", "Primary", "Columns"], rows)
    except Exception as e:
        logger.error("list_all_indexes failed: %s", e)
        error(f"\n✗ Error: {e}")


def create_index() -> None:
    header("CREATE INDEX")
    try:
        with readonly_cursor() as cur:
            table_name = select_table(cur)
            if not table_name:
                return
            all_cols = get_table_columns(cur, table_name)

        editable = get_editable_columns(all_cols)
        info("\nSelect column to index:\n")
        for i, col in enumerate(editable, 1):
            print(f"  {i}. {col}")

        choice = int(input("\nColumn number: ").strip())
        col_name = editable[choice - 1]

        is_unique = input("Unique index? (y/n): ").lower() == "y"
        unique_kw = "UNIQUE " if is_unique else ""

        idx_name = f"idx_{table_name}_{col_name}"
        query = (
            f"CREATE {unique_kw}INDEX {quote_ident(idx_name)} "
            f"ON {quote_ident(table_name)} ({quote_ident(col_name)});"
        )

        with transaction() as (_, cur):
            cur.execute(query)
        logger.info("Created index '%s' on '%s'.'%s'.", idx_name, table_name, col_name)
        success(f"\n✓ Index '{idx_name}' created.")

    except (ValueError, IndexError):
        error("\n✗ Invalid selection.")
    except Exception as e:
        logger.error("create_index failed: %s", e)
        error(f"\n✗ Error: {e}")


def drop_index() -> None:
    header("DROP INDEX")
    try:
        with readonly_cursor() as cur:
            table_name = select_table(cur)
            if not table_name:
                return
            idxs = list_indexes(cur, table_name)

        non_pk = [i for i in idxs if not i["is_primary"]]
        if not non_pk:
            warn("\nNo droppable indexes found (primary key indexes cannot be dropped here).")
            return

        for i, idx in enumerate(non_pk, 1):
            print(f"  {i}. {idx['index_name']}  ({idx['columns']})")

        choice = int(input("\nIndex number to drop: ").strip())
        idx_name = non_pk[choice - 1]["index_name"]

        if input(f"\nDrop index '{idx_name}'? (y/n): ").lower() != "y":
            warn("\nCancelled.")
            return

        with transaction() as (_, cur):
            cur.execute(f"DROP INDEX {quote_ident(idx_name)};")
        logger.info("Dropped index '%s'.", idx_name)
        success(f"\n✓ Index '{idx_name}' dropped.")

    except (ValueError, IndexError):
        error("\n✗ Invalid selection.")
    except Exception as e:
        logger.error("drop_index failed: %s", e)
        error(f"\n✗ Error: {e}")


def explain_query() -> None:
    """Run EXPLAIN or EXPLAIN ANALYZE on a user-supplied SQL query."""
    header("EXPLAIN / EXPLAIN ANALYZE")
    info("Enter a SELECT query to analyse (no semicolon needed).")
    sql = input("\nSQL> ").strip().rstrip(";")
    if not sql:
        return

    analyze = input("Run EXPLAIN ANALYZE? (y/n): ").lower() == "y"
    prefix = "EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)" if analyze else "EXPLAIN"

    try:
        with readonly_cursor() as cur:
            cur.execute(f"{prefix} {sql}")
            rows = cur.fetchall()
        print()
        for row in rows:
            muted(row[0])
    except Exception as e:
        logger.error("explain_query failed: %s", e)
        error(f"\n✗ Error: {e}")
