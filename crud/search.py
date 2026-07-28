from db import cursor
from utils.helpers import select_table, get_table_columns, get_editable_columns
from utils.display import display_table, error, info, warn


def search_records():
    try:
        table_name = select_table(cursor)
        if not table_name:
            return

        columns = get_table_columns(cursor, table_name)
        editable = get_editable_columns(columns)

        info("\nSearch by column:\n")
        for i, col in enumerate(editable, 1):
            print(f"  {i}. {col}")

        choice = input("\nEnter column number: ").strip()
        col = editable[int(choice) - 1]

        keyword = input(f"Enter search value for '{col}': ").strip()

        cursor.execute(
            f"SELECT * FROM {table_name} WHERE {col}::text ILIKE %s",
            (f"%{keyword}%",)
        )
        rows = cursor.fetchall()
        display_table(columns, rows)

    except (ValueError, IndexError):
        error("\n✗ Invalid selection.")
    except Exception as e:
        error(f"\n✗ Error: {e}")
