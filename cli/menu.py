"""Terminal menu for local_dbms."""
from colorama import Fore, Style


def print_menu() -> None:
    C = Fore.CYAN
    D = Style.DIM
    B = Style.BRIGHT
    R = Style.RESET_ALL

    sections = [
        ("DATABASE",        ["1. Create Table", "2. Show Tables", "3. Describe", "4. Drop Table", "14. Explorer"]),
        ("RECORDS",         ["5. Insert", "6. View", "7. Search", "8. Update", "9. Delete"]),
        ("IMPORT / EXPORT", ["10. Export CSV", "11. Import CSV"]),
        ("INDEXES",         ["15. List Indexes", "16. Create Index", "17. Drop Index", "18. EXPLAIN"]),
        ("UTILITIES",       ["12. DB Stats", "13. Backup", "19. Restore"]),
        ("ADMIN",           ["20. List Roles", "21. Create Role", "22. Drop Role", "23. Grant", "24. Revoke"]),
    ]

    col_w = 22
    n_cols = len(sections)
    total_w = col_w * n_cols + n_cols - 1

    def pad(text: str) -> str:
        return text.ljust(col_w)

    print()
    print(C + "┌" + "─" * total_w + "┐" + R)
    print(C + "│" + R + B + " LOCAL DBMS — PostgreSQL Administration CLI".center(total_w) + R + C + "│" + R)
    print(C + "├" + ("─" * col_w + "┬") * (n_cols - 1) + "─" * col_w + "┤" + R)

    # Section headers
    header_line = C + "│" + R
    for sec, _ in sections:
        header_line += D + pad(f" {sec}") + R + C + "│" + R
    print(header_line)
    print(C + "├" + ("─" * col_w + "┼") * (n_cols - 1) + "─" * col_w + "┤" + R)

    # Rows
    max_rows = max(len(items) for _, items in sections)
    for row_i in range(max_rows):
        line = C + "│" + R
        for _, items in sections:
            text = items[row_i] if row_i < len(items) else ""
            line += D + " " + pad(text)[: col_w - 1] + R + C + "│" + R
        print(line)

    print(C + "├" + ("─" * col_w + "┴") * (n_cols - 1) + "─" * col_w + "┤" + R)
    print(C + "│" + R + D + "  s. Interactive Shell    0. Exit".ljust(total_w) + R + C + "│" + R)
    print(C + "└" + "─" * total_w + "┘" + R)
