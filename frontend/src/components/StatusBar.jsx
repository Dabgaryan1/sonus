import "./StatusBar.css";

/** `tone` is one of "idle", "busy", "ok", "error". */
export function StatusBar({ message, tone }) {
  return (
    <footer className="status">
      <p className={`status-msg tone-${tone}`} role="status">
        <i aria-hidden="true" />
        {message}
      </p>
    </footer>
  );
}
