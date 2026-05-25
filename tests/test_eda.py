# ================================================================
# tests/test_eda.py — Unit Tests for Module 06
# ================================================================
# WHY TEST EDA CODE?
# ──────────────────
# EDA results feed into ML feature selection, LLM context, and
# MLOps monitoring. If the EDAEngine computes incorrect statistics,
# every downstream module makes decisions on wrong information.
# Tests catch bugs before they contaminate the entire pipeline.
#
# HOW TO RUN:
#   python tests/test_eda.py
# or with pytest:
#   pytest tests/
# ================================================================

import sys, pathlib
_root = pathlib.Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

import pandas as pd
import numpy as np
from src.eda_engine       import EDAEngine
from src.anomaly_detector import AnomalyDetector


# ── TEST DATA FACTORY ─────────────────────────────────────────────

def make_sample_df(rows: int = 50) -> pd.DataFrame:
    """Create a small, predictable DataFrame for testing."""
    import random
    random.seed(42)
    np.random.seed(42)

    categories = ["Electronics", "Grocery", "Clothing", "Home", "Beauty"]
    stores = ["Calgary", "Edmonton", "Red Deer", "Airdrie", "Lethbridge"]

    quantity = np.random.randint(1, 10, rows)
    unit_price = np.random.uniform(5, 500, rows).round(2)
    discount_pct = np.random.choice([0, 5, 10, 15, 20, 25, 30], rows)

    total_amount = (quantity * unit_price * (1 - discount_pct / 100)).round(2)

    return pd.DataFrame({
        "sale_id": range(1, rows + 1),
        "category": [categories[i % len(categories)] for i in range(rows)],
        "store_name": [stores[i % len(stores)] for i in range(rows)],
        "quantity": quantity,
        "unit_price": unit_price,
        "discount_pct": discount_pct,
        "total_amount": total_amount,
        "payment_method": np.random.choice(["Cash", "Card", "Mobile"], rows),
        "customer_type": np.random.choice(["Regular", "Member", "New"], rows),
    })


# ── EDAENGINE TESTS ───────────────────────────────────────────────

def test_profile_computes_correct_row_count():
    """profile() must report the exact row count of the loaded DataFrame."""
    engine = EDAEngine()
    engine.df       = make_sample_df(50)
    engine.num_cols = engine.df.select_dtypes(include=["number"]).columns.tolist()
    engine.cat_cols = engine.df.select_dtypes(include=["object"]).columns.tolist()
    engine.profile()

    assert engine.results["profile"]["rows"] == 50,         "Profile row count should equal the DataFrame length"
    print("  PASS: test_profile_computes_correct_row_count")


def test_profile_null_count_is_zero_for_clean_data():
    """Clean DataFrame should have 0 total nulls in the profile."""
    engine = EDAEngine()
    engine.df       = make_sample_df()
    engine.num_cols = engine.df.select_dtypes(include=["number"]).columns.tolist()
    engine.cat_cols = engine.df.select_dtypes(include=["object"]).columns.tolist()
    engine.profile()

    assert engine.results["profile"]["total_nulls"] == 0,         "Clean DataFrame should have 0 nulls in profile"
    print("  PASS: test_profile_null_count_is_zero_for_clean_data")


def test_group_analysis_produces_results():
    """group_analysis() must populate results with at least one grouping."""
    engine = EDAEngine()
    engine.df       = make_sample_df()
    engine.num_cols = engine.df.select_dtypes(include=["number"]).columns.tolist()
    engine.cat_cols = engine.df.select_dtypes(include=["object"]).columns.tolist()
    engine.group_analysis()

    assert "group_analysis" in engine.results,         "results dict should contain 'group_analysis' key"
    assert len(engine.results["group_analysis"]) > 0,         "group_analysis should have at least one grouping variable"
    print("  PASS: test_group_analysis_produces_results")


def test_group_analysis_rank_starts_at_one():
    """The top-ranked group should always have rank = 1."""
    engine = EDAEngine()
    engine.df       = make_sample_df()
    engine.num_cols = engine.df.select_dtypes(include=["number"]).columns.tolist()
    engine.cat_cols = engine.df.select_dtypes(include=["object"]).columns.tolist()
    engine.group_analysis()

    # Get the first grouping variable and its first metric
    first_cat = list(engine.results["group_analysis"].keys())[0]
    first_num = list(engine.results["group_analysis"][first_cat].keys())[0]
    top_row   = engine.results["group_analysis"][first_cat][first_num][0]

    assert top_row["rank"] == 1,         f"First sorted row should have rank=1, got rank={top_row['rank']}"
    print("  PASS: test_group_analysis_rank_starts_at_one")


