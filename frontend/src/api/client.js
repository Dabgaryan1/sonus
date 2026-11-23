import { mockAnalyze } from "./mock";

/** Mock mode is on unless VITE_USE_MOCK=false is set (see .env.example). */
export const USE_MOCK = import.meta.env.VITE_USE_MOCK !== "false";

/** Number of previous chords the LSTM uses as context (model/lstm_model.py). */
export const MODEL_CONTEXT_LENGTH = 4;

/**
 * Sends the MIDI file to POST /api/analyze. See README.md for the response shape:
 * { progression: [{ chord, start, end }], suggestions: [{ chord, probability, explanation }], key }
 */
export async function analyzeMidi(file, midi) {
  if (USE_MOCK) return mockAnalyze(midi);

  const body = new FormData();
  body.append("file", file);

  let res;
  try {
    res = await fetch("/api/analyze", { method: "POST", body });
  } catch {
    throw new Error("Couldn't reach the Sonus backend. Is the FastAPI server running?");
  }

  if (!res.ok) {
    let detail = "";
    try {
      const data = await res.json();
      detail = typeof data.detail === "string" ? data.detail : "";
    } catch {
      // Response wasn't JSON; fall through to the generic message.
    }
    throw new Error(detail || `Analysis failed (HTTP ${res.status}).`);
  }

  return res.json();
}
