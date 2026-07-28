from crud.create import create_table
from crud.read import show_tables, describe_table, view_records
from crud.insert import insert_record
from crud.update import update_record
from crud.delete import delete_record, drop_table
from crud.export import export_csv
from crud.import_csv import import_csv
from crud.search import search_records
from utils.stats import db_stats
from utils.backup import backup_db
from utils.display import success, error


def print_menu():
    C = "\033[96m"   # cyan
    D = "\033[2m"    # dim
    R = "\033[0m"    # reset

    rows = [
        ("1. Create",   "5. Insert",   "10. Export CSV",  "12. DB Stats"),
        ("2. Show",     "6. View",     "11. Import CSV",  "13. Backup DB"),
        ("3. Describe", "7. Search",   "",                ""),
        ("4. Drop",     "8. Update",   "",                ""),
        ("",            "9. Delete",   "",                ""),
    ]

    W = [16, 18, 18, 20]  # column widths

    def cell(text, w):
        return text.ljust(w)

    print()
    print(C + "┌" + "─" * 76 + "┐" + R)
    print(C + "│" + R + " PostgreSQL Database Manager".center(76) + C + "│" + R)
    print(C + "├" + "─"*W[0] + "┬" + "─"*W[1] + "┬" + "─"*W[2] + "┬" + "─"*W[3] + "┤" + R)
    print(C + "│" + R + D + " DATABASE".ljust(W[0]) + C + "│" + R + D + " RECORDS".ljust(W[1]) + C + "│" + R + D + " IMPORT / EXPORT".ljust(W[2]) + C + "│" + R + D + " UTILITIES".ljust(W[3]) + C + "│" + R)
    print(C + "├" + "─"*W[0] + "┼" + "─"*W[1] + "┼" + "─"*W[2] + "┼" + "─"*W[3] + "┤" + R)

    for r in rows:
        line = C + "│" + R
        for i, col in enumerate(r):
            line += D + " " + cell(col, W[i] - 1) + R + C + "│" + R
        print(line)

    print(C + "├" + "─"*W[0] + "┴" + "─"*W[1] + "┴" + "─"*W[2] + "┴" + "─"*W[3] + "┤" + R)
    print(C + "│" + R + D + " 0. Exit".ljust(76) + C + "│" + R)
    print(C + "└" + "─" * 76 + "┘" + R)


while True:
    print_menu()

    match input("\nEnter Choice: ").strip():
        case "1":  create_table()
        case "2":  show_tables()
        case "3":  describe_table()
        case "4":  drop_table()
        case "5":  insert_record()
        case "6":  view_records()
        case "7":  search_records()
        case "8":  update_record()
        case "9":  delete_record()
        case "10": export_csv()
        case "11": import_csv()
        case "12": db_stats()
        case "13": backup_db()
        case "0":
            success("\nGood Bye!")
            break
        case _:
            error("✗ Invalid Choice")
