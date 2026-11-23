import { MODEL_CONTEXT_LENGTH } from "../api/client";
import { formatChord } from "../lib/chords";
import "./ProgressionStrip.css";

const MAX_VISIBLE = 12;

export function ProgressionStrip({ progression, suggestion, analyzing, keyName }) {
  if (analyzing) {
    return (
      <section className="prog" aria-busy="true">
        <div className="prog-head">
          <span className="label">Detected progression</span>
        </div>
        <ol className="prog-list">
          {Array.from({ length: 5 }, (_, i) => (
            <li key={i} className="chip chip-skeleton" />
          ))}
        </ol>
      </section>
    );
  }

  if (!progression?.length) return null;

  const hidden = Math.max(0, progression.length - MAX_VISIBLE);
  const visible = progression.slice(hidden);
  const contextStart = Math.max(0, progression.length - MODEL_CONTEXT_LENGTH);

  return (
    <section className="prog">
      <div className="prog-head">
        <span className="label">Detected progression</span>
        {keyName && <span className="label">Key · {keyName}</span>}
      </div>

      <ol className="prog-list">
        {hidden > 0 && <li className="chip chip-more">+{hidden} earlier</li>}
        {visible.map((seg, i) => (
          <li key={hidden + i} className={`chip${hidden + i >= contextStart ? " is-context" : ""}`}>
            {formatChord(seg.chord)}
          </li>
        ))}
        <li className={`chip chip-next${suggestion ? " is-filled" : ""}`} aria-label="Next chord">
          {suggestion ? formatChord(suggestion) : "?"}
        </li>
      </ol>

      <p className="prog-note">
        <i className="ctx-swatch" aria-hidden="true" />
        Outlined chords are the last {MODEL_CONTEXT_LENGTH} the model uses to predict what comes next.
      </p>
    </section>
  );
}
