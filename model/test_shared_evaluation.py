
import torch
from torch import nn

from baseline import MarkovBaseline
from shared_evaluation import evaluate_models


class DummyLSTM(nn.Module):
    """Returns predictable scores for testing."""

    def __init__(self, vocab_size=135):
        super().__init__()
        self.vocab_size = vocab_size
        self.seen_contexts = []

    def forward(self, x):
        self.seen_contexts.extend(x.cpu().tolist())
        logits = torch.zeros(
            x.size(0), self.vocab_size, device=x.device
        )
        logits[:, 80] = 10.0
        logits[:, 3] = 9.0
        logits[:, 58] = 8.0
        return logits


def test_shared_evaluation():
    train_sequences = [
        [3, 103, 58, 80, 3, 58],
        [3, 103, 58, 80, 3, 58]
    ]

    test_sequences = [
        [3, 103, 58, 80, 3, 58]
    ]

    markov = MarkovBaseline(n=2)
    markov.fit(train_sequences)

    lstm = DummyLSTM()

    results = evaluate_models(
        markov=markov,
        lstm=lstm,
        sequences=test_sequences,
        device=torch.device("cpu"),
        context_length=4,
        top_k=3,
        batch_size=2
    )

    assert results["markov"]["total_evaluations"] == 2
    assert results["lstm"]["total_evaluations"] == 2

    assert lstm.seen_contexts == [
        [3, 103, 58, 80],
        [103, 58, 80, 3]
    ]

    assert results["markov"]["top_1_accuracy"] == 0.5
    assert results["markov"]["top_3_accuracy"] == 1.0

    assert results["lstm"]["top_1_accuracy"] == 0.0
    assert results["lstm"]["top_3_accuracy"] == 1.0

    print("shared evaluation OK")
    print(results)


def test_special_tokens_and_unseen_contexts():
    train_sequences = [[3, 4, 5, 6, 7]]

    # Includes special-token targets and unseen contexts
    test_sequences = [[3, 4, 1, 5, 2, 6, 7, 8, 0]]

    markov = MarkovBaseline(n=2)
    markov.fit(train_sequences)

    lstm = DummyLSTM()

    results = evaluate_models(
        markov=markov,
        lstm=lstm,
        sequences=test_sequences,
        device=torch.device("cpu"),
        context_length=3,
        top_k=3,
        batch_size=2
    )

    # Valid targets are 5, 6, 7, and 8
    assert results["markov"]["total_evaluations"] == 4
    assert results["lstm"]["total_evaluations"] == 4

    # Unseen Markov contexts count as incorrect
    assert results["markov"]["top_1_accuracy"] == 0.25
    assert results["markov"]["top_3_accuracy"] == 0.25

    assert results["lstm"]["top_1_accuracy"] == 0.0
    assert results["lstm"]["top_3_accuracy"] == 0.0

    assert len(lstm.seen_contexts) == 4

    print("special tokens and unseen contexts OK")

def test_context_lengths():
    # 40 chords, enough for a context length of 32
    sequence = [3, 103, 58, 80] * 10

    markov = MarkovBaseline(n=2)
    markov.fit([sequence])

    for length in [3, 4, 8, 32]:
        lstm = DummyLSTM()

        results = evaluate_models(
            markov=markov,
            lstm=lstm,
            sequences=[sequence],
            device=torch.device("cpu"),
            context_length=length,
            top_k=3,
            batch_size=8
        )

        expected = len(sequence) - length

        assert results["markov"]["total_evaluations"] == expected
        assert results["lstm"]["total_evaluations"] == expected

        assert len(lstm.seen_contexts) == expected
        assert all(
            len(context) == length
            for context in lstm.seen_contexts
        )

        print(f"context length {length} OK ({expected} examples)")

if __name__ == "__main__":
    test_shared_evaluation()
    test_special_tokens_and_unseen_contexts()
    test_context_lengths()
