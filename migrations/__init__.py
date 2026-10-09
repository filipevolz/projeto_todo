from pathlib import Path

MIGRATIONS_DIR = Path(__file__).parent

CREATE_MIGRATIONS_TABLE = """
CREATE TABLE IF NOT EXISTS schema_migrations (
    version text PRIMARY KEY,
    applied_at timestamptz NOT NULL DEFAULT now()
)
"""


def apply(connection):
    connection.execute(CREATE_MIGRATIONS_TABLE)
    connection.commit()
    applied = {
        row[0]
        for row in connection.execute("SELECT version FROM schema_migrations")
    }
    pending = []
    for path in sorted(MIGRATIONS_DIR.glob("*.sql")):
        if path.name in applied:
            continue
        try:
            connection.execute(path.read_text(), prepare=False)
            connection.execute(
                "INSERT INTO schema_migrations (version) VALUES (%s)",
                (path.name,),
            )
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        pending.append(path.name)
    return pending
