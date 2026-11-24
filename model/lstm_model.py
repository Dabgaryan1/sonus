import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from sliding_window import ChordWindowDataset
from pathlib import Path
import random
from chord_vocab import load_vocab
from dataset_split import load_dataset_csv, split_songs
from baseline import load_dataset_sequences, DATASET_CSV

class ChordLSTM(nn.Module):
    def __init__(self, vocab_size=135, embedding_dim=64, hidden_dim=128, num_layers=2, dropout=0.2):
        super().__init__()
        # Embedding layer converts integer IDs to continuous vectors
        self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)
        
        # LSTM layer to capture sequential musical structure
        self.lstm = nn.LSTM(
            input_size=embedding_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            dropout=dropout if num_layers > 1 else 0.0,
            batch_first=True
        )
        
        # Regularization dropout layer
        self.dropout = nn.Dropout(dropout)
        
        # Fully connected output layer mapping hidden states back to vocabulary logits
        self.fc = nn.Linear(hidden_dim, vocab_size)

    def forward(self, x):
        embedded = self.embedding(x)
        lstm_out, _ = self.lstm(embedded)
        
        # Extract output from the final time step in the window sequence
        last_step_out = lstm_out[:, -1, :]
        
        out = self.dropout(last_step_out)
        logits = self.fc(out)
        return logits


def evaluate_lstm(model, dataloader, device, top_k=3):
    model.eval()
    top_1_correct = 0
    top_k_correct = 0
    total_evaluations = 0
    special_ids = {0, 1, 2}

    with torch.no_grad():
        for contexts, targets in dataloader:
            contexts, targets = contexts.to(device), targets.to(device)
            logits = model(contexts)

            for i in range(logits.size(0)):
                pred_logits = logits[i].clone()
                
                # Mask out special tokens so they are excluded from recommendations
                for sp_id in special_ids:
                    pred_logits[sp_id] = -float('inf')

                # Get top-k predictions based on highest logits
                _, top_preds = torch.topk(pred_logits, k=top_k)
                top_preds_list = top_preds.tolist()
                actual = targets[i].item()

                total_evaluations += 1
                if top_preds_list[0] == actual:
                    top_1_correct += 1
                if actual in top_preds_list:
                    top_k_correct += 1

    top_1_acc = top_1_correct / total_evaluations if total_evaluations > 0 else 0.0
    top_k_acc = top_k_correct / total_evaluations if total_evaluations > 0 else 0.0

    return {
        "total_evaluations": total_evaluations,
        "top_1_accuracy": top_1_acc,
        "top_3_accuracy": top_k_acc,
    }


def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    print("Loading vocabulary...")
    chord_to_id, id_to_chord = load_vocab()
    vocab_size = len(chord_to_id)

    print("Loading dataset splits...")
    train_csv = DATASET_CSV.parent / "train.csv"
    test_csv = DATASET_CSV.parent / "test.csv"

    print("Loading and encoding training & test sequences...")
    train_sequences = load_dataset_sequences(train_csv, chord_to_id)
    test_sequences = load_dataset_sequences(test_csv, chord_to_id)

    # Hyperparameters
    context_length = 4
    batch_size = 128
    embedding_dim = 64
    hidden_dim = 128
    num_layers = 2
    epochs = 3
    learning_rate = 1e-3

    print("Building datasets and dataloaders...")
    train_dataset = ChordWindowDataset(train_sequences, context_length=context_length)
    test_dataset = ChordWindowDataset(test_sequences, context_length=context_length)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

    print(f"Train windows: {len(train_dataset)} | Test windows: {len(test_dataset)}")

    model = ChordLSTM(
        vocab_size=vocab_size,
        embedding_dim=embedding_dim,
        hidden_dim=hidden_dim,
        num_layers=num_layers
    ).to(device)

    criterion = nn.CrossEntropyLoss(ignore_index=0)  # Ignore padding index 0
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

    print("\nStarting LSTM Training...")
    for epoch in range(epochs):
        model.train()
        total_loss = 0.0

        for contexts, targets in train_loader:
            contexts, targets = contexts.to(device), targets.to(device)

            optimizer.zero_grad()
            logits = model(contexts)
            loss = criterion(logits, targets)
            loss.backward()
            optimizer.step()

            total_loss += loss.item() * contexts.size(0)

        epoch_loss = total_loss / len(train_dataset)
        print(f"Epoch {epoch + 1}/{epochs} - Loss: {epoch_loss:.4f}")

    print("\nEvaluating LSTM on test set...")
    results = evaluate_lstm(model, test_loader, device, top_k=3)

    print("\nLSTM Evaluation Results")
    print(f"Total Evaluations: {results['total_evaluations']}")
    print(f"LSTM Top-1 Accuracy: {results['top_1_accuracy']:.4f}")
    print(f"LSTM Top-3 Accuracy: {results['top_3_accuracy']:.4f}")


if __name__ == "__main__":
    main()