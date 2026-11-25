import torch
from torch.utils.data import DataLoader

from sliding_window import ChordWindowDataset


def evaluate_models(markov, lstm, sequences, device,
                    context_length=4, top_k=3, batch_size=128):
    """
    Evaluate Markov and LSTM on identical next-chord examples.

    The LSTM receives the full context window.
    The bigram Markov model receives the final chord only.
    Both models predict the same target.
    """
    if context_length < 1:
        raise ValueError("context_length must be at least 1")
    if top_k < 1:
        raise ValueError("top_k must be at least 1")

    dataset = ChordWindowDataset(
        sequences,
        context_length=context_length
    )

    loader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=False
    )

    results = {
        "markov": {"top_1": 0, "top_3": 0},
        "lstm": {"top_1": 0, "top_3": 0}
    }

    total = 0
    special_ids = {0, 1, 2}

    lstm.eval()

    with torch.no_grad():
        for contexts, targets in loader:
            contexts = contexts.to(device)
            targets = targets.to(device)

            # LSTM predictions for the entire batch
            logits = lstm(contexts)
            logits[:, list(special_ids)] = float("-inf")

            k = min(top_k, logits.shape[1] - len(special_ids))
            lstm_predictions = torch.topk(logits, k=k, dim=1).indices

            for i in range(len(targets)):
                actual = targets[i].item()

                # Bigram Markov uses only the last context chord
                last_chord = contexts[i, -1].item()
                markov_predictions = markov.predict_next_chord_ids(
                    [last_chord],
                    top_k=k
                )

                lstm_preds = lstm_predictions[i].tolist()

                total += 1

                if markov_predictions:
                    if markov_predictions[0] == actual:
                        results["markov"]["top_1"] += 1
                    if actual in markov_predictions:
                        results["markov"]["top_3"] += 1

                if lstm_preds[0] == actual:
                    results["lstm"]["top_1"] += 1
                if actual in lstm_preds:
                    results["lstm"]["top_3"] += 1

    for name in results:
        results[name] = {
            "top_1_accuracy": (
                results[name]["top_1"] / total if total else 0.0
            ),
            "top_3_accuracy": (
                results[name]["top_3"] / total if total else 0.0
            ),
            "total_evaluations": total
        }

    return results