from enum import StrEnum


class TxType(StrEnum):
    EXPENSE_NON_RECURRING = "Expense non-recurring"
    EXPENSE_RECURRING = "Expense recurring"
    REVENUE = "Revenue"
    LOANS_IN = "Loans - in"
    LOANS_OUT = "Loans - out"
    INTERCOMPANY = "Intercompany transfer"


class Bucket(StrEnum):
    OPERATING = "operating"
    FINANCING = "financing"
    INTERCOMPANY = "intercompany"


CASH_OUT_TYPES = frozenset(
    {
        TxType.EXPENSE_NON_RECURRING,
        TxType.EXPENSE_RECURRING,
        TxType.LOANS_OUT,
        TxType.INTERCOMPANY,
    }
)

EXCEL_COLS = ["Month", "Type", "Category", "Subcategory", "Amount"]
CANONICAL = [
    "period",
    "type",
    "category",
    "subcategory",
    "amount",
    "signed_amount",
    "bucket",
    "source",
]


def cash_sign(tx_type: str) -> int:
    return -1 if TxType(tx_type) in CASH_OUT_TYPES else 1
