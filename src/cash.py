import pandas as pd

from src.schema import Bucket


def cash_walk(rows: pd.DataFrame, opening_cash: float) -> pd.DataFrame:
    if rows.empty:
        return pd.DataFrame(
            columns=[
                "period",
                "opening",
                "ops_in",
                "ops_out",
                "fin_in",
                "fin_out",
                "ic_out",
                "net",
                "closing",
            ]
        )
    tmp = rows.copy()
    ops = tmp["bucket"] == Bucket.OPERATING
    fin = tmp["bucket"] == Bucket.FINANCING
    ic = tmp["bucket"] == Bucket.INTERCOMPANY
    tmp["ops_in"] = tmp["signed_amount"].where(ops & (tmp["signed_amount"] > 0), 0)
    tmp["ops_out"] = (-tmp["signed_amount"]).where(ops & (tmp["signed_amount"] < 0), 0)
    tmp["fin_in"] = tmp["signed_amount"].where(fin & (tmp["signed_amount"] > 0), 0)
    tmp["fin_out"] = (-tmp["signed_amount"]).where(fin & (tmp["signed_amount"] < 0), 0)
    tmp["ic_out"] = tmp["amount"].where(ic, 0)
    monthly = (
        tmp.groupby("period", as_index=False)[
            ["ops_in", "ops_out", "fin_in", "fin_out", "ic_out"]
        ]
        .sum()
        .sort_values("period")
        .reset_index(drop=True)
    )
    monthly["net"] = (
        monthly["ops_in"]
        - monthly["ops_out"]
        + monthly["fin_in"]
        - monthly["fin_out"]
        - monthly["ic_out"]
    )
    openings: list[float] = []
    closings: list[float] = []
    opening = float(opening_cash)
    for net in monthly["net"]:
        openings.append(opening)
        opening = opening + float(net)
        closings.append(opening)
    monthly.insert(1, "opening", openings)
    monthly["closing"] = closings
    return monthly
