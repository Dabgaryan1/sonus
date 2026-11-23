import "./Header.css";

const STEPS = ["Import", "Analyze", "Suggest"];

/** `step` is the active step: 0 Import, 1 Analyze, 2 Suggest. */
export function Header({ step, onNewSession, canReset }) {
  return (
    <header className="header">
      <button className="brand" onClick={onNewSession} aria-label="Sonus home">
        <span className="brand-mark" aria-hidden="true">
          <svg viewBox="0 0 24 24" width="22" height="22">
            <rect x="3" y="8" width="3" height="8" />
            <rect x="8" y="4" width="3" height="16" />
            <rect x="13" y="7" width="3" height="10" />
            <rect x="18" y="10" width="3" height="4" />
          </svg>
        </span>
        <span className="brand-text">
          <span className="brand-name">Sonus</span>
        </span>
      </button>

      <ol className="steps" aria-label="Progress">
        {STEPS.map((label, i) => {
          const state = i < step ? "done" : i === step ? "active" : "todo";
          return (
            <li key={label} className={`step is-${state}`} aria-current={i === step ? "step" : undefined}>
              <span className="step-num">{i < step ? "✓" : i + 1}</span>
              {label}
            </li>
          );
        })}
      </ol>

      <button className="btn btn-ghost" onClick={onNewSession} disabled={!canReset}>
        + New session
      </button>
    </header>
  );
}
