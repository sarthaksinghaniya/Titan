import asyncio
from typing import Any, Dict, List
import structlog

from app.agents.research.providers.base import EvidenceProvider
from app.agents.research.providers.academic import ArXivProvider, SemanticScholarProvider
from app.agents.research.providers.economic import WorldBankProvider, IMFProvider, OECDProvider
from app.agents.research.providers.datasets import HuggingFaceProvider, KaggleProvider
from app.agents.research.providers.policy import UNDataProvider, GovOpenDataProvider

logger = structlog.get_logger(__name__)

class ProviderRegistry:
    """Central orchestration layer for dispatching search queries across multiple EvidenceProviders."""
    
    def __init__(self):
        self.providers: Dict[str, EvidenceProvider] = {}
        self._register_default_providers()

    def _register_default_providers(self):
        self.register(ArXivProvider())
        self.register(SemanticScholarProvider())
        self.register(WorldBankProvider())
        self.register(IMFProvider())
        self.register(OECDProvider())
        self.register(HuggingFaceProvider())
        self.register(KaggleProvider())
        self.register(UNDataProvider())
        self.register(GovOpenDataProvider())

    def register(self, provider: EvidenceProvider):
        self.providers[provider.provider_id] = provider

    async def execute_parallel_search(self, queries: List[str], max_results_per_provider: int = 2) -> List[Dict[str, Any]]:
        """
        Execute queries across all registered providers in parallel.
        Returns a deduplicated list of EvidenceItem dictionaries.
        """
        tasks = []
        for provider in self.providers.values():
            for query in queries:
                tasks.append(provider.search(query, max_results=max_results_per_provider))
                
        logger.info("Executing parallel provider search", num_tasks=len(tasks), providers=len(self.providers))
        
        # Execute concurrently with a fast timeout (fail-safe logic is in the providers)
        results_matrix = await asyncio.gather(*tasks, return_exceptions=True)
        
        flattened = []
        for res in results_matrix:
            if isinstance(res, list):
                flattened.extend(res)
            elif isinstance(res, Exception):
                logger.warning("Unhandled exception from provider task", error=str(res))

        # Deduplicate roughly by title to prevent spamming the validation model
        seen = set()
        unique_results = []
        for item in flattened:
            title = item.get("title", "").strip().lower()
            if title and title not in seen:
                seen.add(title)
                unique_results.append(item)
                
        # Sort by base confidence score (highest first)
        unique_results.sort(key=lambda x: x.get("confidence_score", 0), reverse=True)
        
        logger.info("Parallel search complete", total_raw=len(flattened), unique=len(unique_results))
        return unique_results
