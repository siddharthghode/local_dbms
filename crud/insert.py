from db import conn, cursor
from utils.helpers import get_table_columns, get_editable_columns, select_table
from utils.display import success, error, info


def insert_record():
    try:
        table_name = select_table(cursor)
        if not table_name:
            return

        columns = get_table_columns(cursor, table_name)
        if not columns:
            error("\n✗ Table does not exist.")
            return

        editable = get_editable_columns(columns)

        info("\n========== ENTER RECORD ==========\n")
        values = []
        for col in editable:
            values.append(input(f"Enter {col}: ").strip())

        placeholders = ", ".join(["%s"] * len(values))
        columns_sql = ", ".join(editable)

        cursor.execute(
            f"INSERT INTO {table_name} ({columns_sql}) VALUES ({placeholders});",
            values
        )
        conn.commit()
        success("\n✓ Record inserted successfully!")

    except Exception as e:
        conn.rollback()
        error(f"\n✗ Error: {e}")
