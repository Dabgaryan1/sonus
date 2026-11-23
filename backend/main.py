from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
import json

#create the FastAPI app
app = FastAPI(title="Sonus API")

# Create Database table if it does not exist
def initialize_database():
    with sqlite3.connect("sonus.db") as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS music_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                email TEXT NOT NULL
            )
            """
        )

#runs database setup when the application starts
initialize_database()


class ChordRequest(BaseModel):
    chord: str

#root directory
@app.get("/")
def root():
    return {"message": "Sonus is running"}

#create session
@app.post("/sessions")
def create_session():
    with sqlite3.connect("sonus.db") as connection:
        cursor = connection.execute(
            "INSERT INTO music_sessions (chord_sequence) VALUES (?)",
            (json.dumps([]),)
        )
        return{
            "session_id": cursor.lastrowid,
            "chord_sequence": []
        }

#add chords from parsed chords
@app.post("/sessions/{session_id}/chords")
def save_parsed_chords(session_id: int, chords: list[str]):
    result = connection.execute(
        """
        UPDATE music_sessions
        SET chord_sequence = ?
        where id = ?
        """,
        (json.dumps(chords), session_id)
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Session not found")
    return{
        "session_id": session_id,
        "chord_sequence": chords
    }

#add chord selected from recomendations
@app.post("/sessions/{session_id}/choose")
def choose_chord(session_id: int, chord: ChordRequest):
    with sqlite3.connect("sonus.db") as connection:
        result = connection.execute(
            "SELECT chord_sequence FROM music_sessions WHERE id = ?",
            (session_id,)
        ).fetchone()

        if result is None:
            raise HTTPException(status_code=404, detail="Session not found")
            chords = json.loads(result[0])
            chords.append(request.chord)
            connection.execute(
                """
                UPDATE music_sessions
                SET chord_sequence = ?
                WHERE id = ?
                """,
                (json.dumps(chords), session_id)
            )
            return {
                "selected_chord": request.chord,
                "updated_sequence": chords
            }