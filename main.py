#!/usr/bin/env python3
"""
main.py – Crypto Sentiment Agent entry point

Usage:
    python main.py                          # print report to stdout
    python main.py --save-json              # also save report.json
    python main.py --save-markdown          # also save report.md
    python main.py --save-json --save-markdown --max 15
"""

import argparse
import sys

from agent.news_fetcher  import fetch_all_news
from agent.coin_detector import tag_articles
from agent.sentiment     import score_articles
from agent.reporter      import build_report, print_report, save_json, save_markdown


def parse_args():
    p = argparse.ArgumentParser(description="Crypto News Sentiment Agent")
    p.add_argument("--max",           type=int, default=10,
                   help="Max articles per feed (default: 10)")
    p.add_argument("--save-json",     action="store_true",
                   help="Save report as JSON (outputs/report.json)")
    p.add_argument("--save-markdown", action="store_true",
                   help="Save report as Markdown (outputs/report.md)")
    p.add_argument("--coins",         nargs="*",
                   help="Filter report to specific coin symbols, e.g. BTC ETH")
    return p.parse_args()


def main():
    args = parse_args()

    print("[agent] Fetching news …")
    articles = fetch_all_news(max_per_feed=args.max)
    print(f"[agent] Fetched {len(articles)} articles.")

    print("[agent] Detecting coin mentions …")
    articles = tag_articles(articles)

    print("[agent] Scoring sentiment …")
    articles = score_articles(articles)

    print("[agent] Building report …")
    report = build_report(articles)

    # optional coin filter
    if args.coins:
        filter_set = {c.upper() for c in args.coins}
        report["coins"] = {k: v for k, v in report["coins"].items() if k in filter_set}

    print_report(report)

    if args.save_json:
        save_json(report, path="outputs/report.json")

    if args.save_markdown:
        save_markdown(report, path="outputs/report.md")

    return 0


if __name__ == "__main__":
    sys.exit(main())
