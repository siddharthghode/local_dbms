from db import cursor
from utils.display import display_table, error
from utils.helpers import get_table_columns, select_table


def show_tables():
    try:
        cursor.execute("""
            SELECT tablename FROM pg_tables
            WHERE schemaname = 'public'
            ORDER BY tablename;
        """)
        tables = cursor.fetchall()
        if not tables:
            error("\n✗ No tables found.")
            return
        display_table(["#", "Table"], [(i, t[0]) for i, t in enumerate(tables, 1)])
    except Exception as e:
        error(f"Error: {e}")


def describe_table():
    table_name = select_table(cursor)
    if not table_name:
        return
    try:
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = %s
            ORDER BY ordinal_position;
        """, (table_name,))
        columns = cursor.fetchall()
        if not columns:
            error("✗ Table not found.")
            return
        display_table(["Column", "Type", "Nullable"], columns)
    except Exception as e:
        error(f"Error: {e}")


def view_records(table_name=None):
    if table_name is None:
        table_name = select_table(cursor)
        if not table_name:
            return
    try:
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        headers = get_table_columns(cursor, table_name)
        display_table(headers, rows)
    except Exception as e:
        error(f"Error: {e}")
