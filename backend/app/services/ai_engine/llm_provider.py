"""
YAMA AI — LLM Provider Factory
Configures and returns the appropriate LLM based on settings.
Returns None when LLM_PROVIDER is "none" (standalone mode).
"""

import logging

from app.core.config import settings


logger = logging.getLogger("yama_ai.llm")


def get_llm():
    """
    Return configured LLM instance based on LLM_PROVIDER setting.
    Returns None if provider is "none" (standalone reasoning mode).
    """

    provider = settings.LLM_PROVIDER.lower()

    if provider == "none":
        return None

    try:
        if provider == "openai":
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model=settings.OPENAI_MODEL,
                api_key=settings.OPENAI_API_KEY,
                temperature=0.3,
                max_tokens=4000,
            )

        elif provider == "anthropic":
            from langchain_anthropic import ChatAnthropic
            return ChatAnthropic(
                model=settings.ANTHROPIC_MODEL,
                api_key=settings.ANTHROPIC_API_KEY,
                temperature=0.3,
                max_tokens=4000,
            )

        elif provider == "ollama":
            from langchain_community.chat_models import ChatOllama
            return ChatOllama(
                model=settings.OLLAMA_MODEL,
                base_url=settings.OLLAMA_BASE_URL,
                temperature=0.3,
            )

        elif provider == "gemini":
            from langchain_google_genai import ChatGoogleGenerativeAI
            return ChatGoogleGenerativeAI(
                model=settings.GEMINI_MODEL,
                google_api_key=settings.GOOGLE_API_KEY,
                temperature=0.3,
                max_output_tokens=1500,  # Reduced from 2000 for faster responses
            )

        raise ValueError(
            f"Unsupported LLM provider: {provider}. Use 'none', 'openai', 'anthropic', 'ollama', or 'gemini'."
        )
    except ModuleNotFoundError as e:
        logger.warning(
            "LLM provider '%s' unavailable due to missing dependency (%s). Falling back to standalone mode.",
            provider,
            e,
        )
        return None
