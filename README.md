# Cash P&L

One-company local cash-P&L from a bank-transaction Excel dump. Python 3.12. Binds to 127.0.0.1.

Excel columns: `Month`, `Type`, `Category`, `Subcategory`, `Amount`. Amounts are positive; sign comes from Type.

## Run

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Open http://127.0.0.1:8501 and upload `sample.xlsx`.

## TODOs

- Intercompany in vs out (v1 treats Intercompany transfer as cash out)
- Recurring run-rate without zero-filling missing months
- Loan draw / repayment schedule in the forecast
- Seasonality on revenue instead of a flat %
- Opening cash by bank account
- Persist scenario runs in DuckDB
- Royalty vs true intercompany mapping
- Actual vs forecast variance table
