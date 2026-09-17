# financial-analysis-basic

Local cash P&L and a short cash forecast from a bank-transaction Excel dump.

One company. No cloud. No login. Data stays on the machine that runs the app.

Repo: [otterlyfrank/financial-analysis-basic](https://github.com/otterlyfrank/financial-analysis-basic)

## What it does

Upload the transaction sheet you already keep. The app rebuilds the monthly pivot, splits operating cash from loans and intercompany, then projects the next three months.

**Charts**
- Monthly operating cash in vs cash out
- Cash walk from opening cash through each month’s net

**Tables (the report)**
- Mapped transaction rows
- Month × category (operating, signed)
- Recurring vs non-recurring by month
- Cash in vs cash out by month
- Cash walk (opening → net → closing)

This is a cash ledger tool, not an accrual 3-statement model. There is no balance sheet.

## Who it is for

A CEO or bookkeeper who already codes bank lines into Excel as:

| Month | Type | Category | Subcategory | Amount |
|---|---|---|---|---|

Amounts are **positive**. Direction comes from `Type`.

### `Type` values (exact spelling)

| Type | Treated as |
|---|---|
| `Revenue` | Operating cash in |
| `Expense recurring` | Operating cash out; forecast uses last-3-month average by subcategory |
| `Expense non-recurring` | Operating cash out; **not** forecast unless you tick the box |
| `Loans - in` | Financing in (history only in v1) |
| `Loans - out` | Financing out (history only in v1) |
| `Intercompany transfer` | Related-party; v1 signs it as cash out and keeps it off the operating charts |

### `Category` examples

Payroll, G&A, COGS, Occupancy costs, royalty — plus any subcategory under those.

## Install — macOS app

This is the path for a non-technical user. Build the `.app` on a Mac first (see **Package the Mac app** below).

### Run the app

1. Install Python 3.12 from [python.org](https://www.python.org/downloads/) once. On the installer, tick **Add Python to PATH**.
2. Get a copy of this repo (clone or Code → Download ZIP) and keep the folder together. The `.app` expects `app.py`, `src/`, `requirements.txt`, and `.streamlit/` next to it or inside the repo root.
3. Open `dist/Cash P&L.app`.
4. First open on an unsigned build: right-click the app → **Open** → **Open**. Gatekeeper only asks once.
5. First launch creates a private environment under  
   `~/Library/Application Support/CashPnL/`  
   and may take a minute while it installs dependencies.
6. A window or browser tab opens at [http://127.0.0.1:8501](http://127.0.0.1:8501).
7. Upload your bank Excel, or `sample.xlsx` from this repo.

Quit by closing the window. Company workbooks are not uploaded anywhere.

### Package the Mac app

Do this on a Mac. Linux CI cannot produce a usable `.app`.

```bash
cd financial-analysis-basic
chmod +x scripts/build_macos.sh
./scripts/build_macos.sh
```

Output:

```
dist/Cash P&L.app
```

Copy that app to Applications or send the whole `dist/` folder. Rebuild after you change `app.py`, `src/`, or `requirements.txt`.

The bundle id is `global.otterly.cashpnl`. Icon source is `assets/icon.png` (converted to `assets/icon.icns` by the build script).

Notarization and Apple Developer signing are **not** included. Recipients use right-click → Open.

## Install — from source (any OS)

Needs Python 3.12+ and a copy of this repo.

```bash
git clone https://github.com/otterlyfrank/financial-analysis-basic.git
cd financial-analysis-basic
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Windows PowerShell:

```powershell
git clone https://github.com/otterlyfrank/financial-analysis-basic.git
cd financial-analysis-basic
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

Open [http://127.0.0.1:8501](http://127.0.0.1:8501). The server binds to localhost only.

First run: upload `sample.xlsx` from this repo to confirm the screen.

## Use

1. Upload the `.xlsx` bank dump.
2. Enter **Opening cash**.
3. Pick a revenue scenario: `base`, `up`, or `down`.
4. Set the up/down percent (default 10).
5. Leave **Forecast non-recurring** off unless you want one-offs repeated.

Forecast horizon is the next **3 months**. Recurring costs and revenue use the average of the last 3 periods in the file. Revenue is then scaled by the scenario percent. Loans are not projected.

## Privacy

- Streamlit telemetry is off (`.streamlit/config.toml`).
- The process listens on `127.0.0.1:8501` only.
- Uploaded rows go into a local DuckDB file (`cash.duckdb`, gitignored).
- The Mac app keeps its venv and DuckDB under `~/Library/Application Support/CashPnL/`.
- Do not deploy this to Streamlit Community Cloud if the workbook is company data.

## Project layout

```
app.py                 # Streamlit UI
sample.xlsx            # tiny demo dump
requirements.txt
.streamlit/config.toml
assets/icon.png        # Mac / tab icon source
scripts/build_macos.sh # builds dist/Cash P&L.app
src/schema.py
src/ingest.py
src/classify.py
src/store.py
src/pivot.py
src/forecast.py
src/cash.py
tests/test_pivot.py
```

## Dependencies

Pinned in `requirements.txt`: Streamlit, pandas, openpyxl, DuckDB, Plotly.

## Not in v1

- Excel/PDF download of the report
- Loan draw or repayment schedule in the forecast
- Seasonality (revenue is a flat % on the 3-month average)
- Multi-company consolidation
- Signed / notarized Mac installer
- Balance sheet

## Tests

```bash
source .venv/bin/activate
python -m pytest tests/test_pivot.py
```

## License

Not set. Add one before you share the repo widely.
