"""
config.py — Shared constants for EmotionLens.
"""

API_URL = "http://127.0.0.1:5001/predict"

EMOTION_META = {
    "admiration":    {"emoji": "🤩", "color": "#F59E0B"},
    "amusement":     {"emoji": "😄", "color": "#10B981"},
    "anger":         {"emoji": "😠", "color": "#EF4444"},
    "annoyance":     {"emoji": "😒", "color": "#F97316"},
    "approval":      {"emoji": "👍", "color": "#22C55E"},
    "caring":        {"emoji": "🤗", "color": "#EC4899"},
    "confusion":     {"emoji": "😕", "color": "#8B5CF6"},
    "curiosity":     {"emoji": "🤔", "color": "#06B6D4"},
    "desire":        {"emoji": "😍", "color": "#F43F5E"},
    "disappointment":{"emoji": "😞", "color": "#6B7280"},
    "disapproval":   {"emoji": "👎", "color": "#DC2626"},
    "disgust":       {"emoji": "🤢", "color": "#65A30D"},
    "embarrassment": {"emoji": "😳", "color": "#FB7185"},
    "excitement":    {"emoji": "🎉", "color": "#F59E0B"},
    "fear":          {"emoji": "😨", "color": "#7C3AED"},
    "gratitude":     {"emoji": "🙏", "color": "#34D399"},
    "grief":         {"emoji": "😢", "color": "#475569"},
    "joy":           {"emoji": "😊", "color": "#FBBF24"},
    "love":          {"emoji": "❤️",  "color": "#F43F5E"},
    "nervousness":   {"emoji": "😬", "color": "#A78BFA"},
    "optimism":      {"emoji": "🌟", "color": "#FCD34D"},
    "pride":         {"emoji": "😤", "color": "#60A5FA"},
    "realization":   {"emoji": "💡", "color": "#34D399"},
    "relief":        {"emoji": "😌", "color": "#6EE7B7"},
    "remorse":       {"emoji": "😔", "color": "#94A3B8"},
    "sadness":       {"emoji": "😭", "color": "#60A5FA"},
    "surprise":      {"emoji": "😲", "color": "#F97316"},
    "neutral":       {"emoji": "😐", "color": "#9CA3AF"},
}

EMOTION_GROUPS = {
    "Positive":  ["admiration","amusement","approval","caring","excitement","gratitude",
                  "joy","love","optimism","pride","realization","relief"],
    "Negative":  ["anger","annoyance","disappointment","disapproval","disgust",
                  "embarrassment","fear","grief","nervousness","remorse","sadness"],
    "Ambiguous": ["confusion","curiosity","desire","surprise","neutral"],
}