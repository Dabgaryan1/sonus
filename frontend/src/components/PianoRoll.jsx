import { useEffect, useMemo, useRef, useState } from "react";
import { chordPitches, formatChord, pitchName } from "../lib/chords";
import "./PianoRoll.css";

const RULER_H = 20;
const LANE_H = 26;
const HEADER_H = RULER_H + LANE_H;
const KEYS_W = 46;
const MIN_PX_PER_BEAT = 18;
const TARGET_ROLL_H = 300;
const BLACK_KEYS = new Set([1, 3, 6, 8, 10]);

/**
 * Piano roll of the uploaded MIDI, with a chord lane on top.
 * `suggestion` (e.g. "F:maj") is previewed as dashed notes for one bar after the input ends.
 */
export function PianoRoll({ midi, progression, suggestion, analyzing }) {
  const scrollRef = useRef(null);
  const [viewWidth, setViewWidth] = useState(640);

  useEffect(() => {
    const el = scrollRef.current;
    if (!el) return;
    const ro = new ResizeObserver(([entry]) => setViewWidth(entry.contentRect.width));
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  const layout = useMemo(() => {
    const { beatsPerBar, endBeat, notes } = midi;

    // The suggested chord is previewed for one bar, starting on the next beat after the input.
    const ghostStart = Math.ceil(endBeat - 1e-6);
    const ghostEnd = ghostStart + beatsPerBar;
    const totalBeats = Math.ceil(ghostEnd / beatsPerBar - 1e-6) * beatsPerBar;
    const pxPerBeat = Math.max(MIN_PX_PER_BEAT, viewWidth / totalBeats);

    // Voice the preview chord near the register of the last bar of input.
    const tail = notes.filter((n) => n.start + n.duration > endBeat - beatsPerBar);
    const source = tail.length ? tail : notes;
    const center = source.reduce((sum, n) => sum + n.pitch, 0) / source.length;
    const ghostPitches = suggestion ? chordPitches(suggestion, Math.round(center)) : [];

    let lo = 127;
    let hi = 0;
    for (const p of [...notes.map((n) => n.pitch), ...ghostPitches]) {
      lo = Math.min(lo, p);
      hi = Math.max(hi, p);
    }
    lo -= 2;
    hi += 2;
    const minSpan = 24;
    if (hi - lo < minSpan) {
      const pad = Math.ceil((minSpan - (hi - lo)) / 2);
      lo -= pad;
      hi += pad;
    }
    lo = Math.max(0, lo);
    hi = Math.min(127, hi);

    const rows = hi - lo + 1;
    const rowH = Math.max(6, Math.min(14, Math.round(TARGET_ROLL_H / rows)));

    const segments = (progression ?? []).map((seg) => ({
      label: formatChord(seg.chord),
      start: midi.secondsToBeats(seg.start),
      end: midi.secondsToBeats(seg.end),
    }));

    return {
      ghostStart,
      ghostEnd,
      totalBeats,
      pxPerBeat,
      ghostPitches,
      lo,
      hi,
      rows,
      rowH,
      width: totalBeats * pxPerBeat,
      height: HEADER_H + rows * rowH,
      segments,
    };
  }, [midi, progression, suggestion, viewWidth]);

  // Keep the preview area in view when the roll is wider than the panel.
  useEffect(() => {
    const el = scrollRef.current;
    if (el && suggestion) el.scrollLeft = el.scrollWidth;
  }, [suggestion]);

  const { lo, hi, rows, rowH, pxPerBeat: ppb, width, height, totalBeats, ghostStart, ghostEnd } = layout;
  const y = (pitch) => HEADER_H + (hi - pitch) * rowH;
  const pitchesDesc = Array.from({ length: rows }, (_, i) => hi - i);
  const bars = Math.round(totalBeats / midi.beatsPerBar);
  const inputEndX = midi.endBeat * ppb;

  return (
    <figure className="roll" aria-label="Piano roll of the uploaded MIDI">
      <div className="roll-body">
        <svg className="roll-keys" width={KEYS_W} height={height} aria-hidden="true">
          <text className="roll-lane-title" x={6} y={RULER_H + LANE_H / 2 + 4}>
            Chords
          </text>
          {pitchesDesc.map((p) => {
            const black = BLACK_KEYS.has(p % 12);
            return (
              <g key={p}>
                <rect
                  className={black ? "key-black" : "key-white"}
                  x={0}
                  y={y(p)}
                  width={black ? KEYS_W * 0.62 : KEYS_W}
                  height={rowH - 0.5}
                />
                {p % 12 === 0 && rowH >= 8 && (
                  <text className="key-label" x={KEYS_W - 4} y={y(p) + rowH - 2} textAnchor="end">
                    {pitchName(p)}
                  </text>
                )}
              </g>
            );
          })}
        </svg>

        <div className="roll-scroll" ref={scrollRef}>
          <svg width={width} height={height} role="img" aria-label={`${midi.noteCount} notes across ${midi.bars} bars`}>
            <defs>
              <pattern id="roll-hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
                <line x1="0" y1="0" x2="0" y2="6" className="hatch-line" />
              </pattern>
            </defs>

            {/* Row backgrounds */}
            {pitchesDesc.map((p) => (
              <rect
                key={p}
                className={BLACK_KEYS.has(p % 12) ? "row-black" : "row-white"}
                x={0}
                y={y(p)}
                width={width}
                height={rowH}
              />
            ))}

            {/* Region after the input ends */}
            <rect x={inputEndX} y={HEADER_H} width={width - inputEndX} height={rows * rowH} fill="url(#roll-hatch)" />

            {/* Beat and bar lines */}
            {Array.from({ length: totalBeats + 1 }, (_, b) => {
              const isBar = b % midi.beatsPerBar === 0;
              if (!isBar && ppb < 14) return null;
              return (
                <line
                  key={b}
                  className={isBar ? "grid-bar" : "grid-beat"}
                  x1={b * ppb}
                  x2={b * ppb}
                  y1={isBar ? 0 : HEADER_H}
                  y2={height}
                />
              );
            })}

            {/* Ruler */}
            <line className="grid-bar" x1={0} x2={width} y1={RULER_H} y2={RULER_H} />
            <line className="grid-bar" x1={0} x2={width} y1={HEADER_H} y2={HEADER_H} />
            {Array.from({ length: bars }, (_, i) => (
              <text key={i} className="ruler-label" x={i * midi.beatsPerBar * ppb + 5} y={14}>
                {i + 1}
              </text>
            ))}

            {/* Chord lane */}
            {analyzing && (
              <g className="lane-loading">
                <rect x={2} y={RULER_H + 4} width={Math.max(0, inputEndX - 4)} height={LANE_H - 8} rx={2} />
                <text x={10} y={RULER_H + LANE_H / 2 + 4}>
                  Detecting chords…
                </text>
              </g>
            )}
            {layout.segments.map((seg, i) => {
              const x = seg.start * ppb + 2;
              const w = (seg.end - seg.start) * ppb - 4;
              if (w <= 0) return null;
              return (
                <g key={i}>
                  <rect className="lane-chord" x={x} y={RULER_H + 4} width={w} height={LANE_H - 8} rx={2} />
                  {w > 22 && (
                    <text className="lane-chord-label" x={x + 6} y={RULER_H + LANE_H / 2 + 4}>
                      {seg.label}
                    </text>
                  )}
                </g>
              );
            })}
            {suggestion && (
              <g>
                <rect
                  className="lane-ghost"
                  x={ghostStart * ppb + 2}
                  y={RULER_H + 4}
                  width={(ghostEnd - ghostStart) * ppb - 4}
                  height={LANE_H - 8}
                  rx={2}
                />
                <text className="lane-ghost-label" x={ghostStart * ppb + 8} y={RULER_H + LANE_H / 2 + 4}>
                  {formatChord(suggestion)}?
                </text>
              </g>
            )}

            {/* Notes */}
            {midi.notes.map((n, i) =>
              n.pitch < lo || n.pitch > hi ? null : (
                <rect
                  key={i}
                  className="note"
                  x={n.start * ppb + 0.5}
                  y={y(n.pitch) + 0.5}
                  width={Math.max(2, n.duration * ppb - 1)}
                  height={rowH - 1}
                  opacity={0.55 + 0.45 * n.velocity}
                />
              ),
            )}

            {/* Suggested chord preview */}
            {layout.ghostPitches.map((p) => (
              <rect
                key={p}
                className="note-ghost"
                x={ghostStart * ppb + 1}
                y={y(p) + 1}
                width={(ghostEnd - ghostStart) * ppb - 3}
                height={rowH - 2}
              />
            ))}

            {/* Input end marker */}
            <line className="end-marker" x1={inputEndX} x2={inputEndX} y1={0} y2={height} />
            {width - inputEndX > 90 && (
              <text className="end-label" x={inputEndX + 6} y={14}>
                End of input
              </text>
            )}
          </svg>
        </div>
      </div>

      <figcaption className="roll-legend">
        <span>
          <i className="swatch swatch-note" /> Your notes
        </span>
        <span>
          <i className="swatch swatch-ghost" /> Suggested chord (preview)
        </span>
      </figcaption>
    </figure>
  );
}
