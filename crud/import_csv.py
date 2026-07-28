import csv
import os

from db import conn, cursor
from utils.helpers import select_table, get_table_columns, get_editable_columns
from utils.display import success, error, warn, info


IMPORT_DIR = "imports"


def import_csv():
    try:
        info(f"\n  Place your CSV files in the '{IMPORT_DIR}/' folder.")

        # List available CSV files in imports/
        csv_files = [f for f in os.listdir(IMPORT_DIR) if f.endswith(".csv")]

        if csv_files:
            info("\nAvailable CSV files:")
            for i, f in enumerate(csv_files, 1):
                print(f"  {i}. {f}")
            print()

        file_input = input("Enter CSV number or filename: ").strip()

        # Resolve number to filename from the listed csv_files
        if file_input.isdigit() and csv_files:
            idx = int(file_input) - 1
            if 0 <= idx < len(csv_files):
                file_path = os.path.join(IMPORT_DIR, csv_files[idx])
            else:
                error("\n✗ Invalid number.")
                return
        else:
            file_path = file_input if os.path.isabs(file_input) else os.path.join(IMPORT_DIR, file_input)

        if not os.path.exists(file_path):
            error(f"\n✗ File not found: {file_path}")
            return

        table_name = select_table(cursor)
        if not table_name:
            return

        table_columns = get_table_columns(cursor, table_name)
        insert_columns = get_editable_columns(table_columns)

        placeholders = ", ".join(["%s"] * len(insert_columns))
        column_string = ", ".join(insert_columns)
        query = f"INSERT INTO {table_name} ({column_string}) VALUES ({placeholders})"

        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            missing = [col for col in insert_columns if col not in reader.fieldnames]
            if missing:
                error(f"\n✗ CSV is missing columns: {', '.join(missing)}")
                return

            count = 0
            for row in reader:
                values = [row.get(col, None) for col in insert_columns]
                cursor.execute(query, values)
                count += 1

        conn.commit()
        success(f"\n✓ {count} record(s) imported successfully into '{table_name}'!")

    except Exception as e:
        conn.rollback()
        error(f"\n✗ Error: {e}")
