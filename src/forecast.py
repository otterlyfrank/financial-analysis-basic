import pandas as pd

from src.classify import classify
from src.schema import CANONICAL, TxType, cash_sign


def _next_periods(last: str, n: int) -> list[str]:
    year, month = (int(p) for p in last.split("-"))
    out: list[str] = []
    for _ in range(n):
        month += 1
        if month == 13:
            month = 1
            year += 1
        out.append(f"{year:04d}-{month:02d}")
    return out


def _avg_by_subcategory(df: pd.DataFrame, periods: list[str], tx_type: TxType) -> pd.DataFrame:
    sub = df[df["type"] == tx_type]
    if sub.empty or not periods:
        return pd.DataFrame(columns=["category", "subcategory", "amount"])
    monthly = sub.groupby(["period", "category", "subcategory"], as_index=False)[
        "amount"
    ].sum()
    keys = monthly[["category", "subcategory"]].drop_duplicates()
    grid = keys.merge(pd.DataFrame({"period": periods}), how="cross")
    monthly = grid.merge(monthly, on=["period", "category", "subcategory"], how="left")
    monthly["amount"] = monthly["amount"].fillna(0)
    return monthly.groupby(["category", "subcategory"], as_index=False)["amount"].mean()


def _emit(period: str, tx_type: TxType, category: str, subcategory: str, amount: float) -> dict:
    return {
        "period": period,
        "type": str(tx_type),
        "category": category,
        "subcategory": subcategory,
        "amount": float(amount),
        "signed_amount": cash_sign(tx_type) * float(amount),
        "source": "forecast",
    }


def forecast(
    rows: pd.DataFrame,
    *,
    horizon: int = 3,
    scenario: str = "base",
    pct: float = 10.0,
    include_non_recurring: bool = False,
) -> pd.DataFrame:
    if rows.empty:
        return pd.DataFrame(columns=CANONICAL)
    window_periods = sorted(rows["period"].unique())[-3:]
    window = rows[rows["period"].isin(window_periods)]
    future = _next_periods(window_periods[-1], horizon)
    factor = {"base": 1.0, "up": 1 + pct / 100.0, "down": 1 - pct / 100.0}[scenario]
    emitted: list[dict] = []
    rec = _avg_by_subcategory(window, window_periods, TxType.EXPENSE_RECURRING)
    rev = _avg_by_subcategory(window, window_periods, TxType.REVENUE)
    rev["amount"] = rev["amount"] * factor
    parts = [(TxType.EXPENSE_RECURRING, rec), (TxType.REVENUE, rev)]
    if include_non_recurring:
        parts.append(
            (
                TxType.EXPENSE_NON_RECURRING,
                _avg_by_subcategory(window, window_periods, TxType.EXPENSE_NON_RECURRING),
            )
        )
    for tx_type, avg in parts:
        for _, row in avg.iterrows():
            if row["amount"] == 0:
                continue
            for period in future:
                emitted.append(
                    _emit(
                        period,
                        tx_type,
                        row["category"],
                        row["subcategory"],
                        row["amount"],
                    )
                )
    if not emitted:
        return pd.DataFrame(columns=CANONICAL)
    return classify(pd.DataFrame(emitted))
