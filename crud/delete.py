from db import conn, cursor
from crud.read import view_records
from utils.helpers import get_table_columns, select_table
from utils.display import display_table, success, error, warn, info


def delete_record():
    try:
        table_name = select_table(cursor)
        if not table_name:
            return
        view_records(table_name)

        record_id = input("\nEnter ID to Delete: ").strip()
        columns = get_table_columns(cursor, table_name)

        cursor.execute(f"SELECT * FROM {table_name} WHERE id = %s", (record_id,))
        record = cursor.fetchone()
        if record is None:
            error("\n✗ Record not found.")
            return

        info("\nSelected Record:")
        display_table(columns, [record])

        if input("\nAre you sure you want to delete? (y/n): ").lower() != "y":
            warn("\nDeletion cancelled.")
            return

        cursor.execute(f"DELETE FROM {table_name} WHERE id = %s", (record_id,))
        conn.commit()
        success("\n✓ Record deleted successfully!")

    except Exception as e:
        conn.rollback()
        error(f"\n✗ Error: {e}")


def drop_table():
    table_name = select_table(cursor)
    if not table_name:
        return

    if input(f"\nAre you sure you want to drop '{table_name}'? (y/n): ").lower() != "y":
        warn("\nOperation cancelled.")
        return

    try:
        cursor.execute(f"DROP TABLE {table_name}")
        conn.commit()
        success("\n✓ Table dropped successfully!")
    except Exception as e:
        conn.rollback()
        error(f"\n✗ Error: {e}")
