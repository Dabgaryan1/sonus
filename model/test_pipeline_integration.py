import torch

from chord_encoder import encode_chord
from chord_vocab import load_vocab
from sliding_window import ChordWindowDataset


def test_encoder_to_sliding_window():
    chord_to_id, id_to_chord = load_vocab()

    # Simulated chord progression extracted from MIDI
    raw_chords = [
        "C",
        "Amin",
        "F",
        "G",
        "C",
        "Amin"
    ]

    # Encode using Hanna's existing encoder
    encoded = [
        encode_chord(chord, chord_to_id)
        for chord in raw_chords
    ]

    assert all(chord_id is not None for chord_id in encoded)

    # Generate context/target pairs
    context_length = 3
    dataset = ChordWindowDataset(
        [encoded],
        context_length=context_length
    )
    
    expected_windows = len(encoded) - context_length
    assert len(dataset) == expected_windows

    # Verify input/target tensors
    for context, target in dataset:
        assert isinstance(context, torch.Tensor)
        assert isinstance(target, torch.Tensor)

        assert context.dtype == torch.long
        assert target.dtype == torch.long

        assert context.shape == (context_length,)
        assert target.ndim == 0

        # No padding or special-token targets
        assert 0 not in context.tolist()
        assert target.item() not in (0, 1, 2)

    # Verify first window matches expected chords
    first_context, first_target = dataset[0]

    decoded_context = [
        id_to_chord[chord_id]
        for chord_id in first_context.tolist()
    ]

    decoded_target = id_to_chord[first_target.item()]

    assert decoded_context == [
        "C:maj", "A:min", "F:maj"
    ]
    assert decoded_target == "G:maj"

    print("encoder to sliding-window integration OK")

def test_special_tokens_and_short_progressions():
    chord_to_id, _ = load_vocab()

    raw_chords = ["C", "Am", "F", "G", "C", "Amin"]

    encoded = [
        encode_chord(chord, chord_to_id)
        for chord in raw_chords
    ]

    # "Am" is unsupported and maps to <UNK>.
    assert encoded[1] == chord_to_id["<UNK>"]

    dataset = ChordWindowDataset(
        [encoded],
        context_length=3
    )

    # <UNK> is allowed in input contexts, but not as a target.
    assert len(dataset) == 3

    for context, target in dataset:
        assert target.item() not in (0, 1, 2)
        assert 0 not in context.tolist()

    # A progression shorter than the context length
    # should produce no training windows.
    short_sequence = [
        encode_chord("C", chord_to_id),
        encode_chord("F", chord_to_id)
    ]

    short_dataset = ChordWindowDataset(
        [short_sequence],
        context_length=3
    )

    assert len(short_dataset) == 0

    print("special tokens and short progressions OK")
    
def test_special_token_targets():
    chord_to_id, _ = load_vocab()

    # C, F, G, and D are valid chords.
    # "Am" is unsupported and becomes <UNK>.
    # "N" represents <NC>.
    raw_chords = ["C", "F", "G", "Am", "N", "D"]

    encoded = [
        encode_chord(chord, chord_to_id)
        for chord in raw_chords
    ]

    assert encoded[3] == chord_to_id["<UNK>"]
    assert encoded[4] == chord_to_id["<NC>"]

    dataset = ChordWindowDataset(
        [encoded],
        context_length=3
    )

    # Candidate targets are <UNK>, <NC>, and D.
    # Only D should be retained.
    assert len(dataset) == 1

    context, target = dataset[0]

    assert target.item() == chord_to_id["D:maj"]
    assert context.tolist() == encoded[2:5]

    print("special token target filtering OK")

if __name__ == "__main__":
    test_encoder_to_sliding_window()
    test_special_tokens_and_short_progressions()
    test_special_token_targets()
