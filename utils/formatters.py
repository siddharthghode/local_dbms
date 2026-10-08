"""Terminal output formatters for local_dbms."""
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from colorama import Fore, Style, init
from tabulate import tabulate

init(autoreset=True)


# ── colored print helpers ──────────────────────────────────────────────────────

def success(msg: str) -> None:
    print(Fore.GREEN + msg)

def error(msg: str) -> None:
    print(Fore.RED + msg)

def warn(msg: str) -> None:
    print(Fore.YELLOW + msg)

def info(msg: str) -> None:
    print(Fore.CYAN + msg)

def muted(msg: str) -> None:
    print(Fore.WHITE + Style.DIM + msg)

def bold(msg: str) -> None:
    print(Style.BRIGHT + msg)

def header(title: str) -> None:
    print()
    print(Fore.CYAN + Style.BRIGHT + f"  ── {title} " + "─" * max(0, 50 - len(title)))


# ── value formatting ───────────────────────────────────────────────────────────

def _fmt(value: Any) -> Any:
    if value is None:
        return Fore.WHITE + Style.DIM + "NULL" + Style.RESET_ALL
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(value, date):
        return str(value)
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, bool):
        return "true" if value else "false"
    return value


# ── table display ──────────────────────────────────────────────────────────────

def display_table(headers: list[str], rows: list[Any], fmt: str = "fancy_grid") -> None:
    if not rows:
        warn("\nNo records found.")
        return
    formatted = [[_fmt(cell) for cell in row] for row in rows]
    print(tabulate(formatted, headers=headers, tablefmt=fmt))


def display_page(
    headers: list[str],
    rows: list[Any],
    page: int,
    total_pages: int,
    total_rows: int,
) -> None:
    """Display a page of results with pagination info."""
    display_table(headers, rows)
    print()
    muted(
        f"  Page {page}/{total_pages}  ·  "
        f"Showing {len(rows)} of {total_rows} rows  ·  "
        "Commands: next · prev · first · last · page N · exit"
    )


# ── timing ─────────────────────────────────────────────────────────────────────

def fmt_duration(seconds: float) -> str:
    if seconds < 1:
        return f"{seconds * 1000:.1f} ms"
    return f"{seconds:.2f} s"


# ── tree view ──────────────────────────────────────────────────────────────────

def print_tree(
    db_name: str,
    tables: list[str],
    views: list[str],
    indexes: list[str],
    sequences: list[str],
) -> None:
    C = Fore.CYAN
    G = Fore.GREEN
    Y = Fore.YELLOW
    M = Fore.MAGENTA
    R = Style.RESET_ALL

    print(f"\n{C}Database: {Style.BRIGHT}{db_name}{R}")
    print(f"{C}├── Tables{R}")
    for i, t in enumerate(tables):
        prefix = "│   └──" if i == len(tables) - 1 else "│   ├──"
        print(f"{C}{prefix}{R} {G}{t}{R}")
    print(f"{C}├── Views{R}")
    for i, v in enumerate(views):
        prefix = "│   └──" if i == len(views) - 1 else "│   ├──"
        print(f"{C}{prefix}{R} {Y}{v}{R}")
    print(f"{C}├── Indexes{R}")
    for i, idx in enumerate(indexes):
        prefix = "│   └──" if i == len(indexes) - 1 else "│   ├──"
        print(f"{C}{prefix}{R} {M}{idx}{R}")
    print(f"{C}└── Sequences{R}")
    for i, s in enumerate(sequences):
        prefix = "    └──" if i == len(sequences) - 1 else "    ├──"
        print(f"{C}{prefix}{R} {s}")
