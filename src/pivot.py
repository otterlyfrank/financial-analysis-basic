import pandas as pd

from src.schema import Bucket, TxType


def month_category(df: pd.DataFrame) -> pd.DataFrame:
    ops = df[df["bucket"] == Bucket.OPERATING]
    if ops.empty:
        return pd.DataFrame(columns=["period"])
    return (
        ops.pivot_table(
            index="period",
            columns="category",
            values="signed_amount",
            aggfunc="sum",
            fill_value=0,
        )
        .reset_index()
        .rename_axis(None, axis=1)
        .sort_values("period")
        .reset_index(drop=True)
    )


def month_recurring(df: pd.DataFrame) -> pd.DataFrame:
    labels = {
        TxType.EXPENSE_RECURRING: "recurring",
        TxType.EXPENSE_NON_RECURRING: "non_recurring",
    }
    exp = df[df["type"].isin(labels)]
    if exp.empty:
        return pd.DataFrame(columns=["period", "recurring", "non_recurring"])
    tmp = exp.copy()
    tmp["recurrence"] = [labels[TxType(t)] for t in tmp["type"]]
    out = tmp.pivot_table(
        index="period",
        columns="recurrence",
        values="amount",
        aggfunc="sum",
        fill_value=0,
    ).reset_index()
    for col in ["recurring", "non_recurring"]:
        if col not in out.columns:
            out[col] = 0
    return out[["period", "recurring", "non_recurring"]].sort_values("period").reset_index(drop=True)


def month_cash(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["period", "cash_in", "cash_out"])
    tmp = df.copy()
    tmp["cash_in"] = tmp["signed_amount"].clip(lower=0)
    tmp["cash_out"] = (-tmp["signed_amount"]).clip(lower=0)
    return (
        tmp.groupby("period", as_index=False)[["cash_in", "cash_out"]]
        .sum()
        .sort_values("period")
        .reset_index(drop=True)
    )
