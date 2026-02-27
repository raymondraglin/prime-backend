"""
Directly create all PRIME tables using SQLAlchemy metadata.
Bypasses Alembic entirely — safe to run multiple times.
File: scripts/create_tables.py
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:newpassword123@localhost:5432/control_center"
)
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

from sqlalchemy import create_engine, inspect, text
from app.prime.models import Base

engine = create_engine(DATABASE_URL, echo=False)

print("Creating all PRIME tables...")
Base.metadata.create_all(engine)

# Verify
inspector = inspect(engine)
existing = sorted(inspector.get_table_names())
prime_tables = [
    "domains", "subjects", "subfields", "foundations",
    "corpus_documents", "corpus_chunks", "prime_notebook_entries",
    "study_jobs", "failure_cases", "prime_artifacts",
    "prime_memories", "prime_conversations", "prime_projects"
]

print(f"\nVerification:")
all_good = True
for t in prime_tables:
    exists = t in existing
    status = "✓" if exists else "✗ MISSING"
    print(f"  {status}  {t}")
    if not exists:
        all_good = False

if all_good:
    # Stamp alembic_version_prime so future alembic commands work correctly
    with engine.connect() as conn:
        conn.execute(text(
            "INSERT INTO alembic_version_prime (version_num) "
            "VALUES ('001_prime_data_spine') ON CONFLICT DO NOTHING"
        ))
        conn.commit()
    print("\n✓ All 13 tables created successfully.")
    print("✓ alembic_version_prime stamped.")
    print("\nNext: python scripts/seed_taxonomy.py")
else:
    print("\n✗ Some tables missing — check errors above.")

engine.dispose()