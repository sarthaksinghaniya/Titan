import asyncio
import time
from typing import Any, Dict, List, Optional

import structlog
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import settings
from app.agents.ministers.base import extract_json

logger = structlog.get_logger(__name__)

class SpecialistAgent:
    """Base class for new specialist intelligence nodes."""
    role: str = ""
    title: str = ""
    model_tier: str = "flash"
    
    def _get_llm(self) -> ChatGoogleGenerativeAI:
        if self.model_tier == "pro":
            return ChatGoogleGenerativeAI(
                model=settings.GEMINI_PRO_MODEL,
                google_api_key=settings.GEMINI_API_KEY,
                temperature=0.4,
                max_output_tokens=8192,
            )
        return ChatGoogleGenerativeAI(
            model=settings.GEMINI_FLASH_MODEL,
            google_api_key=settings.GEMINI_API_KEY,
            temperature=settings.GEMINI_TEMPERATURE,
            max_output_tokens=settings.GEMINI_MAX_OUTPUT_TOKENS,
        )


class FactCheckerAgent(SpecialistAgent):
    role = "fact_checker_agent"
    title = "Fact Checker"
    
    SCHEMA = """
{
  "agent_role": "fact_checker_agent",
  "phase": "fact_check",
  "argument": "<your full audit report, identifying specific unsupported claims or logical contradictions from the ministers. Include corrections.>",
  "attacking_roles": ["<roles you are correcting>"],
  "defending_positions": [],
  "concessions": [],
  "new_evidence": ["<evidence you bring to correct the record>"],
  "contradictions_detected": ["<contradiction 1>"],
  "cited_sources": ["<source 1>"],
  "confidence_score": 90,
  "word_count": <integer>
}"""

    async def audit_analyses(self, problem: str, all_analyses: List[Dict[str, Any]], evidence_dossier: str) -> Dict[str, Any]:
        """Runs after the initial analysis fan-out to flag hallucinations."""
        llm = self._get_llm()
        analyses_ctx = "\n\n".join(
            f"[{a.get('role_title', a.get('agent_role', '?'))}]\n"
            f"Assessment: {a.get('situation_assessment', '')}\n"
            f"Solutions: {'; '.join(a.get('proposed_solutions', []))}\n"
            f"Cited Sources: {'; '.join(a.get('cited_sources', []))}"
            for a in all_analyses
        )

        sys_prompt = """You are the Fact Checker Agent.
Your job is to audit the ministers' claims against the provided Evidence Dossier.
If a minister invented a statistic, flag it. If their proposed solution contradicts the data, expose it.
Be clinical, objective, and unforgiving of hallucinations."""

        user_msg = f"""PROBLEM: {problem}

VERIFIED EVIDENCE DOSSIER:
{evidence_dossier}

MINISTERIAL ANALYSES:
{analyses_ctx}

Audit these analyses. Return ONLY JSON:
{self.SCHEMA}"""

        try:
            resp = await asyncio.wait_for(
                llm.ainvoke([SystemMessage(content=sys_prompt), HumanMessage(content=user_msg)]),
                timeout=settings.AGENT_TIMEOUT_SECONDS
            )
            result = extract_json(str(resp.content))
            result["round_number"] = 0
            return result
        except Exception as e:
            logger.error("Fact check failed", error=str(e))
            return {}


class RiskAgent(SpecialistAgent):
    role = "risk_agent"
    title = "Risk Agent"
    model_tier = "pro"

    SCHEMA = """
{
  "black_swan_crisis": "<Name of the crisis>",
  "black_swan_impact": "<Description of how it shatters the proposed policy>",
  "resilience_score": <0-100 integer>
}"""

    async def generate_black_swan(self, policy: str) -> Dict[str, Any]:
        llm = self._get_llm()
        sys_prompt = """You are the Risk Agent (formerly Black Swan Engine).
Your job is to invent a highly disruptive, low-probability 'Tail Risk' or 'Black Swan' event 
that perfectly exploits the weaknesses in the provided policy.
Do not be generic. Be surgical."""

        user_msg = f"FINAL POLICY:\n{policy}\n\nGenerate the crisis JSON:\n{self.SCHEMA}"
        try:
            resp = await asyncio.wait_for(
                llm.ainvoke([SystemMessage(content=sys_prompt), HumanMessage(content=user_msg)]),
                timeout=settings.AGENT_TIMEOUT_SECONDS
            )
            return extract_json(str(resp.content))
        except Exception:
            return {}


class EconomicForecastAgent(SpecialistAgent):
    role = "economic_forecast_agent"
    title = "Economic Forecaster"
    
    SCHEMA = """
{
  "economic_score": <0-100>,
  "cost_estimate_usd_millions": <integer>,
  "projected_population_impact": <float millions>,
  "fiscal_analysis": "<Brief economic impact summary>"
}"""

    async def forecast(self, option: str) -> Dict[str, Any]:
        llm = self._get_llm()
        sys_prompt = "You are the Economic Forecast Agent. Quantitatively model the fiscal impact of this policy option."
        user_msg = f"OPTION: {option}\n\nReturn JSON:\n{self.SCHEMA}"
        try:
            resp = await asyncio.wait_for(
                llm.ainvoke([SystemMessage(content=sys_prompt), HumanMessage(content=user_msg)]),
                timeout=settings.AGENT_TIMEOUT_SECONDS
            )
            return extract_json(str(resp.content))
        except Exception:
            return {}


class ScenarioPlanningAgent(SpecialistAgent):
    role = "scenario_planning_agent"
    title = "Scenario Planner"
    
    SCHEMA = """
{
  "social_score": <0-100>,
  "environmental_score": <0-100>,
  "feasibility_score": <0-100>,
  "risk_level": "<low|medium|high|critical>",
  "key_risks": ["<risk 1>"],
  "key_benefits": ["<benefit 1>"]
}"""

    async def plan_scenario(self, option: str, future_context: str) -> Dict[str, Any]:
        llm = self._get_llm()
        sys_prompt = f"You are the Scenario Planning Agent. Evaluate this policy under the '{future_context}' future scenario."
        user_msg = f"OPTION: {option}\n\nReturn JSON:\n{self.SCHEMA}"
        try:
            resp = await asyncio.wait_for(
                llm.ainvoke([SystemMessage(content=sys_prompt), HumanMessage(content=user_msg)]),
                timeout=settings.AGENT_TIMEOUT_SECONDS
            )
            return extract_json(str(resp.content))
        except Exception:
            return {}
