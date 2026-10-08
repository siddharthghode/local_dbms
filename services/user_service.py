"""PostgreSQL role/user management service."""
import logging

from db.transactions import readonly_cursor, transaction
from utils.formatters import display_table, error, header, info, success, warn
from utils.validators import safe_identifier

logger = logging.getLogger(__name__)


def list_roles() -> None:
    header("ROLES")
    try:
        with readonly_cursor() as cur:
            cur.execute("""
                SELECT
                    rolname,
                    rolsuper,
                    rolcreatedb,
                    rolcreaterole,
                    rolcanlogin,
                    rolconnlimit
                FROM pg_roles
                WHERE rolname NOT LIKE 'pg_%'
                ORDER BY rolname;
            """)
            rows = cur.fetchall()
        if not rows:
            info("\nNo roles found.")
            return
        display_table(
            ["Role", "Superuser", "CreateDB", "CreateRole", "Login", "ConnLimit"],
            rows,
        )
    except Exception as e:
        logger.error("list_roles failed: %s", e)
        error(f"\n✗ Error: {e}")


def create_role() -> None:
    header("CREATE ROLE")
    try:
        role_name = safe_identifier(input("Role name: ").strip())
        can_login = input("Can login? (y/n): ").lower() == "y"
        is_super  = input("Superuser? (y/n): ").lower() == "y"

        login_kw = "LOGIN" if can_login else "NOLOGIN"
        super_kw = "SUPERUSER" if is_super else "NOSUPERUSER"

        # Password only if login role
        password_clause = ""
        if can_login:
            import getpass
            pw = getpass.getpass("Password (leave blank for no password): ")
            if pw:
                password_clause = " PASSWORD %s"

        query = f"CREATE ROLE {role_name} {login_kw} {super_kw}"
        params = []
        if password_clause:
            query += password_clause
            params.append(pw)
        query += ";"

        with transaction() as (_, cur):
            cur.execute(query, params or None)
        logger.info("Created role '%s'.", role_name)
        success(f"\n✓ Role '{role_name}' created.")

    except ValueError as e:
        error(f"\n✗ {e}")
    except Exception as e:
        logger.error("create_role failed: %s", e)
        error(f"\n✗ Error: {e}")


def drop_role() -> None:
    header("DROP ROLE")
    try:
        role_name = safe_identifier(input("Role name to drop: ").strip())
        if input(f"\nDrop role '{role_name}'? (y/n): ").lower() != "y":
            warn("\nCancelled.")
            return
        with transaction() as (_, cur):
            cur.execute(f"DROP ROLE {role_name};")
        logger.info("Dropped role '%s'.", role_name)
        success(f"\n✓ Role '{role_name}' dropped.")
    except ValueError as e:
        error(f"\n✗ {e}")
    except Exception as e:
        logger.error("drop_role failed: %s", e)
        error(f"\n✗ Error: {e}")


def grant_privilege() -> None:
    header("GRANT PRIVILEGE")
    try:
        with readonly_cursor() as cur:
            cur.execute("""
                SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename;
            """)
            tables = [r[0] for r in cur.fetchall()]

        if not tables:
            warn("\nNo tables found.")
            return

        for i, t in enumerate(tables, 1):
            print(f"  {i}. {t}")
        choice = int(input("\nTable number: ").strip())
        table_name = tables[choice - 1]

        role_name = safe_identifier(input("Role name: ").strip())
        info("\nPrivileges: SELECT, INSERT, UPDATE, DELETE, ALL")
        privilege = input("Privilege: ").strip().upper()
        if privilege not in ("SELECT", "INSERT", "UPDATE", "DELETE", "ALL"):
            error("\n✗ Invalid privilege.")
            return

        with transaction() as (_, cur):
            cur.execute(f"GRANT {privilege} ON {table_name} TO {role_name};")
        logger.info("Granted %s on '%s' to '%s'.", privilege, table_name, role_name)
        success(f"\n✓ Granted {privilege} on '{table_name}' to '{role_name}'.")

    except (ValueError, IndexError):
        error("\n✗ Invalid selection.")
    except Exception as e:
        logger.error("grant_privilege failed: %s", e)
        error(f"\n✗ Error: {e}")


def revoke_privilege() -> None:
    header("REVOKE PRIVILEGE")
    try:
        with readonly_cursor() as cur:
            cur.execute("""
                SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename;
            """)
            tables = [r[0] for r in cur.fetchall()]

        for i, t in enumerate(tables, 1):
            print(f"  {i}. {t}")
        choice = int(input("\nTable number: ").strip())
        table_name = tables[choice - 1]

        role_name = safe_identifier(input("Role name: ").strip())
        privilege = input("Privilege (SELECT/INSERT/UPDATE/DELETE/ALL): ").strip().upper()

        with transaction() as (_, cur):
            cur.execute(f"REVOKE {privilege} ON {table_name} FROM {role_name};")
        logger.info("Revoked %s on '%s' from '%s'.", privilege, table_name, role_name)
        success(f"\n✓ Revoked {privilege} on '{table_name}' from '{role_name}'.")

    except (ValueError, IndexError):
        error("\n✗ Invalid selection.")
    except Exception as e:
        logger.error("revoke_privilege failed: %s", e)
        error(f"\n✗ Error: {e}")
