# app/prime/research/models.py
"""
PRIME Research Models

Data structures for the multi-step research pipeline:
  ResearchSubQuestion  -- one focused question from the planner
  ResearchFinding      -- answer + citations for one sub-question
  ResearchReport       -- final synthesized output across all findings
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class ResearchSubQuestion:
    index:    int
    question: str
    focus:    str = ""

    def to_dict(self) -> dict:
        return {"index": self.index, "question": self.question, "focus": self.focus}


@dataclass
class ResearchFinding:
    index:           int
    sub_question:    str
    focus:           str
    answer:          str
    citations:       list[dict] = field(default_factory=list)
    tool_calls_made: list[str]  = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "index":           self.index,
            "sub_question":    self.sub_question,
            "focus":           self.focus,
            "answer":          self.answer,
            "citations":       self.citations,
            "tool_calls_made": self.tool_calls_made,
        }


@dataclass
class ResearchReport:
    query:                   str
    depth:                   str
    plan:                    list[dict]
    findings:                list[dict]
    report:                  str
    citations:               list[dict]
    sub_questions_answered:  int
    sources_consulted:       int
    assembled_at:            str

    def to_dict(self) -> dict:
        return {
            "query":                  self.query,
            "depth":                  self.depth,
            "plan":                   self.plan,
            "findings":               self.findings,
            "report":                 self.report,
            "citations":              self.citations,
            "sub_questions_answered": self.sub_questions_answered,
            "sources_consulted":      self.sources_consulted,
            "assembled_at":           self.assembled_at,
        }
