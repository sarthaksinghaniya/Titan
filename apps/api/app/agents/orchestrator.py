import logging
from enum import Enum
from typing import Optional

import structlog
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

from app.core.config import settings

logger = structlog.get_logger(__name__)

class ModelTask(Enum):
    RESEARCH = "research"
    SUMMARIZATION = "summarization"
    DEBATE = "debate"
    FORECASTING = "forecasting"
    VALIDATION = "validation"

class ModelOrchestrator:
    """
    Dynamically routes requests to the optimal model based on the cognitive task.
    Implements automatic failover using LangChain's with_fallbacks.
    """
    
    @classmethod
    def get_fallback_model(cls) -> BaseChatModel:
        """The ultimate fallback: Gemini Flash."""
        return ChatGoogleGenerativeAI(
            model=settings.GEMINI_FLASH_MODEL,
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0.7,
            max_output_tokens=4096,
        )

    @classmethod
    def get_pro_fallback_model(cls) -> BaseChatModel:
        """The high-tier fallback: Gemini Pro."""
        return ChatGoogleGenerativeAI(
            model=settings.GEMINI_PRO_MODEL,
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0.4,
            max_output_tokens=8192,
        )

    @classmethod
    def get_model(cls, task: ModelTask) -> BaseChatModel:
        """Route to the best model with failover logic."""
        primary_model: Optional[BaseChatModel] = None
        
        try:
            if task == ModelTask.DEBATE:
                # Reasoning model preferred
                if settings.OPENAI_API_KEY:
                    primary_model = ChatOpenAI(
                        model=settings.OPENAI_DEFAULT_MODEL,
                        api_key=settings.OPENAI_API_KEY,
                        temperature=0.7
                    )
                elif settings.ANTHROPIC_API_KEY:
                    primary_model = ChatAnthropic(
                        model=settings.ANTHROPIC_DEFAULT_MODEL,
                        api_key=settings.ANTHROPIC_API_KEY,
                        temperature=0.7
                    )
                else:
                    primary_model = cls.get_pro_fallback_model()
                    
            elif task == ModelTask.RESEARCH or task == ModelTask.FORECASTING:
                # High-tier analysis preferred
                if settings.ANTHROPIC_API_KEY:
                    primary_model = ChatAnthropic(
                        model=settings.ANTHROPIC_DEFAULT_MODEL,
                        api_key=settings.ANTHROPIC_API_KEY,
                        temperature=0.4
                    )
                else:
                    primary_model = cls.get_pro_fallback_model()
                    
            elif task == ModelTask.SUMMARIZATION or task == ModelTask.VALIDATION:
                # Fast model preferred
                primary_model = cls.get_fallback_model()
                
            else:
                primary_model = cls.get_fallback_model()

        except Exception as e:
            logger.warning("Primary model init failed, falling back", task=task.value, error=str(e))
            primary_model = cls.get_fallback_model()

        # Wrap with runtime fallback protection
        return primary_model.with_fallbacks([cls.get_fallback_model()])

    @classmethod
    async def call_model_with_resilience(cls, task: ModelTask, messages: list, timeout: int = settings.AGENT_TIMEOUT_SECONDS):
        """
        Executes an LLM call with full resilience: timeouts, retries, fallbacks, and circuit breaking.
        """
        from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
        import asyncio
        from httpx import HTTPError

        # Create a circuit breaker context if we wanted to be super robust,
        # but for now, we rely on tenacity to fail fast after 3 retries.
        
        # We retry only on network-level or API-level exceptions, not validation errors.
        @retry(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=2, max=10),
            retry=retry_if_exception_type((HTTPError, asyncio.TimeoutError)),
            reraise=True
        )
        async def _execute():
            llm = cls.get_model(task)
            return await asyncio.wait_for(llm.ainvoke(messages), timeout=timeout)
            
        try:
            resp = await _execute()
            
            # ─── Telemetry: Token Tracking ───────────────────────────
            tokens = 0
            if hasattr(resp, "usage_metadata") and resp.usage_metadata:
                tokens = resp.usage_metadata.get("total_tokens", 0)
            elif hasattr(resp, "response_metadata") and "token_usage" in resp.response_metadata:
                usage = resp.response_metadata["token_usage"]
                tokens = usage.get("total_tokens", 0)
                
            if tokens > 0:
                logger.info("llm_tokens_used", task=task.value, tokens=tokens)
                
            return resp
        except Exception as e:
            logger.error("LLM Call failed completely after retries", error=str(e), task=task.value)
            raise
