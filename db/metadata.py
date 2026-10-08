"""
Database metadata queries for local_dbms.
All queries use parameterized inputs; identifiers are validated before use.
"""
import logging
from typing import Any

import psycopg

logger = logging.getLogger(__name__)


# ── identifier safety ──────────────────────────────────────────────────────────

def quote_ident(name: str) -> str:
    """
    Return a safely double-quoted PostgreSQL identifier.
    Raises ValueError for names containing null bytes.
    """
    if "\x00" in name:
        raise ValueError(f"Invalid identifier: {name!r}")
    return '"' + name.replace('"', '""') + '"'


def validate_identifier(name: str) -> str:
    """
    Validate that a name is a safe PostgreSQL identifier.
    Allows letters, digits, underscores, and dollar signs only.
    """
    import re
    if not re.match(r'^[A-Za-z_][A-Za-z0-9_$]*$', name):
        raise ValueError(
            f"Invalid identifier {name!r}. "
            "Use only letters, digits, underscores, or dollar signs."
        )
    return name


# ── table metadata ─────────────────────────────────────────────────────────────

def list_tables(cur: psycopg.Cursor) -> list[str]:
    cur.execute("""
        SELECT tablename FROM pg_tables
        WHERE schemaname = 'public'
        ORDER BY tablename;
    """)
    return [row[0] for row in cur.fetchall()]


def list_views(cur: psycopg.Cursor) -> list[str]:
    cur.execute("""
        SELECT viewname FROM pg_views
        WHERE schemaname = 'public'
        ORDER BY viewname;
    """)
    return [row[0] for row in cur.fetchall()]


def list_sequences(cur: psycopg.Cursor) -> list[str]:
    cur.execute("""
        SELECT sequencename FROM pg_sequences
        WHERE schemaname = 'public'
        ORDER BY sequencename;
    """)
    return [row[0] for row in cur.fetchall()]


def get_columns(cur: psycopg.Cursor, table_name: str) -> list[dict[str, Any]]:
    """Return column metadata for a table."""
    cur.execute("""
        SELECT
            c.column_name,
            c.data_type,
            c.character_maximum_length,
            c.is_nullable,
            c.column_default,
            CASE WHEN pk.column_name IS NOT NULL THEN 'YES' ELSE 'NO' END AS is_primary_key
        FROM information_schema.columns c
        LEFT JOIN (
            SELECT ku.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage ku
              ON tc.constraint_name = ku.constraint_name
             AND tc.table_name = ku.table_name
            WHERE tc.constraint_type = 'PRIMARY KEY'
              AND tc.table_name = %s
        ) pk ON pk.column_name = c.column_name
        WHERE c.table_name = %s
        ORDER BY c.ordinal_position;
    """, (table_name, table_name))
    rows = cur.fetchall()
    return [
        {
            "name":        r[0],
            "type":        r[1],
            "max_length":  r[2],
            "nullable":    r[3],
            "default":     r[4],
            "primary_key": r[5],
        }
        for r in rows
    ]


def get_column_names(cur: psycopg.Cursor, table_name: str) -> list[str]:
    cur.execute("""
        SELECT column_name FROM information_schema.columns
        WHERE table_name = %s
        ORDER BY ordinal_position;
    """, (table_name,))
    return [row[0] for row in cur.fetchall()]


def get_foreign_keys(cur: psycopg.Cursor, table_name: str) -> list[dict[str, str]]:
    cur.execute("""
        SELECT
            kcu.column_name,
            ccu.table_name  AS foreign_table,
            ccu.column_name AS foreign_column
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
          ON tc.constraint_name = kcu.constraint_name
         AND tc.table_schema = kcu.table_schema
        JOIN information_schema.constraint_column_usage AS ccu
          ON ccu.constraint_name = tc.constraint_name
         AND ccu.table_schema = tc.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY'
          AND tc.table_name = %s;
    """, (table_name,))
    return [
        {"column": r[0], "foreign_table": r[1], "foreign_column": r[2]}
        for r in cur.fetchall()
    ]


# ── index metadata ─────────────────────────────────────────────────────────────

def list_indexes(cur: psycopg.Cursor, table_name: str | None = None) -> list[dict[str, Any]]:
    """List indexes, optionally filtered by table."""
    query = """
        SELECT
            i.relname        AS index_name,
            t.relname        AS table_name,
            ix.indisunique   AS is_unique,
            ix.indisprimary  AS is_primary,
            array_to_string(array_agg(a.attname ORDER BY k.n), ', ') AS columns
        FROM pg_class t
        JOIN pg_index ix ON t.oid = ix.indrelid
        JOIN pg_class i  ON i.oid = ix.indexrelid
        JOIN pg_namespace n ON n.oid = t.relnamespace
        JOIN LATERAL unnest(ix.indkey) WITH ORDINALITY AS k(attnum, n)
          ON TRUE
        JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = k.attnum
        WHERE n.nspname = 'public'
    """
    params: list[Any] = []
    if table_name:
        query += " AND t.relname = %s"
        params.append(table_name)
    query += " GROUP BY i.relname, t.relname, ix.indisunique, ix.indisprimary ORDER BY t.relname, i.relname;"
    cur.execute(query, params)
    return [
        {
            "index_name": r[0],
            "table_name": r[1],
            "is_unique":  r[2],
            "is_primary": r[3],
            "columns":    r[4],
        }
        for r in cur.fetchall()
    ]


# ── statistics ─────────────────────────────────────────────────────────────────

def get_table_stats(cur: psycopg.Cursor) -> list[dict[str, Any]]:
    """Return per-table stats: rows, size, index size, column count, index count."""
    cur.execute("""
        SELECT
            t.tablename,
            pg_size_pretty(pg_total_relation_size(quote_ident(t.tablename)))  AS total_size,
            pg_size_pretty(pg_relation_size(quote_ident(t.tablename)))        AS table_size,
            pg_size_pretty(
                pg_total_relation_size(quote_ident(t.tablename))
                - pg_relation_size(quote_ident(t.tablename))
            )                                                                  AS index_size,
            COUNT(DISTINCT c.column_name)                                      AS columns,
            COUNT(DISTINCT i.indexname)                                        AS indexes
        FROM pg_tables t
        JOIN information_schema.columns c ON c.table_name = t.tablename
        LEFT JOIN pg_indexes i ON i.tablename = t.tablename
        WHERE t.schemaname = 'public'
        GROUP BY t.tablename
        ORDER BY pg_total_relation_size(quote_ident(t.tablename)) DESC;
    """)
    rows = cur.fetchall()
    stats = []
    for table, total, tsize, isize, cols, idxs in rows:
        cur.execute(f"SELECT COUNT(*) FROM {quote_ident(table)}")
        row_count = cur.fetchone()[0]
        stats.append({
            "table":      table,
            "rows":       row_count,
            "total_size": total,
            "table_size": tsize,
            "index_size": isize,
            "columns":    cols,
            "indexes":    idxs,
        })
    return stats


def get_db_size(cur: psycopg.Cursor, dbname: str) -> str:
    cur.execute("SELECT pg_size_pretty(pg_database_size(%s));", (dbname,))
    return cur.fetchone()[0]
