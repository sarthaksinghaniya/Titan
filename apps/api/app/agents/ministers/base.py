"""
Base Minister Agent
===================
Abstract base that every minister inherits from.
Enforces a consistent interface: system_prompt, goals, constraints,
analysis_schema, and an async invoke() that always returns structured JSON.
"""
from __future__ import annotations

import asyncio
import json
import re
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

import structlog
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import settings

logger = structlog.get_logger(__name__)


# ──────────────────────────────────────────────────────────────
# JSON extraction helper
# ──────────────────────────────────────────────────────────────

def extract_json(text: str) -> Dict[str, Any]:
    """
    Robustly extract a JSON object from an LLM response.
    Strategy:
      1. Strip markdown code fences
      2. Try full-string parse
      3. Find the outermost { ... } block
      4. Return empty dict if all fail (caller handles gracefully)
    """
    # Strip ```json ... ``` fences
    cleaned = re.sub(r"```(?:json)?\s*", "", text).replace("```", "").strip()

    # 1 — direct parse
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # 2 — find outermost braces
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(cleaned[start : end + 1])
        except json.JSONDecodeError:
            pass

    logger.warning("JSON extraction failed", preview=text[:120])
    return {}


# ──────────────────────────────────────────────────────────────
# Abstract Base Agent
# ──────────────────────────────────────────────────────────────

