# 🪙 Crypto Sentiment Agent

A Python AI agent that fetches crypto news from multiple sources, detects coin mentions, scores sentiment, and generates human-readable reports — automatically, on a schedule.

---

## Features

| Feature | Details |
|---|---|
| **News sources** | CoinDesk, Decrypt, CryptoPanic, The Block, Bitcoin Magazine, CoinGecko |
| **Sentiment engine** | VADER (default, no API key) · FinBERT transformer (optional) |
| **Coin detection** | 20+ coins/tickers auto-detected per article |
| **Output formats** | Stdout · JSON · Markdown |
| **Automation** | GitHub Actions (every 6 h) · local scheduler script |

---

## Quickstart

```bash
# 1. Clone
git clone https://github.com/YOUR_USERNAME/crypto-sentiment-agent.git
cd crypto-sentiment-agent

# 2. Install
pip install -r requirements.txt

# 3. Run
python main.py
```

### Save a report

```bash
python main.py --save-json --save-markdown
# outputs saved to outputs/report.json and outputs/report.md
```

### Filter to specific coins

```bash
python main.py --coins BTC ETH SOL
```

### Run on a schedule (local)

```bash
python scheduler.py --interval 30 --save-json --save-markdown
```

---

## Optional: Upgrade to FinBERT (transformer model)

For higher-quality financial sentiment analysis:

```bash
pip install transformers torch
USE_TRANSFORMER=true python main.py
```

---

## GitHub Actions

The workflow at `.github/workflows/sentiment.yml` runs automatically every 6 hours and uploads the report as a build artefact.

To enable it, push the repo to GitHub — no secrets required for the default setup.

---

## Project structure

```
crypto-sentiment-agent/
├── agent/
│   ├── news_fetcher.py    # RSS + CoinGecko news fetching
│   ├── coin_detector.py   # Coin/ticker mention detection
│   ├── sentiment.py       # VADER / FinBERT scoring
│   └── reporter.py        # Report builder (stdout / JSON / Markdown)
├── tests/
│   └── test_sentiment.py  # Unit tests (pytest)
├── .github/workflows/
│   └── sentiment.yml      # Scheduled GitHub Actions workflow
├── main.py                # CLI entry point
├── scheduler.py           # Local periodic scheduler
├── requirements.txt
└── README.md
```

---

## Extending the agent

- **Add more coins** → edit `COIN_KEYWORDS` in `agent/coin_detector.py`
- **Add more RSS feeds** → edit `RSS_FEEDS` in `agent/news_fetcher.py`
- **Post to Slack/Discord** → add a notifier module and call it from `main.py`
- **Store history in SQLite** → replace `outputs/` with a simple DB writer

---

## Running tests

```bash
pip install pytest
pytest tests/ -v
```

---

## License

MIT
