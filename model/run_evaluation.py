from pathlib import Path
import time
import torch

from baseline import DATASET_CSV, MarkovBaseline, load_dataset_sequences
from chord_vocab import load_vocab
from lstm_model import DEFAULT_WEIGHTS_PATH, load_weights
from shared_evaluation import evaluate_models


def main(weights_path=DEFAULT_WEIGHTS_PATH, top_k=3, batch_size=128):
    start_time = time.perf_counter()
    weights_path = Path(weights_path)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[1/6] Using device: {device}")

    print("[2/6] Loading chord vocabulary...")
    chord_to_id, _ = load_vocab()
    vocab_size = len(chord_to_id)
    print(f"      Loaded vocabulary with {vocab_size} tokens.")

    train_csv = DATASET_CSV.parent / "train.csv"
    test_csv = DATASET_CSV.parent / "test.csv"
    print(f"[3/6] Loading and encoding training sequences from {train_csv}...")
    train_sequences = load_dataset_sequences(train_csv, chord_to_id)
    print(f"      Loaded {len(train_sequences)} training sequences.")

    print(f"[4/6] Fitting bigram Markov baseline (n=2)...")
    markov_start = time.perf_counter()
    markov = MarkovBaseline(n=2)
    markov.fit(train_sequences)
    print(f"      Markov model ready in {time.perf_counter() - markov_start:.2f}s.")

    if not weights_path.exists():
        raise FileNotFoundError(
            f"LSTM weights not found at {weights_path}. Run lstm_model.py first."
        )

    print(f"[5/6] Loading saved LSTM weights from {weights_path}...")
    lstm, checkpoint = load_weights(
        weights_path,
        device=device,
        expected_vocab_size=vocab_size,
    )
    context_length = checkpoint.get("context_length", 4)
    print(f"      LSTM loaded (context_length={context_length}).")

    print(f"[6/6] Loading test sequences from {test_csv} and running shared evaluation...")
    test_sequences = load_dataset_sequences(test_csv, chord_to_id)
    print(f"      Loaded {len(test_sequences)} test sequences. Evaluating windows (batch_size={batch_size}, top_k={top_k})...")

    eval_start = time.perf_counter()
    results = evaluate_models(
        markov=markov,
        lstm=lstm,
        sequences=test_sequences,
        device=device,
        context_length=context_length,
        top_k=top_k,
        batch_size=batch_size,
    )
    print(f"      Shared evaluation finished in {time.perf_counter() - eval_start:.2f}s.")

    print("\n Shared Evaluation Results ")
    for model_name, metrics in results.items():
        print(
            f"{model_name.upper():<8} | "
            f"Top-1: {metrics['top_1_accuracy']:.4f} | "
            f"Top-3: {metrics['top_3_accuracy']:.4f} | "
            f"Evaluations: {metrics['total_evaluations']}"
        )

    print(f"\nTotal runtime: {time.perf_counter() - start_time:.2f}s")


if __name__ == "__main__":
    main()