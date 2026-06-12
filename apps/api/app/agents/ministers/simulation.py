"""Simulation Agent — runs synthetic stress-tests on policy options."""
import json
import time
import structlog
from typing import Any, Dict

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import settings
from app.agents.ministers.base import extract_json

logger = structlog.get_logger(__name__)


class SimulationAgent:
    role = "simulation_agent"
    title = "Simulation Agent"

    SYSTEM_PROMPT = """You are the TITAN Future Simulation Engine.
Your job is to simulate the long-term impact of a proposed policy across 4 distinct futures (Future A, Future B, Future C, Future D).

You must evaluate the policy against 5 core variables:
1. Budget
2. Population
3. Resources
4. Education
5. Infrastructure

You will return a synthetic outcome with scores out of 100 for:
- economic_score
- environment_score
- citizen_score (social impact)
- risk_score (feasibility/risk)

OUTPUT SCHEMA:
Return ONLY valid JSON:
{
  "future_name": "<Future A|B|C|D>",
  "option_name": "<name of the policy option being simulated>",
  "scenario_data": {
    "budget_impact": "<brief impact>",
    "population_impact": "<brief impact>",
    "resources_impact": "<brief impact>",
    "education_impact": "<brief impact>",
    "infrastructure_impact": "<brief impact>"
  },
  "economic_score": <0-100>,
  "environment_score": <0-100>,
  "citizen_score": <0-100>,
  "risk_score": <0-100>,
  "composite_score": <average of the four scores>,
  "risk_level": "<low|medium|high|critical>",
  "time_to_implement_months": <integer>,
  "cost_estimate_usd_millions": <float>,
  "projected_population_impact": <float millions>,
  "key_risks": ["<risk1>", "<risk2>"],
  "key_benefits": ["<benefit1>", "<benefit2>"]
}"""

    def _get_llm(self) -> ChatGoogleGenerativeAI:
        return ChatGoogleGenerativeAI(
            model=settings.GEMINI_FLASH_MODEL,
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0.7, # slightly higher temp for diverse futures
            max_output_tokens=settings.GEMINI_MAX_OUTPUT_TOKENS,
        )

    async def simulate(self, problem: str, option_name: str, future_designation: str) -> Dict[str, Any]:
        """Run a simulation for a specific policy option and future designation (A/B/C/D)."""
        llm = self._get_llm()

        user_msg = f"""PROBLEM: {problem}

POLICY OPTION TO SIMULATE: {option_name}
DESIGNATION: {future_designation}

Run the simulation engine on this policy. Consider how it interacts with budget, population, resources, education, and infrastructure. Output the required JSON format."""

        t0 = time.monotonic()
        try:
            resp = await llm.ainvoke([
                SystemMessage(content=self.SYSTEM_PROMPT),
                HumanMessage(content=user_msg),
            ])
            elapsed_ms = int((time.monotonic() - t0) * 1000)
            result = extract_json(str(resp.content))
            
            # Map risk_score to feasibility_score and citizen_score to social_score to match DB
            result["social_score"] = result.get("citizen_score", 50)
            result["feasibility_score"] = 100 - result.get("risk_score", 50) # lower risk = higher feasibility
            if "composite_score" not in result:
                result["composite_score"] = sum([
                    result.get("economic_score", 50),
                    result.get("environment_score", 50),
                    result.get("citizen_score", 50),
                    result.get("feasibility_score", 50)
                ]) / 4.0
                
            result["_elapsed_ms"] = elapsed_ms
            return result
        except Exception as exc:
            logger.error("Simulation failed", option=option_name, error=str(exc))
            return self._fallback_simulation(option_name, future_designation)

    def _fallback_simulation(self, option_name: str, future_designation: str) -> Dict[str, Any]:
        return {
            "future_name": future_designation,
            "option_name": option_name,
            "scenario_data": {},
            "economic_score": 50.0,
            "environment_score": 50.0,
            "citizen_score": 50.0,
            "social_score": 50.0,
            "risk_score": 50.0,
            "feasibility_score": 50.0,
            "composite_score": 50.0,
            "risk_level": "medium",
            "time_to_implement_months": 12,
            "cost_estimate_usd_millions": 0.0,
            "projected_population_impact": 0.0,
            "key_risks": ["Simulation error fallback"],
            "key_benefits": [],
        }

SIMULATION_AGENT = SimulationAgent()
