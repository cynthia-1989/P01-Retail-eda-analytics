# ================================================================
# src/query_runner.py
# P01 Retail SQL — Query Runner
# ================================================================

import sys
import pathlib
import time
import pandas as pd

_root = pathlib.Path(__file__).resolve().parent
while not (_root / "config.py").exists() and _root != _root.parent:
    _root = _root.parent

if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from config import engine, DB_AVAILABLE, SQL_DIR, INDUSTRY, logger


class SQLQueryRunner:
    """
    Executes SQL queries against the healthcare PostgreSQL database.
    Returns SQL results as pandas DataFrames.
    """

    def __init__(self):
        self.industry = INDUSTRY
        self.history = []
        logger.info(f"SQLQueryRunner ready — schema: {self.industry}, db_available: {DB_AVAILABLE}")

    def run(self, sql: str, params: dict = None) -> pd.DataFrame:
        """
        Execute a SQL query and return the result as a DataFrame.
        """
        if not DB_AVAILABLE or engine is None:
            logger.error("[SQL] Database not available. Check DB_URL in .env.")
            return pd.DataFrame()

        sql = sql.replace("{industry}", self.industry)
        start_time = time.time()

        try:
            df = pd.read_sql(sql, engine, params=params)

            duration_ms = round((time.time() - start_time) * 1000, 1)

            self.history.append({
                "sql_preview": sql[:100].strip(),
                "rows": len(df),
                "cols": len(df.columns),
                "duration_ms": duration_ms,
                "status": "success",
            })

            logger.info(
                f"[SQL] Query complete — {len(df):,} rows × {len(df.columns)} columns | {duration_ms} ms"
            )

            return df

        except Exception as e:
            duration_ms = round((time.time() - start_time) * 1000, 1)

            self.history.append({
                "sql_preview": sql[:100].strip(),
                "rows": 0,
                "cols": 0,
                "duration_ms": duration_ms,
                "status": f"error: {str(e)[:100]}",
            })

            logger.error(f"[SQL] Query failed: {e}")
            return pd.DataFrame()

    def run_file(self, filename: str) -> pd.DataFrame:
        """
        Load a SQL file from the sql/ folder and execute it.
        """
        sql_path = SQL_DIR / filename

        if not sql_path.exists():
            logger.error(f"[SQL] File not found: {sql_path}")
            return pd.DataFrame()

        logger.info(f"[SQL] Loading SQL file: {filename}")

        sql_text = sql_path.read_text(encoding="utf-8")
        return self.run(sql_text)

    def demo_basics(self) -> None:
        """
        Run basic retail table checks.
        """
        demos = [
            (
                "Sample sales",
                f"""
                SELECT
                    sale_id,
                    sale_date,
                    product_id,
                    store_id,
                    quantity,
                    unit_price,
                    discount_pct,
                    total_amount,
                    payment_method,
                    customer_type
                FROM {self.industry}.sales
                LIMIT 10;
                """
            ),
            (
                "Sample products",
                f"""
                SELECT
                    product_id,
                    product_name,
                    category,
                    sub_category,
                    brand,
                    sku,
                    unit_cost,
                    margin_pct
                FROM {self.industry}.products
                LIMIT 10;
                """
            ),
           (
                "Sample stores",
                f"""
                SELECT
                    store_id,
                    store_name,
                    city,
                    region,
                    store_type,
                    sqft,
                    opened_date,
                    manager
                FROM {self.industry}.stores
                LIMIT 10;
                """
            ),
        ]

        for title, sql in demos:
            print(f"\n── {title}:")
            df = self.run(sql)
            if not df.empty:
                print(df.to_string(index=False))

    def demo_aggregation(self) -> None:
        """
        Run retail sales aggregation.
        """
        sql = f"""
        SELECT
            p.category,
            st.store_name,
            COUNT(s.sale_id) AS total_sales,
            SUM(s.quantity) AS total_units_sold,
            SUM(s.total_amount) AS total_revenue,
            AVG(s.total_amount) AS average_revenue_per_sale,
            AVG(s.discount_pct) AS average_discount_pct
        FROM {self.industry}.sales s
        JOIN {self.industry}.products p
            ON s.product_id = p.product_id
        JOIN {self.industry}.stores st
            ON s.store_id = st.store_id
        GROUP BY
            p.category,
            st.store_name
        ORDER BY total_revenue DESC;

         print("\n── Retail Revenue Aggregation by Category and Store:")
        df = self.run(sql)
        if not df.empty:
            print(df.to_string(index=False))


    def demo_joins(self) -> None:
        """
        """
        Run joined retail extract preview.
        """
        sql = f"""
        SELECT
            s.sale_id,
            s.sale_date,
            s.quantity,
            s.unit_price,
            s.discount_pct,
            s.total_amount,
            s.payment_method,
            s.customer_type,

            p.product_id,
            p.product_name,
            p.category,
            p.sub_category,
            p.brand,
            p.sku,
            p.unit_cost,
            p.margin_pct,

            st.store_id,
            st.store_name,
            st.city,
            st.region,
            st.store_type,
            st.sqft,
            st.opened_date,
            st.manager,

            r.return_id,
            r.return_date,
            r.reason AS return_reason,
            r.refund_amount,
            r.status AS return_status

        FROM {self.industry}.sales s
        JOIN {self.industry}.products p
            ON s.product_id = p.product_id
        JOIN {self.industry}.stores st
            ON s.store_id = st.store_id
        LEFT JOIN {self.industry}.returns r
            ON s.sale_id = r.sale_id
        LIMIT 10;
        """

        print("\n── Retail Joined Extract Preview:")
        df = self.run(sql)
        if not df.empty:
            print(df.to_string(index=False))

    def __str__(self) -> str:
        return f"SQLQueryRunner(industry={self.industry!r}, queries_run={len(self.history)})"

    def __repr__(self) -> str:
        return f"SQLQueryRunner(industry={self.industry!r})"