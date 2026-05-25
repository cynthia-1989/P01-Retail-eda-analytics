# ================================================================
# src/validator.py
# ================================================================
# We are building this file together as a class.
#
# CONTEXT: We just ran Module 03 and extracted retail sales data from
# ShopSmart Retail Group's database into raw-data.csv.
# Before we clean anything, we need to know WHAT is wrong.
# That is exactly what this file does.
#
# THE ANALOGY:
# Imagine you work in a hospital laboratory.
# Before a doctor can treat a patient, the lab runs tests first.
# The tests do not treat the patient — they just report what is wrong.
# A DataValidator is the lab test for your data.
# It NEVER changes the data. It only reads and reports.
#
# WHAT WE ARE BUILDING:
# A class called DataValidator with 5 methods:
#   1. check_not_empty()      → is there any data at all?
#   2. check_nulls()          → which columns have missing values?
#   3. check_duplicates()     → are any rows exact copies?
#   4. check_numeric_ranges() → are there impossible values in retail data?
#   5. compute_stats()        → summarise everything we found
#
# HOW WE USE IT (preview — we build this in etl_pipeline.py):
#   validator = DataValidator(raw_dataframe)
#   validator.check_not_empty().check_nulls().check_duplicates().compute_stats()
#   if validator._passed:
#       print("Data is good — proceed to transformation")
# ================================================================

# ── What are imports? ─────────────────────────────────────────────────
# When Python runs a file, it only knows about built-in functions (print, len, etc.)
# To use pandas, logging, or our config — we have to explicitly import them.
# Think of it like opening a toolbox before you can use the tools inside.

import sys       # sys lets us modify Python's module search path
import pathlib   # pathlib gives us cross-platform file path tools

# sys.path is a list of folders Python looks in when you write "import something".
# By default it does not include our project root folder.
# This block walks UP the folder tree until it finds config.py,
# then adds that folder to sys.path so Python can find our config module.
_root = pathlib.Path(__file__).resolve().parent   # start at src/ folder
while not (_root / "config.py").exists() and _root != _root.parent:
    _root = _root.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

# Now we can import from our project's config.py
import pandas as pd
from config import logger, MAX_NULL_PERCENT, MAX_DUPLICATE_PERCENT


# ================================================================
# THE DataValidator CLASS
# ================================================================
# In Python, a class is a blueprint for creating objects.
# An object bundles together:
#   - DATA (called attributes or instance variables): self.df, self.issues
#   - BEHAVIOUR (called methods): check_nulls(), check_duplicates()
#
# Why use a class here instead of separate functions?
# ──────────────────────────────────────────────────
# If we used separate functions, each function would run and throw away its results.
# The class REMEMBERS everything. After running 5 checks, we can still read:
#   validator.issues     → all problems found
#   validator.stats      → summary statistics
#   validator._passed    → overall pass/fail result
#
# The ETLPipeline (etl_pipeline.py) will read these to make decisions.
# ================================================================

