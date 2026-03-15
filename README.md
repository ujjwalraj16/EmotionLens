# 🔍 EmotionLens

EmotionLens is an end-to-end deep learning application that detects emotions from text in real time. Built with a CNN trained on the GoEmotions dataset (28 emotion classes), it features a Streamlit frontend and a Flask REST API backend.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🧠 **28 Emotion Classes** | Trained on Google's GoEmotions dataset — from *joy* and *love* to *remorse* and *grief* |
| 📄 **File Upload** | Supports `.txt` and `.pdf` — text extracted automatically |
| 📊 **Interactive Visualizations** | Confidence ring, donut chart, probability bars, emotion explanation panel |
| 🔑 **Keyword Extraction** | Highlights the key words that drove the prediction |
| 🌙 **Dark / Light Mode** | Full theme toggle with proper background switching |

---

## 🏗️ Project Structure

```
EmotionLens/
├── app.py        # Streamlit UI
├── charts.py     # SVG visualizations
├── styles.py     # Theme + CSS injection
├── config.py     # Shared constants
└── backend.py    # Flask API
```

---

## ⚙️ Tech Stack

| Layer | Technology |
|---|---|
| **Model** | CNN with custom tokenizer — TensorFlow / Keras |
| **Dataset** | [GoEmotions](https://github.com/google-research/google-research/tree/master/goemotions) — 58k Reddit comments, 28 classes |
| **Backend** | Flask + Flask-CORS |
| **Frontend** | Streamlit with custom SVG charts |
| **File Parsing** | pypdf (PDF), built-in (TXT) |

---

## 🚀 Run Locally

### 1. Clone the repo

```bash
git clone https://github.com/your-username/EmotionLens.git
cd EmotionLens
```

### 2. Install dependencies

```bash
pip install tensorflow keras flask flask-cors streamlit numpy pypdf
```

### 3. Start the backend

```bash
python backend.py
# → Running on http://0.0.0.0:5001
```

### 4. Start the frontend

```bash
streamlit run app.py
# → Local URL: http://localhost:8501
```

---

## 📄 License

[MIT](LICENSE)
