import json
from pathlib import Path

ROOTS = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
QUALITIES = ["maj", "min", "dim", "aug", "sus2", "sus4", "7", "maj7", "min7", "min7b5", "dim7"]
SPECIAL_TOKENS = {"<PAD>": 0, "<UNK>": 1, "<NC>": 2}

VOCAB_PATH = Path(__file__).parent / "chord_vocab.json"


def build_vocab():
    chord_to_id = dict(SPECIAL_TOKENS)
    idx = len(SPECIAL_TOKENS)
    for root in ROOTS:
        for quality in QUALITIES:
            chord_to_id[f"{root}:{quality}"] = idx
            idx += 1
    id_to_chord = {v: k for k, v in chord_to_id.items()}
    return chord_to_id, id_to_chord


def save_vocab(path=VOCAB_PATH):
    chord_to_id, id_to_chord = build_vocab()
    data = {
        "special_tokens": SPECIAL_TOKENS,
        "roots": ROOTS,
        "qualities": QUALITIES,
        "chord_to_id": chord_to_id,
        "id_to_chord": id_to_chord,
    }
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def load_vocab(path=VOCAB_PATH):
    with open(path) as f:
        data = json.load(f)
    id_to_chord = {int(k): v for k, v in data["id_to_chord"].items()}
    return data["chord_to_id"], id_to_chord


if __name__ == "__main__":
    save_vocab()
