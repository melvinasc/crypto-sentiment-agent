"""
sentiment.py
Scores news articles for sentiment using VADER (no API key required).
Optionally upgrades to a transformer model when USE_TRANSFORMER=true.
"""

import os
from typing import Dict, List

# ── VADER (default, zero-dependency) ──────────────────────────────────────────
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

_vader = SentimentIntensityAnalyzer()

# ── optional transformer ───────────────────────────────────────────────────────
USE_TRANSFORMER = os.getenv("USE_TRANSFORMER", "false").lower() == "true"
_transformer_pipeline = None

if USE_TRANSFORMER:
    try:
        from transformers import pipeline as hf_pipeline
        _transformer_pipeline = hf_pipeline(
            "text-classification",
            model="ProsusAI/finbert",   # finance-tuned BERT
            truncation=True,
            max_length=512,
        )
        print("[sentiment] Using FinBERT transformer model.")
    except ImportError:
        print("[sentiment] transformers not installed – falling back to VADER.")


# ── public API ─────────────────────────────────────────────────────────────────

def score_article(article: Dict) -> Dict:
    """
    Add sentiment fields to a single article dict and return it.

    Added keys:
        compound   : float in [-1, 1]  (VADER compound or mapped FinBERT score)
        label      : "BULLISH" | "BEARISH" | "NEUTRAL"
        confidence : float in [0, 1]
    """
    text = f"{article.get('title', '')} {article.get('summary', '')}".strip()

    if _transformer_pipeline:
        result     = _transformer_pipeline(text)[0]
        raw_label  = result["label"].upper()   # POSITIVE / NEGATIVE / NEUTRAL
        confidence = round(result["score"], 4)
        label_map  = {"POSITIVE": "BULLISH", "NEGATIVE": "BEARISH", "NEUTRAL": "NEUTRAL"}
        label      = label_map.get(raw_label, "NEUTRAL")
        # map confidence to [-1, 1] compound-style score
        compound   = confidence if label == "BULLISH" else (-confidence if label == "BEARISH" else 0.0)
    else:
        scores     = _vader.polarity_scores(text)
        compound   = round(scores["compound"], 4)
        confidence = round(abs(compound), 4)
        label      = _vader_label(compound)

    return {**article, "compound": compound, "label": label, "confidence": confidence}


def score_articles(articles: List[Dict]) -> List[Dict]:
    """Score a list of articles; returns them sorted by |compound| descending."""
    scored = [score_article(a) for a in articles]
    return sorted(scored, key=lambda x: abs(x["compound"]), reverse=True)


# ── helpers ────────────────────────────────────────────────────────────────────

def _vader_label(compound: float) -> str:
    if compound >= 0.05:
        return "BULLISH"
    if compound <= -0.05:
        return "BEARISH"
    return "NEUTRAL"
