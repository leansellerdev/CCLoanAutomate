from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

STATEMENTS_DIR = BASE_DIR / "statements"
PDFS_DIR = BASE_DIR / "pdfs"
TEMPLATES_DIR = BASE_DIR / "core/templates"
CREDS_DIR = BASE_DIR / "core/creds"
CASE_DIR = BASE_DIR / "cases"

DB_FILE = BASE_DIR / "db.sqlite3"
