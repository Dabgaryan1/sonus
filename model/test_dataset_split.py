import pandas as pd

from dataset_split import split_songs


def make_songs(n=300):
    genres = (["pop"] * (n // 3)) + (["rock"] * (n // 3)) + (["jazz"] * (n // 3))
    return pd.DataFrame({"id": range(n), "main_genre": genres})


def test_no_overlap():
    df = make_songs()
    train_ids, val_ids, test_ids = split_songs(df)
    assert train_ids.isdisjoint(val_ids), "train/val overlap"
    assert train_ids.isdisjoint(test_ids), "train/test overlap"
    assert val_ids.isdisjoint(test_ids), "val/test overlap"
    print("no overlap OK")


def test_full_coverage():
    df = make_songs()
    train_ids, val_ids, test_ids = split_songs(df)
    assert train_ids | val_ids | test_ids == set(df["id"]), "split does not cover every song"
    print("full coverage OK")


def test_reproducible():
    df = make_songs()
    first = split_songs(df, seed=42)
    second = split_songs(df, seed=42)
    assert first == second, "same seed produced different splits"
    print("reproducible OK")


def test_different_seed_differs():
    df = make_songs()
    a = split_songs(df, seed=42)
    b = split_songs(df, seed=7)
    assert a != b, "different seeds produced identical splits"
    print("seed sensitivity OK")


def test_approximate_ratios():
    df = make_songs(n=3000)
    train_ids, val_ids, test_ids = split_songs(df, val_size=0.10, test_size=0.10, seed=42)
    total = len(train_ids) + len(val_ids) + len(test_ids)
    assert total == len(df)
    assert 0.75 <= len(train_ids) / total <= 0.85, f"train ratio off: {len(train_ids) / total}"
    assert 0.05 <= len(val_ids) / total <= 0.15, f"val ratio off: {len(val_ids) / total}"
    assert 0.05 <= len(test_ids) / total <= 0.15, f"test ratio off: {len(test_ids) / total}"
    print("approximate ratios OK")


if __name__ == "__main__":
    test_no_overlap()
    test_full_coverage()
    test_reproducible()
    test_different_seed_differs()
    test_approximate_ratios()
