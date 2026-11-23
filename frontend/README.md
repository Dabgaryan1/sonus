# Sonus Frontend

React + Vite (JavaScript) UI for Sonus. Upload a MIDI file, see the detected chord progression on a piano roll, and get three suggested next chords with explanations.

## Setup

Requires [Node.js](https://nodejs.org/) 18 or newer.

```bash
cd frontend
npm install
npm run dev
```

Open the URL Vite prints (usually `http://localhost:5173`). Use **Try a sample progression** on the upload screen if you don't have a MIDI file handy.

## Mock mode vs. the real backend

The backend endpoint doesn't exist yet, so the UI uses **mock data by default** (see [src/api/mock.js](src/api/mock.js)). A "Mock data" badge appears in the status bar while it's on.

To use the FastAPI backend instead:

1. Copy `.env.example` to `.env` and set `VITE_USE_MOCK=false`.
2. Start the backend from the repo root: `fastapi dev backend/main.py`.
3. Run `npm run dev`. Vite forwards `/api/*` requests to `http://127.0.0.1:8000`.

## API contract

The frontend expects one endpoint:

**`POST /api/analyze`**: multipart form upload with the MIDI file in a field named `file`.

```json
{
  "progression": [
    { "chord": "A:min", "start": 0.0, "end": 2.4 },
    { "chord": "F:maj", "start": 2.4, "end": 4.8 }
  ],
  "suggestions": [
    { "chord": "A:min", "probability": 0.46, "explanation": "..." },
    { "chord": "E:min", "probability": 0.21, "explanation": "..." },
    { "chord": "C:maj", "probability": 0.14, "explanation": "..." }
  ],
  "key": null
}
```

- `chord` uses the shared vocabulary format from `model/chord_vocab.py` (`ROOT:quality`).
- `start` and `end` are in seconds from the start of the file.
- `probability` is the LSTM's softmax output for that chord.
- `explanation` is one per suggestion. (The current prototype in `backend/explanations.py` returns a single block of text for all three, so it will need to be split.)
- `key` is optional and can be `null` until key detection exists.
- On failure, return an HTTP error with a JSON `detail` string. The UI shows it to the user.

The mock response in [src/api/mock.js](src/api/mock.js) follows this shape.

## Structure

```text
src/
├── App.jsx               # Page layout and upload → analyze → suggest flow
├── api/
│   ├── client.js         # analyzeMidi(): calls the backend or the mock
│   └── mock.js           # Fake analysis used until the backend is ready
├── lib/
│   ├── chords.js         # Chord formatting ("A:min" → "Am") and chord tones
│   └── midi.js           # Reads MIDI in the browser for the piano roll
├── components/           # Header, Dropzone, FileCard, PianoRoll, ProgressionStrip, Suggestions, StatusBar
└── styles/global.css     # Color and font tokens, buttons
```
