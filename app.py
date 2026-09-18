from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.cash import cash_walk
from src.classify import classify
from src.export import workbook_bytes
from src.forecast import forecast
from src.ingest import ingest_excel
from src.pivot import month_cash, month_category, month_recurring
from src.schema import Bucket
from src.store import (
    clear_facts,
    load_settings,
    read_facts,
    save_settings,
    replace_facts,
)

ROOT = Path(__file__).resolve().parent


def show_df(df: pd.DataFrame) -> None:
    try:
        st.dataframe(df, use_container_width=True)
    except TypeError:
        st.dataframe(df)


def show_chart(fig) -> None:
    try:
        st.plotly_chart(fig, use_container_width=True)
    except TypeError:
        st.plotly_chart(fig)


st.set_page_config(page_title="Cash P&L", layout="wide")
st.title("Cash P&L")

saved = load_settings()
if "opening_cash" not in st.session_state:
    st.session_state.opening_cash = float(saved["opening_cash"])
if "scenario" not in st.session_state:
    st.session_state.scenario = saved["scenario"]
if "pct" not in st.session_state:
    st.session_state.pct = float(saved["pct"])
if "include_nr" not in st.session_state:
    st.session_state.include_nr = bool(saved["include_non_recurring"])

with st.sidebar:
    st.subheader("Assumptions")
    st.number_input(
        "Opening cash",
        min_value=0.0,
        step=1.0,
        format="%.2f",
        key="opening_cash",
        help="Type the bank balance at the start of the first month.",
    )
    st.radio("Revenue scenario", ["base", "up", "down"], key="scenario")
    st.number_input("Up/down %", min_value=0.0, step=1.0, format="%.1f", key="pct")
    st.checkbox("Forecast non-recurring", key="include_nr")
    if st.button("Clear saved work"):
        clear_facts()
        save_settings(
            {
                "opening_cash": 0.0,
                "scenario": "base",
                "pct": 10.0,
                "include_non_recurring": False,
                "source_name": "",
            }
        )
        for k in ("opening_cash", "scenario", "pct", "include_nr"):
            if k in st.session_state:
                del st.session_state[k]
        st.rerun()

uploaded = st.file_uploader("Bank dump (.xlsx)", type=["xlsx"])
load_error = None
if uploaded is not None:
    try:
        replace_facts(classify(ingest_excel(uploaded)))
        save_settings({"source_name": uploaded.name})
        st.success(f"Loaded {uploaded.name}")
    except Exception as exc:
        load_error = str(exc)
        st.error(f"Could not read that file: {load_error}")

try:
    facts = read_facts()
except Exception as exc:
    st.error(f"Could not read saved transactions: {exc}")
    facts = pd.DataFrame()

if load_error is None and facts.empty:
    sample = ROOT / "sample.xlsx"
    st.info("Upload your bank workbook, or load the sample to test the screen.")
    if sample.exists() and st.button("Load sample.xlsx"):
        replace_facts(classify(ingest_excel(sample)))
        save_settings({"source_name": "sample.xlsx"})
        st.rerun()
    st.stop()

if facts.empty:
    st.stop()

opening_cash = float(st.session_state.opening_cash)
scenario = st.session_state.scenario
pct = float(st.session_state.pct)
include_nr = bool(st.session_state.include_nr)
save_settings(
    {
        "opening_cash": opening_cash,
        "scenario": scenario,
        "pct": pct,
        "include_non_recurring": include_nr,
    }
)

future = forecast(
    facts, scenario=scenario, pct=pct, include_non_recurring=include_nr
)
combined = pd.concat([facts, future], ignore_index=True)
cat_tbl = month_category(combined)
rec_tbl = month_recurring(combined)
cash_tbl = month_cash(combined)
walk = cash_walk(combined, opening_cash)

source = load_settings().get("source_name") or "saved workbook"
st.caption(f"Using {source} · {len(facts)} actual rows · {len(future)} forecast rows")

xlsx = workbook_bytes(
    {
        "mapped_rows": combined,
        "month_category": cat_tbl,
        "recurring": rec_tbl,
        "cash_in_out": cash_tbl,
        "cash_walk": walk,
    }
)
st.download_button(
    "Download Excel report",
    data=xlsx,
    file_name="cash_pnl_report.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)

st.subheader("Mapped rows")
show_df(combined)

c1, c2, c3 = st.columns(3)
with c1:
    st.caption("Month × category (ops, signed)")
    show_df(cat_tbl)
with c2:
    st.caption("Recurring vs non-recurring")
    show_df(rec_tbl)
with c3:
    st.caption("Cash in vs out")
    show_df(cash_tbl)

st.subheader("Cash walk")
show_df(walk)

ops = combined[combined["bucket"] == Bucket.OPERATING]
if ops.empty:
    st.warning("No operating rows to chart.")
else:
    ops_in = ops.loc[ops["signed_amount"] > 0].groupby("period")["signed_amount"].sum()
    ops_out = (
        ops.loc[ops["signed_amount"] < 0].groupby("period")["signed_amount"].sum().abs()
    )
    ops_chart = (
        pd.DataFrame({"ops_in": ops_in, "ops_out": ops_out})
        .fillna(0)
        .reset_index()
        .rename(columns={"index": "period"})
    )
    if "period" not in ops_chart.columns:
        ops_chart = ops_chart.rename(columns={ops_chart.columns[0]: "period"})
    ops_chart = ops_chart.melt(
        id_vars="period",
        value_vars=[c for c in ("ops_in", "ops_out") if c in ops_chart.columns],
        var_name="flow",
        value_name="amount",
    )
    fig_ops = px.bar(
        ops_chart,
        x="period",
        y="amount",
        color="flow",
        barmode="group",
        title="Monthly operating cash in / out",
    )
    show_chart(fig_ops)

if not walk.empty:
    fig_walk = go.Figure(
        go.Waterfall(
            x=["Opening", *walk["period"].tolist(), "Closing"],
            measure=["absolute", *["relative"] * len(walk), "total"],
            y=[opening_cash, *walk["net"].tolist(), 0],
            name="cash",
        )
    )
    fig_walk.update_layout(title="Cash walk")
    show_chart(fig_walk)
