import asyncio
import urllib.parse
from typing import Any, Dict, List
import structlog
import httpx
import xml.etree.ElementTree as ET

logger = structlog.get_logger(__name__)

class ResearchClients:
    """Async clients for retrieving evidence from external databases."""
    
    @staticmethod
    async def search_arxiv(query: str, max_results: int = 3) -> List[Dict[str, Any]]:
        """Search ArXiv API for academic papers."""
        encoded_query = urllib.parse.quote(query)
        url = f"https://export.arxiv.org/api/query?search_query=all:{encoded_query}&start=0&max_results={max_results}"
        
        results = []
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                resp = await client.get(url)
                resp.raise_for_status()
                
                # Parse XML
                root = ET.fromstring(resp.text)
                namespace = {'atom': 'http://www.w3.org/2005/Atom'}
                
                for entry in root.findall('atom:entry', namespace):
                    title = entry.find('atom:title', namespace)
                    summary = entry.find('atom:summary', namespace)
                    published = entry.find('atom:published', namespace)
                    
                    if title is not None and summary is not None:
                        results.append({
                            "source": "ArXiv",
                            "title": title.text.strip().replace('\n', ' ') if title.text else "",
                            "snippet": summary.text.strip().replace('\n', ' ')[:500] + "..." if summary.text else "",
                            "date": published.text[:10] if published is not None and published.text else "Unknown"
                        })
        except Exception as e:
            logger.warning("ArXiv search failed", query=query, error=str(e))
            
        return results

    @staticmethod
    async def search_semantic_scholar(query: str, max_results: int = 3) -> List[Dict[str, Any]]:
        """Search Semantic Scholar for broader policy/science papers."""
        url = "https://api.semanticscholar.org/graph/v1/paper/search"
        params = {
            "query": query,
            "limit": max_results,
            "fields": "title,abstract,year,authors"
        }
        
        results = []
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                resp = await client.get(url, params=params)
                resp.raise_for_status()
                data = resp.json()
                
                for item in data.get("data", []):
                    abstract = item.get("abstract") or "No abstract provided."
                    authors = [a.get("name") for a in item.get("authors", [])]
                    author_str = ", ".join(authors[:2]) + (" et al." if len(authors) > 2 else "")
                    
                    results.append({
                        "source": "Semantic Scholar",
                        "title": item.get("title", ""),
                        "snippet": abstract[:500] + "...",
                        "date": str(item.get("year", "Unknown")),
                        "authors": author_str
                    })
        except Exception as e:
            logger.warning("Semantic Scholar search failed", query=query, error=str(e))
            
        return results

    @classmethod
    async def run_parallel_searches(cls, queries: List[str]) -> List[Dict[str, Any]]:
        """Run searches across all configured sources in parallel."""
        tasks = []
        for q in queries:
            tasks.append(cls.search_arxiv(q))
            tasks.append(cls.search_semantic_scholar(q))
            
        all_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        flattened = []
        for res in all_results:
            if isinstance(res, list):
                flattened.extend(res)
                
        # Deduplicate by title
        seen = set()
        unique_results = []
        for item in flattened:
            title = item.get("title", "").lower()
            if title and title not in seen:
                seen.add(title)
                unique_results.append(item)
                
        return unique_results
