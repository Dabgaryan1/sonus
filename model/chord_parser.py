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
    "add9": "maj",
    "minadd9": "min", "minadd11": "min", "minadd13": "min",
    "add11": "maj", "add13": "maj",
    "11": "7",
    "13": "7",
    "maj11": "maj7", "maj13": "maj7",
    "min13": "min7",
    "7sus2": "7",
    "maj7sus2": "maj7", "maj7sus4": "maj7",
    "augmaj7": "aug",
    "7b9": "7",
    "dim13b9": "dim7",
}

# no definable triad quality (no 3rd) - excluded from training data, not <UNK>
DROPPED_QUALITIES = {"1", "5", "no3d"}

VALID_QUALITIES = set(QUALITIES)
EXTRA_NOTES_RE = re.compile(r"\(.*?\)")
TAG_RE = re.compile(r"^<.*>$")


def classify_suffix(suffix):
    if suffix == "":
        return "maj"
    if suffix in VALID_QUALITIES:
        return suffix
    if suffix in DROPPED_QUALITIES:
        return "<DROP>"
    return QUALITY_COLLAPSE.get(suffix)


def split_root_quality(token):
    # e.g. "Fsmin" (F#, min) vs "Csus4" (C, sus4) - both start "Cs"/"Fs",
    # so only consume the accidental if what's left is a real quality.
    if len(token) >= 2 and token[1] in ("s", "b"):
        candidate_root, candidate_rest = token[:2], token[2:]
        quality = classify_suffix(candidate_rest)
        if quality is not None:
            return candidate_root, quality

    root, rest = token[:1], token[1:]
    return root, classify_suffix(rest)


def normalize_root(root):
    if len(root) == 2 and root[1] == "s":
        root = root[0] + "#"
    return ROOT_NORMALIZATION.get(root, root)


def parse_chord(raw_label):
    raw_label = raw_label.strip()

    if TAG_RE.match(raw_label):
        return "<TAG>"
    if raw_label == "N":
        return "<NC>"

    raw_label = raw_label.split("/", 1)[0]
    raw_label = EXTRA_NOTES_RE.sub("", raw_label)

    if not raw_label or raw_label[0] not in "ABCDEFG":
        return None

    root, quality = split_root_quality(raw_label)
    root = normalize_root(root)
    if root not in ROOTS:
        return None

    if quality is None:
        return None
    if quality == "<DROP>":
        return "<DROP>"

    return f"{root}:{quality}"
