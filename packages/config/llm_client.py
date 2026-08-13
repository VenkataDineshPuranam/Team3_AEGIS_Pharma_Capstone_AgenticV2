"""LLM client -- Stage 20a Phase 5. Implements services/api/nodes/llm_interface.py's
LLMNodes protocol for two providers, selected by LLM_PROVIDER (.env.example documents
both):

  anthropic  -- Route A (ADR-009). The only provider whose output counts toward Stage
                20a's interim-assumption exit criteria.
  groq       -- dev-only substitute (user request, this session) for exercising the real
                call path while ANTHROPIC_API_KEY was being sorted. Defaults to a small/
                cheap model (GROQ_MODEL, default llama-3.1-8b-instant) to conserve
                tokens. Output from this provider is PROVISIONAL -- see .env.example's
                LLM_PROVIDER comment and ADR-009 SS"Model hosting route".

Both providers are prompted identically and parsed identically -- the only difference is
which SDK sends the request, which is the entire point of ADR-009's "one client interface"
guardrail: swapping providers is a constructor choice, not a prompt or parsing change.
"""
from __future__ import annotations

import json
import os

from pydantic import ValidationError

from packages.domain.evidence import Claim
from packages.domain.state import DecisionSupportOutput, GovernedState, ReasonCode

_SYNTHESIZE_SYSTEM = """You are the Batch-Review decision-support agent for a GxP pharmaceutical batch reconciliation system.

Your ONLY job is to summarize the reconciliation findings factually, citing evidence_ids for every claim. You must NEVER recommend, suggest, or imply a release, rejection, reprocessing, relabeling, or recall decision -- that decision belongs exclusively to a human Qualified Person. Do not use words like "release", "reject", "approve for release", "recommend", or "cleared".

Respond with ONLY a JSON object matching this shape, no other text:
{"summary": "<factual summary>", "claims": [{"text": "<claim text>", "cites": ["<evidence_id>", ...]}]}

Every claim MUST cite at least one evidence_id from the evidence provided. Do not fabricate evidence_ids."""

_CRITIC_SYSTEM = """You are the Critic/Verifier for a GxP batch reconciliation decision-support system. You review a draft summary for citation quality ONLY -- you do not evaluate whether the batch should be released.

Check:
1. Does every claim have at least one citation? If not: MISSING_CITATION
2. Do all cited evidence_ids exist in the provided evidence list? If not: CITATION_UNRESOLVED
3. Does any claim assert something the cited evidence does not support? If so: CLAIM_EXCEEDS_EVIDENCE
4. Does the draft read as a disposition signal (release/reject/approve/recall recommendation)? If so: PROHIBITION_ADJACENT
5. Otherwise: approve.

Respond with ONLY a JSON object, no other text:
{"verdict": "approve_for_human" or "reject", "reason_code": null or one of "MISSING_CITATION"/"CITATION_UNRESOLVED"/"CLAIM_EXCEEDS_EVIDENCE"/"CONTRACT_VIOLATION"/"PROHIBITION_ADJACENT"}"""


def _build_synthesize_user_prompt(state: GovernedState) -> str:
    payload = state["domain_payload"]
    evidence = [{"evidence_id": e.evidence_id, "status": e.status, "source": e.source} for e in state["evidence"]]
    findings = [f.model_dump() for f in payload.findings]
    return json.dumps({"batch_id": payload.batch_id, "findings": findings, "available_evidence": evidence})


def _build_critic_user_prompt(state: GovernedState) -> str:
    draft = state["draft_output"]
    evidence_ids = [e.evidence_id for e in state["evidence"]]
    return json.dumps({"draft": draft.model_dump(), "available_evidence_ids": evidence_ids})


def _parse_synthesize_response(text: str) -> DecisionSupportOutput:
    data = json.loads(text.strip().removeprefix("```json").removesuffix("```").strip())
    claims = tuple(Claim(text=c["text"], cites=tuple(c.get("cites", []))) for c in data["claims"])
    return DecisionSupportOutput(summary=data["summary"], claims=claims)


