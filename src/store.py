from pathlib import Path

import duckdb
import pandas as pd

from src.schema import CANONICAL

DB_PATH = Path(__file__).resolve().parent.parent / "cash.duckdb"


def connect() -> duckdb.DuckDBPyConnection:
    con = duckdb.connect(str(DB_PATH))
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS facts (
            period VARCHAR,
            type VARCHAR,
            category VARCHAR,
            subcategory VARCHAR,
            amount DOUBLE,
            signed_amount DOUBLE,
            bucket VARCHAR,
            source VARCHAR
        )
        """
    )
    return con


def replace_facts(df: pd.DataFrame) -> None:
    ordered = df[CANONICAL]
    con = connect()
    con.execute("CREATE OR REPLACE TABLE facts AS SELECT * FROM ordered")
    con.close()


def read_facts() -> pd.DataFrame:
    con = connect()
    df = con.execute("SELECT * FROM facts").df()
    con.close()
    return df
