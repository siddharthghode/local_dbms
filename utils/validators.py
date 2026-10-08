"""Input validation helpers."""
import re


def non_empty(value: str, label: str = "Value") -> str:
    if not value.strip():
        raise ValueError(f"{label} cannot be empty.")
    return value.strip()


def positive_int(value: str, label: str = "Number") -> int:
    try:
        n = int(value)
        if n <= 0:
            raise ValueError
        return n
    except ValueError:
        raise ValueError(f"{label} must be a positive integer.")


def safe_identifier(name: str) -> str:
    """
    Validate a PostgreSQL identifier (table/column name).
    Raises ValueError if the name contains unsafe characters.
    """
    name = name.strip()
    if not name:
        raise ValueError("Identifier cannot be empty.")
    if not re.match(r'^[A-Za-z_][A-Za-z0-9_$]*$', name):
        raise ValueError(
            f"Invalid identifier {name!r}. "
            "Only letters, digits, underscores, and dollar signs are allowed."
        )
    if len(name) > 63:
        raise ValueError(f"Identifier {name!r} exceeds PostgreSQL's 63-character limit.")
    return name.lower()