def _parse_critic_response(text: str) -> tuple[str, ReasonCode | None]:
    data = json.loads(text.strip().removeprefix("```json").removesuffix("```").strip())
    verdict = data["verdict"]
    reason_code = ReasonCode(data["reason_code"]) if data.get("reason_code") else None
    return verdict, reason_code


class AnthropicLLM:
    """Route A (ADR-009). Direct Anthropic API in dev/20a; Azure AI Foundry is the
    deployment-time binding behind this same interface (ADR-009 SS"Azure is the
    DEPLOYMENT target")."""

    def __init__(self, model: str | None = None):
        import anthropic

        self._client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        self._model = model or os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-5")

    def _call(self, system: str, user: str) -> tuple[str, int, int]:
        resp = self._client.messages.create(
            model=self._model, max_tokens=1024, system=system,
            messages=[{"role": "user", "content": user}],
        )
        return resp.content[0].text, resp.usage.input_tokens, resp.usage.output_tokens

    def synthesize(self, state: GovernedState) -> tuple[DecisionSupportOutput, int, int]:
        text, tin, tout = self._call(_SYNTHESIZE_SYSTEM, _build_synthesize_user_prompt(state))
        try:
            return _parse_synthesize_response(text), tin, tout
        except (json.JSONDecodeError, KeyError, ValidationError):
            return DecisionSupportOutput(summary="[PARSE_ERROR]", claims=()), tin, tout

    def critic(self, state: GovernedState) -> tuple[str, ReasonCode | None, int, int]:
        text, tin, tout = self._call(_CRITIC_SYSTEM, _build_critic_user_prompt(state))
        try:
            verdict, reason_code = _parse_critic_response(text)
        except (json.JSONDecodeError, KeyError, ValueError):
            verdict, reason_code = "reject", ReasonCode.CONTRACT_VIOLATION
        return verdict, reason_code, tin, tout


class GroqLLM:
    """Dev-only, provisional (see module docstring). OpenAI-compatible API -- reuses the
    `openai` SDK with Groq's base_url, no new dependency."""

    def __init__(self, model: str | None = None):
        import openai

        self._client = openai.OpenAI(api_key=os.environ["GROQ_API_KEY"], base_url="https://api.groq.com/openai/v1")
        self._model = model or os.environ.get("GROQ_MODEL", "llama-3.1-8b-instant")

    def _call(self, system: str, user: str) -> tuple[str, int, int]:
        resp = self._client.chat.completions.create(
            model=self._model,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        )
        text = resp.choices[0].message.content
        usage = resp.usage
        return text, usage.prompt_tokens, usage.completion_tokens

    def synthesize(self, state: GovernedState) -> tuple[DecisionSupportOutput, int, int]:
        text, tin, tout = self._call(_SYNTHESIZE_SYSTEM, _build_synthesize_user_prompt(state))
        try:
            return _parse_synthesize_response(text), tin, tout
        except (json.JSONDecodeError, KeyError, ValidationError):
            return DecisionSupportOutput(summary="[PARSE_ERROR]", claims=()), tin, tout

    def critic(self, state: GovernedState) -> tuple[str, ReasonCode | None, int, int]:
        text, tin, tout = self._call(_CRITIC_SYSTEM, _build_critic_user_prompt(state))
        try:
            verdict, reason_code = _parse_critic_response(text)
        except (json.JSONDecodeError, KeyError, ValueError):
            verdict, reason_code = "reject", ReasonCode.CONTRACT_VIOLATION
        return verdict, reason_code, tin, tout


def get_llm():
    """Provider selected by LLM_PROVIDER (.env.example). Raises KeyError with a clear
    message if the corresponding API key is absent -- callers should catch this the same
    way Phase 4's stub-vs-live test split treats a missing key: skip, don't fail."""
    provider = os.environ.get("LLM_PROVIDER", "anthropic")
    if provider == "anthropic":
        return AnthropicLLM()
    if provider == "groq":
        return GroqLLM()
    raise ValueError(f"Unknown LLM_PROVIDER {provider!r} -- expected 'anthropic' or 'groq'.")
