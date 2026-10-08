"""Integration tests for CSV import and export."""
import csv
import os
import tempfile

from db.metadata import quote_ident
from db.transactions import readonly_cursor, transaction
from tests.conftest import TEST_TABLE


def _insert_rows(rows: list[tuple]):
    with transaction() as (_, cur):
        for name, email, age in rows:
            cur.execute(
                f"INSERT INTO {TEST_TABLE} (name, email, age) VALUES (%s, %s, %s)",
                (name, email, age),
            )


# ── EXPORT ─────────────────────────────────────────────────────────────────────

def test_export_produces_csv():
    _insert_rows([("Alice", "alice@example.com", 30), ("Bob", "bob@example.com", 25)])

    with readonly_cursor() as cur:
        cur.execute(f"SELECT * FROM {TEST_TABLE}")
        rows = cur.fetchall()
        cur.execute("""
            SELECT column_name FROM information_schema.columns
            WHERE table_name = %s ORDER BY ordinal_position
        """, (TEST_TABLE,))
        headers = [r[0] for r in cur.fetchall()]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
        fname = f.name

    try:
        with open(fname, newline="") as f:
            reader = csv.reader(f)
            exported = list(reader)
        assert exported[0] == headers
        assert len(exported) == 3  # header + 2 rows
    finally:
        os.unlink(fname)


# ── IMPORT ─────────────────────────────────────────────────────────────────────

def test_import_from_csv():
    csv_data = "name,email,age\nCarol,carol@example.com,28\nDave,dave@example.com,35\n"

    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write(csv_data)
        fname = f.name

    try:
        insert_columns = ["name", "email", "age"]
        placeholders = ", ".join(["%s"] * len(insert_columns))
        cols_sql = ", ".join(quote_ident(c) for c in insert_columns)
        query = f"INSERT INTO {TEST_TABLE} ({cols_sql}) VALUES ({placeholders})"

        with open(fname, newline="") as f:
            reader = csv.DictReader(f)
            with transaction() as (_, cur):
                for row in reader:
                    cur.execute(query, [row.get(c) for c in insert_columns])

        with readonly_cursor() as cur:
            cur.execute(f"SELECT COUNT(*) FROM {TEST_TABLE}")
            count = cur.fetchone()[0]
        assert count == 2
    finally:
        os.unlink(fname)


def test_import_missing_column_detected():
    """CSV missing a required column should be caught before insert."""
    csv_data = "name,age\nEve,22\n"  # missing 'email'
    required = ["name", "email", "age"]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write(csv_data)
        fname = f.name

    try:
        with open(fname, newline="") as f:
            reader = csv.DictReader(f)
            missing = [c for c in required if c not in (reader.fieldnames or [])]
        assert "email" in missing
    finally:
        os.unlink(fname)
