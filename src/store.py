from pathlib import Path
import json

import duckdb
import pandas as pd

from src.schema import CANONICAL

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "cash.duckdb"
SETTINGS_PATH = ROOT / "settings.json"

DEFAULT_SETTINGS = {
    "opening_cash": 0.0,
    "scenario": "base",
    "pct": 10.0,
    "include_non_recurring": False,
    "source_name": "",
}


def connect() -> duckdb.DuckDBPyConnection:
    con = duckdb.connect(str(DB_PATH))
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS facts (
            period VARCHAR,
            type VARCHAR,
            category VARCHAR,
            subcategory VARCHAR,
            amount DOUBLE,
            signed_amount DOUBLE,
            bucket VARCHAR,
            source VARCHAR
        )
        """
    )
    return con


def replace_facts(df: pd.DataFrame) -> None:
    ordered = df[CANONICAL].copy()
    con = connect()
    con.execute("CREATE OR REPLACE TABLE facts AS SELECT * FROM ordered")
    con.close()


def read_facts() -> pd.DataFrame:
    con = connect()
    try:
        df = con.execute("SELECT * FROM facts").df()
    except Exception:
        df = pd.DataFrame(columns=CANONICAL)
    con.close()
    if df.empty:
        return pd.DataFrame(columns=CANONICAL)
    return df


def clear_facts() -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()


def load_settings() -> dict:
    if not SETTINGS_PATH.exists():
        return dict(DEFAULT_SETTINGS)
    try:
        data = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
    except Exception:
        return dict(DEFAULT_SETTINGS)
    out = dict(DEFAULT_SETTINGS)
    out.update({k: data[k] for k in DEFAULT_SETTINGS if k in data})
    return out


def save_settings(settings: dict) -> None:
    current = load_settings()
    current.update(settings)
    SETTINGS_PATH.write_text(json.dumps(current, indent=2), encoding="utf-8")
