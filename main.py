"""
LOCAL DBMS — Lightweight PostgreSQL Administration CLI
Entry point: initialises logging, connection pool, then runs the menu loop.
"""
import logging
import sys

from utils.logging_setup import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


def _init_pool() -> bool:
    """Initialise the connection pool; return False on failure."""
    try:
        from db.pool import get_pool
        get_pool()
        return True
    except OSError as e:
        from utils.formatters import error
        error(f"\n✗ Configuration error: {e}")
        error("  Create a .env file with DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, DB_PORT.")
        return False
    except Exception as e:
        from utils.formatters import error
        error(f"\n✗ Could not connect to PostgreSQL: {e}")
        return False


def run_menu() -> None:
    from cli.menu import print_menu
    from cli.shell import run_shell
    from services.backup_service import backup_db, restore_db
    from services.export_service import export_csv
    from services.import_service import import_csv
    from services.index_service import (
        create_index,
        drop_index,
        explain_query,
        list_all_indexes,
    )
    from services.record_service import (
        delete_record,
        insert_record,
        search_records,
        update_record,
        view_records,
    )
    from services.stats_service import db_stats
    from services.table_service import (
        create_table,
        describe_table,
        drop_table,
        explore_db,
        show_tables,
    )
    from services.user_service import (
        create_role,
        drop_role,
        grant_privilege,
        list_roles,
        revoke_privilege,
    )
    from utils.formatters import error, success

    DISPATCH = {
        "1":  create_table,
        "2":  show_tables,
        "3":  describe_table,
        "4":  drop_table,
        "5":  insert_record,
        "6":  view_records,
        "7":  search_records,
        "8":  update_record,
        "9":  delete_record,
        "10": export_csv,
        "11": import_csv,
        "12": db_stats,
        "13": backup_db,
        "14": explore_db,
        "15": list_all_indexes,
        "16": create_index,
        "17": drop_index,
        "18": explain_query,
        "19": restore_db,
        "20": list_roles,
        "21": create_role,
        "22": drop_role,
        "23": grant_privilege,
        "24": revoke_privilege,
    }

    while True:
        print_menu()
        try:
            choice = input("\nEnter Choice: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if choice == "0":
            success("\nGood Bye!")
            break
        elif choice == "s":
            run_shell()
        elif choice in DISPATCH:
            DISPATCH[choice]()
        else:
            error("✗ Invalid Choice")


def main() -> None:
    logger.info("LOCAL DBMS starting.")

    # Support --shell flag for direct shell mode
    shell_mode = "--shell" in sys.argv

    if not _init_pool():
        sys.exit(1)

    from utils.formatters import success
    success("  Database connected successfully!")
    logger.info("Connected to PostgreSQL at %s.", __import__("db.config", fromlist=["DB_CONFIG"]).DB_CONFIG["host"])

    try:
        if shell_mode:
            from cli.shell import run_shell
            run_shell()
        else:
            run_menu()
    finally:
        from db.pool import close_pool
        close_pool()
        logger.info("LOCAL DBMS shutdown.")


if __name__ == "__main__":
    main()