class DataValidator:
    """
    Inspects a raw DataFrame and reports all data quality issues.

    DESIGN PRINCIPLE: Read-Only
    This class never modifies the data. Its only job is to look and report.
    Fixing data is DataTransformer's responsibility.

    This separation (inspect vs fix) comes from the
    Single Responsibility Principle — each class does ONE thing well.
    """

    # ── CLASS ATTRIBUTES ─────────────────────────────────────────────────
    # Class attributes are defined at the class level (not inside any method).
    # They are SHARED by all instances of this class.
    # Think of them as settings that apply to every DataValidator we ever create.
    #
    # We use the values from config.py (imported above) so they are consistent
    # across the whole project.
    MAX_NULL_PCT = MAX_NULL_PERCENT
    MAX_DUP_PCT = MAX_DUPLICATE_PERCENT

    def __init__(self, df: pd.DataFrame):
        """
        __init__ is the constructor — it runs automatically when you create an object.
        When you write:
            validator = DataValidator(my_dataframe)
        Python calls __init__(self, my_dataframe) for you.

        'self' refers to this specific instance being created.
        It is how a method accesses the object's own data.

        The colon in (df: pd.DataFrame) is a TYPE HINT.
        It tells you and your teammates: "df should be a pandas DataFrame."
        Python does not enforce this — it is documentation for humans.

        Args:
            df    the raw DataFrame to inspect
        """

        # df.copy() creates an INDEPENDENT copy of the DataFrame in memory.
        # If we stored df directly (self.df = df), then any changes to self.df
        # would also change the original df in the caller's code.
        # That would be a very hard-to-find bug.
        # Copying is defensive programming — we protect the caller's data.
        self.df = df.copy()

        # self.issues is a list that starts empty and grows as we find problems.
        self.issues = []

        # self.stats is a dictionary that will hold summary statistics.
        self.stats = {}

        # self._passed starts True (we assume the data is good).
        self._passed = True

    # ================================================================
    # THE 5 CHECK METHODS
    # ================================================================

    def check_not_empty(self) -> "DataValidator":
        """
        Check 1: Does the DataFrame have any rows at all?

        Why this check exists:
        ─────────────────────────
        If the SQL query in Module 03 had a bug in the WHERE clause,
        it might return zero rows. Every downstream check on zero rows
        would either crash or produce meaningless results.
        We catch this immediately and stop early.
        """

        if len(self.df) == 0:
            self._add_issue(
                severity="CRITICAL",
                column="row_count",
                message=(
                    "DataFrame has 0 rows. "
                    "Check that Module 03 ran successfully and "
                    "that INDUSTRY in config.py is correct."
                )
            )
            self._passed = False

        else:
            logger.info(f"[VALIDATE] Row count: {len(self.df):,} rows ✓")

        return self

    def check_nulls(self) -> "DataValidator":
        """
        Check 2: Which columns have missing (null/NaN) values?

        WHAT IS A NULL VALUE?
        ─────────────────────
        NULL in SQL, NaN in pandas — both mean "no value here."
        Not zero. Not empty string. The ABSENCE of a value.

        NULL values are dangerous because:
          - total_amount.mean() on a column with NaN returns misleading results
          - You cannot compare NaN to anything: NaN != NaN
          - ML models cannot handle NaN — training will crash or produce garbage

        WHERE DO NULLS COME FROM?
        ──────────────────────────
        - LEFT JOINs in SQL: when the right table has no match, the joined
          columns become NULL for that row.
        - Missing product/store information.
        - Missing customer type, payment method, return data, or inventory fields.

        OUR THRESHOLDS:
        ────────────────
        0%  to 50% null → WARNING
        >50% null        → CRITICAL
        """

        null_counts = self.df.isna().sum()

        for col, count in null_counts.items():

            if count == 0:
                continue

            pct = round(count / len(self.df) * 100, 1)

            if pct > self.MAX_NULL_PCT:
                severity = "CRITICAL"
                self._passed = False
            else:
                severity = "WARNING"

            self._add_issue(
                severity=severity,
                column=col,
                message=f"{count:,} null values ({pct}% of rows)"
            )

        n_cols_with_nulls = int((null_counts > 0).sum())
        logger.info(
            f"[VALIDATE] Null check complete — "
            f"{n_cols_with_nulls} columns have null values"
        )

        return self

    def check_duplicates(self) -> "DataValidator":
        """
        Check 3: Are any rows exact copies of another row?

        WHAT IS A DUPLICATE ROW?
        ─────────────────────────
        A duplicate is a row where EVERY column value is identical to
        another row in the same DataFrame.

        HOW DO DUPLICATES ENTER PRODUCTION DATA?
        ──────────────────────────────────────────
        1. SQL JOIN ERRORS
           A JOIN between sales, products, stores, returns, and inventory
           where the join key is not unique can create multiple copies.

        2. PIPELINE RAN TWICE
           An ETL pipeline was triggered twice by a scheduling bug.

        3. MANUAL DATA ENTRY
           Someone imported a spreadsheet twice.

        WHY DUPLICATES HURT YOUR ANALYSIS:
        ────────────────────────────────────
        If one sale appears 3 times:
          - Revenue is overstated
          - Average revenue per sale becomes wrong
          - Discount impact analysis becomes misleading
        """

        dup_count = int(self.df.duplicated(keep="first").sum())

        if dup_count > 0:

            dup_pct = round(dup_count / len(self.df) * 100, 1)

            if dup_pct > self.MAX_DUP_PCT:
                severity = "CRITICAL"
                self._passed = False
            else:
                severity = "WARNING"

            self._add_issue(
                severity=severity,
                column="duplicates",
                message=(
                    f"{dup_count:,} exact duplicate rows "
                    f"({dup_pct}% of dataset)"
                )
            )

        else:
            logger.info("[VALIDATE] Duplicate check: 0 duplicate rows found ✓")

        return self

    def check_numeric_ranges(self) -> "DataValidator":
        """
        Check 4: Do numeric columns have values that are logically impossible?

        EXAMPLES OF IMPOSSIBLE VALUES:
        ────────────────────────────────
        quantity          = -5      → sold quantity should not normally be negative
        unit_price        = -20     → product price should not normally be negative
        total_amount      = -100    → sales total should not normally be negative
        discount_pct      = 150     → discount percentage should be between 0 and 100
        margin_pct        = 150     → margin percentage should normally be between 0 and 100
        refund_amount     = -50     → refund amount should not normally be negative

        WHERE DO IMPOSSIBLE VALUES COME FROM?
        ──────────────────────────────────────
        - Sign errors in calculations
        - Unit mismatches
        - Data entry errors
        - Bad SQL joins or incorrect formulas

        IMPORTANT — SOME NEGATIVES ARE VALID:
        ───────────────────────────────────────
        "Difference" columns legitimately go negative:
          revenue_vs_category_avg = -500 means this sale/store is below category average
          store_revenue_gap = -200 means the store is below benchmark
          profit_delta = -100 means profit decreased

        We skip these columns because negative values are expected there.
        """

        DELTA_COLUMNS = {
            "revenue_vs_category_avg",
            "amount_vs_category_avg",
            "sales_delta",
            "revenue_delta",
            "discount_delta",
            "profit_delta",
            "margin_delta",
            "refund_delta",
            "net_sales_difference",
            "gross_vs_net_difference",
            "store_revenue_gap",
            "category_revenue_gap",
        }

        for col in self.df.select_dtypes(include=["number"]).columns:

            if col in DELTA_COLUMNS:
                continue

            neg_count = int((self.df[col] < 0).sum())

            if neg_count > 0:
                self._add_issue(
                    severity="WARNING",
                    column=col,
                    message=(
                        f"{neg_count} unexpected negative values. "
                        f"Check if '{col}' should always be positive."
                    )
                )

            if col == "discount_pct":
                invalid_discount = int(((self.df[col] < 0) | (self.df[col] > 100)).sum())

                if invalid_discount > 0:
                    self._add_issue(
                        severity="WARNING",
                        column=col,
                        message=(
                            f"{invalid_discount} invalid discount values. "
                            "Discount percentage should be between 0 and 100."
                        )
                    )

            if col == "margin_pct":
                invalid_margin = int(((self.df[col] < 0) | (self.df[col] > 100)).sum())

                if invalid_margin > 0:
                    self._add_issue(
                        severity="WARNING",
                        column=col,
                        message=(
                            f"{invalid_margin} invalid margin values. "
                            "Margin percentage should be between 0 and 100."
                        )
                    )

            if col == "quantity":
                zero_or_negative_qty = int((self.df[col] <= 0).sum())

                if zero_or_negative_qty > 0:
                    self._add_issue(
                        severity="WARNING",
                        column=col,
                        message=(
                            f"{zero_or_negative_qty} invalid quantity values. "
                            "Retail sale quantity should normally be greater than 0."
                        )
                    )

        return self

    def compute_stats(self) -> "DataValidator":
        """
        Check 5 (not really a check — a summary): Compute dataset statistics.

        This gathers key facts about the dataset in one dictionary.
        These stats are used by:
          - ETLPipeline.report() to show what we received
          - Module 06 EDA engine as a starting profile
          - Module 14 MLOps monitor as the baseline for drift detection

        WHAT IS A DICTIONARY?
        ──────────────────────
        A dictionary (dict) maps keys to values:
            my_dict = {"store_name": "Calgary", "total_amount": 920}
            my_dict["total_amount"]  → 920
        """

        num_col_count = len(self.df.select_dtypes(include=["number"]).columns)
        txt_col_count = len(self.df.select_dtypes(include=["object"]).columns)
        boo_col_count = len(self.df.select_dtypes(include=["bool"]).columns)

        self.stats = {
            "rows": len(self.df),
            "columns": len(self.df.columns),
            "numeric_cols": num_col_count,
            "text_cols": txt_col_count,
            "bool_cols": boo_col_count,
            "total_nulls": int(self.df.isna().sum().sum()),
            "null_pct": round(self.df.isna().sum().sum() / self.df.size * 100, 2),
            "duplicates": int(self.df.duplicated().sum()),
            "memory_mb": round(self.df.memory_usage(deep=True).sum() / 1024**2, 2),
            "total_issues": len(self.issues),
            "critical_count": sum(
                1 for i in self.issues if i["severity"] == "CRITICAL"
            ),
            "warning_count": sum(
                1 for i in self.issues if i["severity"] == "WARNING"
            ),
            "passed": self._passed,
        }

        logger.info(
            f"[VALIDATE] Stats computed: "
            f"{self.stats['rows']:,} rows | "
            f"{self.stats['total_nulls']:,} nulls | "
            f"{self.stats['total_issues']} issues found | "
            f"result: {'PASSED ✓' if self._passed else 'FAILED ✗'}"
        )

        return self

    # ================================================================
    # PRIVATE HELPER METHOD
    # ================================================================

    def _add_issue(self, severity: str, column: str, message: str) -> None:
        """
        Record one data quality issue in self.issues.

        Also logs it at the appropriate level so it appears in the terminal.

        Args:
            severity  "CRITICAL" or "WARNING"
            column    which column the issue affects
            message   human-readable description of the problem
        """

        issue = {
            "severity": severity,
            "column": column,
            "message": message,
        }

        self.issues.append(issue)

        if severity == "CRITICAL":
            logger.error(f"[VALIDATE] CRITICAL | {column} | {message}")
        else:
            logger.warning(f"[VALIDATE] WARNING  | {column} | {message}")

    # ================================================================
    # DUNDER (MAGIC) METHODS
    # ================================================================

    def __str__(self) -> str:
        """
        Called automatically when you write print(validator).
        Should return a SHORT, human-readable summary.
        """
        status = "PASSED ✓" if self._passed else "FAILED ✗"
        return (
            f"DataValidator("
            f"result={status} | "
            f"{len(self.issues)} issues found | "
            f"{len(self.df):,} rows inspected)"
        )

    def __repr__(self) -> str:
        """
        Called in the Python REPL and debugger.
        Should return a string that shows the object's key state.
        """
        return (
            f"DataValidator("
            f"rows={len(self.df):,}, "
            f"issues={len(self.issues)}, "
            f"passed={self._passed})"
        )


