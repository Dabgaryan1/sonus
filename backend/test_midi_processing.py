import sys
import tempfile
from pathlib import Path
import pretty_midi

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1] / "model")
)

from chord_encoder import encode_chord
from chord_vocab import load_vocab

from backend.midi_processing import (
    extract_midi_notes,
    group_notes_by_time,
    identify_chord,
    extract_chord_progression
)

def test_extract_midi_notes():
    # Create a MIDI file containing a C major chord.
    midi = pretty_midi.PrettyMIDI()
    piano = pretty_midi.Instrument(program=0)

    for pitch in [60, 64, 67]:
        piano.notes.append(
            pretty_midi.Note(
                velocity=100,
                pitch=pitch,
                start=0.0,
                end=2.0
            )
        )

    midi.instruments.append(piano)

    # Save to a temporary MIDI file.
    with tempfile.TemporaryDirectory() as temp_dir:
        midi_path = Path(temp_dir) / "test_chord.mid"
        midi.write(str(midi_path))

        # Run Erendira's updated extraction function.
        notes = extract_midi_notes(midi_path)

        assert len(notes) == 3

        assert [note["pitch"] for note in notes] == [
            60, 64, 67
        ]

        for note in notes:
            assert note["start"] == 0.0
            assert abs(note["end"] - 2.0) < 0.01
            assert note["instrument"] == 0

        print("MIDI note extraction OK")
        print("Extracted notes:", notes)
    

def test_group_notes_by_time():
    # C major (C, E, G) followed by A minor (A, C, E)
    notes = [
        {"pitch": 60, "start": 0.0, "end": 2.0, "instrument": 0},
        {"pitch": 64, "start": 0.0, "end": 2.0, "instrument": 0},
        {"pitch": 67, "start": 0.0, "end": 2.0, "instrument": 0},
        {"pitch": 69, "start": 2.0, "end": 4.0, "instrument": 0},
        {"pitch": 72, "start": 2.0, "end": 4.0, "instrument": 0},
        {"pitch": 76, "start": 2.0, "end": 4.0, "instrument": 0},
    ]

    groups = group_notes_by_time(notes)

    assert len(groups) == 2

    assert groups[0]["pitches"] == [60, 64, 67]
    assert groups[0]["start"] == 0.0
    assert groups[0]["end"] == 2.0

    assert groups[1]["pitches"] == [69, 72, 76]
    assert groups[1]["start"] == 2.0
    assert groups[1]["end"] == 4.0

    print("MIDI note grouping OK")


def test_identify_chord():
    # Major chords
    assert identify_chord([60, 64, 67]) == "C"
    assert identify_chord([65, 69, 72]) == "F"
    assert identify_chord([67, 71, 74]) == "G"

    # Minor chords
    assert identify_chord([69, 72, 76]) == "Amin"
    assert identify_chord([62, 65, 69]) == "Dmin"

    # Chord inversions
    assert identify_chord([64, 67, 72]) == "C"
    assert identify_chord([72, 76, 81]) == "Amin"

    # Duplicate notes across octaves
    assert identify_chord([60, 64, 67, 72]) == "C"

    # Unsupported or incomplete chords
    assert identify_chord([]) is None
    assert identify_chord([60, 67]) is None
    assert identify_chord([60, 62, 64, 67]) is None

    print("MIDI chord identification OK")

def test_extract_chord_progression():
    # Create a MIDI file containing four consecutive chords.
    midi = pretty_midi.PrettyMIDI()
    piano = pretty_midi.Instrument(program=0)

    chord_data = [
        ([60, 64, 67], 0.0, 2.0),  # C major
        ([69, 72, 76], 2.0, 4.0),  # A minor
        ([65, 69, 72], 4.0, 6.0),  # F major
        ([67, 71, 74], 6.0, 8.0),  # G major
    ]

    for pitches, start, end in chord_data:
        for pitch in pitches:
            piano.notes.append(
                pretty_midi.Note(
                    velocity=100,
                    pitch=pitch,
                    start=start,
                    end=end
                )
            )

    midi.instruments.append(piano)

    with tempfile.TemporaryDirectory() as temp_dir:
        midi_path = Path(temp_dir) / "test_progression.mid"
        midi.write(str(midi_path))

        progression = extract_chord_progression(midi_path)

        assert len(progression) == 4
        assert [item["chord"] for item in progression] == [
            "C", "Amin", "F", "G"
        ]
        # Verify compatibility with Hanna's chord encoder.
        chord_to_id, id_to_chord = load_vocab()

        encoded = [
            encode_chord(item["chord"], chord_to_id)
            for item in progression
        ]

        assert encoded == [3, 103, 58, 80]

        decoded = [
            id_to_chord[chord_id]
            for chord_id in encoded
        ]

        assert decoded == [
            "C:maj", "A:min", "F:maj", "G:maj"
        ]

        print("MIDI to chord encoder integration OK")

        for item, (_, start, end) in zip(progression, chord_data):
            assert abs(item["start"] - start) < 0.01
            assert abs(item["end"] - end) < 0.01

        print("MIDI chord progression extraction OK")
        print("Extracted progression:", progression)
        
def test_note_timing_tolerance():
    # Notes starting within 50 ms should form one group.
    notes = [
        {"pitch": 60, "start": 0.00, "end": 2.0, "instrument": 0},
        {"pitch": 64, "start": 0.02, "end": 2.0, "instrument": 0},
        {"pitch": 67, "start": 0.04, "end": 2.0, "instrument": 0},
        {"pitch": 69, "start": 2.00, "end": 4.0, "instrument": 0},
        {"pitch": 72, "start": 2.02, "end": 4.0, "instrument": 0},
        {"pitch": 76, "start": 2.04, "end": 4.0, "instrument": 0},
    ]

    groups = group_notes_by_time(notes, tolerance=0.05)

    assert len(groups) == 2
    assert groups[0]["pitches"] == [60, 64, 67]
    assert groups[1]["pitches"] == [69, 72, 76]

    assert identify_chord(groups[0]["pitches"]) == "C"
    assert identify_chord(groups[1]["pitches"]) == "Amin"

    print("MIDI timing tolerance OK")

def test_empty_midi_and_drums():
    with tempfile.TemporaryDirectory() as temp_dir:
        # Test an empty MIDI file.
        empty_midi = pretty_midi.PrettyMIDI()
        empty_path = Path(temp_dir) / "empty.mid"
        empty_midi.write(str(empty_path))

        assert extract_midi_notes(empty_path) == []
        assert extract_chord_progression(empty_path) == []

        # Test a MIDI file containing only drums.
        drum_midi = pretty_midi.PrettyMIDI()
        drums = pretty_midi.Instrument(program=0, is_drum=True)

        for pitch in [36, 38, 42]:
            drums.notes.append(
                pretty_midi.Note(
                    velocity=100,
                    pitch=pitch,
                    start=0.0,
                    end=1.0
                )
            )

        drum_midi.instruments.append(drums)
        drum_path = Path(temp_dir) / "drums.mid"
        drum_midi.write(str(drum_path))

        assert extract_midi_notes(drum_path) == []
        assert extract_chord_progression(drum_path) == []

        print("Empty MIDI and drum-track handling OK")

if __name__ == "__main__":
    test_extract_midi_notes()
    test_group_notes_by_time()
    test_identify_chord()
    test_extract_chord_progression()
    test_note_timing_tolerance()
    test_empty_midi_and_drums()