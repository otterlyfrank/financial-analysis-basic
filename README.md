# Cash P&L

Upload a bank-transaction Excel sheet. The app builds monthly cash in/out charts and a cash walk (opening cash → each month’s net → closing). It runs only on this computer. Nothing is sent to the cloud.

## Open the app (no Terminal)

1. On GitHub open [otterlyfrank/financial-analysis-basic](https://github.com/otterlyfrank/financial-analysis-basic) → **Code** → **Download ZIP**.
2. Unzip the folder and leave the files together.
3. **Mac:** double-click `Run Cash P&L.command`. First time: right-click the file → **Open** → **Open**.
4. **Windows:** double-click `Run Cash P&L.bat`.
5. The first run can take a minute while it sets up.
6. A browser tab opens at [http://127.0.0.1:8501](http://127.0.0.1:8501).
7. Type **Opening cash** in the left sidebar (bank balance at the start of the first month).
8. Upload your bank `.xlsx`, or click **Load sample.xlsx**.
9. Use **Download Excel report** when you want the tables in a workbook.
Closing the browser does not erase the last upload or the opening-cash figure; they are stored next to the app in `cash.duckdb` and `settings.json`.

Columns must be: `Month`, `Type`, `Category`, `Subcategory`, `Amount`. Amounts are positive; direction comes from `Type`.

## If Python is missing

Install [Python 3.12](https://www.python.org/downloads/) from python.org. Tick **Add Python to PATH**. Then double-click the same file again.

## Optional: Mac .app

On a **Mac only** (does not run on Windows), from Terminal in this folder:

```bash
./scripts/build_macos.sh
```

That writes `dist/Cash P&L.app`. The `.app` is **not** in git; you build it locally. First open: right-click → **Open**. Python 3.12 is still required. This extra is for people who want a Dock icon; the ZIP double-click launchers above are the usual path.

## Type values (exact spelling)

| Type | Treated as |
|---|---|
| `Revenue` | Operating cash in |
| `Expense recurring` | Operating cash out; forecast uses last-3-month average by subcategory |
| `Expense non-recurring` | Operating cash out; not forecast unless you tick the box |
| `Loans - in` | Financing in (history only in v1) |
| `Loans - out` | Financing out (history only in v1) |
| `Intercompany transfer` | Related-party; v1 signs it as cash out and keeps it off the operating charts |

Category examples: Payroll, G&A, COGS, Occupancy costs, royalty.

## Privacy

- Listens on `127.0.0.1:8501` only. Streamlit telemetry is off.
- No cloud, no login, no upload except the file you pick on this machine.
- Rows are stored in a local `cash.duckdb` next to the app. Opening cash and scenario are stored in `settings.json`. Both stay on this machine.
- Optional Mac `.app` keeps those files under `~/Library/Application Support/CashPnL/`.

## Not in v1

No PDF pack, no loan schedule in the forecast, no seasonality, no multi-company roll-up, no signed Mac installer, no balance sheet.

## From source (Terminal)

```bash
git clone https://github.com/otterlyfrank/financial-analysis-basic.git
cd financial-analysis-basic
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py --server.address=127.0.0.1 --browser.gatherUsageStats=false
```

Windows PowerShell: `py -3.12 -m venv .venv`, then `.\.venv\Scripts\Activate.ps1`, then the same `pip` and `streamlit` lines.

Or double-click the ZIP launchers in this folder instead.
