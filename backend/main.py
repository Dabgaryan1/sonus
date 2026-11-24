
import os
import json
import sqlite3
from contextlib import closing

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


DATABASE_PATH = os.getenv("SONUS_DB_PATH", "sonus.db")

app = FastAPI(title="Sonus API")


def initialize_database():
    """Initialize the session table and handle the original schema."""
    with closing(sqlite3.connect(DATABASE_PATH)) as connection:
        with connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS music_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chord_sequence TEXT NOT NULL DEFAULT '[]'
                )
                """
            )

            columns = {
                row[1]
                for row in connection.execute(
                    "PRAGMA table_info(music_sessions)"
                )
            }

            # Migrate the original schema if necessary.
            if "chord_sequence" not in columns:
                connection.execute(
                    """
                    CREATE TABLE music_sessions_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        chord_sequence TEXT NOT NULL DEFAULT '[]'
                    )
                    """
                )

                # Preserve existing session IDs.
                connection.execute(
                    """
                    INSERT INTO music_sessions_new (id)
                    SELECT id FROM music_sessions
                    """
                )

                connection.execute(
                    "DROP TABLE music_sessions"
                )
                connection.execute(
                    """
                    ALTER TABLE music_sessions_new
                    RENAME TO music_sessions
                    """
                )


# Initialize the database when the module loads.
initialize_database()


class ChordRequest(BaseModel):
    chord: str


@app.get("/")
def root():
    return {"message": "Sonus is running"}


@app.post("/sessions")
def create_session():
    with closing(sqlite3.connect(DATABASE_PATH)) as connection:
        with connection:
            cursor = connection.execute(
                """
                INSERT INTO music_sessions (chord_sequence)
                VALUES (?)
                """,
                (json.dumps([]),)
            )
            session_id = cursor.lastrowid

    return {
        "session_id": session_id,
        "chord_sequence": []
    }


@app.post("/sessions/{session_id}/chords")
def save_parsed_chords(session_id: int, chords: list[str]):
    with closing(sqlite3.connect(DATABASE_PATH)) as connection:
        with connection:
            result = connection.execute(
                """
                UPDATE music_sessions
                SET chord_sequence = ?
                WHERE id = ?
                """,
                (json.dumps(chords), session_id)
            )

            if result.rowcount == 0:
                raise HTTPException(
                    status_code=404,
                    detail="Session not found"
                )

    return {
        "session_id": session_id,
        "chord_sequence": chords
    }


@app.post("/sessions/{session_id}/choose")
def choose_chord(session_id: int, chord: ChordRequest):
    with closing(sqlite3.connect(DATABASE_PATH)) as connection:
        with connection:
            result = connection.execute(
                """
                SELECT chord_sequence
                FROM music_sessions
                WHERE id = ?
                """,
                (session_id,)
            ).fetchone()

            if result is None:
                raise HTTPException(
                    status_code=404,
                    detail="Session not found"
                )

            chords = json.loads(result[0])
            chords.append(chord.chord)

            connection.execute(
                """
                UPDATE music_sessions
                SET chord_sequence = ?
                WHERE id = ?
                """,
                (json.dumps(chords), session_id)
            )

    return {
        "selected_chord": chord.chord,
        "updated_sequence": chords
    }
