import { useRef, useState } from "react";
import "./Dropzone.css";

const SAMPLE_URL = "/samples/am-f-c-g.mid";

export function Dropzone({ onFile, busy, error }) {
  const [over, setOver] = useState(false);
  const inputRef = useRef(null);

  function pick(files) {
    const file = files?.[0];
    if (file) onFile(file);
  }

  async function loadSample() {
    const res = await fetch(SAMPLE_URL);
    if (!res.ok) {
      onFile(new File([], "am-f-c-g.mid", { type: "audio/midi" }));
      return;
    }
    const blob = await res.blob();
    onFile(new File([blob], "am-f-c-g.mid", { type: "audio/midi" }));
  }

  return (
    <div
      className={`dropzone${over ? " is-over" : ""}${busy ? " is-busy" : ""}`}
      onDragOver={(e) => {
        e.preventDefault();
        setOver(true);
      }}
      onDragLeave={() => setOver(false)}
      onDrop={(e) => {
        e.preventDefault();
        setOver(false);
        if (!busy) pick(e.dataTransfer.files);
      }}
    >
      <span className="dropzone-icon-wrap" aria-hidden="true">
        <svg className="dropzone-icon" viewBox="0 0 24 24" width="24" height="24">
          <path d="M12 16V4m0 0-5 5m5-5 5 5M4 16v3a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-3" />
        </svg>
      </span>

      {busy ? (
        <p className="dropzone-title">Reading MIDI…</p>
      ) : (
        <>
          <p className="dropzone-title">Drop a MIDI file here</p>
          <p className="dropzone-hint">Sonus reads the chords in your .mid or .midi file and suggests what could come next.</p>
          <button className="btn btn-primary" onClick={() => inputRef.current?.click()}>
            Browse files
          </button>
          <button className="link-btn" onClick={loadSample}>
            No file handy? Try a sample progression
          </button>
        </>
      )}

      {error && (
        <p className="dropzone-error" role="alert">
          {error}
        </p>
      )}

      <input
        ref={inputRef}
        type="file"
        accept=".mid,.midi,audio/midi,audio/x-midi"
        hidden
        onChange={(e) => {
          pick(e.target.files);
          e.target.value = "";
        }}
      />
    </div>
  );
}
