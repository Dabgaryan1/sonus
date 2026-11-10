from sliding_window import generate_windows, ChordWindowDataset
from torch.utils.data import DataLoader


def test_basic_windows():
    sequence = [3, 103, 58, 80, 3]
    result = list(generate_windows(sequence, context_length=3))

    assert result == [
        ([3, 103, 58], 80),
        ([103, 58, 80], 3)
    ]
    print("basic windows OK")


def test_special_tokens():
    sequence = [3, 103, 1, 58, 80, 2, 3, 0]
    result = list(generate_windows(sequence, context_length=3))

    assert result == [
        ([3, 103, 1], 58),
        ([103, 1, 58], 80),
        ([58, 80, 2], 3)
    ]
    print("special tokens OK")


def test_multiple_songs():
    sequences = [
        [3, 103, 58, 80, 3],
        [58, 80, 2, 3, 1, 103, 0]
    ]

    dataset = ChordWindowDataset(sequences, context_length=3)

    assert len(dataset) == 4
    assert dataset[0][0].tolist() == [3, 103, 58]
    assert dataset[1][0].tolist() == [103, 58, 80]
    assert dataset[2][0].tolist() == [58, 80, 2]
    assert dataset[3][0].tolist() == [2, 3, 1]
    print("multiple songs OK")


def test_dataloader():
    dataset = ChordWindowDataset(
        [[3, 103, 58, 80, 3]],
        context_length=3
    )

    loader = DataLoader(dataset, batch_size=2, shuffle=False)
    inputs, targets = next(iter(loader))

    assert inputs.shape == (2, 3)
    assert targets.shape == (2,)
    assert targets.tolist() == [80, 3]
    print("DataLoader OK")


def test_context_lengths():
    sequence = [3, 103, 58, 80, 3, 58, 80, 103, 3]

    for length in [3, 5, 8]:
        result = list(generate_windows(sequence, context_length=length))
        assert len(result) == len(sequence) - length
        assert all(len(context) == length for context, _ in result)

    print("context lengths OK")


if __name__ == "__main__":
    test_basic_windows()
    test_special_tokens()
    test_multiple_songs()
    test_dataloader()
    test_context_lengths()