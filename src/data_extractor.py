# ================================================================
# src/data_extractor.py
# P01 Retail SQL — Data Extractor
# ================================================================

import sys
import pathlib

_root = pathlib.Path(__file__).resolve().parent
while not (_root / "config.py").exists() and _root != _root.parent:
    _root = _root.parent

if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from config import INDUSTRY, RAW_DATA_PATH, DB_AVAILABLE, logger
from src.query_runner import SQLQueryRunner


class DataExtractor:
    """
    Runs the retail production extraction query and saves raw-data.csv.

    SQL file used:
        sql/05_extract_raw_data.sql

    Output:
        data/raw/raw-data.csv
    """

    def __init__(self):
        self.industry = INDUSTRY
        self.runner = SQLQueryRunner()
        self.raw_df = None
        self._status = "ready"

    def extract(self) -> "DataExtractor":
        """Run the retail extraction SQL query using the real database only."""
        logger.info(f"[EXTRACT] Starting retail extraction — industry: {self.industry}")

        if not DB_AVAILABLE:
            raise RuntimeError(
                "Database is NOT connected. Check your .env file and DB_URL."
            )

        self.raw_df = self.runner.run_file("05_extract_raw_data.sql")

        if self.raw_df is None:
            raise RuntimeError(
                "SQL did not return data. Check sql/05_extract_raw_data.sql."
            )

        if len(self.raw_df) == 0:
            raise RuntimeError(
                "SQL returned 0 rows. Check your joins or confirm the retail tables have data."
            )

        self._status = "extracted"

        logger.info(
            f"[EXTRACT] Extracted {len(self.raw_df):,} rows × {self.raw_df.shape[1]} columns"
        )

        return self

    def save(self) -> "DataExtractor":
        """Save extracted retail data to data/raw/raw-data.csv."""
        if self.raw_df is None or len(self.raw_df) == 0:
            raise RuntimeError("No data to save. Run extract() first.")

        RAW_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)

        self.raw_df.to_csv(RAW_DATA_PATH, index=False, encoding="utf-8")

        file_size_kb = RAW_DATA_PATH.stat().st_size / 1024

        logger.info(
            f"[EXTRACT] Saved {len(self.raw_df):,} rows to {RAW_DATA_PATH} "
            f"({file_size_kb:.1f} KB)"
        )

        self._status = "saved"
        return self

    def report(self) -> None:
        """Print a simple project report after extraction."""
        if self.raw_df is None:
            print("No data extracted. Run extract() first.")
            return

        print()
        print("=" * 70)
        print("  P01 RETAIL SQL — EXTRACTION COMPLETE")
        print("=" * 70)
        print(f"  Industry/schema:   {self.industry}")
        print(f"  Rows extracted:    {len(self.raw_df):,}")
        print(f"  Columns extracted: {self.raw_df.shape[1]}")
        print(f"  Output file:       {RAW_DATA_PATH}")
        print()

        print("  Columns in raw-data.csv:")
        for col in self.raw_df.columns:
            print(f"    - {col}")

        print()
        print("  Basic data quality check:")

        nulls = self.raw_df.isna().sum()
        missing_cols = nulls[nulls > 0]

        if len(missing_cols) == 0:
            print("    No missing values detected.")
        else:
            for col in missing_cols.index:
                pct = round(missing_cols[col] / len(self.raw_df) * 100, 1)
                print(f"    NULL {col}: {missing_cols[col]:,} rows ({pct}%)")

        print()
        print("  Deliverable created:")
        print(f"    {RAW_DATA_PATH}")
        print("=" * 70)

    def __str__(self):
        return f"DataExtractor(industry={self.industry!r}, status={self._status!r})"

    def __repr__(self):
        return f"DataExtractor(industry={self.industry!r})"