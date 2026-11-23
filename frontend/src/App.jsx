import { useRef, useState } from "react";
import { analyzeMidi, USE_MOCK } from "./api/client";
import { Dropzone } from "./components/Dropzone";
import { FileCard } from "./components/FileCard";
import { Header } from "./components/Header";
import { PianoRoll } from "./components/PianoRoll";
import { ProgressionStrip } from "./components/ProgressionStrip";
import { StatusBar } from "./components/StatusBar";
import { Suggestions } from "./components/Suggestions";
import { MIDI_EXTENSIONS, parseMidiFile } from "./lib/midi";
import "./App.css";

// phase: "empty" → "reading" → "analyzing" → "done", or "error" at any point.

export default function App() {
  const [phase, setPhase] = useState("empty");
  const [file, setFile] = useState(null);
  const [midi, setMidi] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [error, setError] = useState(null);
  const [selected, setSelected] = useState(0);

  // Ignore results from a request that was superseded by a newer upload or reset.
  const requestId = useRef(0);

  async function runAnalysis(f, parsed, id) {
    setPhase("analyzing");
    setError(null);
    try {
      const result = await analyzeMidi(f, parsed);
      if (id !== requestId.current) return;
      setAnalysis(result);
      setSelected(0);
      setPhase("done");
    } catch (e) {
      if (id !== requestId.current) return;
      setError(e instanceof Error ? e.message : "Something went wrong while analyzing.");
      setPhase("error");
    }
  }

  async function handleFile(f) {
    const id = ++requestId.current;
    setFile(f);
    setMidi(null);
    setAnalysis(null);
    setError(null);

    if (!MIDI_EXTENSIONS.test(f.name)) {
      setError(`"${f.name}" isn't a MIDI file. Choose a .mid or .midi file.`);
      setPhase("error");
      return;
    }

    setPhase("reading");
    try {
      const parsed = await parseMidiFile(f);
      if (id !== requestId.current) return;
      setMidi(parsed);
      await runAnalysis(f, parsed, id);
    } catch (e) {
      if (id !== requestId.current) return;
      setError(e instanceof Error ? e.message : "Couldn't read this file.");
      setPhase("error");
    }
  }

  function reset() {
    requestId.current++;
    setPhase("empty");
    setFile(null);
    setMidi(null);
    setAnalysis(null);
    setError(null);
  }

  const analyzing = phase === "analyzing";
  const suggestion = analysis?.suggestions[selected]?.chord ?? null;
  const step = phase === "empty" ? 0 : phase === "done" ? 2 : midi ? 1 : 0;

  let suggestionsState;
  if (analysis) {
    suggestionsState = { kind: "ready", suggestions: analysis.suggestions, selected, onSelect: setSelected };
  } else if (analyzing) {
    suggestionsState = { kind: "loading" };
  } else if (phase === "error" && midi && file) {
    suggestionsState = {
      kind: "error",
      message: error ?? "Analysis failed.",
      onRetry: () => runAnalysis(file, midi, ++requestId.current),
    };
  } else {
    suggestionsState = { kind: "empty" };
  }

  const status = statusFor(phase, midi, analysis, error);

  return (
    <div className="app">
      <Header step={step} onNewSession={reset} canReset={phase !== "empty"} />

      <main className="workspace">
        <section className="panel panel-input" aria-labelledby="input-title">
          <PanelHead
            title="Your MIDI"
            id="input-title"
            meta={midi ? `${midi.noteCount} notes · ${midi.bars} bars` : "No file"}
          />
          <div className="panel-body">
            {midi ? (
              <>
                <FileCard midi={midi} onReplace={handleFile} onRemove={reset} />
                <PianoRoll
                  midi={midi}
                  progression={analysis?.progression ?? null}
                  suggestion={suggestion}
                  analyzing={analyzing}
                />
                <ProgressionStrip
                  progression={analysis?.progression ?? null}
                  suggestion={suggestion}
                  analyzing={analyzing}
                  keyName={analysis?.key}
                />
              </>
            ) : (
              <Dropzone onFile={handleFile} busy={phase === "reading"} error={phase === "error" ? error : null} />
            )}
          </div>
        </section>

        <section className="panel panel-suggest" aria-labelledby="suggest-title">
          <PanelHead
            title={analysis ? "What could come next" : "How it works"}
            id="suggest-title"
            meta={analysis ? `${analysis.suggestions.length} suggestions` : ""}
          />
          <div className="panel-body">
            <Suggestions state={suggestionsState} />
          </div>
        </section>
      </main>

      <StatusBar message={status.message} tone={status.tone} mock={USE_MOCK} />
    </div>
  );
}

function PanelHead({ title, meta, id }) {
  return (
    <div className="panel-head">
      <h2 id={id}>{title}</h2>
      {meta && <span className="panel-meta">{meta}</span>}
    </div>
  );
}

function statusFor(phase, midi, analysis, error) {
  switch (phase) {
    case "reading":
      return { message: "Reading MIDI…", tone: "busy" };
    case "analyzing":
      return { message: "Detecting chords and generating suggestions…", tone: "busy" };
    case "done":
      return {
        message: `${analysis.progression.length} chords detected · ${analysis.suggestions.length} suggestions ready`,
        tone: "ok",
      };
    case "error":
      return { message: midi ? "Analysis failed" : (error ?? "Couldn't read file"), tone: "error" };
    default:
      return { message: "Waiting for a MIDI file", tone: "idle" };
  }
}
