import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.cash import cash_walk
from src.classify import classify
from src.forecast import forecast
from src.ingest import ingest_excel
from src.pivot import month_cash, month_category, month_recurring
from src.schema import Bucket
from src.store import read_facts, replace_facts

st.set_page_config(page_title="Cash P&L", layout="wide")
st.title("Cash P&L")

uploaded = st.file_uploader("Bank dump (.xlsx)", type=["xlsx"])
if uploaded is not None:
    replace_facts(classify(ingest_excel(uploaded)))
    st.success("Loaded transactions")

facts = read_facts()
if facts.empty:
    st.info("Upload sample.xlsx")
    st.stop()

opening_cash = st.number_input("Opening cash", value=0.0, step=1000.0, format="%.2f")
scenario = st.radio("Revenue scenario", ["base", "up", "down"], horizontal=True)
pct = st.number_input("Up/down %", value=10.0, min_value=0.0, step=1.0)
include_nr = st.checkbox("Forecast non-recurring", value=False)

future = forecast(
    facts, scenario=scenario, pct=pct, include_non_recurring=include_nr
)
combined = pd.concat([facts, future], ignore_index=True)

st.subheader("Mapped rows")
st.dataframe(combined, width="stretch")

c1, c2, c3 = st.columns(3)
with c1:
    st.caption("Month × category (ops, signed)")
    st.dataframe(month_category(combined), width="stretch")
with c2:
    st.caption("Recurring vs non-recurring")
    st.dataframe(month_recurring(combined), width="stretch")
with c3:
    st.caption("Cash in vs out")
    st.dataframe(month_cash(combined), width="stretch")

walk = cash_walk(combined, opening_cash)
st.subheader("Cash walk")
st.dataframe(walk, width="stretch")

ops = combined[combined["bucket"] == Bucket.OPERATING]
ops_in = ops.loc[ops["signed_amount"] > 0].groupby("period")["signed_amount"].sum()
ops_out = (
    ops.loc[ops["signed_amount"] < 0].groupby("period")["signed_amount"].sum().abs()
)
ops_chart = (
    pd.DataFrame({"ops_in": ops_in, "ops_out": ops_out})
    .fillna(0)
    .reset_index()
    .melt(id_vars="period", value_vars=["ops_in", "ops_out"], var_name="flow", value_name="amount")
)
fig_ops = px.bar(
    ops_chart,
    x="period",
    y="amount",
    color="flow",
    barmode="group",
    title="Monthly operating cash in / out",
)
st.plotly_chart(fig_ops, width="stretch")

if walk.empty:
    st.stop()
fig_walk = go.Figure(
    go.Waterfall(
        x=["Opening", *walk["period"].tolist(), "Closing"],
        measure=["absolute", *["relative"] * len(walk), "total"],
        y=[opening_cash, *walk["net"].tolist(), 0],
        name="cash",
    )
)
fig_walk.update_layout(title="Cash walk")
st.plotly_chart(fig_walk, width="stretch")
