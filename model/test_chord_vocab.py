import csv
from pathlib import Path

from chord_vocab import load_vocab
from chord_parser import parse_chord
from chord_encoder import encode_chord, decode_chord, encode_progression, decode_predictions

DATASET_PATH = Path(__file__).parent.parent / "data" / "chordonomicon_v2.csv"
CHORD_COLUMN = "chords"


def test_round_trip():
    chord_to_id, id_to_chord = load_vocab()
    for chord_id, chord in id_to_chord.items():
        assert chord_to_id[chord] == chord_id, f"round-trip failed for id {chord_id} ({chord})"
    print(f"round-trip OK for {len(id_to_chord)} tokens")


def test_uniqueness():
    chord_to_id, id_to_chord = load_vocab()
    assert len(chord_to_id) == len(set(chord_to_id.values())), "two chords share an id"
    assert len(id_to_chord) == len(set(id_to_chord.values())), "two ids share a chord name"
    print("uniqueness OK")


def test_parser_cases():
    cases = [
        ("C", "C:maj"),            # bare letter = major
        ("Amin", "A:min"),         # plain minor
        ("E7", "E:7"),             # dominant 7th
        ("Fsmin", "F#:min"),       # sharp root (s) + quality
        ("Csus4", "C:sus4"),       # ambiguity: "Cs" must NOT be read as C#
        ("Cadd9", "C:maj"),        # extended chord collapsed via Section 3 table
        ("C5", "<DROP>"),          # power chord, no definable triad quality
        ("N", "<NC>"),             # no chord
        ("<verse_1>", "<TAG>"),    # song-structure tag, not a chord
        ("D/Fs", "D:maj"),         # bass note dropped
        ("garbage", None),         # unrecognized
    ]
    for raw, expected in cases:
        result = parse_chord(raw)
        assert result == expected, f"parse_chord({raw!r}) = {result!r}, expected {expected!r}"
    print(f"parser cases OK ({len(cases)} cases)")


def test_encode_decode_round_trip():
    chord_to_id, id_to_chord = load_vocab()
    assert encode_chord("C", chord_to_id) == chord_to_id["C:maj"]
    assert encode_chord("N", chord_to_id) == chord_to_id["<NC>"]
    assert encode_chord("garbage", chord_to_id) == chord_to_id["<UNK>"]
    assert encode_chord("C5", chord_to_id) is None
    assert encode_chord("<verse_1>", chord_to_id) is None
    assert decode_chord(chord_to_id["A:min7"], id_to_chord) == "A:min7"
    print("encode/decode OK")


def test_encode_progression():
    chord_to_id, _ = load_vocab()
    ids = encode_progression(["C", "Amin", "C5", "F"], max_len=5, chord_to_id=chord_to_id)
    assert len(ids) == 3 + 2  # C, Amin, F kept; C5 dropped; padded to 5
    assert ids[-1] == chord_to_id["<PAD>"]
    print("encode_progression OK")


def test_decode_predictions():
    chord_to_id, id_to_chord = load_vocab()
    scores = [0.0] * len(id_to_chord)
    scores[chord_to_id["<PAD>"]] = 99  # must never be picked despite highest score
    scores[chord_to_id["C:maj"]] = 10
    scores[chord_to_id["A:min"]] = 9
    scores[chord_to_id["F:maj"]] = 8
    top3 = decode_predictions(scores, id_to_chord, k=3)
    assert top3 == ["C:maj", "A:min", "F:maj"], top3
    print("decode_predictions OK")


def test_dataset_coverage():
    if not DATASET_PATH.exists():
        print(f"SKIPPED coverage check - dataset not found at {DATASET_PATH}")
        print("download chordonomicon_v2.csv into data/ to run this check")
        return

    total = 0
    unknown = 0
    with open(DATASET_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            for raw_label in row[CHORD_COLUMN].split():
                parsed = parse_chord(raw_label)
                if parsed == "<TAG>":
                    continue  # song-structure tag, not a chord - don't count
                total += 1
                if parsed is None:
                    unknown += 1

    rate = (unknown / total * 100) if total else 0
    print(f"coverage check: {unknown}/{total} labels unknown ({rate:.2f}%)")


if __name__ == "__main__":
    test_round_trip()
    test_uniqueness()
    test_parser_cases()
    test_encode_decode_round_trip()
    test_encode_progression()
    test_decode_predictions()
    test_dataset_coverage()
