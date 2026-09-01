"""
YAMA AI — LLM Provider Factory
Configures and returns the appropriate LLM based on settings.
Returns None when LLM_PROVIDER is "none" (standalone mode).
"""

import logging
import httpx
from langchain_core.runnables import Runnable
from langchain_core.messages import AIMessage

from app.core.config import settings


logger = logging.getLogger("yama_ai.llm")


class DirectGeminiLLM(Runnable):
    """
    Direct REST API wrapper for Google Gemini v1beta.
    Eliminates LangChain dependency mismatches and ComputerUse import errors.
    """
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash", temperature: float = 0.3):
        self.api_key = api_key
        self.model = model if model else "gemini-1.5-flash"
        self.temperature = temperature

    def _call(self, prompt: str, stop=None, run_manager=None, **kwargs) -> str:
        res = self.invoke(prompt, config=kwargs)
        return res.content if hasattr(res, "content") else str(res)

    def invoke(self, input, config=None, **kwargs):
        if isinstance(input, str):
            contents = [{"role": "user", "parts": [{"text": input}]}]
            system_instruction = None
        else:
            if hasattr(input, "to_messages"):
                messages = input.to_messages()
            elif isinstance(input, list):
                messages = input
            else:
                messages = []

            system_instruction = None
            contents = []
            for msg in messages:
                msg_type = getattr(msg, "type", "")
                content_str = getattr(msg, "content", "") or str(msg)
                if msg_type == "system" or "SystemMessage" in str(type(msg)):
                    system_instruction = {"parts": [{"text": content_str}]}
                elif msg_type in ["human", "user"] or "HumanMessage" in str(type(msg)):
                    contents.append({"role": "user", "parts": [{"text": content_str}]})
                elif msg_type in ["ai", "assistant"] or "AIMessage" in str(type(msg)):
                    contents.append({"role": "model", "parts": [{"text": content_str}]})
                else:
                    contents.append({"role": "user", "parts": [{"text": content_str}]})

            if not contents and hasattr(input, "to_string"):
                contents = [{"role": "user", "parts": [{"text": input.to_string()}]}]
            elif not contents and input:
                contents = [{"role": "user", "parts": [{"text": str(input)}]}]


        gen_config = {
            "temperature": self.temperature,
            "maxOutputTokens": 8192
        }
        prompt_text_summary = str(contents)
        if (config and config.get("response_mime_type") == "application/json") or "JSON" in prompt_text_summary or "schema" in prompt_text_summary:
            gen_config["responseMimeType"] = "application/json"

        payload = {
            "contents": contents,
            "generationConfig": gen_config
        }
        if system_instruction:
            payload["systemInstruction"] = system_instruction


        models_to_try = [
            self.model,
            "gemini-flash-lite-latest",
            "gemini-2.0-flash",
            "gemma-4-31b-it",
            "gemini-flash-latest",
            "gemini-2.0-flash-lite"
        ]

        seen = set()
        last_err = None
        with httpx.Client(timeout=14.0) as client:

            for m in models_to_try:
                if m in seen:
                    continue
                seen.add(m)
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={self.api_key}"
                try:
                    res = client.post(url, json=payload)
                    if res.status_code == 200:
                        data = res.json()
                        text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                        return AIMessage(content=text or "I could not generate an analysis. Please try clarifying your situation.")
                    else:
                        last_err = f"Status {res.status_code}: {res.text}"
                        logger.warning(f"Model {m} failed: {last_err}")
                except Exception as e:
                    last_err = str(e)
                    logger.warning(f"Model {m} error: {last_err}")

        raise RuntimeError(f"Gemini API call failed across all fallback models: {last_err}")


def get_llm(custom_api_key=None, custom_model=None):
    """
    Return configured LLM instance based on LLM_PROVIDER setting or custom user overrides.
    If provider is 'gemini', uses DirectGeminiLLM for instant, error-free API responses.
    Returns None if provider is "none" (standalone reasoning mode).
    """

    provider = settings.LLM_PROVIDER.lower()

    if provider == "none":
        return None

    # Use custom overrides if provided by the user
    if custom_api_key:
        logger.info(f"Using Custom Gemini override: {custom_model or 'gemini-1.5-flash'}")
        return DirectGeminiLLM(
            api_key=custom_api_key,
            model=custom_model or "gemini-1.5-flash",
            temperature=0.3
        )

    # Check Gemini first if provider is gemini
    if provider == "gemini":
        if settings.GOOGLE_API_KEY:
            logger.info("Initializing DirectGeminiLLM as primary LLM...")
            return DirectGeminiLLM(
                api_key=settings.GOOGLE_API_KEY,
                model=getattr(settings, "GEMINI_MODEL", "gemini-1.5-flash"),
                temperature=0.3
            )
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
