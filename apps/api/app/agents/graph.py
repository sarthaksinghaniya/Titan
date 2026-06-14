"""
TITAN Governance Agent Graph
=============================
Compiles the complete LangGraph StateGraph for the AI cabinet.

Full Flow:
                    ┌─────────────────┐
                    │ input_validation │
                    └────────┬────────┘
                             │ route_after_validation
              ┌──────────────┴──────────────┐
         [error]                       [analyzing]
              │                             │
              ▼                     route_to_ministers
       error_handler           ┌────────────┴────────────┐
                          Send × 6 (parallel fan-out)
                    ┌─────┬────┴─────┬─────┬──────┬──────┐
                    │     │          │     │      │      │
              econ  tech  infra  citizen  env  opp
                    │                             │
                    └──────────┬──────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │  aggregate_analyses  │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │    debate_round      │  (5 ministers sequential)
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  opposition_attack   │  (dedicated attack node)
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │   rebuttal_round     │  (5 ministers parallel)
                    └──────────┬──────────┘
                               │
                        route_to_voting
                    ┌─────┬────┴────┬──────┐
                    │     │         │      │
              Send × 6 (parallel voting fan-out)
                    │                      │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼──────────┐
                    │     tally_votes      │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  simulation_phase    │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  prime_minister_     │
                    │     synthesis        │
                    └──────────┬──────────┘
                               │ route_after_synthesis
                    ┌──────────┴──────────┐
                [failed]              [__end__]
                    │
             error_handler
"""
from __future__ import annotations

import time
from functools import wraps
from typing import Any, Dict

import structlog
from langgraph.graph import StateGraph, END

logger = structlog.get_logger(__name__)

from app.agents.state import GovernanceState
from app.agents.nodes import (
    node_input_validation,
    node_minister_analysis,
    node_aggregate_analyses,
    node_debate_round,
    node_opposition_attack,
    node_rebuttal_round,
    node_minister_vote,
    node_tally_votes,
    node_simulation_phase,
    node_prime_minister_synthesis,
    node_black_swan_engine,
    node_error_handler,
    route_after_validation,
    route_to_ministers,
    route_to_voting,
    route_after_synthesis,
)
from app.agents.research.research_nodes import (
    node_research_retrieval,
    node_evidence_ranking,
    node_context_compression,
)


def time_node(func):
    @wraps(func)
    async def wrapper(state: GovernanceState):
        t0 = time.monotonic()
        try:
            return await func(state)
        finally:
            elapsed_ms = int((time.monotonic() - t0) * 1000)
            logger.info("Node execution time", node=func.__name__, elapsed_ms=elapsed_ms)
    return wrapper


def build_graph() -> Any:
    """
    Construct and compile the TITAN governance StateGraph.

    Returns a compiled LangGraph runnable — call .ainvoke(state) to execute.
    """
    g = StateGraph(GovernanceState)

    # ── Register all nodes ─────────────────────────────────────
    g.add_node("input_validation",         time_node(node_input_validation))
    g.add_node("research_retrieval",       time_node(node_research_retrieval))
    g.add_node("evidence_ranking",         time_node(node_evidence_ranking))
    g.add_node("context_compression",      time_node(node_context_compression))
    g.add_node("minister_analysis",        time_node(node_minister_analysis))   # fan-out target
    g.add_node("aggregate_analyses",       time_node(node_aggregate_analyses))
    g.add_node("debate_round",             time_node(node_debate_round))
    g.add_node("opposition_attack",        time_node(node_opposition_attack))
    g.add_node("rebuttal_round",           time_node(node_rebuttal_round))
    g.add_node("minister_vote",            time_node(node_minister_vote))        # fan-out target
    g.add_node("tally_votes",              time_node(node_tally_votes))
    g.add_node("simulation_phase",         time_node(node_simulation_phase))
    g.add_node("prime_minister_synthesis", time_node(node_prime_minister_synthesis))
    g.add_node("black_swan_engine",        time_node(node_black_swan_engine))
    g.add_node("error_handler",            time_node(node_error_handler))

    # ── Entry point ────────────────────────────────────────────
    g.set_entry_point("input_validation")

    # ── Conditional edge: validation → parallel analysis | fail ───
    g.add_conditional_edges(
        "input_validation",
        route_after_validation,
    )

    # ── Research Pipeline ──────────────────────────────────────
    g.add_edge("research_retrieval", "evidence_ranking")
    g.add_edge("evidence_ranking", "context_compression")
    g.add_conditional_edges("context_compression", route_to_ministers)

    # ── Collect fan-out results ────────────────────────────────
    g.add_edge("minister_analysis", "aggregate_analyses")

    # ── Linear debate pipeline ─────────────────────────────────
    g.add_edge("aggregate_analyses", "debate_round")
    g.add_edge("debate_round",       "opposition_attack")
    g.add_edge("opposition_attack",  "rebuttal_round")

    # ── Parallel fan-out: 6 ministers vote simultaneously ──────
    g.add_conditional_edges(
        "rebuttal_round",
        route_to_voting,
    )

    # ── Collect voting fan-out results ─────────────────────────
    g.add_edge("minister_vote", "tally_votes")

    # ── Simulation phase ───────────────────────────────────────
    g.add_edge("tally_votes", "simulation_phase")

    # ── PM synthesis & Black Swan ──────────────────────────────
    g.add_edge("simulation_phase", "prime_minister_synthesis")
    g.add_edge("prime_minister_synthesis", "black_swan_engine")

    # ── Final edge: black_swan_engine → END | error ────────────
    g.add_conditional_edges(
        "black_swan_engine",
        route_after_synthesis,
        {
            "__end__": END,
            "failed":  "error_handler",
        },
    )

    # ── Error handler is terminal ──────────────────────────────
    g.add_edge("error_handler", END)

    return g.compile()


# ── Singleton compiled graph — created once at import time ────
governance_graph = build_graph()


def create_governance_graph(*args, **kwargs) -> Any:
    """
    Backwards-compatible factory used by session_service.py.
    Ignores db/event_bus (those are handled via middleware layer).
    """
    return governance_graph