# ================================================================
# QUICK SELF-TEST
# ================================================================

if __name__ == "__main__":
    import pandas as pd

    print("Running DataValidator self-test...")
    print("=" * 50)

    # Test 1: Clean data — should pass
    clean_df = pd.DataFrame({
        "sale_id": [1, 2, 3, 4, 5],
        "store_name": ["Calgary", "Edmonton", "Red Deer", "Airdrie", "Lethbridge"],
        "category": ["Electronics", "Grocery", "Clothing", "Home", "Beauty"],
        "quantity": [2, 5, 1, 3, 4],
        "unit_price": [120, 25, 200, 80, 45],
        "discount_pct": [10, 0, 15, 5, 20],
        "margin_pct": [30, 25, 40, 20, 35],
        "total_amount": [216, 125, 170, 228, 144],
    })

    v1 = DataValidator(clean_df)
    v1.check_not_empty().check_nulls().check_duplicates().check_numeric_ranges().compute_stats()
    print(f"Test 1 (clean data): {v1}")

    # Test 2: Data with nulls — should warn
    dirty_df = clean_df.copy()
    dirty_df.loc[0, "total_amount"] = None
    dirty_df.loc[1, "discount_pct"] = 150
    dirty_df.loc[2, "margin_pct"] = 130
    dirty_df.loc[3, "quantity"] = -2

    v2 = DataValidator(dirty_df)
    v2.check_not_empty().check_nulls().check_duplicates().check_numeric_ranges().compute_stats()
    print(f"Test 2 (with null): {v2}")

    # Test 3: Empty data — should FAIL
    empty_df = pd.DataFrame()
    v3 = DataValidator(empty_df)
    v3.check_not_empty()
    print(f"Test 3 (empty):     {v3}")

    print("\nSelf-test complete.")