import random
from pathlib import Path

import pandas as pd
from datasets import load_dataset

SEED = 42
VAL_SIZE = 0.10
TEST_SIZE = 0.10
MIN_GROUP_SIZE = 3  # genres with fewer songs than this are folded into "other" for stratification

DATA_DIR = Path(__file__).parent.parent / "data"
DATASET_CSV = DATA_DIR / "chordonomicon_v2.csv"


def download_dataset(path=DATASET_CSV):
    df = load_dataset("ailsntua/Chordonomicon")["train"].to_pandas()
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return df


def load_dataset_csv(path=DATASET_CSV):
    if not path.exists():
        return download_dataset(path)
    return pd.read_csv(path)


def stratify_labels(df, min_group_size=MIN_GROUP_SIZE):
    labels = df["main_genre"].fillna("unknown")
    rare = labels.value_counts().loc[lambda c: c < min_group_size].index
    return labels.where(~labels.isin(rare), "other")


def split_songs(df, val_size=VAL_SIZE, test_size=TEST_SIZE, seed=SEED):
    assert df["id"].is_unique, "expected one row per song"

    labels = stratify_labels(df)
    rng = random.Random(seed)

    train_ids, val_ids, test_ids = set(), set(), set()
    for _, group in df.groupby(labels, sort=False):
        ids = list(group["id"])
        rng.shuffle(ids)
        n_val = round(len(ids) * val_size)
        n_test = round(len(ids) * test_size)
        val_ids.update(ids[:n_val])
        test_ids.update(ids[n_val:n_val + n_test])
        train_ids.update(ids[n_val + n_test:])

    return train_ids, val_ids, test_ids


def save_split(df, train_ids, val_ids, test_ids, out_dir=DATA_DIR):
    out_dir.mkdir(parents=True, exist_ok=True)
    df[df["id"].isin(train_ids)].to_csv(out_dir / "train.csv", index=False)
    df[df["id"].isin(val_ids)].to_csv(out_dir / "val.csv", index=False)
    df[df["id"].isin(test_ids)].to_csv(out_dir / "test.csv", index=False)


def main():
    df = load_dataset_csv()
    train_ids, val_ids, test_ids = split_songs(df)
    save_split(df, train_ids, val_ids, test_ids)
    print(f"train={len(train_ids)} val={len(val_ids)} test={len(test_ids)}")


if __name__ == "__main__":
    main()
