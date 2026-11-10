import torch
from torch.utils.data import Dataset

def generate_windows(sequence, context_length=3):
    """
    Generate sliding-window input/target pairs from encoded chords.

    Special tokens:
        0 = <PAD>
        1 = <UNK>
        2 = <NC>

    Skips padding and non-chord targets.
    """
    if context_length < 1:
        raise ValueError("context_length must be at least 1")

    for i in range(len(sequence) - context_length):
        context = sequence[i:i + context_length]
        target = sequence[i + context_length]

        # Padding should never appear in a training example.
        if 0 in context or target == 0:
            continue

        # Only actual chords should be prediction targets.
        if target in (1, 2):
            continue

        yield context, target

        import torch
from torch.utils.data import Dataset


class ChordWindowDataset(Dataset):
    """
    PyTorch dataset for next-chord prediction.

    Accepts encoded song sequences and creates fixed-length
    input/target pairs without storing every window separately.
    """

    def __init__(self, sequences, context_length=3):
        if context_length < 1:
            raise ValueError("context_length must be at least 1")

        self.sequences = sequences
        self.context_length = context_length
        self.window_indices = []

        for song_idx, sequence in enumerate(sequences):
            for start in range(len(sequence) - context_length):
                context = sequence[start:start + context_length]
                target = sequence[start + context_length]

                if 0 in context or target in (0, 1, 2):
                    continue

                self.window_indices.append((song_idx, start))

    def __len__(self):
        return len(self.window_indices)

    def __getitem__(self, idx):
        song_idx, start = self.window_indices[idx]
        sequence = self.sequences[song_idx]

        context = sequence[start:start + self.context_length]
        target = sequence[start + self.context_length]

        return (
            torch.tensor(context, dtype=torch.long),
            torch.tensor(target, dtype=torch.long)
        )