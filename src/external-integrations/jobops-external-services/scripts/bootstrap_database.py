from __future__ import annotations

import os
import subprocess
import sys
from urllib.parse import urlparse

import psycopg


EXPECTED_TABLES = {
    "jobs",
    "job_scores",
    "applications",
    "application_events",
    "browser_runs",
    "execution_requests",
    "alembic_version",
}


def classify_existing_tables(table_names: set[str]) -> tuple[bool, set[str]]:
    foreign = table_names - EXPECTED_TABLES
    return not foreign, foreign


def require_neon_url(database_url: str) -> None:
    parsed = urlparse(database_url)
    host = (parsed.hostname or "").lower()

    if parsed.scheme not in {"postgres", "postgresql"}:
        raise RuntimeError("JOBOPS_DATABASE_URL must be a PostgreSQL URL")
    if not host.endswith(".neon.tech"):
        raise RuntimeError(
            "Refusing bootstrap: JOBOPS_DATABASE_URL is not a Neon database host"
        )


def public_tables(connection: psycopg.Connection) -> set[str]:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
              AND table_type = 'BASE TABLE'
            """
        )
        return {row[0] for row in cursor.fetchall()}


def verify_fresh_or_jobops(connection: psycopg.Connection) -> None:
    tables = public_tables(connection)
    safe, foreign = classify_existing_tables(tables)

    if not safe:
        names = ", ".join(sorted(foreign))
        raise RuntimeError(
            "Refusing bootstrap: database contains non-JobOps tables: " + names
        )

    if tables:
        print("Preflight: existing tables are JobOps-only; safe to migrate.")
    else:
        print("Preflight: database is fresh; safe to initialize JobOps.")


def run_alembic(database_url: str) -> None:
    env = os.environ.copy()
    env["DATABASE_URL"] = database_url
    subprocess.run(
        ["alembic", "upgrade", "head"],
        check=True,
        env=env,
    )


def verify_schema(connection: psycopg.Connection) -> None:
    tables = public_tables(connection)
    missing = EXPECTED_TABLES - tables
    if missing:
        raise RuntimeError(
            "Migration incomplete; missing JobOps tables: "
            + ", ".join(sorted(missing))
        )

    with connection.cursor() as cursor:
        cursor.execute("SELECT version_num FROM alembic_version")
        row = cursor.fetchone()

    if row is None or row[0] != "0003_execution_queue":
        raise RuntimeError(
            "Unexpected Alembic revision after migration: "
            + (row[0] if row else "<none>")
        )

    print("Schema verified: JobOps revision 0003_execution_queue is active.")
    print("Tables: " + ", ".join(sorted(EXPECTED_TABLES)))


def main() -> int:
    database_url = os.getenv("JOBOPS_DATABASE_URL") or os.getenv("DATABASE_URL")
    if not database_url:
        print(
            "JOBOPS_DATABASE_URL is required. Do not commit it to the repository.",
            file=sys.stderr,
        )
        return 2

    try:
        require_neon_url(database_url)

        with psycopg.connect(database_url) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT current_database(), current_user")
                database_name, user_name = cursor.fetchone()
            print(f"Connected to isolated Neon database: {database_name}")
            print(f"Database role: {user_name}")
            verify_fresh_or_jobops(connection)

        run_alembic(database_url)

        with psycopg.connect(database_url) as connection:
            verify_schema(connection)

        print("JobOps database bootstrap completed successfully.")
        return 0
    except Exception as exc:
        print(f"BOOTSTRAP FAILED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
