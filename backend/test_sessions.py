
import os
import sqlite3
import tempfile
import json

from fastapi.testclient import TestClient


def test_session_endpoints():
    # Use a temporary database so existing data is untouched.
    with tempfile.TemporaryDirectory() as temp_dir:
        os.environ["SONUS_DB_PATH"] = os.path.join(
            temp_dir, "test_sessions.db"
        )

        from backend.main import app, initialize_database

        initialize_database()

        with TestClient(app) as client:

            # Create a session
            response = client.post("/sessions")
            assert response.status_code == 200
            session_id = response.json()["session_id"]
            assert response.json()["chord_sequence"] == []

            # Save a progression
            chords = ["C:maj", "A:min", "F:maj"]
            response = client.post(
                f"/sessions/{session_id}/chords",
                json=chords
            )
            assert response.status_code == 200
            assert response.json()["chord_sequence"] == chords

            # Select a recommended chord
            response = client.post(
                f"/sessions/{session_id}/choose",
                json={"chord": "G:maj"}
            )
            assert response.status_code == 200
            assert response.json()["updated_sequence"] == [
                "C:maj", "A:min", "F:maj", "G:maj"
            ]

            # Missing sessions should return 404
            response = client.post(
                "/sessions/999999/chords",
                json=["C:maj"]
            )
            assert response.status_code == 404

            response = client.post(
                "/sessions/999999/choose",
                json={"chord": "G:maj"}
            )
            assert response.status_code == 404

        # Verify the progression was saved in SQLite.
        conn = sqlite3.connect(os.environ["SONUS_DB_PATH"])
        try:
            saved = conn.execute(
                "SELECT chord_sequence FROM music_sessions WHERE id = ?",
                (session_id,)
            ).fetchone()
        finally:
            conn.close()

        assert saved is not None
        assert json.loads(saved[0]) == [
            "C:maj", "A:min", "F:maj", "G:maj"
        ]

        print("session endpoint tests OK")


if __name__ == "__main__":
    test_session_endpoints()
