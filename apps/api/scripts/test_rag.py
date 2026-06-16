import asyncio
from app.agents.graph import governance_graph
from app.agents.state import GovernanceState

async def test_rag():
    state = {
        "problem": "How to reduce carbon emissions by 50% in 10 years without hurting GDP?",
        "project_id": "test_rag_123",
        "context": ""
    }
    try:
        result = await governance_graph.ainvoke(state)
        print("Graph execution finished successfully!")
        print("Phases visited, or final phase:", result.get("current_phase"))
    except Exception as e:
        print(f"Error executing graph: {e}")

if __name__ == "__main__":
    asyncio.run(test_rag())
