#!/usr/bin/env python3
"""
scheduler.py
Runs the sentiment agent on a fixed interval (default: every 30 minutes).

Usage:
    python scheduler.py                    # run every 30 min
    python scheduler.py --interval 60      # run every 60 min
    python scheduler.py --interval 5 --save-json --save-markdown
"""

import argparse
import time
import subprocess
import sys
from datetime import datetime


def parse_args():
    p = argparse.ArgumentParser(description="Periodic Crypto Sentiment Scheduler")
    p.add_argument("--interval",      type=int, default=30,
                   help="Minutes between runs (default: 30)")
    p.add_argument("--save-json",     action="store_true")
    p.add_argument("--save-markdown", action="store_true")
    p.add_argument("--max",           type=int, default=10)
    return p.parse_args()


def run_agent(args):
    cmd = [sys.executable, "main.py", "--max", str(args.max)]
    if args.save_json:
        cmd.append("--save-json")
    if args.save_markdown:
        cmd.append("--save-markdown")
    print(f"\n[scheduler] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} — running agent …")
    subprocess.run(cmd, check=False)


def main():
    args  = parse_args()
    delay = args.interval * 60

    print(f"[scheduler] Starting. Will run every {args.interval} minute(s). Press Ctrl+C to stop.")
    while True:
        run_agent(args)
        print(f"[scheduler] Next run in {args.interval} minute(s) …")
        time.sleep(delay)


if __name__ == "__main__":
    main()
