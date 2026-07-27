from db import conn, cursor
from utils.validators import non_empty, positive_int


DATATYPE_MAP = {
    "1": "INT",
    "3": "TEXT",
    "4": "DATE",
    "5": "BOOLEAN",
    "7": "FLOAT",
    "8": "TIMESTAMP",
}


def _get_datatype():
    print("""
Choose Data Type
1. INT      2. VARCHAR  3. TEXT
4. DATE     5. BOOLEAN  6. DECIMAL
7. FLOAT    8. TIMESTAMP
""")
    choice = input("Enter Choice: ").strip()

    if choice in DATATYPE_MAP:
        return DATATYPE_MAP[choice]
    elif choice == "2":
        length = input("VARCHAR Length: ").strip()
        return f"VARCHAR({length})"
    elif choice == "6":
        p = input("Precision (e.g. 10): ").strip()
        s = input("Scale (e.g. 2): ").strip()
        return f"DECIMAL({p},{s})"
    else:
        raise ValueError("Invalid datatype selected.")


def create_table():
    print("\n========== CREATE TABLE ==========\n")
    try:
        table_name = non_empty(input("Enter Table Name: "), "Table name")
        total_columns = positive_int(input("Enter Number of Columns: "), "Column count")

        columns = []
        for i in range(total_columns):
            print(f"\n---------- Column {i + 1} ----------")
            col_name = non_empty(input("Column Name: "), "Column name")
            datatype = _get_datatype()
            constraint = ""
            if input("NOT NULL? (y/n): ").lower() == "y":
                constraint += " NOT NULL"
            if input("UNIQUE? (y/n): ").lower() == "y":
                constraint += " UNIQUE"
            columns.append(f"{col_name} {datatype}{constraint}")

        query = f"""
        CREATE TABLE {table_name} (
            id SERIAL PRIMARY KEY,
            {', '.join(columns)},
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        cursor.execute(query)
        conn.commit()
        print("\n✅ Table created successfully!")

    except ValueError as e:
        print(f"\n❌ {e}")
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Error: {e}")
