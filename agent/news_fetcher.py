"""
news_fetcher.py
Fetches crypto news from free public RSS feeds and the CoinGecko news API.
"""

import feedparser
import requests
from datetime import datetime, timezone
from typing import List, Dict

RSS_FEEDS = {
    "CoinDesk":       "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "CryptoPanic":    "https://cryptopanic.com/news/rss/",
    "Decrypt":        "https://decrypt.co/feed",
    "TheBlock":       "https://www.theblock.co/rss.xml",
    "Bitcoin Magazine":"https://bitcoinmagazine.com/.rss/full/",
}

COINGECKO_NEWS_URL = "https://api.coingecko.com/api/v3/news"

HEADERS = {"User-Agent": "CryptoSentimentAgent/1.0"}


def fetch_rss_news(max_per_feed: int = 10) -> List[Dict]:
    """Parse all configured RSS feeds and return a flat list of articles."""
    articles = []
    for source, url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:max_per_feed]:
                articles.append({
                    "source": source,
                    "title": entry.get("title", "").strip(),
                    "summary": entry.get("summary", "").strip(),
                    "url": entry.get("link", ""),
                    "published": _parse_date(entry),
                })
        except Exception as exc:
            print(f"[news_fetcher] Error fetching {source}: {exc}")
    return articles


def fetch_coingecko_news(max_articles: int = 20) -> List[Dict]:
    """Fetch news from CoinGecko's public news endpoint (no API key needed)."""
    articles = []
    try:
        resp = requests.get(COINGECKO_NEWS_URL, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        data = resp.json().get("data", [])
        for item in data[:max_articles]:
            articles.append({
                "source": "CoinGecko",
                "title": item.get("title", "").strip(),
                "summary": item.get("description", "").strip(),
                "url": item.get("url", ""),
                "published": item.get("created_at", ""),
            })
    except Exception as exc:
        print(f"[news_fetcher] CoinGecko news error: {exc}")
    return articles


def fetch_all_news(max_per_feed: int = 10) -> List[Dict]:
    """Aggregate articles from all sources, deduplicated by title."""
    rss = fetch_rss_news(max_per_feed)
    cg  = fetch_coingecko_news(max_per_feed)
    combined = rss + cg

    # Deduplicate by lowercased title
    seen, unique = set(), []
    for article in combined:
        key = article["title"].lower()
        if key not in seen:
            seen.add(key)
            unique.append(article)
    return unique


# ── helpers ────────────────────────────────────────────────────────────────────

def _parse_date(entry) -> str:
    try:
        t = entry.get("published_parsed")
        if t:
            return datetime(*t[:6], tzinfo=timezone.utc).isoformat()
    except Exception:
        pass
    return datetime.now(timezone.utc).isoformat()
