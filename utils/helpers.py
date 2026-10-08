"""Shared CLI helper utilities."""
from colorama import Fore, Style

from db.metadata import get_column_names, list_tables

SKIP_COLUMNS = {"id", "created_at", "updated_at"}


def select_table(cur) -> str | None:
    """Prompt user to pick a table from the public schema."""
    tables = list_tables(cur)
    if not tables:
        print(Fore.RED + "\n✗ No tables found.")
        return None
    print()
    for i, name in enumerate(tables, 1):
        print(Fore.CYAN + f"  {i}. " + Style.RESET_ALL + name)
    try:
        choice = int(input("\nEnter Table Number: ").strip())
        if 1 <= choice <= len(tables):
            return tables[choice - 1]
        print(Fore.RED + "✗ Invalid choice.")
    except ValueError:
        print(Fore.RED + "✗ Invalid input.")
    return None


def get_table_columns(cur, table_name: str) -> list[str]:
    return get_column_names(cur, table_name)


def get_editable_columns(columns: list[str]) -> list[str]:
    return [col for col in columns if col not in SKIP_COLUMNS]
