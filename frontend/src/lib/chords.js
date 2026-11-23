// Helpers for the chord vocabulary in model/chord_vocab.py ("ROOT:quality").

const QUALITY_SYMBOL = {
  maj: "",
  min: "m",
  dim: "dim",
  aug: "aug",
  sus2: "sus2",
  sus4: "sus4",
  "7": "7",
  maj7: "maj7",
  min7: "m7",
  min7b5: "m7♭5",
  dim7: "dim7",
};

const QUALITY_NAME = {
  maj: "major",
  min: "minor",
  dim: "diminished",
  aug: "augmented",
  sus2: "suspended 2nd",
  sus4: "suspended 4th",
  "7": "dominant 7th",
  maj7: "major 7th",
  min7: "minor 7th",
  min7b5: "half-diminished 7th",
  dim7: "diminished 7th",
};

const QUALITY_INTERVALS = {
  maj: [0, 4, 7],
  min: [0, 3, 7],
  dim: [0, 3, 6],
  aug: [0, 4, 8],
  sus2: [0, 2, 7],
  sus4: [0, 5, 7],
  "7": [0, 4, 7, 10],
  maj7: [0, 4, 7, 11],
  min7: [0, 3, 7, 10],
  min7b5: [0, 3, 6, 10],
  dim7: [0, 3, 6, 9],
};

const ROOTS = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"];

/** "A:min" → { root: "A", quality: "min" }, or null for special tokens like "<UNK>". */
export function splitChord(chord) {
  const [root, quality] = chord.split(":");
  if (!ROOTS.includes(root) || !(quality in QUALITY_INTERVALS)) return null;
  return { root, quality };
}

function prettyRoot(root) {
  return root.replace("#", "♯");
}

/** "A:min" → "Am", "F#:maj7" → "F♯maj7". Special tokens pass through unchanged. */
export function formatChord(chord) {
  const parts = splitChord(chord);
  if (!parts) return chord;
  return prettyRoot(parts.root) + QUALITY_SYMBOL[parts.quality];
}

/** "A:min" → "A minor". */
export function describeChord(chord) {
  const parts = splitChord(chord);
  if (!parts) return chord;
  return `${prettyRoot(parts.root)} ${QUALITY_NAME[parts.quality]}`;
}

/** MIDI pitches for a chord, voiced close to `center`. */
export function chordPitches(chord, center = 60) {
  const parts = splitChord(chord);
  if (!parts) return [];
  const pc = ROOTS.indexOf(parts.root);
  const intervals = QUALITY_INTERVALS[parts.quality];
  const mid = intervals[intervals.length - 1] / 2;
  const base = Math.round((center - mid - pc) / 12) * 12 + pc;
  return intervals.map((i) => base + i);
}

/** 60 → "C4". */
export function pitchName(pitch) {
  return `${ROOTS[pitch % 12]}${Math.floor(pitch / 12) - 1}`;
}
