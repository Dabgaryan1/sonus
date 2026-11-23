import { describeChord, formatChord } from "../lib/chords";
import "./Suggestions.css";

/**
 * `state.kind` decides what the panel shows:
 * - "empty":   how-it-works steps
 * - "loading": skeleton cards
 * - "error":   { message, onRetry }
 * - "ready":   { suggestions, selected, onSelect }
 */
export function Suggestions({ state }) {
  switch (state.kind) {
    case "loading":
      return (
        <div className="sugg" aria-busy="true">
          <p className="sugg-status">Reading chords and finding what fits next…</p>
          {[0, 1, 2].map((i) => (
            <div key={i} className="sugg-card sugg-skeleton" />
          ))}
        </div>
      );

    case "error":
      return (
        <div className="sugg">
          <div className="sugg-error" role="alert">
            <p>{state.message}</p>
            <button className="btn btn-small" onClick={state.onRetry}>
              Try again
            </button>
          </div>
        </div>
      );

    case "ready":
      return (
        <div className="sugg">
          <div className="sugg-list" role="radiogroup" aria-label="Suggested next chords">
            {state.suggestions.map((s, i) => {
              const selected = i === state.selected;
              const pct = Math.round(s.probability * 100);
              return (
                <button
                  key={s.chord}
                  role="radio"
                  aria-checked={selected}
                  className={`sugg-card${selected ? " is-selected" : ""}`}
                  onClick={() => state.onSelect(i)}
                >
                  <div className="sugg-top">
                    <span className="sugg-rank">{i + 1}</span>
                    <div className="sugg-chord">
                      <span className="sugg-symbol">{formatChord(s.chord)}</span>
                      <span className="sugg-name">{describeChord(s.chord)}</span>
                    </div>
                    <span className="sugg-pct">{pct}%</span>
                  </div>
                  <div className="sugg-bar" aria-hidden="true">
                    <span style={{ width: `${pct}%` }} />
                  </div>
                  <p className="sugg-why">{s.explanation}</p>
                </button>
              );
            })}
          </div>
          <p className="sugg-foot">
            Select a suggestion to preview it on the piano roll. Percentages show how confident Sonus is, not how
            "correct" a chord is in music theory.
          </p>
        </div>
      );

    default:
      return <HowItWorks />;
  }
}

function HowItWorks() {
  const steps = [
    ["Import", "Drop in a MIDI file of a chord progression or a short piece."],
    ["Analyze", "Sonus figures out which chords you played, bar by bar."],
    ["Suggest", "Sonus suggests what could come next, and explains why it fits."],
  ];
  return (
    <div className="sugg">
      <ol className="how">
        {steps.map(([title, body], i) => (
          <li key={title}>
            <span className="how-num">{i + 1}</span>
            <div>
              <p className="how-title">{title}</p>
              <p className="how-body">{body}</p>
            </div>
          </li>
        ))}
      </ol>
    </div>
  );
}
