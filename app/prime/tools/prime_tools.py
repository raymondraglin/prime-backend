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

Tools (Layer D — academic corpus):
  academic_search — Search external_corpus/ with vector, keyword, or hybrid mode

Tools (Layer E — GitHub):
  read_github_file      — Read a file from any public GitHub repo
  list_github_repo      — List files in a directory from any GitHub repo
  create_github_branch  — Create a new branch (requires GITHUB_TOKEN)
  push_github_file      — Commit and push a file (requires GITHUB_TOKEN)
  create_pull_request   — Open a PR (requires GITHUB_TOKEN)
  search_github_code    — Search code across all of GitHub (requires GITHUB_TOKEN)
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
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(asyncio.run, coro)
            return future.result()
    except RuntimeError:
        return asyncio.run(coro)


# ---------------------------------------------------------------------------
# TOOL DEFINITIONS — OpenAI function-calling schema
# ---------------------------------------------------------------------------

TOOL_DEFINITIONS = [
    # ── Layer A: Codebase tools ─────────────────────────────────────────────────
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

    # ── Layer B: Web tools ─────────────────────────────────────────────────────────
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

    # ── Layer C: Execution tools ─────────────────────────────────────────────────
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

    # ── Layer D: Academic corpus ──────────────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "academic_search",
            "description": (
                "Search PRIME's academic corpus (textbooks, papers, course notes) "
                "stored in external_corpus/. Uses pgvector semantic search by default. "
                "Supports three modes: 'vector' (semantic), 'keyword' (BM25), 'hybrid' (both). "
                "Returns ranked passages with source attribution."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Natural language academic search query"
                    },
                    "k": {
                        "type": "integer",
                        "description": "Number of results to return (default 5, max 20)",
                        "default": 5
                    },
                    "domain": {
                        "type": "string",
                        "description": (
                            "Optional corpus subdomain filter. Examples: "
                            "'cs_ict', 'math', 'healthcare', 'law', 'philosophy'"
                        )
                    },
                    "mode": {
                        "type": "string",
                        "description": (
                            "Search mode: 'auto' (default, picks best), 'vector' (semantic), "
                            "'keyword' (BM25), or 'hybrid' (vector + keyword reranking)"
                        ),
                        "default": "auto"
                    }
                },
                "required": ["query"],
            },
        },
    },

    # ── Layer E: GitHub ──────────────────────────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "read_github_file",
            "description": (
                "Read a file from any public GitHub repository. "
                "Use this to inspect code or docs from external projects."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "owner": {"type": "string", "description": "Repository owner (user or org)"},
                    "repo":  {"type": "string", "description": "Repository name"},
                    "path":  {"type": "string", "description": "File path within the repo"},
                    "ref":   {"type": "string", "description": "Branch or tag name (default: main)", "default": "main"},
                },
                "required": ["owner", "repo", "path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_github_repo",
            "description": (
                "List files and directories in a GitHub repository. "
                "Use this to explore structure before reading specific files."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "owner": {"type": "string", "description": "Repository owner"},
                    "repo":  {"type": "string", "description": "Repository name"},
                    "path":  {"type": "string", "description": "Directory path (empty for root)", "default": ""},
                    "ref":   {"type": "string", "description": "Branch or tag name (default: main)", "default": "main"},
                },
                "required": ["owner", "repo"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_github_branch",
            "description": (
                "Create a new branch in a GitHub repository you have write access to. "
                "Requires GITHUB_TOKEN. Use this before pushing changes."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "owner":       {"type": "string", "description": "Repository owner"},
                    "repo":        {"type": "string", "description": "Repository name"},
                    "branch":      {"type": "string", "description": "Name for the new branch"},
                    "from_branch": {"type": "string", "description": "Branch to create from (default: main)", "default": "main"},
                },
                "required": ["owner", "repo", "branch"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "push_github_file",
            "description": (
                "Commit and push a file to a GitHub repository. "
                "Creates new file if path doesn't exist; updates if it does. "
                "Requires GITHUB_TOKEN with repo scope."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "owner":   {"type": "string", "description": "Repository owner"},
                    "repo":    {"type": "string", "description": "Repository name"},
                    "path":    {"type": "string", "description": "File path in the repo"},
                    "content": {"type": "string", "description": "File content (UTF-8 text)"},
                    "message": {"type": "string", "description": "Commit message"},
                    "branch":  {"type": "string", "description": "Branch to push to (default: main)", "default": "main"},
                    "sha":     {"type": "string", "description": "Existing file SHA (for updates)"},
                },
                "required": ["owner", "repo", "path", "content", "message"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_pull_request",
            "description": (
                "Open a pull request from head branch to base branch. "
                "Requires GITHUB_TOKEN with repo scope."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "owner": {"type": "string", "description": "Repository owner"},
                    "repo":  {"type": "string", "description": "Repository name"},
                    "title": {"type": "string", "description": "PR title"},
                    "head":  {"type": "string", "description": "Branch containing changes"},
                    "base":  {"type": "string", "description": "Branch to merge into (default: main)", "default": "main"},
                    "body":  {"type": "string", "description": "PR description", "default": ""},
                },
                "required": ["owner", "repo", "title", "head"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_github_code",
            "description": (
                "Search code across all of GitHub using GitHub's code search. "
                "Use this to find examples, implementations, or usage patterns. "
                "Requires GITHUB_TOKEN."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Code search query (supports GitHub search syntax)"},
                    "k":     {"type": "integer", "description": "Number of results (default 5, max 30)", "default": 5},
                },
                "required": ["query"],
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
        # ── Layer A: Codebase ───────────────────────────────────────────────────
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

        # ── Layer B: Web ─────────────────────────────────────────────────────────────
        elif tool_name == "web_search":
            from app.prime.tools.web_tools import search_web
            result = _run_async(search_web(
                tool_args["query"],
                k=tool_args.get("k", 5),
            ))

        elif tool_name == "fetch_url":
            from app.prime.tools.web_tools import fetch_url
            result = _run_async(fetch_url(tool_args["url"]))

        # ── Layer C: Execution ────────────────────────────────────────────────────
        elif tool_name == "run_python":
            from app.prime.tools.exec_tools import run_python
            result = run_python(tool_args["code"])

        elif tool_name == "run_command":
            from app.prime.tools.exec_tools import run_command
            result = run_command(tool_args["command"])

        # ── Layer D: Academic corpus ───────────────────────────────────────────────
        elif tool_name == "academic_search":
            from app.prime.academic.search import academic_search
            hits = academic_search(
                query  = tool_args["query"],
                k      = tool_args.get("k", 5),
                domain = tool_args.get("domain"),
                mode   = tool_args.get("mode", "auto"),
            )
            result = {"query": tool_args["query"], "hits": hits, "count": len(hits)}

        # ── Layer E: GitHub ──────────────────────────────────────────────────────────
        elif tool_name == "read_github_file":
            from app.prime.tools.github_tools import read_github_file
            result = read_github_file(
                owner = tool_args["owner"],
                repo  = tool_args["repo"],
                path  = tool_args["path"],
                ref   = tool_args.get("ref", "main"),
            )

        elif tool_name == "list_github_repo":
            from app.prime.tools.github_tools import list_github_repo
            result = list_github_repo(
                owner = tool_args["owner"],
                repo  = tool_args["repo"],
                path  = tool_args.get("path", ""),
                ref   = tool_args.get("ref", "main"),
            )

        elif tool_name == "create_github_branch":
            from app.prime.tools.github_tools import create_github_branch
            result = create_github_branch(
                owner       = tool_args["owner"],
                repo        = tool_args["repo"],
                branch      = tool_args["branch"],
                from_branch = tool_args.get("from_branch", "main"),
            )

        elif tool_name == "push_github_file":
            from app.prime.tools.github_tools import push_github_file
            result = push_github_file(
                owner   = tool_args["owner"],
                repo    = tool_args["repo"],
                path    = tool_args["path"],
                content = tool_args["content"],
                message = tool_args["message"],
                branch  = tool_args.get("branch", "main"),
                sha     = tool_args.get("sha"),
            )

        elif tool_name == "create_pull_request":
            from app.prime.tools.github_tools import create_pull_request
            result = create_pull_request(
                owner = tool_args["owner"],
                repo  = tool_args["repo"],
                title = tool_args["title"],
                head  = tool_args["head"],
                base  = tool_args.get("base", "main"),
                body  = tool_args.get("body", ""),
            )

        elif tool_name == "search_github_code":
            from app.prime.tools.github_tools import search_github_code
            result = search_github_code(
                query = tool_args["query"],
                k     = tool_args.get("k", 5),
            )

        elif tool_name in TOOL_IMPLEMENTATIONS:
            result = TOOL_IMPLEMENTATIONS[tool_name](**tool_args)

        else:
            result = {"error": f"Unknown tool: {tool_name}"}

        return json.dumps(result, default=str)

    except Exception as exc:
        return json.dumps({"error": str(exc)})

# ─── PUSH 1: Live Tool Execution Layer ─────────────────────────────────────────────────────
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
