from db import cursor
from utils.display import display_table, error, info


def db_stats():
    try:
        cursor.execute("""
            SELECT
                t.tablename,
                pg_size_pretty(pg_total_relation_size(quote_ident(t.tablename))) AS size,
                COUNT(c.column_name) AS columns
            FROM pg_tables t
            JOIN information_schema.columns c ON c.table_name = t.tablename
            WHERE t.schemaname = 'public'
            GROUP BY t.tablename
            ORDER BY t.tablename;
        """)
        rows = cursor.fetchall()

        if not rows:
            info("\nNo tables found.")
            return

        # Row counts per table
        stats = []
        for table, size, cols in rows:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            row_count = cursor.fetchone()[0]
            stats.append((table, cols, row_count, size))

        display_table(["Table", "Columns", "Rows", "Size"], stats)

    except Exception as e:
        error(f"\n✗ Error: {e}")
