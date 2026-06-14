import abc
from typing import Any, Dict, List, Optional
import structlog
from tenacity import retry, wait_exponential, stop_after_attempt

logger = structlog.get_logger(__name__)

class EvidenceItem:
    """Standardized schema for all retrieved evidence."""
    def __init__(self, source: str, title: str, snippet: str, date: str = "Unknown", confidence_score: float = 50.0, url: str = "", provider_id: str = ""):
        self.source = source
        self.title = title
        self.snippet = snippet
        self.date = date
        self.confidence_score = confidence_score
        self.url = url
        self.provider_id = provider_id

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "title": self.title,
            "snippet": self.snippet,
            "date": self.date,
            "confidence_score": self.confidence_score,
            "url": self.url,
            "provider_id": self.provider_id
        }

class EvidenceProvider(abc.ABC):
    """Abstract base class for all TITAN evidence providers."""
    
    def __init__(self):
        self._cache: Dict[str, List[Dict[str, Any]]] = {}

    @property
    @abc.abstractmethod
    def provider_id(self) -> str:
        """Unique identifier for this provider."""
        pass
        
    @property
    @abc.abstractmethod
    def base_confidence(self) -> float:
        """Base confidence score assigned to data from this provider."""
        pass

    @retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(3), reraise=False)
    async def search(self, query: str, max_results: int = 3) -> List[Dict[str, Any]]:
        """
        Public entrypoint for executing a search.
        Automatically wraps the abstract fetch logic with retries, caching, and converts to dicts.
        """
        cache_key = f"{query}_{max_results}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        try:
            items = await self._execute_search(query, max_results)
            results = [item.to_dict() for item in items]
            self._cache[cache_key] = results
            return results
        except Exception as e:
            logger.error("Provider search failed", provider=self.provider_id, query=query, error=str(e))
            return []

    @abc.abstractmethod
    async def _execute_search(self, query: str, max_results: int) -> List[EvidenceItem]:
        """
        Internal execution logic. Must be implemented by subclasses.
        Should return a list of structured EvidenceItem objects.
        """
        pass
