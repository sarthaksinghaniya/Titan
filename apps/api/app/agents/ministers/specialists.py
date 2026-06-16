import asyncio
import json
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
    {"claim": "<claim from minister>", "status": "verified|refuted", "evidence_id": "<EV-123>", "evidence_source": "<source>"}
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


class ForecastingAgent(SpecialistAgent):
    role = "forecasting_agent"
    title = "Forecasting Engine"
    
    SCHEMA = """
{
  "scenario": "<scenario name>",
  "economic_score": 50,
  "infrastructure_score": 50,
  "technology_score": 50,
  "environmental_score": 50,
  "social_score": 50,
  "risk_level": "low|medium|high|critical",
  "key_risks": ["<risk 1>"],
  "key_benefits": ["<benefit 1>"],
  "assumptions": ["<explicit assumption 1>", "<explicit assumption 2>"],
  "cited_evidence_ids": ["<EV-123>", "<EV-456>"],
  "forecast_confidence": 85
}"""

    async def forecast_scenario(self, option: str, scenario: str, evidence_dossier: str) -> Dict[str, Any]:
        sys_prompt = f"""You are the TITAN Forecasting Engine. 
Evaluate the following policy option under the '{scenario}' scenario.
Score the predicted impact (0-100) across 5 domains: Economic, Infrastructure, Technology, Environmental, and Social.
You MUST base your forecast explicitly on the provided Evidence Dossier.
Do not speculate without citing specific evidence IDs. Be highly analytical and realistic."""
        user_msg = f"POLICY OPTION: {option}\n\nEVIDENCE DOSSIER:\n{evidence_dossier}\n\nReturn ONLY JSON:\n{self.SCHEMA}"
        
        try:
            resp = await ModelOrchestrator.call_model_with_resilience(
                ModelTask.FORECASTING,
                [SystemMessage(content=sys_prompt), HumanMessage(content=user_msg)]
            )
            return extract_json(str(resp.content))
        except Exception as e:
            logger.error("Forecasting failed", error=str(e))
            return {}


class ExecutiveReportingAgent(SpecialistAgent):
    role = "executive_reporting_agent"
    title = "Executive Intelligence Reporting"
    
    # Distinct logic dictionaries for audiences
    AUDIENCE_CONFIGS = {
        "Government": {
            "prompt": "You are the TITAN Executive Reporting Agent for Government. Focus strictly on policy implications, legislative changes, national security, and public sentiment.",
            "schema": """{
  "audience": "Government",
  "executive_summary": "<summary>",
  "policy_implications": ["<policy 1>"],
  "legislative_requirements": ["<req 1>"],
  "public_sentiment_risk": "<risk assessment>",
  "confidence_score": 90
}"""
        },
        "Enterprise": {
            "prompt": "You are the TITAN Executive Reporting Agent for Enterprise. Focus strictly on market impact, compliance costs, competitive advantages, and ROI implications.",
            "schema": """{
  "audience": "Enterprise",
  "executive_summary": "<summary>",
  "market_impact": ["<impact 1>"],
  "compliance_costs": ["<cost 1>"],
  "competitive_advantages": ["<advantage 1>"],
  "roi_forecast": {
    "projection": "<roi assessment>",
    "assumptions": ["<assumption 1>"],
    "cited_evidence_ids": ["<EV-123>"],
    "forecast_confidence": 85
  },
  "confidence_score": 90
}"""
        },
        "Investors": {
            "prompt": "You are the TITAN Executive Reporting Agent for Investors. Focus strictly on capital allocation, systemic market risks, startup opportunities, and yield curves.",
            "schema": """{
  "audience": "Investors",
  "executive_summary": "<summary>",
  "market_risks": ["<risk 1>"],
  "startup_opportunities": ["<opp 1>"],
  "capital_allocation_strategy": "<strategy>",
  "yield_forecast": {
    "projection": "<yield forecast>",
    "assumptions": ["<assumption 1>"],
    "cited_evidence_ids": ["<EV-123>"],
    "forecast_confidence": 85
  },
  "confidence_score": 90
}"""
        },
        "Universities": {
            "prompt": "You are the TITAN Executive Reporting Agent for Universities. Focus strictly on academic implications, research funding opportunities, theoretical shifts, and peer review needs.",
            "schema": """{
  "audience": "Universities",
  "executive_summary": "<summary>",
  "research_opportunities": ["<research 1>"],
  "theoretical_shifts": ["<shift 1>"],
  "grant_funding_areas": ["<funding 1>"],
  "confidence_score": 90
}"""
        }
    }

    async def extract_global_evidence(self, evidence_dossier: str) -> List[Dict[str, Any]]:
        """Extracts a SINGLE global evidence table to ensure absolute consistency across all audiences."""
        sys_prompt = "You are the TITAN Evidence Extraction Engine. Extract all concrete claims from the dossier."
        schema = """{
  "evidence_table": [ {"claim": "<claim>", "evidence_id": "<EV-123>", "source": "<source>", "confidence": 95} ]
}"""
        user_msg = f"DOSSIER:\n{evidence_dossier}\n\nReturn ONLY JSON:\n{schema}"
        try:
            resp = await ModelOrchestrator.call_model_with_resilience(
                ModelTask.SYNTHESIS,
                [SystemMessage(content=sys_prompt), HumanMessage(content=user_msg)]
            )
            return extract_json(str(resp.content)).get("evidence_table", [])
        except Exception as e:
            logger.error("Global evidence extraction failed", error=str(e))
            return []

    async def generate_report(self, final_report: Dict[str, Any], evidence_dossier: str, forecasting_results: List[Dict[str, Any]], audience: str, global_evidence: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        config = self.AUDIENCE_CONFIGS.get(audience, self.AUDIENCE_CONFIGS["Government"])
        sys_prompt = config["prompt"]
        schema = config["schema"]
        
        context_payload = {
            "final_report": final_report,
            "evidence": evidence_dossier[:2000],
            "forecasting": forecasting_results
        }
        
        user_msg = f"CONTEXT:\n{json.dumps(context_payload, indent=2)}\n\nGenerate the intelligence report for {audience}.\nReturn ONLY JSON:\n{schema}"
        
        try:
            resp = await ModelOrchestrator.call_model_with_resilience(
                ModelTask.SYNTHESIS,
                [SystemMessage(content=sys_prompt), HumanMessage(content=user_msg)]
            )
            result = extract_json(str(resp.content))
            result["audience"] = audience
            result["evidence_table"] = global_evidence or []  # Guarantee identical evidence across audiences
            return result
        except Exception as e:
            logger.error(f"Reporting failed for {audience}", error=str(e))
            return {"audience": audience, "error": "Synthesis failed"}
