import re

import pandas as pd

from src.schema import EXCEL_COLS, cash_sign

_PERIOD = re.compile(r"^\d{4}-\d{2}$")


def parse_period(value) -> str:
    if pd.isna(value):
        raise ValueError("blank Month")
    if hasattr(value, "strftime"):
        return value.strftime("%Y-%m")
    text = str(value).strip()
    if _PERIOD.fullmatch(text):
        return text
    parsed = pd.to_datetime(text, errors="coerce")
    if pd.isna(parsed):
        raise ValueError(f"bad Month: {value!r}")
    return parsed.strftime("%Y-%m")


def ingest_excel(source) -> pd.DataFrame:
    raw = pd.read_excel(source, engine="openpyxl")
    raw.columns = [str(c).strip() for c in raw.columns]
    missing = [c for c in EXCEL_COLS if c not in raw.columns]
    if missing:
        raise ValueError(f"missing columns: {missing}")
    rows = pd.DataFrame(
        {
            "period": [parse_period(v) for v in raw["Month"]],
            "type": raw["Type"].astype(str).str.strip(),
            "category": raw["Category"].astype(str).str.strip(),
            "subcategory": raw["Subcategory"].fillna("").astype(str).str.strip(),
            "amount": pd.to_numeric(raw["Amount"], errors="coerce").abs(),
        }
    )
    rows = rows.dropna(subset=["amount"])
    rows["signed_amount"] = [
        cash_sign(t) * a for t, a in zip(rows["type"], rows["amount"])
    ]
    rows["source"] = "actual"
    return rows.reset_index(drop=True)
