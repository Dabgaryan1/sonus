import re

from chord_vocab import ROOTS, QUALITIES

ROOT_NORMALIZATION = {
    "Db": "C#", "Eb": "D#", "Gb": "F#", "Ab": "G#", "Bb": "A#",
    "Fb": "E", "Cb": "B", "E#": "F", "B#": "C",
}

QUALITY_COLLAPSE = {
    "maj6": "maj", "6": "maj",
    "min6": "min",
    "maj9": "maj7",
    "9": "7",
    "min9": "min7", "min11": "min7",
    "minmaj7": "min7",
    "hdim7": "min7b5",
    "7sus4": "7", "b7sus4": "7",
}

# no definable triad quality (no 3rd) - power chords dropped from training data, not <UNK>
DROPPED_QUALITIES = {"1", "5"}

VALID_QUALITIES = set(QUALITIES)
EXTRA_NOTES_RE = re.compile(r"\(.*?\)")


def normalize_root(root):
    return ROOT_NORMALIZATION.get(root, root)


def normalize_quality(quality):
    if quality in VALID_QUALITIES:
        return quality
    return QUALITY_COLLAPSE.get(quality)


def parse_chord(raw_label):
    raw_label = raw_label.strip()
    if raw_label == "N":
        return "<NC>"

    raw_label = raw_label.split("/", 1)[0]
    raw_label = EXTRA_NOTES_RE.sub("", raw_label)

    if ":" not in raw_label:
        return None

    root, quality = raw_label.split(":", 1)
    root = normalize_root(root)
    if root not in ROOTS:
        return None

    if quality in DROPPED_QUALITIES:
        return "<DROP>"

    quality = normalize_quality(quality)
    if quality is None:
        return None

    return f"{root}:{quality}"
