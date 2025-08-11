"""
Data loading and preprocessing for the CTM model.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

import numpy as np
import torch
from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader, Dataset


@dataclass
class BowData:
    """
    Bag of Words data.
    """

    X_train: np.ndarray
    X_val: np.ndarray
    X_test: np.ndarray
    vocab: List[str]


class NewsgroupsBOW:
    """
    Bag of Words data for the 20 Newsgroups dataset.
    """

    def __init__(
        self,
        vocab_size: int,
        max_df: float,
        min_df: int,
        remove_headers: bool,
        remove_footers: bool,
        remove_quotes: bool,
        seed: int,
        val_split: float,
        use_lemmatization: bool,
        spacy_model: str,
        vocabulary: Optional[List[str]] = None,
    ) -> None:
        self.vocab_size = vocab_size
        self.max_df = max_df
        self.min_df = min_df
        self.remove_headers = remove_headers
        self.remove_footers = remove_footers
        self.remove_quotes = remove_quotes
        self.seed = seed
        self.val_split = val_split
        self.use_lemmatization = use_lemmatization
        self.spacy_model = spacy_model
        # If provided, enforce this exact vocabulary and column order for all matrices
        self.vocabulary = vocabulary

    def load(self) -> BowData:
        remove = ()
        if self.remove_headers:
            remove += ("headers",)
        if self.remove_footers:
            remove += ("footers",)
        if self.remove_quotes:
            remove += ("quotes",)

        train = fetch_20newsgroups(subset="train", remove=remove)
        test = fetch_20newsgroups(subset="test", remove=remove)
        texts_train = train.data
        texts_test = test.data

        token_pattern: Optional[str] = (
            r"(?u)\b[a-zA-Z]{3,}\b"  # drop words of length <=3
        )

        if self.vocabulary is None:
            vectorizer = CountVectorizer(
                max_df=self.max_df,
                min_df=self.min_df,
                max_features=self.vocab_size,
                lowercase=True,
                stop_words="english",
                ngram_range=(1, 3),  # include bigrams and trigrams
                token_pattern=token_pattern,
            )
            X_train = vectorizer.fit_transform(texts_train)
            X_test = vectorizer.transform(texts_test)
            vocab = list(vectorizer.get_feature_names_out())
        else:
            # Reconstruct matrices using the exact saved vocabulary to ensure column alignment
            vectorizer = CountVectorizer(
                lowercase=True,
                stop_words="english",
                ngram_range=(1, 3),
                token_pattern=token_pattern,
                vocabulary=self.vocabulary,
            )
            X_train = vectorizer.transform(texts_train)
            X_test = vectorizer.transform(texts_test)
            vocab = list(self.vocabulary)

        # validation split from train
        idx = np.arange(X_train.shape[0])
        train_idx, val_idx = train_test_split(
            idx,
            test_size=self.val_split,
            random_state=self.seed,
            shuffle=True,
        )
        X_tr = X_train[train_idx]
        X_val = X_train[val_idx]

        return BowData(X_tr, X_val, X_test, vocab)


class BowDataset(Dataset):
    """
    Dataset for the Bag of Words data.
    """

    def __init__(self, X_csr) -> None:
        self.X = X_csr.tocsr()
        self.N, self.V = self.X.shape

        # Pre-extract indices and counts for speed in collate
        self.doc_indices = []
        self.doc_counts = []
        for i in range(self.N):
            start, end = self.X.indptr[i], self.X.indptr[i + 1]
            idx = self.X.indices[start:end].astype(np.int64, copy=False)
            cnt = self.X.data[start:end].astype(np.float32, copy=False)
            self.doc_indices.append(idx)
            self.doc_counts.append(cnt)

    def __len__(self) -> int:
        return self.N

    def __getitem__(self, i: int):
        return self.doc_indices[i], self.doc_counts[i]


def collate_to_dense(batch, V: int, device: str = "cpu"):
    """
    Collate a batch of documents into a dense tensor.

    Args:
        batch: Batch of documents.
        V: Vocabulary size.
        device: Device to use.

    Returns:
        Dense tensor of shape (B, V).
    """

    B = len(batch)
    X = torch.zeros((B, V), dtype=torch.float32, device=device)
    for b, (idx, cnt) in enumerate(batch):
        if len(idx) > 0:
            X[b, torch.as_tensor(idx, device=device)] = torch.as_tensor(
                cnt, device=device
            )
    return X


def make_dataloaders(X_train, X_val, batch_size: int, device: str = "cpu"):
    """
    Make dataloaders for the training and validation sets.

    Args:
        X_train: Training set.
        X_val: Validation set.
        batch_size: Batch size.
        device: Device to use.

    Returns:
        Train loader, val loader, train dataset size, val dataset size,
        vocabulary size.
    """

    train_ds = BowDataset(X_train)
    val_ds = BowDataset(X_val)
    V = X_train.shape[1]

    def collate(batch):
        return collate_to_dense(batch, V, device=device)

    train_loader = DataLoader(
        train_ds,
        batch_size=batch_size,
        shuffle=True,
        drop_last=False,
        collate_fn=collate,
    )
    val_loader = DataLoader(
        val_ds,
        batch_size=batch_size,
        shuffle=False,
        drop_last=False,
        collate_fn=collate,
    )
    return train_loader, val_loader, train_ds.N, val_ds.N, V
