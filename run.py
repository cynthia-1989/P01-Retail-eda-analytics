# ================================================================
# run.py — Full Retail ETL + EDA Pipeline
# ================================================================

from config import (
    logger,
    PROCESSED_DATA_PATH,
)

from src.data_extractor import DataExtractor
from src.validator import DataValidator
from src.transformer import DataTransformer
from src.eda_engine import EDAEngine
from src.anomaly_detector import AnomalyDetector


def main():

    logger.info("=" * 60)
    logger.info("  P01 RETAIL EDA PIPELINE")
    logger.info("=" * 60)

    # ============================================================
    # STEP 1 — EXTRACT RAW DATA
    # ============================================================

    extractor = DataExtractor()

    (
        extractor
        .extract()
        .save()
    )

    extractor.report()

    # ============================================================
    # STEP 2 — VALIDATE RAW DATA
    # ============================================================

    validator = DataValidator(extractor.raw_df)

    (
        validator
        .check_not_empty()
        .check_nulls()
        .check_duplicates()
        .check_numeric_ranges()
        .compute_stats()
    )

    print()
    print(validator)

    # ============================================================
    # STEP 3 — TRANSFORM DATA
    # ============================================================

    transformer = DataTransformer(extractor.raw_df)

    (
        transformer
        .fill_nulls()
        .drop_duplicates()
        .fix_types()
        .add_derived_columns()
        .add_metadata()
    )

    # Save processed data
    transformer.df.to_csv(PROCESSED_DATA_PATH, index=False)

    logger.info(
        f"[PIPELINE] Processed data saved → {PROCESSED_DATA_PATH}"
    )

    # ============================================================
    # STEP 4 — RUN EDA
    # ============================================================

    eda = EDAEngine()

    (
        eda
        .load()
        .profile()
        .group_analysis()
        .correlation()
        .report()
    )

    logger.info("[PIPELINE] EDA complete")

    # ============================================================
    # STEP 5 — ANOMALY DETECTION
    # ============================================================

    detector = AnomalyDetector(eda.df)

    (
        detector
        .run()
        .save_anomalies()
    )

    print()
    print(detector.summary())

    logger.info("[PIPELINE] Anomaly detection complete")

    logger.info("=" * 60)
    logger.info("  RETAIL PIPELINE COMPLETE")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()