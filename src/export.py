from io import BytesIO

import pandas as pd


def workbook_bytes(sheets: dict[str, pd.DataFrame]) -> bytes:
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        for name, frame in sheets.items():
            safe = name[:31]
            out = frame.copy()
            if out.empty:
                out = pd.DataFrame({"note": ["no rows"]})
            out.to_excel(writer, sheet_name=safe, index=False)
    return buf.getvalue()
