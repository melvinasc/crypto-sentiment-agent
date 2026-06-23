"""Unit tests – no network calls required."""

from agent.sentiment     import score_article, _vader_label
from agent.coin_detector import detect_coins


# ── sentiment ──────────────────────────────────────────────────────────────────

def test_bullish_headline():
    article = {"title": "Bitcoin surges to new all-time high as institutional buyers pile in",
                "summary": ""}
    result = score_article(article)
    assert result["label"] == "BULLISH"
    assert result["compound"] > 0


def test_bearish_headline():
    article = {"title": "Crypto market crashes as regulators impose harsh crackdown",
                "summary": ""}
    result = score_article(article)
    assert result["label"] == "BEARISH"
    assert result["compound"] < 0


def test_neutral_headline():
    article = {"title": "Ethereum developers publish updated EIP roadmap",
                "summary": ""}
    result = score_article(article)
    assert result["label"] in ("NEUTRAL", "BULLISH", "BEARISH")   # just doesn't crash


def test_label_thresholds():
    assert _vader_label(0.5)  == "BULLISH"
    assert _vader_label(-0.5) == "BEARISH"
    assert _vader_label(0.0)  == "NEUTRAL"


# ── coin detector ──────────────────────────────────────────────────────────────

def test_detect_bitcoin():
    art = {"title": "Bitcoin hits $100k", "summary": "BTC rally continues"}
    assert "BTC" in detect_coins(art)


def test_detect_multiple_coins():
    art = {"title": "ETH and SOL both outperform the market",
            "summary": "Ethereum and Solana lead the charge"}
    coins = detect_coins(art)
    assert "ETH" in coins
    assert "SOL" in coins


def test_no_coins():
    art = {"title": "Federal Reserve raises interest rates again", "summary": ""}
    assert detect_coins(art) == []
