"""
Fix Alembic version conflict and run PRIME migration.
File: scripts/fix_alembic.py
"""

from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv(Path(__file__).resolve().parents[1] / ".env")
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:newpassword123@localhost:5432/control_center"
)

# Force psycopg2 driver if not specified
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

engine = create_engine(DATABASE_URL, echo=False)

with engine.connect() as conn:
    # Step 1: Show current state
    rows = conn.execute(text("SELECT * FROM alembic_version")).fetchall()
    print(f"Current alembic_version rows: {rows}")

    # Step 2: Insert prime-backend revision alongside existing one
    # alembic_version supports multiple rows (one per branch head)
    conn.execute(text(
        "INSERT INTO alembic_version (version_num) "
        "VALUES ('001_prime_data_spine') "
        "ON CONFLICT DO NOTHING"
    ))
    conn.commit()

    # Step 3: Confirm
    rows = conn.execute(text("SELECT * FROM alembic_version")).fetchall()
    print(f"After fix alembic_version rows: {rows}")
    print("Done. Now run: alembic upgrade head")

engine.dispose()