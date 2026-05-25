# ================================================================
# config.py — Module 06 Configuration
# ================================================================
# WHAT THIS FILE DOES:
#   Provides a single, shared source of truth for:
#     - Which industry we are analysing (INDUSTRY)
#     - Where the input data lives (DATA_PATH)
#     - Where to save outputs (REPORTS_DIR)
#     - How to log messages (logger)
#
# ALL OTHER FILES import from here. Change a setting once → updated everywhere.
# ================================================================

import os
import pathlib
import logging
from dotenv import load_dotenv

# Load variables from .env into os.environ
# The .env file stores secrets (passwords, API keys) — it is never committed to Git
load_dotenv()

# ── INDUSTRY SETTING ─────────────────────────────────────────────
# The teaching project always uses bootcamp_data (GlobalTech workforce data)
# Students change this to their industry schema in their projects
INDUSTRY = os.getenv("INDUSTRY", "retail")
LEARNER_SCHEMA = os.getenv("LEARNER_SCHEMA", "learner_45")

# ── PROJECT PATHS ─────────────────────────────────────────────────
# pathlib.Path(__file__) → path to THIS file (config.py)
# .resolve() → convert to absolute path (no relative ".." parts)
# .parent → go up one folder (from config.py's folder to the project root)
PROJECT_ROOT = pathlib.Path(__file__).resolve().parent

# Data folder: where processed-data.csv lives
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
SQL_DIR = PROJECT_ROOT / "sql"
REPORTS_DIR = PROJECT_ROOT / "reports"

DATA_DIR.mkdir(exist_ok=True)
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
SQL_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)

# Input: processed-data.csv from Module 05
# This is the CLEAN data — Module 05 already fixed nulls, types, and duplicates
RAW_DATA_PATH = RAW_DATA_DIR / "raw-data.csv"
PROCESSED_DATA_PATH = PROCESSED_DATA_DIR / "processed-data.csv"

# Keep DATA_PATH for EDAEngine compatibility
DATA_PATH = PROCESSED_DATA_PATH

# Output: where analysis reports and anomaly CSVs are saved
# REPORTS_DIR already created above

# ── ANALYSIS SETTINGS ─────────────────────────────────────────────
# How many top groups to show in the report (e.g. top 8 departments by salary)
TOP_N_GROUPS = 8

# Minimum correlation strength to include in the report
# Below 0.3 is considered "negligible" in business analytics
CORRELATION_THRESHOLD = 0.3

# ── VALIDATION SETTINGS ───────────────────────────────────────────
MAX_NULL_PERCENT = 50.0
MAX_DUPLICATE_PERCENT = 5.0

# ── LOGGER SETUP ──────────────────────────────────────────────────
# Logger explains what is happening step by step.
# Much better than print() because:
#   - Includes timestamp automatically
#   - Has severity levels: INFO, WARNING, ERROR
#   - Can be redirected to files without changing any code

def _setup_logger() -> logging.Logger:
    """
    Create and return the shared project logger.

    All modules import this logger:
        from config import logger
        logger.info("Starting analysis...")
    """
    lgr = logging.getLogger("module06")
    lgr.setLevel(logging.INFO)

    if not lgr.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        ))
        lgr.addHandler(handler)

    return lgr

# Create the shared logger — all files import this
logger = _setup_logger()

# DB_URL comes entirely from .env — no fallback with credentials here.
# If .env is missing or DB_URL is not set, DB_AVAILABLE will be False
# and the project will tell you clearly what to do.
DB_URL = os.getenv("DB_URL", "")

try:
    from sqlalchemy import create_engine, text

    if not DB_URL:
        raise ValueError("DB_URL not set. Check your .env file.")

    engine = create_engine(
        DB_URL,
        pool_pre_ping=True,
        connect_args={"connect_timeout": 10}
    )

    with engine.connect() as c:
        c.execute(text("SELECT 1"))

    DB_AVAILABLE = True
    logger.info("Database connection successful.")

except Exception as e:
    logger.warning(f"Database not connected. Check your .env file — {e}")
    engine = None
    DB_AVAILABLE = False