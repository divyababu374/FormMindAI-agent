from app.config import settings
from app.services.ai.base_provider import BaseAIProvider
from app.services.ai.smart_engine import SmartHeuristicEngine
from app.services.ai.gemini_provider import GeminiProvider
from app.services.ai.openai_provider import OpenAICompatibleProvider

def get_ai_provider() -> BaseAIProvider:
    """
    Factory that instantiates the appropriate AIProvider based on environment variables.
    """
    provider = settings.AI_PROVIDER.lower().strip()

    if provider == "gemini" or (provider == "auto" and settings.GEMINI_API_KEY):
        return GeminiProvider(
            api_key=settings.GEMINI_API_KEY or settings.AI_API_KEY,
            model_name=settings.MODEL_NAME or "gemini-1.5-flash"
        )
    elif provider == "groq" or (provider == "auto" and settings.GROQ_API_KEY):
        return OpenAICompatibleProvider(
            api_key=settings.GROQ_API_KEY or settings.AI_API_KEY,
            base_url="https://api.groq.com/openai/v1",
            model_name=settings.MODEL_NAME or "llama-3.3-70b-versatile"
        )
    elif provider == "openai" or (provider == "auto" and settings.OPENAI_API_KEY):
        return OpenAICompatibleProvider(
            api_key=settings.OPENAI_API_KEY or settings.AI_API_KEY,
            base_url="https://api.openai.com/v1",
            model_name=settings.MODEL_NAME or "gpt-4o-mini"
        )
    elif provider == "ollama":
        return OpenAICompatibleProvider(
            api_key="ollama",
            base_url=f"{settings.OLLAMA_BASE_URL}/v1",
            model_name=settings.MODEL_NAME or "llama3"
        )
    
    # Default to built-in SmartHeuristicEngine (guaranteed to work everywhere without keys)
    return SmartHeuristicEngine()
