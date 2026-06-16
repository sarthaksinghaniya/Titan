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

from app.services.rag import rag_pipeline

# ══════════════════════════════════════════════════════════════
# NODE 0D — KNOWLEDGE RETRIEVAL
# ══════════════════════════════════════════════════════════════

async def node_knowledge_retrieval(state: GovernanceState) -> Dict[str, Any]:
    """Chunks validated evidence, embeds it, and semantic searches for precedents."""
    logger.info("Knowledge retrieval starting")
    problem = state["problem"]
    context = state.get("context", "")
    session_id = state.get("project_id", "unknown_session")
    validated_evidence = state.get("validated_evidence", [])

    # 1. Ingest external evidence into the vector store
    await rag_pipeline.ingest_evidence(validated_evidence, session_id)

    # 2. Retrieve and Rerank combined precedents and external evidence
    reranked_chunks = await rag_pipeline.retrieve_and_rerank(
        query=problem,
        context=context,
        session_id=session_id,
        top_k=5
    )

    logger.info("Knowledge retrieval complete", chunks=len(reranked_chunks))
    return {
        "precedents": reranked_chunks,
        "current_phase": "compressing_context"
    }


# ══════════════════════════════════════════════════════════════
# NODE 0E — CONTEXT COMPRESSION
# ══════════════════════════════════════════════════════════════

async def node_context_compression(state: GovernanceState) -> Dict[str, Any]:
    """Compresses the validated evidence into a dense dossier."""
    logger.info("Context compression starting")
    problem = state["problem"]
    
    precedents = state.get("precedents", [])
    
    if not precedents:
        dossier = "No empirical evidence or past precedents could be retrieved. Rely on foundational principles."
        return {
            "evidence_dossier": dossier,
            "current_phase": "analyzing"
        }

    evidence_text = "\n".join(
        f"- [{item.get('metadata', {}).get('evidence_id', 'EV-???')}] {item.get('metadata', {}).get('source', 'System')}: {item.get('metadata', {}).get('title', 'Precedent')} (Confidence: {item.get('composite_confidence', 50.0):.1f})\n  {item.get('content', '')}"
        for item in precedents
    )

    prompt = f"""You are the Chief Research Officer for the TITAN Cabinet.
Synthesize the following highly confident, reranked evidence chunks into a dense, factual 'Evidence Dossier'.
Extract every statistic, empirical claim, and historical precedent.
Do NOT generate opinions. Do NOT solve the problem. Only organize the facts explicitly mapping them to their sources.

PROBLEM: {problem}

RERANKED EVIDENCE:
{evidence_text}

Format the output as a Markdown summary (max 400 words) with explicit citations."""

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
