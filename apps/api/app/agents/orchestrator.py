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