def test_correlation_only_includes_strong_pairs():
    """All reported correlation pairs must meet the threshold."""
    from config import CORRELATION_THRESHOLD
    engine = EDAEngine()
    engine.df       = make_sample_df()
    engine.num_cols = engine.df.select_dtypes(include=["number"]).columns.tolist()
    engine.cat_cols = engine.df.select_dtypes(include=["object"]).columns.tolist()
    engine.correlation()

    if "correlation" in engine.results:
        for pair in engine.results["correlation"]["strong_pairs"]:
            assert abs(pair["correlation"]) >= CORRELATION_THRESHOLD,                 (f"Pair {pair['col_a']}↔{pair['col_b']} has r={pair['correlation']:.3f} "
                 f"which is below threshold {CORRELATION_THRESHOLD}")
    print("  PASS: test_correlation_only_includes_strong_pairs")


def test_method_chaining_returns_self():
    """Every EDAEngine method must return self for chaining."""
    engine = EDAEngine()
    engine.df       = make_sample_df()
    engine.num_cols = engine.df.select_dtypes(include=["number"]).columns.tolist()
    engine.cat_cols = engine.df.select_dtypes(include=["object"]).columns.tolist()
    engine._status  = "loaded"

    result = engine.profile().group_analysis().correlation()

    assert result is engine,         "Method chaining must return the same EDAEngine object (self)"
    print("  PASS: test_method_chaining_returns_self")


# ── ANOMALYDETECTOR TESTS ─────────────────────────────────────────

def test_anomaly_detector_flags_obvious_outlier():
    """A value 10× higher than all others should be flagged by both methods."""
    df = make_sample_df(30)
    df.loc[0, "total_amount"] = 10_000_000

    detector = AnomalyDetector(df)
    detector.run(columns=["total_amount"])

    # Row 0 should appear in confirmed anomalies
    assert 0 in detector.confirmed.index,         "Row with obvious outlier total_amount should be in confirmed anomalies"
    print("  PASS: test_anomaly_detector_flags_obvious_outlier")


def test_anomaly_detector_clean_data_has_few_anomalies():
    """Normally distributed data should have very few confirmed anomalies."""
    np.random.seed(42)
    df = pd.DataFrame({
        "total_amount": np.random.normal(100, 10, 200)
    })

    detector = AnomalyDetector(df)
    detector.run(columns=["total_amount"])

    # Under a normal distribution, < 0.3% should be confirmed anomalies
    anomaly_pct = len(detector.confirmed) / len(df) * 100
    assert anomaly_pct < 2.0,         f"Normal data should have < 2% anomalies, got {anomaly_pct:.1f}%"
    print("  PASS: test_anomaly_detector_clean_data_has_few_anomalies")


def test_anomaly_detector_summary_has_correct_columns():
    """summary() must return a DataFrame with the expected column names."""
    df = make_sample_df()
    detector = AnomalyDetector(df)
    detector.run()

    summary = detector.summary()
    expected_cols = ["column", "iqr_flagged", "zscore_flagged",
                     "confirmed_anomalies", "anomaly_pct"]
    for col in expected_cols:
        assert col in summary.columns,             f"Summary DataFrame should have column '{col}'"
    print("  PASS: test_anomaly_detector_summary_has_correct_columns")


def test_anomaly_detector_original_data_unchanged():
    """AnomalyDetector must never modify the original DataFrame."""
    df = make_sample_df()
    original_total_amount_0 = df.loc[0, "total_amount"]

    detector = AnomalyDetector(df)
    detector.run()

    assert df.loc[0, "total_amount"] == original_total_amount_0,         "AnomalyDetector should not modify the original DataFrame"
    print("  PASS: test_anomaly_detector_original_data_unchanged")


def test_detector_handles_zero_std_column():
    """Detector should not crash when a column has all identical values (std=0)."""
    df = pd.DataFrame({
        "constant": [100.0] * 20,
        "total_amount": np.random.uniform(50, 500, 20),
    })

    # Should not raise ZeroDivisionError or any other exception
    try:
        detector = AnomalyDetector(df)
        detector.run(columns=["constant", "total_amount"])
        print("  PASS: test_detector_handles_zero_std_column")
    except Exception as e:
        raise AssertionError(f"Detector crashed on zero-std column: {e}")


# ── TEST RUNNER ───────────────────────────────────────────────────

if __name__ == "__main__":
    print()
    print("=" * 60)
    print("  MODULE 06 — EDA AND ANOMALY DETECTION TESTS")
    print("=" * 60)
    print()

    print("  EDAEngine tests:")
    test_profile_computes_correct_row_count()
    test_profile_null_count_is_zero_for_clean_data()
    test_group_analysis_produces_results()
    test_group_analysis_rank_starts_at_one()
    test_correlation_only_includes_strong_pairs()
    test_method_chaining_returns_self()

    print()
    print("  AnomalyDetector tests:")
    test_anomaly_detector_flags_obvious_outlier()
    test_anomaly_detector_clean_data_has_few_anomalies()
    test_anomaly_detector_summary_has_correct_columns()
    test_anomaly_detector_original_data_unchanged()
    test_detector_handles_zero_std_column()

    print()
    print("=" * 60)
    print("  All tests passed ✓")
    print("=" * 60)