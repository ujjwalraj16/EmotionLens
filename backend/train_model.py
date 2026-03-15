import os
import re
import json
import pickle
import numpy as np
from collections import Counter
from tqdm import tqdm

import tensorflow as tf
import keras
from datasets import load_dataset

from model import build_text_cnn   

MAX_SEQ_LEN   = 64       
EMBED_DIM     = 128      
NUM_FILTERS   = 128     
KERNEL_SIZES  = [2, 3, 4]
DROPOUT_RATE  = 0.5
BATCH_SIZE    = 64
EPOCHS        = 15      
MIN_FREQ      = 2       
SAVE_DIR      = "saved_model"

EMOTIONS = [
    "admiration", "amusement", "anger", "annoyance", "approval",
    "caring", "confusion", "curiosity", "desire", "disappointment",
    "disapproval", "disgust", "embarrassment", "excitement", "fear",
    "gratitude", "grief", "joy", "love", "nervousness",
    "optimism", "pride", "realization", "relief", "remorse",
    "sadness", "surprise", "neutral",
]

def clean_text(text: str) -> str:
    """Lowercase, remove URLs and non-alphabetic characters."""
    text = text.lower()
    text = re.sub(r"http\S+", "", text)           
    text = re.sub(r"[^a-z\s']", " ", text)        
    text = re.sub(r"\s+", " ", text).strip()
    return text


def build_vocab(texts: list, min_freq: int = 2) -> dict:
    """
    Build a word → integer-ID vocabulary.

    Reserved IDs:
        0  →  <PAD>  (padding, ignored by embedding with mask_zero=True)
        1  →  <UNK>  (unknown word)
    """
    counter = Counter()
    for text in texts:
        counter.update(text.split())

    vocab = {"<PAD>": 0, "<UNK>": 1}
    for word, freq in counter.items():
        if freq >= min_freq:
            vocab[word] = len(vocab)

    print(f"[Vocab] vocabulary size = {len(vocab):,}")
    return vocab


def encode_and_pad(texts: list, vocab: dict, max_len: int) -> np.ndarray:
    """
    Convert a list of cleaned strings to a 2-D NumPy array of shape
    (num_samples, max_len).  Sequences are truncated or zero-padded.
    """
    encoded = []
    for text in texts:
        tokens = text.split()[:max_len]
        ids    = [vocab.get(tok, vocab["<UNK>"]) for tok in tokens]
        ids   += [0] * (max_len - len(ids))  
        encoded.append(ids)
    return np.array(encoded, dtype=np.int32)

def load_split(split, label_field="labels"):
    """
    Extract single-label (text, label) pairs from a HuggingFace dataset split.
    GoEmotions allows multi-label; we keep only single-label examples for
    a clean multi-class classification task.
    """
    texts, labels = [], []
    for ex in split:
        if len(ex[label_field]) == 1:   # single emotion only
            texts.append(clean_text(ex["text"]))
            labels.append(ex[label_field][0])
    return texts, labels

def main():

    print("[Data] Downloading GoEmotions …")
    dataset  = load_dataset("google-research-datasets/go_emotions", "simplified")
    train_ds = dataset["train"]
    val_ds   = dataset["validation"]
    test_ds  = dataset["test"]

    train_texts, train_labels = load_split(train_ds)
    val_texts,   val_labels   = load_split(val_ds)
    test_texts,  test_labels  = load_split(test_ds)

    print(f"[Data] train={len(train_texts):,}  "
          f"val={len(val_texts):,}  test={len(test_texts):,}")

    vocab = build_vocab(train_texts, min_freq=MIN_FREQ)

    X_train = encode_and_pad(train_texts, vocab, MAX_SEQ_LEN)
    X_val   = encode_and_pad(val_texts,   vocab, MAX_SEQ_LEN)
    X_test  = encode_and_pad(test_texts,  vocab, MAX_SEQ_LEN)

    y_train = np.array(train_labels, dtype=np.int32)
    y_val   = np.array(val_labels,   dtype=np.int32)
    y_test  = np.array(test_labels,  dtype=np.int32)

    num_classes = len(set(train_labels))
    print(f"[Data] num_classes = {num_classes}")

    model = build_text_cnn(
        vocab_size=len(vocab),
        embed_dim=EMBED_DIM,
        num_classes=num_classes,
        num_filters=NUM_FILTERS,
        kernel_sizes=KERNEL_SIZES,
        dropout_rate=DROPOUT_RATE,
        max_seq_len=MAX_SEQ_LEN,
    )

    model.summary()

    os.makedirs(SAVE_DIR, exist_ok=True)
    checkpoint_path = os.path.join(SAVE_DIR, "best_model.keras")

    callbacks = [
        keras.callbacks.ModelCheckpoint(
            filepath=checkpoint_path,
            monitor="val_accuracy",
            save_best_only=True,
            verbose=1,
        ),
        keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.5,
            patience=2,
            verbose=1,
        ),
        keras.callbacks.EarlyStopping(
            monitor="val_loss",
            patience=4,
            restore_best_weights=True,
            verbose=1,
        ),
        keras.callbacks.TerminateOnNaN(),
    ]

    print("\n[Train] Starting training …\n")
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        batch_size=BATCH_SIZE,
        epochs=EPOCHS,
        callbacks=callbacks,
        verbose=1,
    )
    test_loss, test_acc = model.evaluate(X_test, y_test, verbose=0)
    print(f"\n[Test] loss={test_loss:.4f}  accuracy={test_acc:.4f}")

    with open(os.path.join(SAVE_DIR, "vocab.pkl"), "wb") as f:
        pickle.dump(vocab, f)
    meta = {
        "vocab_size":    len(vocab),
        "embed_dim":     EMBED_DIM,
        "num_classes":   num_classes,
        "num_filters":   NUM_FILTERS,
        "kernel_sizes":  KERNEL_SIZES,
        "dropout_rate":  DROPOUT_RATE,
        "max_seq_len":   MAX_SEQ_LEN,
        "emotions":      EMOTIONS[:num_classes],
    }
    with open(os.path.join(SAVE_DIR, "meta.json"), "w") as f:
        json.dump(meta, f, indent=2)

    print(f"\n[Done] Artefacts saved to ./{SAVE_DIR}/")
    print(f"        best_model.keras  ← Keras SavedModel")
    print(f"        vocab.pkl         ← vocabulary dict")
    print(f"        meta.json         ← hyper-params & emotion names")


if __name__ == "__main__":
    main()