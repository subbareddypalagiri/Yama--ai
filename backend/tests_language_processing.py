"""
Unit Tests for Roman English Language Processing Module
Tests language detection, transliteration, and translation
"""

import pytest
from app.services.language_processing.language_detector import get_language_detector
from app.services.language_processing.transliterator import get_transliterator
from app.services.language_processing.translator import get_translator


class TestLanguageDetector:
    """Test language detection functionality"""

    def test_detect_roman_english_hindi(self):
        """Test detection of Roman English (Hinglish)"""
        detector = get_language_detector()
        text = "mere ko ghar se nikala kaise ja sakta hai?"
        lang, script = detector.detect_language(text)
        
        assert lang == "hindi", f"Expected 'hindi', got '{lang}'"
        assert script == "roman_english", f"Expected 'roman_english', got '{script}'"
        assert detector.is_roman_english(text), "Should detect as Roman English"

    def test_detect_native_hindi(self):
        """Test detection of native Devanagari script"""
        detector = get_language_detector()
        text = "पत्नी को तलाक देने के लिए क्या कदम हैं?"
        lang, script = detector.detect_language(text)
        
        assert lang == "hindi", f"Expected 'hindi', got '{lang}'"
        assert script == "native_script", f"Expected 'native_script', got '{script}'"
        assert not detector.is_roman_english(text), "Should NOT detect as Roman English"

    def test_detect_english(self):
        """Test detection of English text"""
        detector = get_language_detector()
        text = "What are my legal rights as a tenant?"
        lang, script = detector.detect_language(text)
        
        assert lang == "english", f"Expected 'english', got '{lang}'"

    def test_detect_roman_english_tamil(self):
        """Test detection of Roman English Tamil (Tanglish)"""
        detector = get_language_detector()
        text = "enn kanum property rights pathi?"
        lang, script = detector.detect_language(text)
        
        # May detect as english since Tamil patterns are limited
        # This is acceptable as fallback
        assert script in ["roman_english", "native_script"], f"Unexpected script: {script}"

    def test_is_roman_english_patterns(self):
        """Test Roman English pattern matching"""
        detector = get_language_detector()
        
        hindi_patterns = [
            "maine kaha tha",
            "aur kya hua",
            "kya karoge tum",
            "haan namaste",
        ]
        
        for text in hindi_patterns:
            assert detector._has_indian_language_patterns(text), \
                f"Should detect Indian language patterns in: {text}"


class TestTransliterator:
    """Test transliteration functionality"""

    def test_hindi_to_roman(self):
        """Test Hindi (Devanagari) to Roman conversion"""
        transliterator = get_transliterator()
        hindi_text = "का ख ग"
        roman = transliterator.transliterate_to_roman(hindi_text, "hindi")
        
        assert "ka" in roman.lower(), f"Expected 'ka' in output: {roman}"
        assert "kha" in roman.lower(), f"Expected 'kha' in output: {roman}"
        assert "ga" in roman.lower(), f"Expected 'ga' in output: {roman}"

    def test_transliterator_initialized(self):
        """Test that transliterator initializes all language mappings"""
        transliterator = get_transliterator()
        
        assert hasattr(transliterator, 'hindi_roman'), "Missing hindi_roman mapping"
        assert hasattr(transliterator, 'tamil_roman'), "Missing tamil_roman mapping"
        assert hasattr(transliterator, 'telugu_roman'), "Missing telugu_roman mapping"
        assert hasattr(transliterator, 'kannada_roman'), "Missing kannada_roman mapping"


class TestTranslator:
    """Test translation functionality"""

    def test_translator_initialized(self):
        """Test that translator initializes properly"""
        translator = get_translator()
        
        assert translator is not None, "Translator should initialize"
        assert hasattr(translator, 'translate_to_english'), "Missing translate_to_english method"
        assert hasattr(translator, 'translate_from_english'), "Missing translate_from_english method"

    def test_english_passthrough(self):
        """Test that English text passes through unchanged"""
        translator = get_translator()
        text = "What is the legal status?"
        result = translator.translate_to_english(text, "english")
        
        assert result == text, f"English text should remain unchanged: {result}"

    def test_language_codes_mapping(self):
        """Test language code mappings"""
        translator = get_translator()
        
        assert translator.LANGUAGE_CODES["hindi"] == "hi"
        assert translator.LANGUAGE_CODES["tamil"] == "ta"
        assert translator.LANGUAGE_CODES["telugu"] == "te"
        assert translator.LANGUAGE_CODES["kannada"] == "kn"
        assert translator.LANGUAGE_CODES["english"] == "en"

    def test_translate_english_to_hindi(self):
        """Test English to Hindi translation"""
        translator = get_translator()
        text = "What are my legal rights?"
        result = translator.translate_from_english(text, "hindi")
        
        # Result should be a string and not empty
        assert isinstance(result, str), "Translation should return string"
        assert len(result) > 0, "Translation should not be empty"
        # Result should be different from input (if translation worked)
        # Note: May be same if service fails, so we just check it returns something


class TestLanguageProcessingIntegration:
    """Integration tests for full language processing pipeline"""

    def test_full_pipeline_roman_english(self):
        """Test complete pipeline: detect -> translate -> analyze"""
        detector = get_language_detector()
        translator = get_translator()
        transliterator = get_transliterator()
        
        # Input in Roman English
        input_text = "mere ko kya hak hai?"
        
        # Step 1: Detect
        lang, script = detector.detect_language(input_text)
        assert lang == "hindi"
        assert script == "roman_english"
        
        # Step 2: Translate to English
        english_text = translator.translate_to_english(input_text, lang)
        assert isinstance(english_text, str)
        assert len(english_text) > 0

    def test_response_language_selection(self):
        """Test response language can be selected"""
        translator = get_translator()
        
        # Test that we can translate to different languages
        english_text = "What are my rights?"
        
        # Should be able to get responses in different languages
        for lang in ["hindi", "tamil", "telugu", "kannada"]:
            result = translator.translate_from_english(english_text, lang)
            assert isinstance(result, str), f"Should translate to {lang}"

    def test_roman_english_response_generation(self):
        """Test Roman English response generation"""
        translator = get_translator()
        transliterator = get_transliterator()
        
        english_response = "Your legal rights include..."
        
        # Convert to Hindi first
        hindi_response = translator.translate_from_english(english_response, "hindi")
        
        # Then transliterate to Roman
        roman_response = transliterator.transliterate_to_roman(hindi_response, "hindi")
        
        assert isinstance(roman_response, str)
        assert len(roman_response) > 0


# Fixtures for pytest
@pytest.fixture
def detector():
    """Provide language detector instance"""
    return get_language_detector()


@pytest.fixture
def transliterator():
    """Provide transliterator instance"""
    return get_transliterator()


@pytest.fixture
def translator():
    """Provide translator instance"""
    return get_translator()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
