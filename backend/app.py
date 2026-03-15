import os
import re
import json
import pickle

import numpy as np
import tensorflow as tf
import keras
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)   # allow the Streamlit frontend to call this API

SAVE_DIR = "saved_model"


MODEL: keras.Model = None
VOCAB:  dict       = None
META:   dict       = None


def load_artefacts():
    global MODEL, VOCAB, META

    with open(os.path.join(SAVE_DIR, "meta.json"), "r") as f:
        META = json.load(f)

    with open(os.path.join(SAVE_DIR, "vocab.pkl"), "rb") as f:
        VOCAB = pickle.load(f)

    MODEL = keras.models.load_model(os.path.join(SAVE_DIR, "best_model.keras"))
    MODEL.trainable = False   # freeze for inference

    print(f"[Startup] Model loaded — num_classes={META['num_classes']}")


def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"[^a-z\s']", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def encode_and_pad(text: str, vocab: dict, max_len: int) -> np.ndarray:
    """Return a (1, max_len) int32 numpy array."""
    tokens = text.split()[:max_len]
    ids    = [vocab.get(tok, vocab["<UNK>"]) for tok in tokens]
    ids   += [0] * (max_len - len(ids))
    return np.array([ids], dtype=np.int32)   # batch dimension = 1


@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "ok", "message": "Emotion Detection API (TF) is running."})


@app.route("/predict", methods=["POST"])
def predict():
    # ── Parse ────────────────────────────────────────────────────────────────
    data = request.get_json(force=True, silent=True)
    if not data or "text" not in data:
        return jsonify({"error": "Send JSON with a 'text' field."}), 400

    raw_text = data["text"].strip()
    if not raw_text:
        return jsonify({"error": "The 'text' field is empty."}), 400

    # ── Preprocess ───────────────────────────────────────────────────────────
    clean  = clean_text(raw_text)
    tensor = encode_and_pad(clean, VOCAB, META["max_seq_len"])

    # model.predict returns a (1, num_classes) float32 array of probabilities
    probs     = MODEL.predict(tensor, verbose=0)[0]   # shape (num_classes,)
    pred_idx  = int(np.argmax(probs))
    emotions  = META["emotions"]

    # Map every emotion label to its probability
    all_emotions = {
        emo: round(float(p), 4)
        for emo, p in zip(emotions, probs)
    }

    return jsonify({
        "emotion":      emotions[pred_idx],
        "confidence":   round(float(probs[pred_idx]), 4),
        "all_emotions": all_emotions,
    })


if __name__ == "__main__":
    load_artefacts()
    app.run(host="0.0.0.0", port=5001, debug=False)