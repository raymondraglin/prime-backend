# app/prime/llm/client.py
from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

import httpx
from pydantic import BaseModel


class LLMConfig(BaseModel):
    base_url: str = "https://api.deepseek.com"
    model: str = "deepseek-chat"
    max_tokens: int = 2048
    temperature: float = 0.85
    top_p: float = 0.9
    timeout: float = 120.0


class LLMMessage(BaseModel):
    role: str
    content: str


class LLMResponse(BaseModel):
    text: str
    model: str = ""
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None


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
            "max_tokens": self.config.max_tokens,
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
        """
        Chat with OpenAI-compatible function calling.
        Automatically executes tool calls and loops until the model returns
        a final plain-text reply.

        Args:
            force_first_tool: If set, round 0 will force the model to call
                this specific tool (e.g. 'list_directory') before anything
                else. Subsequent rounds use tool_choice='auto'. This is the
                'evidence-first' enforcement: PRIME must read before it speaks.
                Example: force_first_tool='list_directory'
        """
        from app.prime.tools.prime_tools import execute_tool

        msg_list: List[Dict[str, Any]] = [
            {"role": m.role, "content": m.content} for m in messages
        ]

        for _round in range(max_tool_rounds):
            # ── tool_choice logic ─────────────────────────────────────────────
            if _round == 0 and force_first_tool:
                # Force a specific tool — evidence-first enforcement.
                # PRIME must call list_directory (or whichever tool is named)
                # before generating any prose on repo/code questions.
                tool_choice_val: Any = {
                    "type": "function",
                    "function": {"name": force_first_tool},
                }
            elif _round == 0:
                # Still require A tool on round 0, just not a specific one
                tool_choice_val = "required"
            else:
                tool_choice_val = "auto"

            payload = {
                "model": self.config.model,
                "messages": msg_list,
                "max_tokens": self.config.max_tokens,
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
                )

            # Append assistant message with tool_calls
            msg_list.append(
                {
                    "role": "assistant",
                    "content": choice.get("content"),
                    "tool_calls": tool_calls,
                }
            )

            # Execute each tool and append results
            for tc in tool_calls:
                tool_name = tc["function"]["name"]
                try:
                    tool_args = json.loads(tc["function"]["arguments"])
                except (json.JSONDecodeError, KeyError):
                    tool_args = {}
                result = execute_tool(tool_name, tool_args)
                print(f"[PRIME tool] {tool_name}({tool_args}) → {result[:120]}")
                msg_list.append(
                    {
                        "role": "tool",
                        "tool_call_id": tc["id"],
                        "content": result,
                    }
                )

        # Max rounds hit — ask for a plain summary
        msg_list.append({"role": "user", "content": "Summarize what you found."})
        safe_msgs = [
            LLMMessage(role=m["role"], content=str(m.get("content") or ""))
            for m in msg_list
            if m.get("role") in ("user", "assistant", "system") and m.get("content")
        ]
        return await self.chat(safe_msgs)

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
