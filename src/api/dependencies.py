"""
FastAPI Dependencies
"""

from functools import lru_cache
from src.infrastructure.llm import GeminiClient
from src.infrastructure.config import get_settings
from src.application.use_cases import GenerateFeedbackUseCase


# Global instances
_gemini_client = None
_use_case = None


def get_gemini_client() -> GeminiClient:
    """
    Dependency para obtener Gemini Client.
    
    Returns:
        GeminiClient: Cliente singleton
    """
    global _gemini_client
    
    if _gemini_client is None:
        settings = get_settings()
        _gemini_client = GeminiClient(api_key=settings.GOOGLE_API_KEY)
    
        return _gemini_client


def get_generate_feedback_use_case() -> GenerateFeedbackUseCase:
    """
    Dependency para obtener GenerateFeedbackUseCase.
    
    Returns:
        GenerateFeedbackUseCase: Use case instance
    """
    global _use_case
    
    if _use_case is None:
        gemini_client = get_gemini_client()
        _use_case = GenerateFeedbackUseCase(llm_client=gemini_client)
    
    return _use_case