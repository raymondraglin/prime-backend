# app/prime/llm/client.py
from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

import httpx
from pydantic import BaseModel, Field


class LLMConfig(BaseModel):
    base_url: str = "https://api.deepseek.com"
    model: str = "deepseek-chat"
    max_completion_tokens: int = 4096
    temperature: float = 0.85
    top_p: float = 0.9
    timeout: float = 120.0


class LLMMessage(BaseModel):
    role: str
    content: str


class LLMResponse(BaseModel):
    text:              str
    model:             str            = ""
    prompt_tokens:     Optional[int]  = None
    completion_tokens: Optional[int]  = None
    tool_calls:        list[dict]     = Field(default_factory=list)
    rounds:            int            = 0


class PrimeLLMClient:
    def __init__(self, config: Optional[LLMConfig] = None):
        self.config = config or LLMConfig()

    def _headers(self) -> Dict[str, str]:
        api_key = os.environ.get("DEEPSEEK_API_KEY", "")
        if not api_key:
            raise RuntimeError("DEEPSEEK_API_KEY is not set in environment.")
        return {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    async def chat(self, messages: List[LLMMessage]) -> LLMResponse:
        payload = {
            "model": self.config.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "max_completion_tokens": self.config.max_completion_tokens,
            "temperature": self.config.temperature,
            "top_p": self.config.top_p,
            "stream": False,
        }
        async with httpx.AsyncClient(timeout=self.config.timeout) as client:
            response = await client.post(
                f"{self.config.base_url}/v1/chat/completions",
                json=payload,
                headers=self._headers(),
            )
            response.raise_for_status()
            data = response.json()

        choice = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {})
        return LLMResponse(
            text=choice.strip(),
            model=data.get("model", self.config.model),
            prompt_tokens=usage.get("prompt_tokens"),
            completion_tokens=usage.get("completion_tokens"),
        )

    async def chat_with_tools(
        self,
        messages: List[LLMMessage],
        tools: List[Dict[str, Any]],
        max_tool_rounds: int = 6,
        force_first_tool: Optional[str] = None,
    ) -> LLMResponse:
        from app.prime.tools.prime_tools import execute_tool

        msg_list: List[Dict[str, Any]] = [
            {"role": m.role, "content": m.content} for m in messages
        ]

        recorded_tool_calls: list[dict] = []
        rounds_completed:    int        = 0

        for _round in range(max_tool_rounds):
            if _round == 0 and force_first_tool:
                tool_choice_val: Any = {
                    "type": "function",
                    "function": {"name": force_first_tool},
                }
            elif _round == 0:
                tool_choice_val = "required"
            else:
                tool_choice_val = "auto"

            payload = {
                "model": self.config.model,
                "messages": msg_list,
                "max_completion_tokens": self.config.max_completion_tokens,
                "temperature": self.config.temperature,
                "top_p": self.config.top_p,
                "stream": False,
                "tools": tools,
                "tool_choice": tool_choice_val,
            }

            async with httpx.AsyncClient(timeout=self.config.timeout) as client:
                response = await client.post(
                    f"{self.config.base_url}/v1/chat/completions",
                    json=payload,
                    headers=self._headers(),
                )
                response.raise_for_status()
                data = response.json()

            choice = data["choices"][0]["message"]
            tool_calls = choice.get("tool_calls") or []

            if not tool_calls:
                text = choice.get("content") or ""
                usage = data.get("usage", {})
                return LLMResponse(
                    text=text.strip(),
                    model=data.get("model", self.config.model),
                    prompt_tokens=usage.get("prompt_tokens"),
                    completion_tokens=usage.get("completion_tokens"),
                    tool_calls=recorded_tool_calls,
                    rounds=rounds_completed,
                )

            msg_list.append(
                {
                    "role": "assistant",
                    "content": choice.get("content"),
                    "tool_calls": tool_calls,
                }
            )

            for tc in tool_calls:
                tool_name = tc["function"]["name"]
                try:
                    tool_args = json.loads(tc["function"]["arguments"])
                except (json.JSONDecodeError, KeyError):
                    tool_args = {}

                import time
                t0     = time.perf_counter()
                result = execute_tool(tool_name, tool_args)
                dur_ms = (time.perf_counter() - t0) * 1000

                print(f"[PRIME tool] {tool_name}({tool_args}) \u2192 {result[:120]}")

                recorded_tool_calls.append({
                    "name":        tool_name,
                    "args":        tool_args,
                    "result":      result[:500],
                    "duration_ms": round(dur_ms, 2),
                    "error":       None,
                })
                msg_list.append(
                    {
                        "role":         "tool",
                        "tool_call_id": tc["id"],
                        "content":      result,
                    }
                )

            rounds_completed += 1

        # Max rounds hit — ask for a plain summary
        msg_list.append({"role": "user", "content": "Summarize what you found."})
        safe_msgs = [
            LLMMessage(role=m["role"], content=str(m.get("content") or ""))
            for m in msg_list
            if m.get("role") in ("user", "assistant", "system") and m.get("content")
        ]
        return await self.chat(safe_msgs)

    async def stream_chat(
        self,
        messages: List[LLMMessage],
    ):
        payload = {
            "model":                self.config.model,
            "messages":             [{"role": m.role, "content": m.content} for m in messages],
            "max_completion_tokens": self.config.max_completion_tokens,
            "temperature":          self.config.temperature,
            "top_p":                self.config.top_p,
            "stream":               True,
        }
        async with httpx.AsyncClient(timeout=self.config.timeout) as client:
            async with client.stream(
                "POST",
                f"{self.config.base_url}/v1/chat/completions",
                json=payload,
                headers=self._headers(),
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line.startswith("data:"):
                        continue
                    raw = line[5:].strip()
                    if raw == "[DONE]":
                        break
                    try:
                        chunk = json.loads(raw)
                        delta = chunk["choices"][0]["delta"].get("content")
                        if delta:
                            yield delta
                    except (json.JSONDecodeError, KeyError, IndexError):
                        continue

    async def chat_or_fallback(
        self,
        messages: List[LLMMessage],
        fallback_text: str,
    ) -> LLMResponse:
        try:
            return await self.chat(messages)
        except Exception as e:
            print(f"[PRIME LLM] Generation error: {e!r}")
            return LLMResponse(text=fallback_text)


prime_llm = PrimeLLMClient()
