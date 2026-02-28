"""
PRIME Observability: Request Tracing
File: app/prime/observability/tracing.py

Structured tracing across the full request lifecycle:
  endpoint → orchestrator → LLM calls → tool calls → DB/web → response

Uses contextvars so the trace propagates automatically across async
calls without passing context objects around explicitly.

Usage:
    ctx = new_trace(session_id="abc123")
    with span("llm.call", model="deepseek-chat"):
        ...  # duration recorded automatically
    record_usage(model="deepseek-chat", prompt_tokens=100,
                 completion_tokens=200, total_tokens=300)
    ctx.emit()  # logs structured JSON

Emit strategy:
  Logs structured JSON to prime.trace logger now.
  Swap ctx.emit() for an OpenTelemetry exporter when ready.
"""

from __future__ import annotations

import json
import logging
import time
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Any, Generator, Optional
from uuid import uuid4

logger = logging.getLogger("prime.trace")


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class SpanRecord:
    name:       str
    start_time: float
    end_time:   float       = 0.0
    duration_ms: float      = 0.0
    attrs:      dict        = field(default_factory=dict)
    error:      Optional[str] = None

    def finish(self, error: Optional[str] = None) -> None:
        self.end_time    = time.monotonic()
        self.duration_ms = round((self.end_time - self.start_time) * 1000, 2)
        self.error       = error


@dataclass
class UsageRecord:
    model:             str
    prompt_tokens:     int
    completion_tokens: int
    total_tokens:      int
    recorded_at:       float = field(default_factory=time.monotonic)


@dataclass
class TraceContext:
    trace_id:   str
    session_id: Optional[str]
    request_id: str
    started_at: float = field(default_factory=time.monotonic)
    spans:      list[SpanRecord]  = field(default_factory=list)
    usage:      list[UsageRecord] = field(default_factory=list)
    metadata:   dict              = field(default_factory=dict)

    def total_duration_ms(self) -> float:
        return round((time.monotonic() - self.started_at) * 1000, 2)

    def total_tokens(self) -> int:
        return sum(u.total_tokens for u in self.usage)

    def tool_call_count(self) -> int:
        return sum(1 for s in self.spans if s.name.startswith("tool."))

    def tool_error_count(self) -> int:
        return sum(1 for s in self.spans if s.name.startswith("tool.") and s.error)

    def to_dict(self) -> dict[str, Any]:
        return {
            "trace_id":        self.trace_id,
            "session_id":      self.session_id,
            "request_id":      self.request_id,
            "total_duration_ms": self.total_duration_ms(),
            "total_tokens":    self.total_tokens(),
            "tool_call_count": self.tool_call_count(),
            "tool_error_count": self.tool_error_count(),
            "spans": [
                {"name": s.name, "duration_ms": s.duration_ms, "error": s.error, **s.attrs}
                for s in self.spans
            ],
            "usage": [
                {
                    "model":             u.model,
                    "prompt_tokens":     u.prompt_tokens,
                    "completion_tokens": u.completion_tokens,
                    "total_tokens":      u.total_tokens,
                }
                for u in self.usage
            ],
            "metadata": self.metadata,
        }

    def emit(self) -> None:
        """Emit trace as structured JSON. Swap for OTEL exporter when ready."""
        logger.info(json.dumps(self.to_dict()))


# ---------------------------------------------------------------------------
# Contextvar
# ---------------------------------------------------------------------------

_current_trace: ContextVar[Optional[TraceContext]] = ContextVar(
    "_current_trace", default=None
)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def new_trace(session_id: Optional[str] = None) -> TraceContext:
    """Create a new trace context and set it as the current trace."""
    ctx = TraceContext(
        trace_id=uuid4().hex,
        session_id=session_id,
        request_id=uuid4().hex,
    )
    _current_trace.set(ctx)
    return ctx


def get_trace() -> Optional[TraceContext]:
    """Return the current trace context, or None if not in a traced request."""
    return _current_trace.get()


@contextmanager
def span(name: str, **attrs: Any) -> Generator[SpanRecord, None, None]:
    """
    Context manager that records a named timing span.

    Usage:
        with span("tool.read_file", path="app/main.py") as s:
            result = read_file("app/main.py")
    """
    s     = SpanRecord(name=name, start_time=time.monotonic(), attrs=attrs)
    error: Optional[str] = None
    try:
        yield s
    except Exception as exc:
        error = str(exc)
        raise
    finally:
        s.finish(error=error)
        ctx = _current_trace.get()
        if ctx is not None:
            ctx.spans.append(s)


def record_usage(
    model:             str,
    prompt_tokens:     int,
    completion_tokens: int,
    total_tokens:      int,
) -> None:
    """Record LLM token usage into the current trace."""
    ctx = _current_trace.get()
    if ctx is None:
        return
    ctx.usage.append(UsageRecord(
        model=model,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
    ))
