from chord_parser import parse_chord


def encode_chord(raw_label, chord_to_id):
    parsed = parse_chord(raw_label)
    if parsed == "<DROP>":
        return None
    if parsed is None:
        return chord_to_id["<UNK>"]
    return chord_to_id[parsed]


def decode_chord(chord_id, id_to_chord):
    return id_to_chord[chord_id]


def encode_progression(raw_labels, max_len, chord_to_id):
    ids = []
    for raw_label in raw_labels:
        encoded = encode_chord(raw_label, chord_to_id)
        if encoded is not None:
            ids.append(encoded)

    pad_id = chord_to_id["<PAD>"]
    ids = ids[:max_len]
    ids += [pad_id] * (max_len - len(ids))
    return ids


def decode_predictions(scores, id_to_chord, k=3):
    special_ids = {0, 1, 2}  # <PAD>, <UNK>, <NC> - never valid suggestions
    candidates = [(score, chord_id) for chord_id, score in enumerate(scores) if chord_id not in special_ids]
    candidates.sort(key=lambda pair: pair[0], reverse=True)
    return [id_to_chord[chord_id] for _, chord_id in candidates[:k]]
