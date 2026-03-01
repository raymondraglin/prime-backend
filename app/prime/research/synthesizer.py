# app/prime/research/synthesizer.py
"""
PRIME Research Synthesizer

Takes all findings from the conductor phase and synthesizes them into
a single coherent research report.

Design:
  - Builds a synthesis prompt with all sub-question findings
  - Calls LLM at temperature=0.4 (slightly warmer for prose quality)
  - Extracts citations from the synthesis reply
  - Merges synthesis citations with finding-level citations (deduped by source)
  - Returns (report_text, all_citations_list)

The synthesizer is the only phase where PRIME is writing final prose.
The conductor phase is evidence-gathering. This phase is the argument.
"""
from __future__ import annotations


async def synthesize_findings(
    query: str,
    findings: list[dict],
    depth: str = "standard",
) -> tuple[str, list[dict]]:
    """
    Synthesize conductor findings into a final research report.

    Returns:
        (report_text, merged_citations_list)
    """
    from app.prime.llm.client import PrimeLLMClient, LLMConfig, LLMMessage
    from app.prime.llm.prompt_builder import CITATION_RULES
    from app.prime.citations.extractor import extract_citations

    client = PrimeLLMClient(config=LLMConfig(temperature=0.4, max_tokens=4096))

    findings_block = "\n\n".join(
        f"FINDING {f['index']} — {f['sub_question']}\n"
        f"{f['answer'][:800]}"
        for f in findings
    )

    system = (
        "You are PRIME. You have completed a multi-step research task. "
        "Your job now is to synthesize the findings below into one authoritative, "
        "coherent report. Rules:\n"
        "  - Write in flowing, direct prose. No bullet points.\n"
        "  - Lead with the most important insight.\n"
        "  - Integrate findings naturally — do not just list them sequentially.\n"
        "  - Be specific. Reference actual file names, function names, column names "
        "  wherever findings mention them.\n"
        "  - Cite sources inline using [CITE: ...] wherever a finding cites a source.\n"
        "  - Do not invent sources not mentioned in the findings.\n"
        + CITATION_RULES
    )

    user_msg = (
        f"Original research query: {query}\n"
        f"Research depth: {depth} ({len(findings)} sub-questions answered)\n\n"
        f"FINDINGS:\n\n{findings_block}\n\n"
        "Write the final synthesized research report now."
    )

    messages = [
        LLMMessage(role="system", content=system),
        LLMMessage(role="user",   content=user_msg),
    ]

    resp         = await client.chat(messages)
    report_text  = resp.text
    synth_cites  = resp.citations or []

    # Merge synthesis-level citations with finding-level citations (deduped by source)
    all_citations: list[dict] = list(synth_cites)
    seen_sources: set[str]    = {c.get("source", "") for c in synth_cites}

    for f in findings:
        for c in f.get("citations", []):
            src = c.get("source", "")
            if src and src not in seen_sources:
                seen_sources.add(src)
                all_citations.append({**c, "index": len(all_citations) + 1})

    return report_text, all_citations
