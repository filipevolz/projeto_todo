import os
from pathlib import Path

import db
from migrations import apply


def load_database_url():
    if os.environ.get("DATABASE_URL"):
        return
    env_path = Path(".env")
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        if line.startswith("DATABASE_URL="):
            os.environ["DATABASE_URL"] = line.split("=", 1)[1]
            return


def main():
    load_database_url()
    connection = db.connect()
    try:
        applied = apply(connection)
    finally:
        connection.close()
    if applied:
        for version in applied:
            print(f"applied {version}")
    else:
        print("up to date")


if __name__ == "__main__":
    main()
