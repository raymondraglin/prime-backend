"""
PRIME Tools
File: app/prime/tools/prime_tools.py

OpenAI function-calling tool definitions and handlers.
These are the tools PRIME can invoke autonomously when answering.

Tools:
  read_file       -- Read any file in the codebase
  list_directory  -- List files in a directory
  search_codebase -- Search for a pattern across files
  query_database  -- Run a read-only SQL SELECT on PostgreSQL
"""

from __future__ import annotations

import json
import os
from typing import Dict, Any

from app.prime.rag.file_reader import read_file, list_directory, search_codebase


# ---------------------------------------------------------------------------
# TOOL DEFINITIONS -- OpenAI function calling schema
# ---------------------------------------------------------------------------

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": (
                "Read the full contents of a file in Raymond's codebase. "
                "Use this when you need to see actual code, config, or any file. "
                "Always read the file before answering questions about its contents."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative path from project root. Example: 'app/main.py' or 'app/prime/api/genius.py'"
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
                "List all files and subdirectories at a given path in the codebase. "
                "Use this to explore the project structure before reading specific files."
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
                "Use this to find where a function, class, variable, or pattern is defined or used. "
                "Returns matching file paths and line previews."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "String to search for (function name, class, variable, pattern)"
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
                "Use this to inspect table schemas, row counts, or data. "
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
]


# ---------------------------------------------------------------------------
# TOOL EXECUTOR
# ---------------------------------------------------------------------------

def execute_tool(tool_name: str, tool_args: Dict[str, Any]) -> str:
    """Execute a tool by name and return the result as a JSON string."""
    try:
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

        else:
            result = {"error": f"Unknown tool: {tool_name}"}

        return json.dumps(result, default=str)

    except Exception as e:
        return json.dumps({"error": str(e)})


def _query_database(sql: str) -> Dict:
    """Execute a read-only SQL query against PostgreSQL."""
    import sqlalchemy

    sql_stripped = sql.strip().upper()
    if not sql_stripped.startswith("SELECT"):
        return {"error": "Only SELECT queries are allowed. No INSERT, UPDATE, DELETE, DROP, etc."}

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        return {"error": "DATABASE_URL not set in environment."}

    try:
        engine = sqlalchemy.create_engine(database_url)
        with engine.connect() as conn:
            result = conn.execute(sqlalchemy.text(sql))
            rows = [dict(row._mapping) for row in result]
            return {"rows": rows[:50], "count": len(rows)}  # Cap at 50 rows
    except Exception as e:
        return {"error": str(e)}
