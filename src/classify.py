import pandas as pd

from src.schema import CANONICAL, Bucket, TxType

_TYPE_BUCKET = {
    TxType.REVENUE: Bucket.OPERATING,
    TxType.EXPENSE_RECURRING: Bucket.OPERATING,
    TxType.EXPENSE_NON_RECURRING: Bucket.OPERATING,
    TxType.LOANS_IN: Bucket.FINANCING,
    TxType.LOANS_OUT: Bucket.FINANCING,
    TxType.INTERCOMPANY: Bucket.INTERCOMPANY,
}


def classify(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=CANONICAL)
    out = df.copy()
    out["bucket"] = [str(_TYPE_BUCKET[TxType(t)]) for t in out["type"]]
    return out[CANONICAL].reset_index(drop=True)
