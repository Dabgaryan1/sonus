from contextlib import closing
import os
import sqlite3
import tempfile


def test_database_migration():
    with tempfile.TemporaryDirectory() as temp_dir:
        database_path = os.path.join(temp_dir, "migration_test.db")

        # Create a database using Erendira's original schema.
        with closing(sqlite3.connect(database_path)) as connection:
            with connection:
                connection.execute(
                    """
                    CREATE TABLE music_sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL,
                        email TEXT NOT NULL
                    )
                    """
                )
                connection.execute(
                    """
                    INSERT INTO music_sessions (id, username, email)
                    VALUES (?, ?, ?)
                    """,
                    (42, "test_user", "test@example.com")
                )

        # Use the temporary database for migration.
        os.environ["SONUS_DB_PATH"] = database_path

        import subprocess
        import sys

        subprocess.run(
            [
                sys.executable,
                "-c",
                "from backend.main import initialize_database; "
                "initialize_database()"
            ],
            check=True,
            env={**os.environ, "SONUS_DB_PATH": database_path}
        )

        connection = sqlite3.connect(database_path)
        try:
            columns = [
                row[1] for row in connection.execute(
                    "PRAGMA table_info(music_sessions)"
                )
            ]

            row = connection.execute(
                "SELECT id, chord_sequence FROM music_sessions WHERE id = 42"
            ).fetchone()
        finally:
            connection.close()

        assert columns == ["id", "chord_sequence"]
        assert row == (42, "[]")

        print("database migration test OK")


if __name__ == "__main__":
    test_database_migration()
