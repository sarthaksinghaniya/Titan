import json
import uuid
from typing import Any, Dict, List
import structlog

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.messages import HumanMessage
from langchain_core.documents import Document

from app.services.vector_store import vector_store_manager
from app.agents.orchestrator import ModelOrchestrator, ModelTask
from app.agents.ministers.base import extract_json

logger = structlog.get_logger(__name__)

class RAGPipeline:
    """Production-grade retrieval pipeline for the Evidence Engine."""
    
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )

    async def ingest_evidence(self, evidence_list: List[Dict[str, Any]], session_id: str):
        """Chunks and ingests external evidence into the vector store."""
        if not evidence_list:
            return

        docs_to_insert = []
        for ev in evidence_list:
            snippet = ev.get("snippet", "")
            if not snippet:
                continue
                
            chunks = self.text_splitter.split_text(snippet)
            for chunk in chunks:
                docs_to_insert.append(Document(
                    page_content=chunk,
                    metadata={
                        "evidence_id": f"EV-{uuid.uuid4().hex[:6].upper()}",
                        "source": ev.get("source", "Unknown"),
                        "title": ev.get("title", "Unknown"),
                        "url": ev.get("url", ""),
                        "base_confidence": ev.get("confidence_score", 50.0),
                        "session_id": session_id,
                        "date": ev.get("date", "Unknown"),
                        "type": "external_evidence"
                    }
                ))

        try:
            # We bypass the manager's add_memory format to insert raw chunks
            vector_store_manager.vector_store.add_documents(docs_to_insert)
            logger.info("Ingested external evidence chunks", chunks=len(docs_to_insert), session_id=session_id)
        except Exception as e:
            logger.error("Failed to ingest evidence chunks", error=str(e))

    async def retrieve_and_rerank(self, query: str, context: str, session_id: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Semantic search followed by LLM-based reranking."""
        # Step 1: Broad semantic search
        # We retrieve more than top_k to allow the reranker to prune
        raw_results = vector_store_manager.search_precedents(query, top_k=top_k * 3)
        if not raw_results:
            return []

        # Filter out session crosstalk if needed (for external evidence, keep only this session's chunks)
        # Historical memory has no session_id or a different type.
        filtered_results = []
        for res in raw_results:
            meta = res.get("metadata", {})
            if meta.get("type") == "external_evidence" and meta.get("session_id") != session_id:
                continue
            filtered_results.append(res)

        if not filtered_results:
            return []

        # Step 2: Rerank
        return await self._llm_rerank(query, context, filtered_results, top_k)

    async def _llm_rerank(self, query: str, context: str, retrieved_chunks: List[Dict[str, Any]], top_k: int) -> List[Dict[str, Any]]:
        """Scores relevance of chunks to the specific query and context."""
        
        chunks_text = ""
        for i, chunk in enumerate(retrieved_chunks):
            meta = chunk.get("metadata", {})
            chunks_text += f"[{i}]\nEVIDENCE_ID: {meta.get('evidence_id', 'EV-???')} | SOURCE: {meta.get('source')} | {meta.get('title')}\nCONTENT: {chunk.get('content')}\n\n"

        schema = """{
  "scored_chunks": [
    {"index": 0, "relevance_score": 95},
    {"index": 1, "relevance_score": 40}
  ]
}"""
        
        prompt = f"""You are a Reranking Engine.
Evaluate the following retrieved chunks against the user's problem.
Score each chunk's relevance from 0 to 100. Be strict: generic or off-topic chunks should score < 50.

PROBLEM: {query}
CONTEXT: {context}

CHUNKS:
{chunks_text}

Return ONLY JSON:
{schema}"""

        try:
            resp = await ModelOrchestrator.call_model_with_resilience(
                ModelTask.RESEARCH,
                [HumanMessage(content=prompt)]
            )
            parsed = extract_json(str(resp.content))
            scored_chunks = parsed.get("scored_chunks", [])
            
            # Map scores back to chunks
            for sc in scored_chunks:
                idx = sc.get("index")
                score = sc.get("relevance_score", 0)
                if isinstance(idx, int) and 0 <= idx < len(retrieved_chunks):
                    # Combine vector similarity (score is typically distance, lower is better in Chroma, but search_precedents might return varied metrics. Let's rely heavily on the LLM score)
                    base_conf = retrieved_chunks[idx]["metadata"].get("base_confidence", 50.0)
                    retrieved_chunks[idx]["composite_confidence"] = (score + base_conf) / 2.0
                    retrieved_chunks[idx]["llm_score"] = score
            
            # Filter and sort
            valid_chunks = [c for c in retrieved_chunks if "composite_confidence" in c]
            valid_chunks.sort(key=lambda x: x["composite_confidence"], reverse=True)
            
            logger.info("Reranking complete", input_chunks=len(retrieved_chunks), valid=len(valid_chunks))
            return valid_chunks[:top_k]
            
        except Exception as e:
            logger.error("LLM reranking failed", error=str(e))
            # Fallback: Just return the top k semantic hits with a default composite
            for chunk in retrieved_chunks[:top_k]:
                chunk["composite_confidence"] = chunk.get("metadata", {}).get("base_confidence", 50.0)
            return retrieved_chunks[:top_k]

rag_pipeline = RAGPipeline()
