from collections import defaultdict
import random
import csv
from chord_encoder import encode_chord
from chord_vocab import load_vocab
from dataset_split import load_dataset_csv, split_songs, DATASET_CSV


def parse_raw_chords_to_ids(raw_str, chord_to_id):
    raw_labels = raw_str.split()
    encoded = []
    for label in raw_labels:
        enc = encode_chord(label, chord_to_id)
        if enc is not None:
            encoded.append(enc)
    return encoded


def load_dataset_sequences(csv_path, chord_to_id, chord_col="chords"):
    sequences = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if chord_col in row and row[chord_col]:
                seq = parse_raw_chords_to_ids(row[chord_col], chord_to_id)
                if len(seq) > 1:
                    sequences.append(seq)
    return sequences


class MarkovBaseline:
    def __init__(self, n=2):
        self.n = n
        self.transition_probs = {}

    def fit(self, train_sequences):
        #Alias for train to support the test suite.
        self.train(train_sequences)

    def train(self, train_sequences):
        #Trains an N-gram transition model on encoded sequences
        transition_counts = defaultdict(lambda: defaultdict(int))
        
        for seq in train_sequences:
            for i in range(len(seq) - (self.n - 1)):
                context = tuple(seq[i:i + self.n - 1])
                target = seq[i + self.n - 1]
                transition_counts[context][target] += 1
                
        self.transition_probs = {}
        for context, targets in transition_counts.items():
            total_count = sum(targets.values())
            self.transition_probs[context] = {
                chord_id: count / total_count for chord_id, count in targets.items()
            }

    def predict_next_chord_ids(self, context, top_k=3):
        #Predicts top-k next chord IDs given a context tuple/list, excluding special tokens.
        special_ids = {0, 1, 2}
        ctx_tuple = tuple(context)
        
        if ctx_tuple not in self.transition_probs:
            return []
            
        filtered_preds = [
            (chord_id, prob) for chord_id, prob in self.transition_probs[ctx_tuple].items()
            if chord_id not in special_ids
        ]
        
        sorted_preds = sorted(filtered_preds, key=lambda x: x[1], reverse=True)
        return [chord_id for chord_id, prob in sorted_preds[:top_k]]

    def predict_next_chords(self, context, id_to_chord, top_k=3):
        #Predicts top-k chord string names given a context.
        chord_ids = self.predict_next_chord_ids(context, top_k=top_k)
        return [id_to_chord[cid] for cid in chord_ids]

    def predict(self, context, top_k=3):
        return self.predict_next_chord_ids(context, top_k=top_k)

    def evaluate(self, test_sequences, top_k=3, sample_size=None):
        return evaluate_baseline(self, test_sequences, top_k=top_k, sample_size=sample_size)


def evaluate_baseline(model, test_sequences, top_k=3, sample_size=None):
    #Evaluates the baseline model on test sequences 
    top_1_correct = 0
    top_k_correct = 0
    total_predictions = 0
    
    if sample_size is not None and len(test_sequences) > sample_size:
        eval_data = random.sample(test_sequences, sample_size)
    else:
        eval_data = test_sequences
        
    print(f"Evaluating on {len(eval_data)} test sequences...")
    
    for seq in eval_data:
        for i in range(len(seq) - (model.n - 1)):
            context = tuple(seq[i:i + (model.n - 1)])
            actual_next_chord = seq[i + (model.n - 1)]
            
            if actual_next_chord in {0, 1, 2}:
                continue
                
            total_predictions += 1
            top_preds = model.predict_next_chord_ids(context, top_k=top_k)
            
            if len(top_preds) > 0 and top_preds[0] == actual_next_chord:
                top_1_correct += 1
            if actual_next_chord in top_preds:
                top_k_correct += 1
                
    top_1_acc = top_1_correct / total_predictions if total_predictions > 0 else 0.0
    top_k_acc = top_k_correct / total_predictions if total_predictions > 0 else 0.0
    
    return {
        "total_evaluations": total_predictions,
        "top_1_accuracy": top_1_acc,
        "top_3_accuracy": top_k_acc,
    }


def main():
    print("Loading vocabulary...")
    chord_to_id, id_to_chord = load_vocab()
    print(f"Loaded {len(chord_to_id)} vocabulary tokens.")

    print("Loading dataset splits...")
    if not DATASET_CSV.exists():
        print("Dataset CSV not found. Downloading from Hugging Face...")
        from dataset_split import download_dataset
        download_dataset()
    
    df = load_dataset_csv()
    train_ids, val_ids, test_ids = split_songs(df)
    
    train_df = df[df["id"].isin(train_ids)]
    test_df = df[df["id"].isin(test_ids)]
    print(f"Train songs: {len(train_df)}, Test songs: {len(test_df)}")

    print("Loading and encoding training sequences...")
    train_csv = DATASET_CSV.parent / "train.csv"
    test_csv = DATASET_CSV.parent / "test.csv"
    
    if not train_csv.exists():
        from dataset_split import save_split
        save_split(df, train_ids, val_ids, test_ids)

    train_sequences = load_dataset_sequences(train_csv, chord_to_id)
    print(f"Loaded {len(train_sequences)} valid training sequences.")

    print("Training Markov baseline model...")
    baseline = MarkovBaseline(n=2)
    baseline.fit(train_sequences)
    print("Training complete.")

    print("Loading test sequences and evaluating on all test data...")
    test_sequences = load_dataset_sequences(test_csv, chord_to_id)
    
    results = evaluate_baseline(baseline, test_sequences, top_k=3, sample_size=None)

    print("\nEvaluation Results")
    print(f"Total Evaluations: {results['total_evaluations']}")
    print(f"Baseline Top-1 Accuracy: {results['top_1_accuracy']:.4f}")
    print(f"Baseline Top-3 Accuracy: {results['top_3_accuracy']:.4f}")


if __name__ == "__main__":
    main()