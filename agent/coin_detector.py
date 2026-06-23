"""
coin_detector.py
Detects cryptocurrency mentions in article text using a keyword map.
Extend COIN_KEYWORDS to add more coins / tickers.
"""

import re
from typing import Dict, List

# name/ticker → canonical symbol
COIN_KEYWORDS: Dict[str, str] = {
    "bitcoin":   "BTC", "btc": "BTC",
    "ethereum":  "ETH", "eth": "ETH", "ether": "ETH",
    "solana":    "SOL", "sol": "SOL",
    "binance":   "BNB", "bnb": "BNB",
    "ripple":    "XRP", "xrp": "XRP",
    "cardano":   "ADA", "ada": "ADA",
    "dogecoin":  "DOGE", "doge": "DOGE",
    "polkadot":  "DOT", "dot": "DOT",
    "avalanche": "AVAX", "avax": "AVAX",
    "chainlink": "LINK", "link": "LINK",
    "polygon":   "MATIC", "matic": "MATIC",
    "uniswap":   "UNI", "uni": "UNI",
    "litecoin":  "LTC", "ltc": "LTC",
    "shiba":     "SHIB", "shib": "SHIB",
    "pepe":      "PEPE",
    "tron":      "TRX",  "trx": "TRX",
    "tether":    "USDT", "usdt": "USDT",
    "usdc":      "USDC",
    "dai":       "DAI",
}

_PATTERN = re.compile(
    r"\b(" + "|".join(re.escape(k) for k in COIN_KEYWORDS) + r")\b",
    re.IGNORECASE,
)


def detect_coins(article: Dict) -> List[str]:
    """Return a deduplicated list of coin symbols found in title + summary."""
    text = f"{article.get('title', '')} {article.get('summary', '')}".lower()
    found = _PATTERN.findall(text)
    symbols = list(dict.fromkeys(COIN_KEYWORDS[m.lower()] for m in found))
    return symbols


def tag_articles(articles: List[Dict]) -> List[Dict]:
    """Add a 'coins' key to each article."""
    for article in articles:
        article["coins"] = detect_coins(article)
    return articles
