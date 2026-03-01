# app/prime/tools/github_tools.py
"""
PRIME GitHub Tools

Wrappers around subprocess git commands and GitHub REST API.

Tools:
  read_github_file      -- Read a file from any public GitHub repo
  list_github_repo      -- List files in a directory from any public GitHub repo
  create_github_branch  -- Create a new branch in a repo (requires GITHUB_TOKEN)
  push_github_file      -- Commit and push a file to a branch (requires GITHUB_TOKEN)
  create_pull_request   -- Open a PR from one branch to another (requires GITHUB_TOKEN)
  search_github_code    -- Search code across all of GitHub (requires GITHUB_TOKEN)

Security:
  - All write operations require GITHUB_TOKEN env var
  - Read-only operations work against any public repo
  - Token must have repo scope for push/PR operations

Design note:
  These are thin wrappers. Complex orchestration (e.g. multi-file commits,
  PR reviews) should happen in higher-level reasoning code, not here.
"""
from __future__ import annotations

import os
import subprocess
from typing import Dict, Any

import httpx


def _github_headers() -> Dict[str, str]:
    token = os.getenv("GITHUB_TOKEN", "")
    if not token:
        return {"Accept": "application/vnd.github+json"}
    return {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def read_github_file(owner: str, repo: str, path: str, ref: str = "main") -> Dict[str, Any]:
    """
    Read a file from a GitHub repository.
    Works with any public repo. Private repos require GITHUB_TOKEN.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    params = {"ref": ref}
    try:
        resp = httpx.get(url, headers=_github_headers(), params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data.get("type") != "file":
            return {"error": f"{path} is not a file (type: {data.get('type')})"}
        import base64
        content = base64.b64decode(data["content"]).decode("utf-8", errors="replace")
        return {
            "path":    path,
            "content": content,
            "sha":     data["sha"],
            "size":    data["size"],
            "url":     data["html_url"],
        }
    except httpx.HTTPStatusError as e:
        return {"error": f"HTTP {e.response.status_code}: {e.response.text[:200]}"}
    except Exception as e:
        return {"error": str(e)}


def list_github_repo(owner: str, repo: str, path: str = "", ref: str = "main") -> Dict[str, Any]:
    """
    List contents of a directory in a GitHub repository.
    Returns {files: [...], directories: [...]}.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    params = {"ref": ref}
    try:
        resp = httpx.get(url, headers=_github_headers(), params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if not isinstance(data, list):
            return {"error": f"{path} is not a directory"}
        files = []
        directories = []
        for item in data:
            if item["type"] == "file":
                files.append({"name": item["name"], "path": item["path"], "size": item["size"]})
            elif item["type"] == "dir":
                directories.append({"name": item["name"], "path": item["path"]})
        return {"path": path, "files": files, "directories": directories}
    except httpx.HTTPStatusError as e:
        return {"error": f"HTTP {e.response.status_code}: {e.response.text[:200]}"}
    except Exception as e:
        return {"error": str(e)}


def create_github_branch(owner: str, repo: str, branch: str, from_branch: str = "main") -> Dict[str, Any]:
    """
    Create a new branch in a GitHub repository.
    Requires GITHUB_TOKEN with repo scope.
    """
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        return {"error": "GITHUB_TOKEN not set -- required for branch creation"}

    try:
        # 1. Get SHA of from_branch HEAD
        ref_url = f"https://api.github.com/repos/{owner}/{repo}/git/refs/heads/{from_branch}"
        ref_resp = httpx.get(ref_url, headers=_github_headers(), timeout=10)
        ref_resp.raise_for_status()
        sha = ref_resp.json()["object"]["sha"]

        # 2. Create new branch
        create_url = f"https://api.github.com/repos/{owner}/{repo}/git/refs"
        payload = {"ref": f"refs/heads/{branch}", "sha": sha}
        create_resp = httpx.post(create_url, headers=_github_headers(), json=payload, timeout=10)
        create_resp.raise_for_status()

        return {
            "branch": branch,
            "from_branch": from_branch,
            "sha": sha,
            "url": f"https://github.com/{owner}/{repo}/tree/{branch}",
        }
    except httpx.HTTPStatusError as e:
        return {"error": f"HTTP {e.response.status_code}: {e.response.text[:200]}"}
    except Exception as e:
        return {"error": str(e)}


def push_github_file(
    owner: str,
    repo: str,
    path: str,
    content: str,
    message: str,
    branch: str = "main",
    sha: str | None = None,
) -> Dict[str, Any]:
    """
    Commit and push a file to a GitHub repository.
    If sha is provided, this updates an existing file. Otherwise, creates new.
    Requires GITHUB_TOKEN with repo scope.
    """
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        return {"error": "GITHUB_TOKEN not set -- required for push operations"}

    import base64
    encoded = base64.b64encode(content.encode("utf-8")).decode("utf-8")
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    payload: Dict[str, Any] = {
        "message": message,
        "content": encoded,
        "branch": branch,
    }
    if sha:
        payload["sha"] = sha

    try:
        resp = httpx.put(url, headers=_github_headers(), json=payload, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        return {
            "path": path,
            "sha": data["content"]["sha"],
            "url": data["content"]["html_url"],
            "commit_sha": data["commit"]["sha"],
            "message": message,
        }
    except httpx.HTTPStatusError as e:
        return {"error": f"HTTP {e.response.status_code}: {e.response.text[:300]}"}
    except Exception as e:
        return {"error": str(e)}


def create_pull_request(
    owner: str,
    repo: str,
    title: str,
    head: str,
    base: str = "main",
    body: str = "",
) -> Dict[str, Any]:
    """
    Create a pull request from head branch to base branch.
    Requires GITHUB_TOKEN with repo scope.
    """
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        return {"error": "GITHUB_TOKEN not set -- required for PR creation"}

    url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
    payload = {"title": title, "head": head, "base": base, "body": body}
    try:
        resp = httpx.post(url, headers=_github_headers(), json=payload, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return {
            "number": data["number"],
            "title": data["title"],
            "url": data["html_url"],
            "state": data["state"],
            "head": head,
            "base": base,
        }
    except httpx.HTTPStatusError as e:
        return {"error": f"HTTP {e.response.status_code}: {e.response.text[:300]}"}
    except Exception as e:
        return {"error": str(e)}


def search_github_code(query: str, k: int = 5) -> Dict[str, Any]:
    """
    Search code across all of GitHub using GitHub's code search API.
    Requires GITHUB_TOKEN (even for public repos -- API rate limits).
    """
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        return {"error": "GITHUB_TOKEN not set -- required for GitHub code search"}

    url = "https://api.github.com/search/code"
    params = {"q": query, "per_page": min(k, 30)}
    try:
        resp = httpx.get(url, headers=_github_headers(), params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        hits = []
        for item in data.get("items", [])[:k]:
            hits.append({
                "name": item["name"],
                "path": item["path"],
                "repo": item["repository"]["full_name"],
                "url": item["html_url"],
            })
        return {"query": query, "total_count": data.get("total_count", 0), "hits": hits}
    except httpx.HTTPStatusError as e:
        return {"error": f"HTTP {e.response.status_code}: {e.response.text[:200]}"}
    except Exception as e:
        return {"error": str(e)}
