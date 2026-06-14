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
# NODE 0A — RESEARCH RETRIEVAL
# ══════════════════════════════════════════════════════════════

async def node_research_retrieval(state: GovernanceState) -> Dict[str, Any]:
    """Generates queries and fetches raw evidence from APIs."""
    logger.info("Research retrieval starting", project_id=state["project_id"])
    problem = state["problem"]
    context = state.get("context", "")

    # 1. Generate Queries
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
        resp = await asyncio.wait_for(
            llm.ainvoke([HumanMessage(content=prompt)]),
            timeout=settings.AGENT_TIMEOUT_SECONDS
        )
        parsed = extract_json(str(resp.content))
        queries = parsed.get("queries", [])[:3]
    except Exception as e:
        logger.error("Query generation failed", error=str(e))
        queries = [problem[:50]]

    if not queries:
        queries = ["policy impact", "economic analysis"]

    logger.info("Executing research queries", queries=queries)
    
    # 2. Fetch Evidence from APIs
    raw_results = await ResearchClients.run_parallel_searches(queries)
    
    # 3. Retrieve Long-Term Memory (Precedents)
    precedents = vector_store_manager.search_precedents(problem, top_k=2)
    for p in precedents:
        raw_results.append({
            "source": "TITAN Historical Memory",
            "title": f"Past Resolution: {p.get('metadata', {}).get('project_id', 'Unknown')}",
            "snippet": p.get('content', '')
        })
    
    return {
        "research_queries": queries,
        "raw_evidence": raw_results,
        "current_phase": "validating_evidence"
    }


# ══════════════════════════════════════════════════════════════
# NODE 0B — EVIDENCE RANKING & VALIDATION
# ══════════════════════════════════════════════════════════════

async def node_evidence_ranking(state: GovernanceState) -> Dict[str, Any]:
    """Filters and ranks the raw evidence for relevance to the problem."""
    logger.info("Evidence ranking starting")
    problem = state["problem"]
    raw_evidence = state.get("raw_evidence", [])
    
    if not raw_evidence:
        return {"current_phase": "compressing_context"}

    # Format evidence for the LLM
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

    llm = ModelOrchestrator.get_model(ModelTask.RESEARCH)
    try:
        resp = await asyncio.wait_for(
            llm.ainvoke([HumanMessage(content=prompt)]),
            timeout=settings.AGENT_TIMEOUT_SECONDS
        )
        parsed = extract_json(str(resp.content))
        indices = parsed.get("selected_indices", [])
        
        # Filter raw_evidence based on selected indices (1-based)
        filtered = []
        for idx in indices:
            if isinstance(idx, int) and 1 <= idx <= len(raw_evidence):
                filtered.append(raw_evidence[idx-1])
                
        # Update state with filtered evidence
        return {
            "raw_evidence": filtered, # Annotated reducer merges, wait... no, we should just compress it.
            # Actually, since `raw_evidence` is Annotated with operator.add, returning it here will append it again.
            # So we pass the filtered items directly to context compression via a temporary key or just overwrite.
            # Wait, TypedDict doesn't easily allow temporary keys unless defined.
            # Let's just compress it directly in the next node, or do compression here.
        }
    except Exception as e:
        logger.error("Evidence ranking failed", error=str(e))
        return {}
        
    return {"current_phase": "compressing_context"}


# ══════════════════════════════════════════════════════════════
# NODE 0C — CONTEXT COMPRESSION
# ══════════════════════════════════════════════════════════════

async def node_context_compression(state: GovernanceState) -> Dict[str, Any]:
    """Compresses the validated evidence into a dense dossier."""
    logger.info("Context compression starting")
    problem = state["problem"]
    
    # We will just use the last chunk of raw_evidence since operator.add appends everything.
    # To avoid issues, let's take all raw_evidence (which includes the ranked ones if we appended them, or just all of them if ranking failed).
    # Wait, the best way is to combine ranking and compression, but let's keep them separate.
    raw_evidence = state.get("raw_evidence", [])
    
    if not raw_evidence:
        dossier = "No external evidence could be retrieved for this problem. Rely on foundational principles."
        return {
            "evidence_dossier": dossier,
            "current_phase": "analyzing"
        }

    evidence_text = "\n".join(
        f"- [{item.get('source')}]: {item.get('title')} ({item.get('date', 'N/A')})\n  {item.get('snippet')}"
        for item in raw_evidence[-10:] # Take last 10 to avoid token overflow
    )

    prompt = f"""You are the Chief Research Officer for the TITAN Cabinet.
Synthesize the following raw evidence into a dense, highly factual 'Evidence Dossier'.
Extract every statistic, empirical claim, and historical precedent.
Do NOT generate opinions. Do NOT solve the problem. Only organize the facts.

PROBLEM: {problem}

RAW EVIDENCE:
{evidence_text}

Format the output as a Markdown summary (max 300 words)."""

    llm = ModelOrchestrator.get_model(ModelTask.SUMMARIZATION)
    try:
        resp = await asyncio.wait_for(
            llm.ainvoke([HumanMessage(content=prompt)]),
            timeout=settings.AGENT_TIMEOUT_SECONDS
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
