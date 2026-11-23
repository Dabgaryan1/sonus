import { Midi } from "@tonejs/midi";

export const MIDI_EXTENSIONS = /\.midi?$/i;

/**
 * Reads a MIDI file in the browser for display (piano roll and file details).
 * Chord detection happens in the backend, not here.
 *
 * Note positions are in quarter-note beats. Drum tracks are left out.
 */
export async function parseMidiFile(file) {
  const buffer = await file.arrayBuffer();

  let midi;
  try {
    midi = new Midi(buffer);
  } catch {
    throw new Error("This file couldn't be read as MIDI. Try exporting it again from your DAW.");
  }

  const { ppq } = midi.header;
  const ts = midi.header.timeSignatures[0]?.timeSignature;
  const timeSignature = ts && ts.length >= 2 ? [ts[0], ts[1]] : [4, 4];
  const bpm = midi.header.tempos[0]?.bpm ?? 120;
  const beatsPerBar = (timeSignature[0] * 4) / timeSignature[1];

  const withNotes = midi.tracks.filter((t) => t.notes.length > 0);
  const pitched = withNotes.filter((t) => !t.instrument.percussion);

  const notes = pitched.flatMap((track) =>
    track.notes.map((n) => ({
      pitch: n.midi,
      start: n.ticks / ppq,
      duration: n.durationTicks / ppq,
      velocity: n.velocity,
    })),
  );

  if (notes.length === 0) {
    throw new Error("No pitched notes found in this file. Drum tracks are ignored.");
  }

  const endBeat = notes.reduce((max, n) => Math.max(max, n.start + n.duration), 0);

  return {
    fileName: file.name,
    sizeBytes: file.size,
    trackCount: pitched.length,
    noteCount: notes.length,
    drumTracksIgnored: withNotes.length - pitched.length,
    bpm,
    timeSignature,
    beatsPerBar,
    bars: Math.max(1, Math.ceil(endBeat / beatsPerBar - 1e-6)),
    durationSec: midi.header.ticksToSeconds(endBeat * ppq),
    notes,
    /** Beat where the last note ends. */
    endBeat,
    secondsToBeats: (s) => midi.header.secondsToTicks(s) / ppq,
    beatsToSeconds: (b) => midi.header.ticksToSeconds(b * ppq),
  };
}

export function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  return `${(bytes / 1024).toFixed(1)} KB`;
}

export function formatDuration(seconds) {
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${s.toString().padStart(2, "0")}`;
}
