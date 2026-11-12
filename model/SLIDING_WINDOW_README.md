
# SONUS — Sliding-Window Dataset

## Overview

The sliding-window dataset converts encoded chord progressions into input/target pairs for next-chord prediction.

It uses Hanna's chord encoder and the shared Chordonomicon train/validation/test splits.

## Features

- Configurable context lengths (3, 5, or 8 chords)
- Generates windows within individual songs
- Excludes `<PAD>`, `<UNK>`, and `<NC>` as prediction targets
- Allows `<UNK>` and `<NC>` in input contexts
- Returns PyTorch tensors compatible with DataLoader

## Usage

Run the following code from the `model` directory:

```python
from baseline import load_dataset_sequences
from chord_vocab import load_vocab
from dataset_split import DATA_DIR
from sliding_window import ChordWindowDataset
from torch.utils.data import DataLoader

chord_to_id, _ = load_vocab()

train_sequences = load_dataset_sequences(
    DATA_DIR / "train.csv", chord_to_id
)

train_dataset = ChordWindowDataset(
    train_sequences, context_length=3
)

train_loader = DataLoader(
    train_dataset, batch_size=64, shuffle=True
)

inputs, targets = next(iter(train_loader))

print("Input shape:", inputs.shape)
print("Target shape:", targets.shape)
```

Expected shapes:

- Inputs: `(64, 3)`
- Targets: `(64,)`

## Testing

```bash
python model/test_sliding_window.py
```

Run this command from the repository root.

## Notes

- The dataset uses the shared 135-token vocabulary.
- Split files must be generated before loading the dataset.
- The current implementation stores encoded song sequences and window indices in memory. It does not store full window tensors.
- The LSTM and Markov baseline should use the same target positions and special-token evaluation rules for a fair comparison.
