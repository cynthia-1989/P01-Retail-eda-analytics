# ================================================================
# tests/test_sql.py — Unit Tests for Module 03
# ================================================================

import sys, pathlib
_root = pathlib.Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

import pandas as pd
from src.query_runner   import SQLQueryRunner
from src.data_extractor import DataExtractor


def test_sql_files_exist():
    """All 5 SQL teaching files must exist in the sql/ directory."""
    from config import SQL_DIR
    expected = ["01_basics.sql","02_aggregation.sql","03_joins.sql",
                "04_advanced.sql","05_extract_raw_data.sql"]
    for fname in expected:
        assert (SQL_DIR / fname).exists(), f"SQL file missing: {fname}"
    print("  PASS: test_sql_files_exist")


def test_sql_files_contain_select_keyword():
    """Each SQL file must contain at least one SELECT statement."""
    from config import SQL_DIR
    for fname in ["01_basics.sql","02_aggregation.sql","03_joins.sql"]:
        content = (SQL_DIR / fname).read_text()
        assert "SELECT" in content.upper(), f"No SELECT found in {fname}"
    print("  PASS: test_sql_files_contain_select_keyword")


def test_extract_sql_contains_industry_placeholder():
    """05_extract_raw_data.sql must use {industry} placeholder."""
    from config import SQL_DIR
    content = (SQL_DIR / "05_extract_raw_data.sql").read_text()
    assert "{industry}" in content,         "Extraction SQL must use {industry} placeholder for multi-schema support"
    print("  PASS: test_extract_sql_contains_industry_placeholder")


def test_query_runner_returns_dataframe():
    """SQLQueryRunner.run() must always return a DataFrame (never crashes)."""
    runner = SQLQueryRunner()
    # Pass a trivially simple query — works even if industry table does not exist
    df = runner.run("SELECT 1 AS test_col")
    assert isinstance(df, pd.DataFrame), "run() must always return a DataFrame"
    print("  PASS: test_query_runner_returns_dataframe")


def test_query_runner_handles_bad_sql_gracefully():
    """A broken query should return empty DataFrame, not crash."""
    runner = SQLQueryRunner()
    df = runner.run("THIS IS NOT VALID SQL AT ALL")
    assert isinstance(df, pd.DataFrame),         "run() should return empty DataFrame on SQL error, not raise exception"
    print("  PASS: test_query_runner_handles_bad_sql_gracefully")


def test_query_runner_history_records_each_run():
    """Every query run must appear in the history log."""
    runner = SQLQueryRunner()
    initial_count = len(runner.history)
    runner.run("SELECT 1")
    runner.run("SELECT 2")
    assert len(runner.history) == initial_count + 2,         "history should record each query run"
    print("  PASS: test_query_runner_history_records_each_run")


def test_extractor_synthetic_data_has_required_columns():
    """Synthetic fallback data must contain all required columns."""
    raw = DataExtractor._synthetic_raw_data(50)
    required = ["employee_id","department","salary","performance_rating",
                "years_experience","source_schema","extracted_date"]
    for col in required:
        assert col in raw.columns, f"Synthetic data missing column: {col}."
    print("  PASS: test_extractor_synthetic_data_has_required_columns")


def test_extractor_synthetic_data_has_quality_issues():
    """Synthetic data must contain intentional data quality issues."""
    raw = DataExtractor._synthetic_raw_data(300)
    # Should have some NULL salaries
    null_salaries = raw["salary"].isna().sum()
    assert null_salaries > 0,         "Synthetic raw data should have some NULL salaries (data quality issues)"
    # Should have some 99-experience entries
    weird_exp = (raw["years_experience"] == 99).sum()
    assert weird_exp > 0,         "Synthetic raw data should have some years_experience=99 entries"
    print("  PASS: test_extractor_synthetic_data_has_quality_issues")


def test_extractor_save_creates_csv(tmp_path):
    """DataExtractor.save() must create raw-data.csv."""
    import pathlib
    import config as cfg
    orig = cfg.RAW_DATA_PATH
    cfg.RAW_DATA_PATH = pathlib.Path(tmp_path) / "raw-data.csv"

    extractor = DataExtractor()
    extractor.raw_df  = DataExtractor._synthetic_raw_data(50)
    extractor._status = "extracted"
    extractor.save()

    assert cfg.RAW_DATA_PATH.exists(), "save() should create raw-data.csv"
    reloaded = pd.read_csv(cfg.RAW_DATA_PATH)
    assert len(reloaded) == 50, "Saved CSV should have correct row count"
    cfg.RAW_DATA_PATH = orig
    print("  PASS: test_extractor_save_creates_csv")


if __name__ == "__main__":
    print()
    print("=" * 60)
    print("  MODULE 03 — SQL UNIT TESTS")
    print("=" * 60)
    print()
    import tempfile, pathlib

    test_sql_files_exist()
    test_sql_files_contain_select_keyword()
    test_extract_sql_contains_industry_placeholder()
    test_query_runner_returns_dataframe()
    test_query_runner_handles_bad_sql_gracefully()
    test_query_runner_history_records_each_run()
    test_extractor_synthetic_data_has_required_columns()
    test_extractor_synthetic_data_has_quality_issues()

    with tempfile.TemporaryDirectory() as tmp:
        test_extractor_save_creates_csv(pathlib.Path(tmp))

    print()
    print("=" * 60)
    print("  All tests passed ✓")
    print("=" * 60)
