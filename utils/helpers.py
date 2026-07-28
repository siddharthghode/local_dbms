from colorama import Fore, Style

SKIP_COLUMNS = {"id", "created_at", "updated_at"}


def select_table(cursor):
    cursor.execute("""
        SELECT tablename FROM pg_tables
        WHERE schemaname = 'public'
        ORDER BY tablename;
    """)
    tables = [row[0] for row in cursor.fetchall()]
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


def get_table_columns(cursor, table_name):
    cursor.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = %s
        ORDER BY ordinal_position;
    """, (table_name,))
    return [row[0] for row in cursor.fetchall()]


def get_editable_columns(columns):
    return [col for col in columns if col not in SKIP_COLUMNS]
