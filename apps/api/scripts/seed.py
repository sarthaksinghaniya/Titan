"""Seed data script for TITAN database."""
import asyncio
import uuid
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.core.database import AsyncSessionLocal, engine
from app.models.session import (
    Project, Agent, Debate, Vote, Simulation, FinalReport,
    ProjectStatus, AgentRole, RiskLevel
)
from datetime import datetime, timezone

async def seed_data():
    async with AsyncSessionLocal() as db:
        print("Creating seed project...")
        project_id = uuid.uuid4()
        project = Project(
            id=project_id,
            title="Transition to 100% Renewable Energy Grid by 2035",
            problem="The nation needs to completely transition its energy grid to renewable sources to meet climate targets without causing economic collapse or energy poverty.",
            context="Current grid is 60% fossil fuels. Budget deficit is at 3%.",
            status=ProjectStatus.COMPLETED,
            metadata_={"winning_option": "Phased Nuclear-Renewable Hybrid", "vote_percentage": 83.3, "consensus_level": "high"},
            completed_at=datetime.now(timezone.utc)
        )
        db.add(project)
        await db.commit()

        print("Creating agent analyses...")
        agent1 = Agent(
            project_id=project_id,
            role=AgentRole.ECONOMIC_MINISTER,
            model_used="gemini-1.5-flash",
            analysis="The economic impact of a rapid transition will cause initial shock but long-term gains.",
            key_points=["High upfront capital cost", "Stranded assets risk", "Green jobs creation"],
            proposed_solutions=["Phased Nuclear-Renewable Hybrid", "Aggressive Carbon Tax with Dividend"],
            concerns=["Inflationary pressure on electricity prices", "Industrial competitiveness drop"],
            tokens_used=1200,
            processing_ms=1500
        )
        agent2 = Agent(
            project_id=project_id,
            role=AgentRole.ENVIRONMENT_MINISTER,
            model_used="gemini-1.5-flash",
            analysis="We must act immediately. Climate tipping points are approaching.",
            key_points=["Significant emissions drop", "Biodiversity co-benefits", "Air quality improvement"],
            proposed_solutions=["100% Distributed Renewables", "Phased Nuclear-Renewable Hybrid"],
            concerns=["Ecological impact of mining for batteries", "Land use for solar farms"],
            tokens_used=1150,
            processing_ms=1400
        )
        db.add_all([agent1, agent2])
        await db.commit()
        await db.refresh(agent1)

        print("Creating debates...")
        debate1 = Debate(
            project_id=project_id,
            agent_id=agent1.id,
            round_number=1,
            argument="While the environmental benefits are clear, we cannot afford to bankrupt the industrial sector. We need baseload power that only a hybrid approach provides.",
            supporting_agents=[AgentRole.INFRASTRUCTURE_MINISTER.value],
            opposing_agents=[AgentRole.ENVIRONMENT_MINISTER.value],
            word_count=45
        )
        db.add(debate1)
        await db.commit()

        print("Creating votes...")
        vote1 = Vote(
            project_id=project_id,
            agent_id=agent1.id,
            voted_option="Phased Nuclear-Renewable Hybrid",
            confidence_score=90.0,
            justification="Best balance of economic stability and emissions reduction."
        )
        db.add(vote1)
        await db.commit()

        print("Creating simulation results...")
        sim1 = Simulation(
            project_id=project_id,
            option_name="Phased Nuclear-Renewable Hybrid",
            option_description="Keep existing nuclear, build new modular reactors, expand solar/wind.",
            economic_score=85.0,
            social_score=75.0,
            environmental_score=92.0,
            feasibility_score=80.0,
            composite_score=83.0,
            risk_level=RiskLevel.MEDIUM,
            time_to_implement_months=120,
            cost_estimate_usd_millions=50000.0,
            projected_population_impact=15.0,
            key_risks=["Nuclear waste storage", "Cost overruns"],
            key_benefits=["Stable baseload", "Zero carbon"],
            scenario_data={"base": "success"}
        )
        db.add(sim1)
        await db.commit()

        print("Creating final report...")
        report = FinalReport(
            project_id=project_id,
            chosen_option="Phased Nuclear-Renewable Hybrid",
            executive_summary="The cabinet has reached consensus on a hybrid approach prioritizing both economic stability and climate action.",
            overall_rationale="Provides baseload power while maximizing renewable expansion.",
            implementation_steps=[
                {"phase": "Phase 1: Foundation", "duration": "Years 1-3", "actions": ["Site selection", "Grid upgrades"], "responsible_ministry": "Infrastructure", "budget_allocation_percent": 20}
            ],
            success_metrics=[{"metric": "Carbon reduction", "target": "40% by year 5", "deadline": "Year 5"}],
            risks_and_mitigations={"Cost overruns": "Strict oversight committee"},
            expected_outcomes=["Stable grid", "Reduced emissions"],
            review_timeline="Annual reviews",
            total_votes=6,
            winning_votes=5,
            vote_percentage=83.3,
            consensus_level="high",
            best_simulation_score=83.0,
            model_used="gemini-1.5-pro"
        )
        db.add(report)
        await db.commit()
        print("Seed data created successfully.")

if __name__ == "__main__":
    asyncio.run(seed_data())
