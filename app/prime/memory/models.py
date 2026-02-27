# app/prime/memory/models.py
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class PrimeConversationTurn(Base):
    """Every single message exchanged — raw, permanent."""
    __tablename__ = "prime_conversation_turns"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    session_id  = Column(String, index=True, nullable=False)
    user_id     = Column(String, index=True, nullable=False, default="raymond")
    role        = Column(String, nullable=False)   # "user" or "assistant"
    content     = Column(Text, nullable=False)
    timestamp   = Column(DateTime, default=datetime.utcnow)
    summarized  = Column(Boolean, default=False)   # True once folded into a summary


class PrimeMemorySummary(Base):
    """Compressed memory — what PRIME actually carries long-term."""
    __tablename__ = "prime_memory_summaries"

    id           = Column(Integer, primary_key=True, autoincrement=True)
    user_id      = Column(String, index=True, nullable=False, default="raymond")
    summary      = Column(Text, nullable=False)
    turn_range   = Column(String, nullable=False)  # e.g. "turns 1-20"
    created_at   = Column(DateTime, default=datetime.utcnow)
    archived     = Column(Boolean, default=False)
