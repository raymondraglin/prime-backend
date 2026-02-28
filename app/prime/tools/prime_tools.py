"""
PRIME Tools
File: app/prime/tools/prime_tools.py

OpenAI function-calling tool definitions and unified executor.

Tools (Layer A — codebase):
  read_file       — Read any file in the codebase
  list_directory  — List files in a directory
  search_codebase — Search for a pattern across files
  query_database  — Run a read-only SELECT on PostgreSQL

Tools (Layer B — web):
  web_search      — Search the web via configured provider (Brave/Tavily)
  fetch_url       — Fetch + clean text from a URL

Tools (Layer C — execution):
  run_python      — Execute a Python snippet in a sandboxed temp dir
  run_command     — Run a whitelisted shell command (pytest, ruff, mypy…)
"""

from __future__ import annotations

import asyncio
import concurrent.futures
import json
import os
from typing import Dict, Any

from app.prime.rag.file_reader import read_file, list_directory, search_codebase


# ---------------------------------------------------------------------------
# Helper: run async functions from sync context
# ---------------------------------------------------------------------------

def _run_async(coro) -> Any:
    """
    Execute a coroutine from a synchronous context.
    Works whether or not an event loop is already running.
    """
    try:
        asyncio.get_running_loop()
        # Already inside a running loop — run in a thread
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(asyncio.run, coro)
            return future.result()
    except RuntimeError:
        return asyncio.run(coro)


# ---------------------------------------------------------------------------
# TOOL DEFINITIONS — OpenAI function-calling schema
# ---------------------------------------------------------------------------

TOOL_DEFINITIONS = [
    # ── Layer A: Codebase tools ──────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": (
                "Read the full contents of a file in Raymond's codebase. "
                "Always read the file before answering questions about its contents."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative path from project root. Example: 'app/main.py'"
                    }
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_directory",
            "description": (
                "List all files and subdirectories at a given path. "
                "Use this to explore structure before reading specific files."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative path to directory. Use '.' for project root.",
                        "default": "."
                    }
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_codebase",
            "description": (
                "Search all files under a directory for a query string. "
                "Use this to find where a function, class, or pattern is defined or used."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "String to search for"
                    },
                    "directory": {
                        "type": "string",
                        "description": "Directory to search in. Default: 'app'",
                        "default": "app"
                    },
                    "file_extension": {
                        "type": "string",
                        "description": "File extension filter. Default: '.py'",
                        "default": ".py"
                    }
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "query_database",
            "description": (
                "Run a read-only SELECT query on Raymond's PostgreSQL database. "
                "Only SELECT statements are permitted."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "sql": {
                        "type": "string",
                        "description": "A read-only SELECT SQL query"
                    }
                },
                "required": ["sql"],
            },
        },
    },

    # ── Layer B: Web tools ─────────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": (
                "Search the web for current information, documentation, or answers. "
                "Use this when the user asks about latest versions, external libraries, "
                "or anything that requires real-time information beyond the codebase."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query string"
                    },
                    "k": {
                        "type": "integer",
                        "description": "Number of results to return (default: 5)",
                        "default": 5
                    }
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_url",
            "description": (
                "Fetch and read the text content of a specific URL. "
                "Use after web_search to read the full content of a search result. "
                "Also useful for reading API docs or GitHub pages."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "Full URL to fetch (must be https://)"
                    }
                },
                "required": ["url"],
            },
        },
    },

    # ── Layer C: Execution tools ─────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "run_python",
            "description": (
                "Execute a Python code snippet in a sandboxed temporary directory. "
                "Use this to verify logic, test calculations, or confirm a fix works "
                "before proposing it. Returns stdout, stderr, and exit code."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Python code to execute"
                    }
                },
                "required": ["code"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": (
                "Run a whitelisted shell command such as pytest, ruff, or mypy. "
                "Use this to run tests, lint checks, or type checks to verify patches. "
                "Only allowed commands will execute; others are blocked."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Shell command to run (e.g. 'pytest app/prime/tests/' or 'ruff check app/')"
                    }
                },
                "required": ["command"],
            },
        },
    },
]


# ---------------------------------------------------------------------------
# TOOL EXECUTOR
# ---------------------------------------------------------------------------

def execute_tool(tool_name: str, tool_args: Dict[str, Any]) -> str:
    """Execute a tool by name and return the result as a JSON string."""
    try:
        # ── Layer A: Codebase ────────────────────────────────────────
        if tool_name == "read_file":
            result = read_file(tool_args["path"])

        elif tool_name == "list_directory":
            result = list_directory(tool_args.get("path", "."))

        elif tool_name == "search_codebase":
            result = search_codebase(
                query=tool_args["query"],
                directory=tool_args.get("directory", "app"),
                file_extension=tool_args.get("file_extension", ".py"),
            )

        elif tool_name == "query_database":
            result = _query_database(tool_args["sql"])

        # ── Layer B: Web ─────────────────────────────────────────────
        elif tool_name == "web_search":
            from app.prime.tools.web_tools import search_web
            result = _run_async(search_web(
                tool_args["query"],
                k=tool_args.get("k", 5),
            ))

        elif tool_name == "fetch_url":
            from app.prime.tools.web_tools import fetch_url
            result = _run_async(fetch_url(tool_args["url"]))

        # ── Layer C: Execution ───────────────────────────────────────
        elif tool_name == "run_python":
            from app.prime.tools.exec_tools import run_python
            result = run_python(tool_args["code"])

        elif tool_name == "run_command":
            from app.prime.tools.exec_tools import run_command
            result = run_command(tool_args["command"])

        else:
            result = {"error": f"Unknown tool: {tool_name}"}

        return json.dumps(result, default=str)

    except Exception as exc:
        return json.dumps({"error": str(exc)})

# ─── PUSH 1: Live Tool Execution Layer ───────────────────────────────────────
TOOL_IMPLEMENTATIONS: dict = {}  # always defined, even if live layer fails

try:
    from app.prime.tools.live_tools import LIVE_TOOL_DEFINITIONS, LIVE_TOOL_IMPLEMENTATIONS

    if isinstance(TOOL_DEFINITIONS, list):
        TOOL_DEFINITIONS.extend(LIVE_TOOL_DEFINITIONS)

    TOOL_IMPLEMENTATIONS.update(LIVE_TOOL_IMPLEMENTATIONS)

except Exception as _live_tool_err:
    import logging
    logging.getLogger(__name__).warning(
        "Live tool layer failed to load: %s", _live_tool_err
    )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _query_database(sql: str) -> Dict:
    """Execute a read-only SQL query against PostgreSQL."""
    import sqlalchemy

    if not sql.strip().upper().startswith("SELECT"):
        return {"error": "Only SELECT queries are allowed."}

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        return {"error": "DATABASE_URL not set in environment."}

    try:
        engine = sqlalchemy.create_engine(database_url)
        with engine.connect() as conn:
            result = conn.execute(sqlalchemy.text(sql))
            rows = [dict(row._mapping) for row in result]
            return {"rows": rows[:50], "count": len(rows)}
    except Exception as exc:
        return {"error": str(exc)}
