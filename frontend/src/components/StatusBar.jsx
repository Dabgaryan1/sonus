import "./StatusBar.css";

/** `tone` is one of "idle", "busy", "ok", "error". */
export function StatusBar({ message, tone, mock }) {
  return (
    <footer className="status">
      <p className={`status-msg tone-${tone}`} role="status">
        <i aria-hidden="true" />
        {message}
      </p>
      {mock && (
        <span className="status-badge" title="Set VITE_USE_MOCK=false to use the FastAPI backend">
          Mock data
        </span>
      )}
    </footer>
  );
}
