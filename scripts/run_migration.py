"""
Full fix: isolate prime-backend Alembic + run migration directly.
File: scripts/run_migration.py
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
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

engine = create_engine(DATABASE_URL, echo=False)

with engine.connect() as conn:
    print("Step 1: Clean up shared alembic_version (remove our test insert)...")
    conn.execute(text(
        "DELETE FROM alembic_version WHERE version_num = '001_prime_data_spine'"
    ))
    conn.commit()
    rows = conn.execute(text("SELECT * FROM alembic_version")).fetchall()
    print(f"  alembic_version now: {rows}")

    print("\nStep 2: Create prime-backend isolated version table...")
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS alembic_version_prime (
            version_num VARCHAR(32) NOT NULL,
            CONSTRAINT alembic_version_prime_pkc PRIMARY KEY (version_num)
        )
    """))
    conn.commit()
    print("  alembic_version_prime table created (or already exists).")

    print("\nStep 3: Check if PRIME tables already exist...")
    result = conn.execute(text("""
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_name IN (
            'domains','subjects','subfields','foundations',
            'corpus_documents','corpus_chunks','prime_notebook_entries',
            'study_jobs','failure_cases','prime_artifacts',
            'prime_memories','prime_conversations','prime_projects'
        )
        ORDER BY table_name
    """))
    existing = [r[0] for r in result.fetchall()]
    print(f"  Existing PRIME tables: {existing if existing else 'none'}")

    if len(existing) == 13:
        print("\n  All 13 tables already exist!")
        print("  Stamping alembic_version_prime as complete...")
        conn.execute(text(
            "INSERT INTO alembic_version_prime (version_num) "
            "VALUES ('001_prime_data_spine') ON CONFLICT DO NOTHING"
        ))
        conn.commit()
        print("  Done. Migration already complete.")
    else:
        print(f"\n  {13 - len(existing)} tables missing. Stamping base...")
        conn.execute(text(
            "INSERT INTO alembic_version_prime (version_num) "
            "VALUES ('001_prime_data_spine') ON CONFLICT DO NOTHING"
        ))
        conn.commit()
        print("  Stamped. Now run: alembic upgrade head")
        print("  (after updating env.py with version_table='alembic_version_prime')")

engine.dispose()
print("\nScript complete.")