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
from utils.display import success, error, info, muted


def print_menu():
    info("\n=========================================")
    info("      PostgreSQL Database Manager")
    info("=========================================")

    info("\n  Database")
    muted("  ---------")
    muted("  1.  Create Table")
    muted("  2.  Show Tables")
    muted("  3.  Describe Table")
    muted("  4.  Drop Table")

    info("\n  Records")
    muted("  --------")
    muted("  5.  Insert Record")
    muted("  6.  View Records")
    muted("  7.  Search Records")
    muted("  8.  Update Record")
    muted("  9.  Delete Record")

    info("\n  Import / Export")
    muted("  ---------------")
    muted("  10. Export Table to CSV")
    muted("  11. Import CSV into Table")

    info("\n  Utilities")
    muted("  ---------")
    muted("  12. Database Statistics")
    muted("  13. Backup Database")

    info("\n  0.  Exit")
    info("=========================================")


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
