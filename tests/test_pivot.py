import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.classify import classify
from src.ingest import ingest_excel
from src.pivot import month_category


class TestPivot(unittest.TestCase):
    def test_month_category_signed_ops(self):
        rows = classify(ingest_excel(ROOT / "sample.xlsx"))
        table = month_category(rows)
        jan = table.loc[table["period"] == "2024-01"].iloc[0]
        self.assertEqual(jan["Sales"], 80000)
        self.assertEqual(jan["Payroll"], -25000)
        self.assertEqual(jan["Occupancy costs"], -5000)
        self.assertEqual(jan["G&A"], -3000)
        self.assertNotIn("royalty", table.columns)
        self.assertEqual(set(table["period"]), {"2024-01", "2024-02", "2024-03"})


if __name__ == "__main__":
    unittest.main()
