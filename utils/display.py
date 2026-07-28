from datetime import datetime
from tabulate import tabulate
from colorama import Fore, Style, init

init(autoreset=True)


# ── colored print helpers ──────────────────────────────────────────────────────

def success(msg):
    print(Fore.GREEN + msg)

def error(msg):
    print(Fore.RED + msg)

def warn(msg):
    print(Fore.YELLOW + msg)

def info(msg):
    print(Fore.CYAN + msg)

def muted(msg):
    print(Fore.WHITE + Style.DIM + msg)


# ── table display ──────────────────────────────────────────────────────────────

def _format_value(value):
    if value is None:
        return "NULL"
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    return value


def display_table(headers, rows):
    if not rows:
        warn("\nNo records found.")
        return
    formatted = [
        [_format_value(cell) for cell in row]
        for row in rows
    ]
    print(tabulate(formatted, headers=headers, tablefmt="fancy_grid"))
