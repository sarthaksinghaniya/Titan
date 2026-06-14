import urllib.parse
import xml.etree.ElementTree as ET
from typing import List
import httpx
import structlog

from app.agents.research.providers.base import EvidenceProvider, EvidenceItem

logger = structlog.get_logger(__name__)

class ArXivProvider(EvidenceProvider):
    """Provider for ArXiv academic papers."""
    
    @property
    def provider_id(self) -> str:
        return "arxiv"

    @property
    def base_confidence(self) -> float:
        return 85.0

    async def _execute_search(self, query: str, max_results: int) -> List[EvidenceItem]:
        encoded_query = urllib.parse.quote(query)
        url = f"https://export.arxiv.org/api/query?search_query=all:{encoded_query}&start=0&max_results={max_results}"
        
        results = []
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            
            root = ET.fromstring(resp.text)
            namespace = {'atom': 'http://www.w3.org/2005/Atom'}
            
            for entry in root.findall('atom:entry', namespace):
                title_node = entry.find('atom:title', namespace)
                summary_node = entry.find('atom:summary', namespace)
                published_node = entry.find('atom:published', namespace)
                id_node = entry.find('atom:id', namespace)
                
                if title_node is not None and summary_node is not None:
                    title = title_node.text.strip().replace('\n', ' ') if title_node.text else ""
                    summary = summary_node.text.strip().replace('\n', ' ')[:500] + "..." if summary_node.text else ""
                    date = published_node.text[:10] if published_node is not None and published_node.text else "Unknown"
                    paper_url = id_node.text if id_node is not None else ""
                    
                    results.append(EvidenceItem(
                        source="ArXiv",
                        title=title,
                        snippet=summary,
                        date=date,
                        confidence_score=self.base_confidence,
                        url=paper_url,
                        provider_id=self.provider_id
                    ))
        return results


class SemanticScholarProvider(EvidenceProvider):
    """Provider for Semantic Scholar database."""
    
    @property
    def provider_id(self) -> str:
        return "semantic_scholar"

    @property
    def base_confidence(self) -> float:
        return 80.0

    async def _execute_search(self, query: str, max_results: int) -> List[EvidenceItem]:
        url = "https://api.semanticscholar.org/graph/v1/paper/search"
        params = {
            "query": query,
            "limit": max_results,
            "fields": "title,abstract,year,authors,url"
        }
        
        results = []
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            
            for item in data.get("data", []):
                abstract = item.get("abstract") or "No abstract provided."
                authors = [a.get("name") for a in item.get("authors", [])]
                author_str = ", ".join(authors[:2]) + (" et al." if len(authors) > 2 else "")
                
                results.append(EvidenceItem(
                    source="Semantic Scholar",
                    title=item.get("title", ""),
                    snippet=abstract[:500] + "...",
                    date=str(item.get("year", "Unknown")),
                    confidence_score=self.base_confidence,
                    url=item.get("url", ""),
                    provider_id=self.provider_id
                ))
        return results
