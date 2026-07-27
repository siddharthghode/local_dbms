from datetime import datetime
from tabulate import tabulate


def _format_value(value):
    if value is None:
        return "NULL"
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    return value


def display_table(headers, rows):
    if not rows:
        print("\nNo records found.")
        return
    formatted = [
        [_format_value(cell) for cell in row]
        for row in rows
    ]
    print(tabulate(formatted, headers=headers, tablefmt="fancy_grid"))
