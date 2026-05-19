"""
Translator - Convert between languages for legal analysis
Uses translatepy for free translation without API keys
"""

import asyncio
from typing import Literal, Optional
from translatepy import Translator as TranslatePyTranslator
from app.services.language_processing.translation_cache import get_translation_cache

try:
    from google.cloud import translate_v2
    GOOGLE_TRANSLATE_AVAILABLE = True
except ImportError:
    GOOGLE_TRANSLATE_AVAILABLE = False


class Translator:
    """Handle translation between Indian languages and English"""

    # Language code mappings
    LANGUAGE_CODES = {
        "hindi": "hi",
        "tamil": "ta",
        "telugu": "te",
        "kannada": "kn",
        "english": "en",
    }

    def __init__(self, use_google: bool = False):
        """
        Initialize translator.
        
        Args:
            use_google: Use Google Cloud Translation (requires API credentials)
                       Falls back to translatepy if not available
        """
        self.use_google = use_google and GOOGLE_TRANSLATE_AVAILABLE
        self.translatepy = TranslatePyTranslator()
        self.cache = get_translation_cache()
        
        if self.use_google:
            try:
                self.google_client = translate_v2.Client()
            except Exception:
                self.use_google = False
                self.google_client = None

    def translate_to_english(
        self,
        text: str,
        source_language: Literal["hindi", "tamil", "telugu", "kannada", "english"]
    ) -> str:
        """Translate text to English with caching."""
        if source_language == "english":
            return text
        
        # Check cache first
        cached = self.cache.get(text, source_language, "english")
        if cached:
            return cached
        
        source_code = self.LANGUAGE_CODES.get(source_language, "hi")
        
        try:
            if self.use_google and self.google_client:
                result = self._translate_google(text, source_code, "en")
            else:
                result = self._translate_translatepy(text, source_code, "en")
            
            # Cache the result
            self.cache.set(text, source_language, "english", result)
            return result
        except Exception as e:
            print(f"Translation failed: {e}, returning original text")
            return text

    def translate_from_english(
        self,
        text: str,
        target_language: Literal["hindi", "tamil", "telugu", "kannada", "roman_english"]
    ) -> str:
        """Translate English text to target language with caching."""
        if target_language == "roman_english" or target_language == "english":
            return text
        
        # Check cache first
        cached = self.cache.get(text, "english", target_language)
        if cached:
            return cached
        
        target_code = self.LANGUAGE_CODES.get(target_language, "hi")
        
        try:
            if self.use_google and self.google_client:
                result = self._translate_google(text, "en", target_code)
            else:
                result = self._translate_translatepy(text, "en", target_code)
            
            # Cache the result
            self.cache.set(text, "english", target_language, result)
            return result
        except Exception as e:
            print(f"Translation failed: {e}, returning original text")
            return text

    def _translate_google(self, text: str, source_lang: str, target_lang: str) -> str:
        """Translate using Google Cloud Translation API."""
        result = self.google_client.translate_text(
            text,
            source_language_code=source_lang,
            target_language_code=target_lang,
        )
        return result["translatedText"]

    def _translate_translatepy(self, text: str, source_lang: str, target_lang: str) -> str:
        """Translate using translatepy (free, no API keys needed)."""
        try:
            result = self.translatepy.translate(text, target_lang, source_lang)
            # Handle both string and TranslationResult object
            if hasattr(result, '__str__'):
                translated = str(result)
            else:
                translated = result
            return translated
        except Exception as e:
            print(f"TranslatePy failed: {e}")
            return text

    def translate_response(
        self,
        response_text: str,
        target_language: Literal["hindi", "tamil", "telugu", "kannada", "roman_english", "english"]
    ) -> str:
        """
        Translate AI response to target language.
        
        For roman_english, this should be called after translating to native script,
        or the translation module will handle it.
        """
        return self.translate_from_english(response_text, target_language)


# Singleton instance
_translator = None


def get_translator(use_google: bool = False) -> Translator:
    """Get or create translator instance."""
    global _translator
    if _translator is None:
        _translator = Translator(use_google=use_google)
    return _translator
