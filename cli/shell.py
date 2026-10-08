"""
Interactive shell mode for local_dbms.

Usage: type 's' from the main menu, or run:
    python main.py --shell

Supported commands:
    tables                      List all tables
    describe <table>            Describe a table
    select <table>              View records (paginated)
    search <table> <col> <kw>   Search records
    indexes [table]             List indexes
    stats                       Database statistics
    explorer                    Database tree view
    backup                      Backup database
    import                      Import CSV
    export                      Export CSV
    sql                         Enter raw SQL console
    help                        Show this help
    clear                       Clear screen
    exit / quit                 Return to menu
"""
import logging
import os
import time

from db.transactions import readonly_cursor, transaction
from utils.formatters import (
    display_table,
    error,
    fmt_duration,
    info,
    muted,
    success,
    warn,
)

logger = logging.getLogger(__name__)

HELP_TEXT = __doc__


def _sql_console() -> None:
    """Raw SQL console — executes arbitrary SQL with timing."""
    info("\nSQL Console — type 'exit' to return.\n")
    while True:
        try:
            sql = input("sql> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not sql or sql.lower() in ("exit", "quit"):
            break
        sql = sql.rstrip(";")
        is_select = sql.strip().upper().startswith("SELECT") or \
                    sql.strip().upper().startswith("EXPLAIN")
        try:
            t0 = time.perf_counter()
            if is_select:
                with readonly_cursor() as cur:
                    cur.execute(sql)
                    rows = cur.fetchall()
                    headers = [desc[0] for desc in cur.description] if cur.description else []
                elapsed = time.perf_counter() - t0
                display_table(headers, rows)
                muted(f"\n  {len(rows)} row(s)  ·  {fmt_duration(elapsed)}")
            else:
                with transaction() as (_, cur):
                    cur.execute(sql)
                    affected = cur.rowcount
                elapsed = time.perf_counter() - t0
                success(f"\n✓ OK  ·  {affected} row(s) affected  ·  {fmt_duration(elapsed)}")
        except Exception as e:
            logger.error("SQL console error: %s", e)
            error(f"\n✗ {e}")


def run_shell() -> None:
    """Start the interactive localdb> shell."""
    from db.metadata import list_indexes
    from db.transactions import readonly_cursor
    from services.backup_service import backup_db, restore_db
    from services.export_service import export_csv
    from services.import_service import import_csv
    from services.record_service import (
        delete_record,
        insert_record,
        update_record,
        view_records,
    )
    from services.stats_service import db_stats
    from services.table_service import (
        create_table,
        drop_table,
        explore_db,
        show_tables,
    )

    info("\n  LOCAL DBMS — Interactive Shell")
    muted("  Type 'help' for commands, 'exit' to return to menu.\n")

    while True:
        try:
            raw = input("localdb> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not raw:
            continue

        parts = raw.split()
        cmd = parts[0].lower()

        if cmd in ("exit", "quit", "q"):
            break

        elif cmd == "help":
            info(HELP_TEXT)

        elif cmd == "clear":
            os.system("clear" if os.name != "nt" else "cls")

        elif cmd == "tables":
            show_tables()

        elif cmd == "describe" and len(parts) >= 2:
            from db.metadata import get_columns, get_foreign_keys
            tname = parts[1]
            try:
                with readonly_cursor() as cur:
                    cols = get_columns(cur, tname)
                    fks  = get_foreign_keys(cur, tname)
                if not cols:
                    error(f"✗ Table '{tname}' not found.")
                    continue
                rows = [
                    (c["name"], c["type"], c["nullable"], c["default"] or "", "✓" if c["primary_key"] == "YES" else "")
                    for c in cols
                ]
                display_table(["Column", "Type", "Nullable", "Default", "PK"], rows)
                if fks:
                    display_table(
                        ["Column", "→ Table", "→ Column"],
                        [(f["column"], f["foreign_table"], f["foreign_column"]) for f in fks],
                    )
            except Exception as e:
                error(f"✗ {e}")

        elif cmd == "select" and len(parts) >= 2:
            view_records(parts[1])

        elif cmd == "search" and len(parts) >= 4:
            tname, col, keyword = parts[1], parts[2], " ".join(parts[3:])
            try:
                from db.metadata import get_column_names, quote_ident
                with readonly_cursor() as cur:
                    all_cols = get_column_names(cur, tname)
                    t0 = time.perf_counter()
                    cur.execute(
                        f"SELECT * FROM {quote_ident(tname)} WHERE {quote_ident(col)}::text ILIKE %s",
                        (f"%{keyword}%",),
                    )
                    rows = cur.fetchall()
                elapsed = time.perf_counter() - t0
                display_table(all_cols, rows)
                muted(f"\n  {len(rows)} row(s)  ·  {fmt_duration(elapsed)}")
            except Exception as e:
                error(f"✗ {e}")

        elif cmd == "indexes":
            from db.metadata import list_indexes
            tname = parts[1] if len(parts) >= 2 else None
            try:
                with readonly_cursor() as cur:
                    idxs = list_indexes(cur, tname)
                if not idxs:
                    warn("No indexes found.")
                    continue
                display_table(
                    ["Index", "Table", "Unique", "Primary", "Columns"],
                    [(i["index_name"], i["table_name"], i["is_unique"], i["is_primary"], i["columns"]) for i in idxs],
                )
            except Exception as e:
                error(f"✗ {e}")

        elif cmd == "stats":
            db_stats()

        elif cmd == "explorer":
            explore_db()

        elif cmd == "backup":
            backup_db()

        elif cmd == "restore":
            restore_db()

        elif cmd == "import":
            import_csv()

        elif cmd == "export":
            export_csv()

        elif cmd == "sql":
            _sql_console()

        elif cmd == "insert":
            insert_record()

        elif cmd == "update":
            update_record()

        elif cmd == "delete":
            delete_record()

        elif cmd == "drop":
            drop_table()

        elif cmd == "create":
            create_table()

        else:
            warn(f"  Unknown command: '{raw}'. Type 'help' for available commands.")
