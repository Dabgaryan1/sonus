// Stand-in for POST /api/analyze until MIDI-to-chord extraction (SCRUM 41/32/42),
// a saved LSTM checkpoint, and the explanation endpoint exist.
// Assigns one chord per bar from a fixed loop so the UI has realistic data to show.

const LOOP = ["A:min", "F:maj", "C:maj", "G:maj"];

export async function mockAnalyze(midi) {
  await new Promise((r) => setTimeout(r, 1400));

  const progression = Array.from({ length: midi.bars }, (_, bar) => ({
    chord: LOOP[bar % LOOP.length],
    start: midi.beatsToSeconds(bar * midi.beatsPerBar),
    end: midi.beatsToSeconds((bar + 1) * midi.beatsPerBar),
  }));

  return {
    progression,
    key: null,
    suggestions: [
      {
        chord: "A:min",
        probability: 0.46,
        explanation:
          "The progression has been cycling A minor, F, C, G, so returning to A minor restarts the loop. It's also the chord the piece opened on, which makes it feel like home.",
      },
      {
        chord: "E:min",
        probability: 0.21,
        explanation:
          "E minor shares two notes, G and B, with the G major chord before it, so the change sounds smooth and connected.",
      },
      {
        chord: "C:maj",
        probability: 0.14,
        explanation:
          "Moving from G down a fifth to C is one of the strongest root movements in Western harmony, and C major already appears earlier in this progression.",
      },
    ],
  };
}
