import asyncio
import time
from typing import Any, Dict, List, Optional

import structlog
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import settings
from app.agents.ministers.base import extract_json
from app.agents.orchestrator import ModelOrchestrator, ModelTask

logger = structlog.get_logger(__name__)

class SpecialistAgent:
    """Base class for new specialist intelligence nodes."""
    role: str = ""
    title: str = ""
    model_tier: str = "flash"
    
    def _get_llm(self) -> BaseChatModel:
        # Default for base specialist, overridden or parameterized by subclasses
        return ModelOrchestrator.get_model(ModelTask.RESEARCH)


class FactCheckerAgent(SpecialistAgent):
    role = "fact_checker_agent"
    title = "Fact Verification Agent"
    
    SCHEMA = """
{
  "agent_role": "fact_checker_agent",
  "phase": "fact_check",
  "verified_claims": [
    {"claim": "<claim from minister>", "status": "verified|refuted", "evidence_citation": "<source>"}
  ],
  "contradictions_detected": [
    {"minister": "<role>", "contradiction": "<description>"}
  ],
  "unsupported_conclusions": [
    {"minister": "<role>", "conclusion": "<unsupported claim>"}
  ],
  "overall_confidence_score": 85,
  "summary": "<short audit summary>"
}"""

    async def audit_analyses(self, problem: str, all_analyses: List[Dict[str, Any]], evidence_dossier: str) -> Dict[str, Any]:
        """Runs after the initial analysis fan-out to flag hallucinations and unsupported claims."""
        analyses_ctx = "\n\n".join(
            f"[{a.get('role_title', a.get('agent_role', '?'))}]\n"
            f"Assessment: {a.get('situation_assessment', '')}\n"
            f"Solutions: {'; '.join(a.get('proposed_solutions', []))}\n"
            f"Cited Sources: {'; '.join(a.get('cited_sources', []))}"
            for a in all_analyses
        )

        sys_prompt = """You are the Fact Verification Agent.
Your mandate is strictly to verify claims made by the ministers against the provided Evidence Dossier.
Detect contradictions, identify unsupported conclusions, and verify factual accuracy.
Be clinical, objective, and unforgiving of hallucinations. Do not participate in the debate, only output the verified findings."""

        user_msg = f"""PROBLEM: {problem}

VERIFIED EVIDENCE DOSSIER:
{evidence_dossier}

MINISTERIAL ANALYSES:
{analyses_ctx}

Audit these analyses. Return ONLY JSON:
{self.SCHEMA}"""

        try:
            resp = await ModelOrchestrator.call_model_with_resilience(
                ModelTask.VALIDATION,
                [SystemMessage(content=sys_prompt), HumanMessage(content=user_msg)]
            )
            result = extract_json(str(resp.content))
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
        llm = ModelOrchestrator.get_model(ModelTask.FORECASTING)
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
        llm = ModelOrchestrator.get_model(ModelTask.FORECASTING)
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
        llm = ModelOrchestrator.get_model(ModelTask.FORECASTING)
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
