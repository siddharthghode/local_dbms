def non_empty(value, label="Value"):
    if not value.strip():
        raise ValueError(f"{label} cannot be empty.")
    return value.strip()


def positive_int(value, label="Number"):
    try:
        n = int(value)
        if n <= 0:
            raise ValueError
        return n
    except ValueError:
        raise ValueError(f"{label} must be a positive integer.")
