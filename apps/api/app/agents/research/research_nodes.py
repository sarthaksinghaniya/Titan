import asyncio
import json
import time
from typing import Any, Dict, List

import structlog
from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.state import GovernanceState
from app.core.config import settings
from app.agents.nodes import _ts
from app.agents.ministers.base import extract_json
from app.agents.research.research_clients import ResearchClients
from app.agents.orchestrator import ModelOrchestrator, ModelTask
from app.services.vector_store import vector_store_manager

logger = structlog.get_logger(__name__)


# ══════════════════════════════════════════════════════════════
# NODE 0A — RESEARCH GENERATION
# ══════════════════════════════════════════════════════════════

async def node_research_generation(state: GovernanceState) -> Dict[str, Any]:
    """Generates highly optimized search strategies."""
    logger.info("Research generation starting", project_id=state["project_id"])
    problem = state["problem"]
    context = state.get("context", "")

    llm = ModelOrchestrator.get_model(ModelTask.RESEARCH)
    query_schema = """{
  "queries": ["query 1", "query 2", "query 3"]
}"""
    prompt = f"""You are an expert Research Librarian.
Generate 3 highly optimized search queries to find empirical evidence, academic studies, or economic data for this problem.
Queries should be short (2-4 words) and focus on factual precedents.

PROBLEM: {problem}
CONTEXT: {context}

Return ONLY JSON:
{query_schema}"""

    try:
        resp = await ModelOrchestrator.call_model_with_resilience(
            ModelTask.RESEARCH,
            [HumanMessage(content=prompt)]
        )
        parsed = extract_json(str(resp.content))
        queries = parsed.get("queries", [])[:3]
    except Exception as e:
        logger.error("Query generation failed", error=str(e))
        queries = [problem[:50]]

    if not queries:
        queries = ["policy impact", "economic analysis"]

    return {
        "research_queries": queries,
        "current_phase": "collecting_evidence"
    }

from app.agents.research.providers.registry import ProviderRegistry

# ══════════════════════════════════════════════════════════════
# NODE 0B — EVIDENCE COLLECTION
# ══════════════════════════════════════════════════════════════

async def node_evidence_collection(state: GovernanceState) -> Dict[str, Any]:
    """Fetches raw evidence from external APIs based on queries."""
    queries = state.get("research_queries", [])
    logger.info("Executing evidence collection", queries=queries)
    
    registry = ProviderRegistry()
    raw_results = await registry.execute_parallel_search(queries, max_results_per_provider=2)
    
    return {
        "raw_evidence": raw_results,
        "current_phase": "validating_evidence"
    }

# ══════════════════════════════════════════════════════════════
# NODE 0C — EVIDENCE VALIDATION
# ══════════════════════════════════════════════════════════════

async def node_evidence_validation(state: GovernanceState) -> Dict[str, Any]:
    """Filters and ranks the raw evidence, dropping hallucinations/low-quality data."""
    logger.info("Evidence validation starting")
    problem = state["problem"]
    raw_evidence = state.get("raw_evidence", [])
    
    if not raw_evidence:
        return {"validated_evidence": [], "current_phase": "knowledge_retrieval"}

    evidence_text = ""
    for i, item in enumerate(raw_evidence):
        evidence_text += f"[{i+1}] SOURCE: {item.get('source')} | TITLE: {item.get('title')}\nSNIPPET: {item.get('snippet')}\n\n"

    ranking_schema = """{
  "selected_indices": [1, 3, 4]
}"""

    prompt = f"""You are an Intelligence Analyst validating research data.
Review the following retrieved evidence. Select the indices of the most highly relevant, empirically dense, and factual items that will help ministers debate the problem. Max 5 items.
Ignore vague or irrelevant items.

PROBLEM: {problem}

EVIDENCE:
{evidence_text}

Return ONLY JSON:
{ranking_schema}"""

    try:
        resp = await ModelOrchestrator.call_model_with_resilience(
            ModelTask.RESEARCH,
            [HumanMessage(content=prompt)]
        )
        parsed = extract_json(str(resp.content))
        indices = parsed.get("selected_indices", [])
        
        filtered = []
        for idx in indices:
            if isinstance(idx, int) and 1 <= idx <= len(raw_evidence):
                filtered.append(raw_evidence[idx-1])
                
        return {
            "validated_evidence": filtered,
            "current_phase": "knowledge_retrieval"
        }
    except Exception as e:
        logger.error("Evidence validation failed", error=str(e))
        return {
            "validated_evidence": raw_evidence[:3],
            "current_phase": "knowledge_retrieval"
        }

# ══════════════════════════════════════════════════════════════
# NODE 0D — KNOWLEDGE RETRIEVAL
# ══════════════════════════════════════════════════════════════

async def node_knowledge_retrieval(state: GovernanceState) -> Dict[str, Any]:
    """Queries Vector DB for precedents and builds final dossier."""
    problem = state["problem"]
    validated = state.get("validated_evidence", [])
    
    logger.info("Knowledge retrieval starting")
    
    # Retrieve Long-Term Memory (Precedents)
    precedents = vector_store_manager.search_precedents(problem, top_k=2)
    for p in precedents:
        validated.append({
            "source": "TITAN Historical Memory",
            "title": f"Past Resolution: {p.get('metadata', {}).get('project_id', 'Unknown')}",
            "snippet": p.get('content', '')
        })
        
    return {
        "validated_evidence": validated,
        "current_phase": "compressing_context"
    }


# ══════════════════════════════════════════════════════════════
# NODE 0E — CONTEXT COMPRESSION
# ══════════════════════════════════════════════════════════════

async def node_context_compression(state: GovernanceState) -> Dict[str, Any]:
    """Compresses the validated evidence into a dense dossier."""
    logger.info("Context compression starting")
    problem = state["problem"]
    
    validated = state.get("validated_evidence", [])
    
    if not validated:
        dossier = "No external evidence could be retrieved for this problem. Rely on foundational principles."
        return {
            "evidence_dossier": dossier,
            "current_phase": "analyzing"
        }

    evidence_text = "\n".join(
        f"- [{item.get('source')}]: {item.get('title')}\n  {item.get('snippet')}"
        for item in validated[-10:] # Take last 10 to avoid token overflow
    )

    prompt = f"""You are the Chief Research Officer for the TITAN Cabinet.
Synthesize the following validated evidence into a dense, highly factual 'Evidence Dossier'.
Extract every statistic, empirical claim, and historical precedent.
Do NOT generate opinions. Do NOT solve the problem. Only organize the facts.

PROBLEM: {problem}

VALIDATED EVIDENCE:
{evidence_text}

Format the output as a Markdown summary (max 300 words)."""

    try:
        resp = await ModelOrchestrator.call_model_with_resilience(
            ModelTask.SUMMARIZATION,
            [HumanMessage(content=prompt)]
        )
        dossier = str(resp.content).strip()
    except Exception as e:
        logger.error("Context compression failed", error=str(e))
        dossier = "Failed to compress evidence dossier due to an internal error."

    logger.info("Context compression complete", length=len(dossier))
    return {
        "evidence_dossier": dossier,
        "current_phase": "analyzing"
    }
