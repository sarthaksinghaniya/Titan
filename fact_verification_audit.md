# Fact Verification Audit Report

**MISSION:** Verify the existence and execution of fact checking capabilities in TITAN V3 and ensure they influence the final outputs.

## 1. Fact Checker Agent Exists
**Status:** Verified
- **File:** `apps/api/app/agents/ministers/specialists.py`
- **Class:** `FactCheckerAgent`
- **Details:** The system incorporates a `FactCheckerAgent` that audits minister analyses. It possesses a strict `SCHEMA` instructing the LLM to verify claims, detect contradictions, identify unsupported conclusions, and determine an overall confidence score.

## 2. Contradiction Detection Exists
**Status:** Verified
- **File:** `apps/api/app/agents/ministers/specialists.py`
- **Details:** The prompt for the `FactCheckerAgent` explicitly requires the agent to "Detect contradictions, identify unsupported conclusions, and verify factual accuracy." The schema tracks `contradictions_detected` arrays to catch flawed minister claims against the Evidence Dossier.

## 3. Claim Verification Exists
**Status:** Verified
- **File:** `apps/api/app/agents/ministers/specialists.py`
- **Details:** Claim verification evaluates facts against the `EVIDENCE DOSSIER` via a `verified_claims` array containing the claim, its status (verified/refuted), and an evidence citation.

## 4. Verification Influences Final Output
**Status:** Verified & **Implemented**
- **Issue Discovered:** The fact checker report was previously generated in `node_fact_check` but deliberately kept out of the minister debate arguments. It was not routed into the subsequent rounds of debate or the Prime Minister's synthesis logic.
- **Resolution:** 
  1. Updated `BaseMinisterAgent.debate()` to natively accept a `fact_check_report` argument and inject it directly into the LLM context prior to debate rounds.
  2. Modified `nodes.py` so that `node_debate_round`, `node_opposition_attack`, and `node_rebuttal_round` pass `state.get("fact_check_report")` downward.
  3. Altered the prompt schema in `node_prime_minister_synthesis` to inject `fact_check_block`, ensuring the Prime Minister factors verified contradictions and unsupported claims into the final, binding policy synthesis.

## 5. Execution Trace
The fact verification pipeline flows through the architecture as follows:
1. `node_aggregate_analyses`: Prepares raw initial minister analyses.
2. `node_fact_check`: Injects `FactCheckerAgent`, which performs validation against the initial RAG dossier and outputs a structured contradiction/verification payload.
3. `node_debate_round`, `node_opposition_attack`, `node_rebuttal_round`: Contextualized debate ensues, with the LLM context now actively holding the fact check context to adjust arguments dynamically.
4. `node_prime_minister_synthesis`: The Prime Minister synthesizes options using vote tallies, debates, simulations, and definitively the fact-check constraints.
