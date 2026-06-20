"""
YAMA AI — LLM Provider Factory
Configures and returns the appropriate LLM based on settings.
Returns None when LLM_PROVIDER is "none" (standalone mode).
"""

import logging

from app.core.config import settings


logger = logging.getLogger("yama_ai.llm")


def get_llm(custom_api_key=None, custom_model=None):
    """
    Return configured LLM instance based on LLM_PROVIDER setting or custom user overrides.
    If provider is 'gemini', it will attempt to load Gemini, and fallback to Ollama if it fails.
    Returns None if provider is "none" (standalone reasoning mode).
    """

    provider = settings.LLM_PROVIDER.lower()

    if provider == "none":
        return None

    # Use custom overrides if provided by the user
    if custom_api_key and custom_model:
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            logger.info(f"Using Custom LLM override: {custom_model}")
            
            # Simple mapping to format the name for the Gemini SDK if it matches the dropdown names
            # Gemini SDK typically expects 'gemini-1.5-flash', 'gemini-1.5-pro', etc.
            # But we pass what the user selected. If it's a generic proxy, they might need OpenAI client.
            # Assuming the user wants Google Generative AI based on their previous request.
            
            return ChatGoogleGenerativeAI(
                model=custom_model, 
                google_api_key=custom_api_key,
                temperature=0.3,
                max_output_tokens=1500,
            )
        except Exception as e:
            logger.warning(f"Failed to initialize custom model {custom_model}: {e}. Falling back to default provider.")

    # Check Gemini first if provider is gemini or even if it's default to see if key exists
    if provider == "gemini":
        if settings.GOOGLE_API_KEY:
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
                logger.info("Initializing Gemini as primary LLM...")
                return ChatGoogleGenerativeAI(
                    model="gemini-1.5-flash", # Fallback default if setting is different
                    google_api_key=settings.GOOGLE_API_KEY,
                    temperature=0.3,
                    max_output_tokens=1500,
                )
            except Exception as e:
                logger.warning("Gemini initialization failed (%s). Falling back to Ollama.", e)
                provider = "ollama"
        else:
            logger.warning("Google API Key not found. Falling back to Ollama.")
            provider = "ollama"

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
            logger.info("Initializing Ollama LLM...")
            return ChatOllama(
                model=settings.OLLAMA_MODEL,
                base_url=settings.OLLAMA_BASE_URL,
                temperature=0.3,
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
