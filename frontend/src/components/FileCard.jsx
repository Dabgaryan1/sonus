import { useRef } from "react";
import { formatBytes, formatDuration } from "../lib/midi";
import "./FileCard.css";

export function FileCard({ midi, onReplace, onRemove }) {
  const inputRef = useRef(null);

  const stats = [
    { label: "Tempo", value: `${Math.round(midi.bpm)} BPM` },
    { label: "Time sig", value: `${midi.timeSignature[0]}/${midi.timeSignature[1]}` },
    { label: "Length", value: `${midi.bars} ${midi.bars === 1 ? "bar" : "bars"}` },
    { label: "Duration", value: formatDuration(midi.durationSec) },
  ];

  return (
    <div className="filecard">
      <div className="filecard-top">
        <span className="filecard-icon" aria-hidden="true">
          <svg viewBox="0 0 24 24" width="18" height="18">
            <path d="M9 18V5l12-2v13M9 18a3 3 0 1 1-6 0 3 3 0 0 1 6 0Zm12-2a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
          </svg>
        </span>
        <div className="filecard-name">
          <p className="filecard-title" title={midi.fileName}>
            {midi.fileName}
          </p>
          <p className="filecard-meta">
            {formatBytes(midi.sizeBytes)} · {midi.trackCount} {midi.trackCount === 1 ? "track" : "tracks"} ·{" "}
            {midi.noteCount} notes
            {midi.drumTracksIgnored > 0 && ` · ${midi.drumTracksIgnored} drum track ignored`}
          </p>
        </div>
        <div className="filecard-actions">
          <button className="btn btn-small" onClick={() => inputRef.current?.click()}>
            Replace
          </button>
          <button className="icon-btn" onClick={onRemove} aria-label="Remove file">
            ×
          </button>
        </div>
      </div>

      <dl className="filecard-stats">
        {stats.map((s) => (
          <div key={s.label}>
            <dt>{s.label}</dt>
            <dd>{s.value}</dd>
          </div>
        ))}
      </dl>

      <input
        ref={inputRef}
        type="file"
        accept=".mid,.midi,audio/midi,audio/x-midi"
        hidden
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) onReplace(file);
          e.target.value = "";
        }}
      />
    </div>
  );
}
