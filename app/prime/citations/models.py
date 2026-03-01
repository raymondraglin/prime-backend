# app/prime/citations/models.py
"""
PRIME Citation Model

A Citation is a single inline source reference that PRIME embeds
in its response text using the [CITE: source | title | snippet] format.

Fields:
  index         -- auto-incremented number, becomes [1], [2], etc. in response
  source        -- file path, corpus path, URL, goal ID, or memory ID
  title         -- human-readable label for the source
  snippet       -- the specific passage, column, or finding cited
  citation_type -- 'file' | 'corpus' | 'memory' | 'goal' | 'web'
"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class Citation:
    index:         int
    source:        str
    title:         str
    snippet:       str
    citation_type: str = "file"   # file | corpus | memory | goal | web

    def to_dict(self) -> dict:
        return {
            "index":         self.index,
            "source":        self.source,
            "title":         self.title,
            "snippet":       self.snippet,
            "citation_type": self.citation_type,
        }
