# app/prime/academic/__init__.py
from app.prime.academic.indexer import get_corpus_chunks, corpus_stats
from app.prime.academic.search import academic_search

__all__ = ["get_corpus_chunks", "corpus_stats", "academic_search"]
