#!/usr/bin/env python3
"""Refresh sp500/constituents.csv from Wikipedia's "List of S&P 500 companies".

The de-facto public source of S&P 500 membership (Massive/Polygon only expose
per-ticker aggregates, not index membership). Output columns: Symbol, Security,
GICS Sector, GICS Sub-Industry — sorted by Symbol for stable diffs. `Symbol` is
the index key crowdsource competitions predict against.
"""
import io
import os

import pandas as pd
import requests

URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
COLS = ["Symbol", "Security", "GICS Sector", "GICS Sub-Industry"]
OUT = os.path.join(os.path.dirname(__file__), "..", "sp500", "constituents.csv")


def main() -> None:
    resp = requests.get(
        URL,
        headers={"User-Agent": "crowdsource-datasets/1.0 (+https://crowdsource.sh)"},
        timeout=30,
    )
    resp.raise_for_status()
    tables = pd.read_html(io.StringIO(resp.text))
    # The constituents table is the one carrying Symbol + Security columns.
    df = next(t for t in tables if {"Symbol", "Security"}.issubset(t.columns))
    df = df[COLS].copy()
    for c in COLS:
        df[c] = df[c].astype(str).str.strip()
    df = df.sort_values("Symbol").drop_duplicates("Symbol").reset_index(drop=True)
    if len(df) < 400:
        raise SystemExit(f"refusing to write only {len(df)} rows (parse likely broke)")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    df.to_csv(OUT, index=False, lineterminator="\n")
    print(f"wrote {len(df)} constituents to {os.path.normpath(OUT)}")


if __name__ == "__main__":
    main()
