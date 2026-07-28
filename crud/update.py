from db import conn, cursor
from crud.read import view_records
from utils.helpers import get_table_columns, get_editable_columns, select_table
from utils.display import display_table, success, error, info


def update_record():
    try:
        table_name = select_table(cursor)
        if not table_name:
            return
        view_records(table_name)

        record_id = input("\nEnter ID to Update: ").strip()
        columns = get_table_columns(cursor, table_name)

        cursor.execute(f"SELECT * FROM {table_name} WHERE id=%s", (record_id,))
        record = cursor.fetchone()
        if record is None:
            error("\n✗ Record not found.")
            return

        info("\nCurrent Record:")
        display_table(columns, [record])

        editable = get_editable_columns(columns)
        info("\nSelect Columns to Update\n")
        for i, col in enumerate(editable, 1):
            print(f"{i}. {col}")

        choices = input("\nEnter column numbers (comma separated): ")
        selected = [int(x.strip()) for x in choices.split(",")]

        updates, values = [], []
        for choice in selected:
            col = editable[choice - 1]
            values.append(input(f"Enter new {col}: "))
            updates.append(f"{col} = %s")

        updates.append("updated_at = CURRENT_TIMESTAMP")
        values.append(record_id)

        cursor.execute(
            f"UPDATE {table_name} SET {', '.join(updates)} WHERE id = %s;",
            values
        )
        conn.commit()
        success("\n✓ Record updated successfully!")

    except Exception as e:
        conn.rollback()
        error(f"\n✗ Error: {e}")