class BaseMinisterAgent(ABC):
    """
    Every minister is a stateless callable.
    Subclasses define:
      - role            : machine identifier  e.g. "economic_minister"
      - title           : display name        e.g. "Economic Minister"
      - system_prompt   : full persona + instruction block
      - goals           : what this minister tries to achieve
      - constraints     : hard limits on their recommendations
      - model_tier      : "flash" | "pro"
    """

    # ── Override in subclasses ─────────────────────────────────
    role: str = ""
    title: str = ""
    system_prompt: str = ""
    goals: List[str] = []
    constraints: List[str] = []
    model_tier: str = "flash"        # "flash" for speed, "pro" for quality

    # ── Shared output schema injected into every prompt ────────
    ANALYSIS_SCHEMA = """
Return ONLY a valid JSON object — no markdown, no explanation before or after:
{
  "agent_role": "<your role key>",
  "role_title": "<your title>",
  "situation_assessment": "<2-3 sentence assessment of the problem>",
  "primary_goal": "<single sentence: what you are trying to achieve>",
  "key_findings": ["<finding 1>", "<finding 2>", "<finding 3>"],
  "proposed_solutions": [
    "<solution 1 with brief rationale>",
    "<solution 2 with brief rationale>",
    "<solution 3 with brief rationale>"
  ],
  "constraints_applied": ["<constraint 1>", "<constraint 2>"],
  "red_lines": ["<condition you will never accept 1>", "<condition 2>"],
  "evidence_score": <0-100 integer>,
  "cited_evidence_ids": ["<EV-123>", "<EV-456>"],
  "assumptions_challenged": ["<assumption 1>", "<assumption 2>"],
  "priority_score": <0-100 integer>
}"""

    DEBATE_SCHEMA = """
Return ONLY a valid JSON object:
{
  "agent_role": "<your role key>",
  "round_number": <integer>,
  "phase": "<debate|opposition_attack|rebuttal>",
  "argument": "<your full argument, 150-250 words>",
  "attacking_roles": ["<roles you are challenging>"],
  "defending_positions": ["<positions you are protecting>"],
  "concessions": ["<points you accept from others>"],
  "new_evidence": ["<new data or reasoning you introduce>"],
  "contradictions_detected": ["<contradiction 1>", "<contradiction 2>"],
  "cited_evidence_ids": ["<EV-123>", "<EV-456>"],
  "word_count": <integer>
}"""

    VOTE_SCHEMA = """
Return ONLY a valid JSON object:
{
  "agent_role": "<your role key>",
  "voted_option": "<exact option name from the list>",
  "justification": "<2-3 sentences explaining your vote>",
  "second_choice": "<your fallback option>",
  "veto_options": ["<options you actively oppose and why — format: option: reason>"]
}"""

    def _get_task(self) -> str:
        # We will determine the task based on context, but default to DEBATE
        # so ministers get reasoning models.
        from app.agents.orchestrator import ModelTask
        return ModelTask.DEBATE

    async def analyze(self, problem: str, context: str = "", evidence_dossier: str = "") -> Dict[str, Any]:
        """Phase 1 — independent analysis. Returns MinisterOutput dict."""
        llm = self._get_llm()
        goals_block = "\n".join(f"  - {g}" for g in self.goals)
        constraints_block = "\n".join(f"  - {c}" for c in self.constraints)

        evidence_block = f"\nEVIDENCE DOSSIER:\n{evidence_dossier}\n\nCRITICAL RULE: You MUST ground your key findings and proposed solutions in the provided Evidence Dossier. Do NOT invent statistics or cite nonexistent studies." if evidence_dossier else ""

        user_msg = f"""PROBLEM SUBMITTED TO CABINET:
{problem}

{f"ADDITIONAL CONTEXT: {context}" if context else ""}
{evidence_block}

YOUR GOALS:
{goals_block}

YOUR CONSTRAINTS:
{constraints_block}

Analyze this problem from your ministerial perspective.
{self.ANALYSIS_SCHEMA}"""

        from app.agents.orchestrator import ModelOrchestrator
        t0 = time.monotonic()
        try:
            resp = await ModelOrchestrator.call_model_with_resilience(
                self._get_task(),
                [
                    SystemMessage(content=self.system_prompt),
                    HumanMessage(content=user_msg),
                ]
            )
            elapsed_ms = int((time.monotonic() - t0) * 1000)
            result = extract_json(str(resp.content))
            result.setdefault("agent_role", self.role)
            result.setdefault("role_title", self.title)
            result["_elapsed_ms"] = elapsed_ms
            
            # Deterministic Confidence Calculation
            findings_score = min(len(result.get("key_findings", [])), 3) / 3.0 * 35.0
            solutions_score = min(len(result.get("proposed_solutions", [])), 2) / 2.0 * 35.0
            sources_score = min(len(result.get("cited_evidence_ids", [])), 2) / 2.0 * 30.0
            result["confidence"] = round(findings_score + solutions_score + sources_score)
            
            return result
        except Exception as exc:
            logger.error("Minister analysis error", role=self.role, error=str(exc))
            return self._fallback_analysis(str(exc))

    async def debate(
        self,
        problem: str,
        all_analyses: List[Dict[str, Any]],
        round_number: int = 1,
        phase: str = "debate",
        prior_arguments: Optional[List[Dict[str, Any]]] = None,
        fact_check_report: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Phase 2/4 — debate argument or rebuttal. Returns DebateArgument dict."""

        analyses_ctx = "\n\n".join(
            f"[{a.get('role_title', a.get('agent_role', '?'))}]\n"
            f"Assessment: {a.get('situation_assessment', '')}\n"
            f"Solutions: {'; '.join(a.get('proposed_solutions', []))}"
            for a in all_analyses
        )

        prior_ctx = ""
        if prior_arguments:
            prior_ctx = "\n\nPREVIOUS ARGUMENTS:\n" + "\n".join(
                f"[{p.get('agent_role','')} - {p.get('phase','')}]: {p.get('argument','')[:200]}..."
                for p in prior_arguments[-6:]
            )

        fact_check_ctx = ""
        if fact_check_report:
            fact_check_ctx = f"\n\nFACT CHECK REPORT:\nContradictions detected: {fact_check_report.get('contradictions_detected', [])}\nUnsupported conclusions: {fact_check_report.get('unsupported_conclusions', [])}"

        user_msg = f"""PROBLEM: {problem}

MINISTERIAL ANALYSES:
{analyses_ctx}
{prior_ctx}
{fact_check_ctx}

You are in ROUND {round_number} — PHASE: {phase.upper()}.
{"ATTACK the weakest proposals. Challenge assumptions. Expose contradictions." if phase == "opposition_attack" else ""}
{"DEFEND your positions with new evidence. Concede only what is logically indefensible." if phase == "rebuttal" else ""}
{"Engage with other ministers' proposals. Build coalitions or challenge opponents." if phase == "debate" else ""}

{self.DEBATE_SCHEMA}"""

        from app.agents.orchestrator import ModelOrchestrator
        try:
            resp = await ModelOrchestrator.call_model_with_resilience(
                self._get_task(),
                [
                    SystemMessage(content=self.system_prompt),
                    HumanMessage(content=user_msg),
                ]
            )
            result = extract_json(str(resp.content))
            result.setdefault("agent_role", self.role)
            result.setdefault("round_number", round_number)
            result.setdefault("phase", phase)
            word_count = len(result.get("argument", "").split())
            result.setdefault("word_count", word_count)
            
            # Deterministic Confidence Calculation
            length_score = min(word_count, 150) / 150.0 * 40.0
            evidence_score = min(len(result.get("new_evidence", [])), 2) / 2.0 * 30.0
            sources_score = min(len(result.get("cited_evidence_ids", [])), 2) / 2.0 * 30.0
            
            penalty = 0
            if fact_check_report:
                for c in fact_check_report.get("contradictions_detected", []):
                    if isinstance(c, dict) and c.get("minister") == self.role:
                        penalty += 20
            
            result["confidence_score"] = max(0, round(length_score + evidence_score + sources_score - penalty))
            
            return result
        except Exception as exc:
            logger.error("Minister debate error", role=self.role, phase=phase, error=str(exc))
            return self._fallback_debate(round_number, phase, str(exc))

    async def vote(
        self,
        problem: str,
        policy_options: List[str],
        all_analyses: List[Dict[str, Any]],
        all_debates: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Phase 5 — cast vote. Returns VoteRecord dict."""

        options_block = "\n".join(f"  {i+1}. {opt}" for i, opt in enumerate(policy_options))
        debate_ctx = "\n".join(
            f"[{d.get('agent_role','')} - {d.get('phase','')}]: {d.get('argument','')[:120]}..."
            for d in all_debates[-10:]
        )

        user_msg = f"""PROBLEM: {problem}

POLICY OPTIONS ON THE TABLE:
{options_block}

DEBATE SUMMARY:
{debate_ctx}

You must now VOTE for the option that best serves your ministerial mandate.
Your goals: {'; '.join(self.goals[:2])}
Your constraints: {'; '.join(self.constraints[:2])}

{self.VOTE_SCHEMA}"""

        from app.agents.orchestrator import ModelOrchestrator
        try:
            resp = await ModelOrchestrator.call_model_with_resilience(
                self._get_task(),
                [
                    SystemMessage(content=self.system_prompt),
                    HumanMessage(content=user_msg),
                ]
            )
            result = extract_json(str(resp.content))
            result.setdefault("agent_role", self.role)
            result.setdefault("voted_option", policy_options[0] if policy_options else "Option 1")
            result.setdefault("second_choice", policy_options[1] if len(policy_options) > 1 else "")
            result.setdefault("veto_options", [])
            
            # Deterministic Confidence Calculation
            just_len = len(result.get("justification", "").split())
            just_score = min(just_len, 50) / 50.0 * 50.0
            veto_score = min(len(result.get("veto_options", [])), 2) / 2.0 * 50.0
            result["confidence_score"] = round(just_score + veto_score)
            
            return result
        except Exception as exc:
            logger.error("Minister vote error", role=self.role, error=str(exc))
            return self._fallback_vote(policy_options, str(exc))

    # ── Fallback helpers (graceful degradation) ────────────────

    def _fallback_analysis(self, error: str) -> Dict[str, Any]:
        return {
            "agent_role": self.role,
            "role_title": self.title,
            "situation_assessment": f"Analysis unavailable due to error: {error[:100]}",
            "primary_goal": self.goals[0] if self.goals else "",
            "key_findings": [],
            "proposed_solutions": [],
            "constraints_applied": self.constraints,
            "red_lines": [],
            "priority_score": 50,
            "confidence": 0,
        }

    def _fallback_debate(self, round_number: int, phase: str, error: str) -> Dict[str, Any]:
        return {
            "agent_role": self.role,
            "round_number": round_number,
            "phase": phase,
            "argument": f"[{self.title} could not respond: {error[:80]}]",
            "attacking_roles": [],
            "defending_positions": [],
            "concessions": [],
            "new_evidence": [],
            "word_count": 0,
        }

    def _fallback_vote(self, options: List[str], error: str) -> Dict[str, Any]:
        return {
            "agent_role": self.role,
            "voted_option": options[0] if options else "Abstain",
            "confidence_score": 0.0,
            "justification": f"Vote cast by default due to error: {error[:80]}",
            "second_choice": options[1] if len(options) > 1 else "",
            "veto_options": [],
        }
