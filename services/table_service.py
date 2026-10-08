"""Table management service."""
import logging

from db.config import DB_CONFIG
from db.metadata import (
    get_columns,
    get_foreign_keys,
    list_indexes,
    list_sequences,
    list_tables,
    list_views,
    quote_ident,
)
from db.transactions import readonly_cursor, transaction
from utils.formatters import (
    display_table,
    error,
    header,
    info,
    print_tree,
    success,
    warn,
)
from utils.helpers import select_table
from utils.validators import non_empty, positive_int, safe_identifier

logger = logging.getLogger(__name__)

DATATYPE_MAP = {
    "1": "INT",
    "3": "TEXT",
    "4": "DATE",
    "5": "BOOLEAN",
    "7": "FLOAT",
    "8": "TIMESTAMP",
}


def _get_datatype() -> str:
    info("""
Choose Data Type
1. INT      2. VARCHAR  3. TEXT
4. DATE     5. BOOLEAN  6. DECIMAL
7. FLOAT    8. TIMESTAMP
""")
    choice = input("Enter Choice: ").strip()
    if choice in DATATYPE_MAP:
        return DATATYPE_MAP[choice]
    if choice == "2":
        length = input("VARCHAR Length: ").strip()
        return f"VARCHAR({length})"
    if choice == "6":
        p = input("Precision (e.g. 10): ").strip()
        s = input("Scale (e.g. 2): ").strip()
        return f"DECIMAL({p},{s})"
    raise ValueError("Invalid datatype selected.")


def create_table() -> None:
    header("CREATE TABLE")
    try:
        table_name = safe_identifier(non_empty(input("Enter Table Name: "), "Table name"))
        total_columns = positive_int(input("Enter Number of Columns: "), "Column count")

        columns: list[str] = []
        for i in range(total_columns):
            info(f"\n---------- Column {i + 1} ----------")
            col_name = safe_identifier(non_empty(input("Column Name: "), "Column name"))
            datatype = _get_datatype()
            constraint = ""
            if input("NOT NULL? (y/n): ").lower() == "y":
                constraint += " NOT NULL"
            if input("UNIQUE? (y/n): ").lower() == "y":
                constraint += " UNIQUE"
            columns.append(f"{quote_ident(col_name)} {datatype}{constraint}")

        col_defs = ",\n            ".join(columns)
        query = f"""
        CREATE TABLE {quote_ident(table_name)} (
            id         SERIAL PRIMARY KEY,
            {col_defs},
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        with transaction() as (_, cur):
            cur.execute(query)
        logger.info("Created table '%s'.", table_name)
        success(f"\n✓ Table '{table_name}' created successfully!")

    except ValueError as e:
        error(f"\n✗ {e}")
    except Exception as e:
        logger.error("create_table failed: %s", e)
        error(f"\n✗ Error: {e}")


def show_tables() -> None:
    try:
        with readonly_cursor() as cur:
            tables = list_tables(cur)
        if not tables:
            warn("\n✗ No tables found.")
            return
        display_table(["#", "Table"], [(i, t) for i, t in enumerate(tables, 1)])
    except Exception as e:
        logger.error("show_tables failed: %s", e)
        error(f"Error: {e}")


def describe_table() -> None:
    try:
        with readonly_cursor() as cur:
            table_name = select_table(cur)
            if not table_name:
                return
            cols = get_columns(cur, table_name)
            fks = get_foreign_keys(cur, table_name)

        if not cols:
            error("✗ Table not found.")
            return

        header(f"DESCRIBE {table_name}")
        rows = [
            (
                c["name"],
                c["type"] + (f"({c['max_length']})" if c["max_length"] else ""),
                c["nullable"],
                c["default"] or "",
                "✓" if c["primary_key"] == "YES" else "",
            )
            for c in cols
        ]
        display_table(["Column", "Type", "Nullable", "Default", "PK"], rows)

        if fks:
            info("\nForeign Keys:")
            display_table(
                ["Column", "→ Table", "→ Column"],
                [(f["column"], f["foreign_table"], f["foreign_column"]) for f in fks],
            )
    except Exception as e:
        logger.error("describe_table failed: %s", e)
        error(f"Error: {e}")


def drop_table() -> None:
    try:
        with readonly_cursor() as cur:
            table_name = select_table(cur)
        if not table_name:
            return

        warn(f"\n⚠  This will permanently delete '{table_name}' and all its data.")
        if input("Type the table name to confirm: ").strip() != table_name:
            info("\nOperation cancelled.")
            return

        with transaction() as (_, cur):
            cur.execute(f"DROP TABLE {quote_ident(table_name)}")
        logger.info("Dropped table '%s'.", table_name)
        success(f"\n✓ Table '{table_name}' dropped.")

    except Exception as e:
        logger.error("drop_table failed: %s", e)
        error(f"\n✗ Error: {e}")


def explore_db() -> None:
    """Print a tree view of the database structure."""
    try:
        with readonly_cursor() as cur:
            tables    = list_tables(cur)
            views     = list_views(cur)
            sequences = list_sequences(cur)
            idxs      = list_indexes(cur)
        index_names = [i["index_name"] for i in idxs]
        print_tree(DB_CONFIG["dbname"], tables, views, index_names, sequences)
    except Exception as e:
        logger.error("explore_db failed: %s", e)
        error(f"\n✗ Error: {e}")
