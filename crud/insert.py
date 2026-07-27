from db import conn, cursor
from utils.helpers import get_table_columns, get_editable_columns, select_table


def insert_record():
    try:
        table_name = select_table(cursor)
        if not table_name:
            return

        columns = get_table_columns(cursor, table_name)
        if not columns:
            print("\nTable does not exist.")
            return

        editable = get_editable_columns(columns)

        print("\n========== ENTER RECORD ==========\n")
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
        print("\n✅ Record inserted successfully!")

    except Exception as e:
        conn.rollback()
        print(f"\nError: {e}")
