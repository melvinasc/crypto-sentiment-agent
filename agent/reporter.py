"""
reporter.py
Aggregates scored articles into a per-coin sentiment report.
Outputs to stdout and optionally saves JSON / Markdown.
"""

import json
import os
from collections import defaultdict
from datetime import datetime, timezone
from typing import Dict, List

from agent.coin_detector import COIN_KEYWORDS

# All unique coin symbols we want to always show
ALL_COINS = sorted(set(COIN_KEYWORDS.values()))


def build_report(articles: List[Dict]) -> Dict:
    coin_buckets: Dict[str, List[Dict]] = defaultdict(list)
    uncategorised: List[Dict] = []

    for article in articles:
        coins = article.get("coins", [])
        if coins:
            for coin in coins:
                coin_buckets[coin].append(article)
        else:
            uncategorised.append(article)

    coins_summary = {}

    # Always include ALL coins, even those with no news
    for coin in ALL_COINS:
        arts = coin_buckets.get(coin, [])
        if arts:
            compounds = [a["compound"] for a in arts]
            avg       = round(sum(compounds) / len(compounds), 4)
            coins_summary[coin] = {
                "article_count": len(arts),
                "avg_compound":  avg,
                "overall":       _label(avg),
                "bullish":       sum(1 for a in arts if a["label"] == "BULLISH"),
                "bearish":       sum(1 for a in arts if a["label"] == "BEARISH"),
                "neutral":       sum(1 for a in arts if a["label"] == "NEUTRAL"),
                "top_articles":  _top(arts, n=3),
                "no_news":       False,
            }
        else:
            # No news today — show coin with neutral defaults
            coins_summary[coin] = {
                "article_count": 0,
                "avg_compound":  0.0,
                "overall":       "NEUTRAL",
                "bullish":       0,
                "bearish":       0,
                "neutral":       0,
                "top_articles":  [],
                "no_news":       True,
            }

    # Sort: coins with news first (by |compound|), then no-news coins alphabetically
    def sort_key(item):
        symbol, data = item
        if data["no_news"]:
            return (1, symbol)
        return (0, -abs(data["avg_compound"]))

    return {
        "generated_at":   datetime.now(timezone.utc).isoformat(),
        "total_articles": len(articles),
        "coins":          dict(sorted(coins_summary.items(), key=sort_key)),
        "uncategorised":  uncategorised,
    }


def print_report(report: Dict) -> None:
    bar = "=" * 60
    print(f"\n{bar}")
    print(f"  🪙  Crypto Sentiment Report")
    print(f"  Generated: {report['generated_at']}")
    print(f"  Articles analysed: {report['total_articles']}")
    print(bar)

    for coin, data in report["coins"].items():
        if data["no_news"]:
            print(f"\n⚪  {coin}  —  NO NEWS TODAY")
            continue
        emoji = {"BULLISH": "🟢", "BEARISH": "🔴", "NEUTRAL": "⚪"}.get(data["overall"], "❓")
        print(f"\n{emoji}  {coin}  —  {data['overall']}  (avg score: {data['avg_compound']:+.3f})")
        print(f"   Articles: {data['article_count']}  |  "
              f"🟢 {data['bullish']}  🔴 {data['bearish']}  ⚪ {data['neutral']}")
        print("   Top headlines:")
        for art in data["top_articles"]:
            tag = {"BULLISH": "↑", "BEARISH": "↓", "NEUTRAL": "~"}.get(art["label"], "?")
            print(f"     [{tag}] {art['title'][:90]}")
            print(f"         {art['url']}")

    print(f"\n{bar}\n")


def save_json(report: Dict, path: str = "report.json") -> None:
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    with open(path, "w") as f:
        json.dump(report, f, indent=2, default=str)
    print(f"[reporter] JSON saved → {path}")


def save_markdown(report: Dict, path: str = "report.md") -> None:
    lines = [
        f"# Crypto Sentiment Report",
        f"",
        f"**Generated:** {report['generated_at']}  ",
        f"**Articles analysed:** {report['total_articles']}",
        f"",
        f"---",
        f"",
    ]
    for coin, data in report["coins"].items():
        if data["no_news"]:
            lines += [f"## ⚪ {coin} — No News Today", f""]
            continue
        emoji = {"BULLISH": "🟢", "BEARISH": "🔴", "NEUTRAL": "⚪"}.get(data["overall"], "❓")
        lines += [
            f"## {emoji} {coin} — {data['overall']}",
            f"",
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| Avg sentiment score | `{data['avg_compound']:+.3f}` |",
            f"| Articles | {data['article_count']} |",
            f"| 🟢 Buy Signal | {data['bullish']} |",
            f"| 🔴 Sell Signal | {data['bearish']} |",
            f"| ⚪ Hold | {data['neutral']} |",
            f"",
            f"**Top headlines:**",
            f"",
        ]
        for art in data["top_articles"]:
            tag = {"BULLISH": "↑", "BEARISH": "↓", "NEUTRAL": "~"}.get(art["label"], "?")
            lines.append(f"- [{tag}] [{art['title']}]({art['url']})")
        lines.append("")

    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    with open(path, "w") as f:
        f.write("\n".join(lines))
    print(f"[reporter] Markdown saved → {path}")


# ── helpers ────────────────────────────────────────────────────────────────────

def _label(compound: float) -> str:
    if compound >= 0.05:  return "BULLISH"
    if compound <= -0.05: return "BEARISH"
    return "NEUTRAL"


def _top(articles: List[Dict], n: int = 3) -> List[Dict]:
    return sorted(articles, key=lambda x: abs(x["compound"]), reverse=True)[:n]
