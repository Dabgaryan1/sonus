
# SONUS — Shared Model Evaluation

## Objective

Ensure the Markov baseline and LSTM are evaluated on identical next-chord prediction examples using consistent metrics.

## Evaluation Approach

Both models use the same encoded test sequences and the shared `ChordWindowDataset` implementation.

For each evaluation example:

- The LSTM receives the complete context window.
- The bigram Markov baseline receives the final chord of that window.
- Both models predict the same target chord.

For example, with a context length of 4:

Input: C → Am → F → G

Target: C

- LSTM input: C → Am → F → G
- Markov input: G
- Expected target for both: C

This allows the models to use their respective architectures while evaluating the same prediction positions.

## Evaluation Rules

- Use Hanna's shared 135-token chord vocabulary.
- Use the same train/validation/test song splits.
- Exclude `<PAD>`, `<UNK>`, and `<NC>` as prediction targets.
- Exclude special tokens from recommended chords.
- Count unseen Markov contexts as incorrect predictions.
- Calculate Top-1 and Top-3 accuracy using the same total number of examples.
- Use validation data for hyperparameter selection and reserve the test set for final evaluation.

## Implementation

`shared_evaluation.py` provides:

```python
evaluate_models(
    markov,
    lstm,
    sequences,
    device,
    context_length=4,
    top_k=3,
    batch_size=128
)
```

The function returns Top-1 accuracy, Top-3 accuracy, and total evaluations for each model.

Both models must already be trained before their results can be used for a meaningful performance comparison.

## Testing

Run from the repository root:

```bash
python model/test_shared_evaluation.py
```

Automated tests verify:

- Identical target positions and evaluation counts
- Special-token handling
- Unseen Markov contexts
- Context lengths of 3, 4, 8, and 32

Compatibility was also tested using Rafi's actual `ChordLSTM` architecture with randomly initialized weights.

## Current Status

The shared evaluation procedure has passed synthetic tests and an LSTM architecture compatibility test.

No trained LSTM checkpoint was found in the local repository during verification. Final comparative accuracy results must be generated after a trained model is available.

The previously reported Markov results (25.09% Top-1 and 54.45% Top-3) were obtained using a different set of evaluation positions and should not be directly compared with the LSTM until reevaluated using this shared procedure.
