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

from typing import Any

from langgraph.graph import END, StateGraph

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
    node_prime_minister_synthesis,
    node_error_handler,
    route_after_validation,
    route_to_ministers,
    route_to_voting,
    route_after_synthesis,
)


def build_graph() -> Any:
    """
    Construct and compile the TITAN governance StateGraph.

    Returns a compiled LangGraph runnable — call .ainvoke(state) to execute.
    """
    g = StateGraph(GovernanceState)

    # ── Register all nodes ─────────────────────────────────────
    g.add_node("input_validation",         node_input_validation)
    g.add_node("minister_analysis",        node_minister_analysis)   # fan-out target
    g.add_node("aggregate_analyses",       node_aggregate_analyses)
    g.add_node("debate_round",             node_debate_round)
    g.add_node("opposition_attack",        node_opposition_attack)
    g.add_node("rebuttal_round",           node_rebuttal_round)
    g.add_node("minister_vote",            node_minister_vote)        # fan-out target
    g.add_node("tally_votes",              node_tally_votes)
    g.add_node("prime_minister_synthesis", node_prime_minister_synthesis)
    g.add_node("error_handler",            node_error_handler)

    # ── Entry point ────────────────────────────────────────────
    g.set_entry_point("input_validation")

    # ── Conditional edge: validation → analyze | fail ─────────
    g.add_conditional_edges(
        "input_validation",
        route_after_validation,
        {
            "analyzing": "minister_analysis",   # uses Send fan-out via route_to_ministers
            "failed":    "error_handler",
        },
    )

    # ── Parallel fan-out: 6 ministers analyze simultaneously ───
    # route_to_ministers returns List[Send("minister_analysis", {...})]
    g.add_conditional_edges(
        "input_validation",
        route_to_ministers,
    )

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

    # ── PM synthesis ───────────────────────────────────────────
    g.add_edge("tally_votes", "prime_minister_synthesis")

    # ── Final edge: synthesis → END | error ───────────────────
    g.add_conditional_edges(
        "prime_minister_synthesis",
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
