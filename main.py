from crud.create import create_table
from crud.read import show_tables, describe_table, view_records
from crud.insert import insert_record
from crud.update import update_record
from crud.delete import delete_record, drop_table
from utils.display import success, error, info, muted


while True:
    info("\n========== DATABASE MENU ==========")
    muted("1. Create Table")
    muted("2. Show Tables")
    muted("3. Describe Table")
    muted("4. Insert Record")
    muted("5. View Records")
    muted("6. Update Record")
    muted("7. Delete Record")
    muted("8. Drop Table")
    muted("9. Exit")
    info("===================================")

    match input("Enter Choice: "):
        case "1": create_table()
        case "2": show_tables()
        case "3": describe_table()
        case "4": insert_record()
        case "5": view_records()
        case "6": update_record()
        case "7": delete_record()
        case "8": drop_table()
        case "9":
            success("\nGood Bye!")
            break
        case _:
            error("Invalid Choice")
