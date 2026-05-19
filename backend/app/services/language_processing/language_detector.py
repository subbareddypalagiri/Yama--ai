"""
Language Detector - Identifies input language and script type
"""

import re
from typing import Tuple, Literal
from langdetect import detect, detect_langs, LangDetectException


class LanguageDetector:
    """Detect language and identify Roman English (Hinglish/Tanglish/etc.)"""

    # Common Roman English patterns for each language
    HINDI_PATTERNS = {
        r'\b(maine|mera|tumhara|hota|kaise|kyun|kya|aur|ya|hai|hain|karo|kar|karte|karke)\b',
        r'\b(namaste|dhanyavaad|shukriya|beta|bhai|babu|ji|arre|accha)\b',
    }
    
    TAMIL_PATTERNS = {
        r'\b(naan|nee|avunga|yen|epdi|sollren|sollran|sollu|paartha)\b',
        r'\b(anbu|anjali|valkai|ulagam)\b',
    }
    
    TELUGU_PATTERNS = {
        r'\b(nenu|meeru|vaallu|enduku|ekkada|ledu|undi|chesanu|cheyyali)\b',
        r'\b(prema|sukham|pillu|pelli)\b',
    }
    
    KANNADA_PATTERNS = {
        r'\b(nanu|neevu|avaru|yaake|yelle|illa|ide|maadi|maadidde)\b',
        r'\b(priya|sukha|koti|hendthi)\b',
    }

    def __init__(self):
        """Initialize language detector."""
        self.hindi_regex = re.compile(
            '|'.join(self.HINDI_PATTERNS),
            re.IGNORECASE
        )
        self.tamil_regex = re.compile(
            '|'.join(self.TAMIL_PATTERNS),
            re.IGNORECASE
        )
        self.telugu_regex = re.compile(
            '|'.join(self.TELUGU_PATTERNS),
            re.IGNORECASE
        )
        self.kannada_regex = re.compile(
            '|'.join(self.KANNADA_PATTERNS),
            re.IGNORECASE
        )

    def is_roman_english(self, text: str) -> bool:
        """
        Check if text is in Roman English (Hinglish/Tanglish/etc.)
        Uses patterns and script detection.
        """
        # If text contains Indic scripts, it's not Roman English
        if self._has_indic_script(text):
            return False
        
        # Check if text is mostly Latin/Roman script with English-like words
        if not self._is_latin_script(text):
            return False
        
        # Check for typical Indian language Roman patterns
        return self._has_indian_language_patterns(text)

    def detect_language(self, text: str) -> Tuple[Literal["hindi", "tamil", "telugu", "kannada", "english"], str]:
        """
        Detect language of input text.
        Returns (language_code, confidence_description)
        """
        # Check if Roman English first
        if self.is_roman_english(text):
            detected = self._detect_roman_english_language(text)
            return (detected, "roman_english")
        
        # Try to detect actual script
        try:
            detected_lang = detect(text)
            
            # Map detected languages
            lang_map = {
                "hi": "hindi",
                "ta": "tamil",
                "te": "telugu",
                "kn": "kannada",
                "en": "english",
            }
            
            language = lang_map.get(detected_lang, "english")
            return (language, "native_script")
        
        except LangDetectException:
            return ("english", "fallback")

    def _detect_roman_english_language(self, text: str) -> str:
        """Detect which Indian language the Roman English represents."""
        text_lower = text.lower()
        
        # Count pattern matches for each language
        hindi_matches = len(self.hindi_regex.findall(text_lower))
        tamil_matches = len(self.tamil_regex.findall(text_lower))
        telugu_matches = len(self.telugu_regex.findall(text_lower))
        kannada_matches = len(self.kannada_regex.findall(text_lower))
        
        matches = {
            "hindi": hindi_matches,
            "tamil": tamil_matches,
            "telugu": telugu_matches,
            "kannada": kannada_matches,
        }
        
        # Return language with most matches
        return max(matches, key=matches.get) if max(matches.values()) > 0 else "hindi"

    def _has_indic_script(self, text: str) -> bool:
        """Check if text contains Indic script characters."""
        # Unicode ranges for major Indic scripts
        indic_ranges = [
            (0x0900, 0x097F),  # Devanagari (Hindi)
            (0x0B80, 0x0BFF),  # Tamil
            (0x0C00, 0x0C7F),  # Telugu
            (0x0C80, 0x0CFF),  # Kannada
        ]
        
        for char in text:
            code = ord(char)
            for start, end in indic_ranges:
                if start <= code <= end:
                    return True
        return False

    def _is_latin_script(self, text: str) -> bool:
        """Check if text is primarily in Latin/Roman script."""
        latin_count = 0
        total_alpha = 0
        
        for char in text:
            if char.isalpha():
                total_alpha += 1
                # Check if ASCII letter or common diacritics
                if ord(char) < 256 or ord(char) in range(0x0100, 0x017F):
                    latin_count += 1
        
        return total_alpha == 0 or (latin_count / total_alpha) > 0.7

    def _has_indian_language_patterns(self, text: str) -> bool:
        """Check if text contains typical Indian language Roman patterns."""
        # Count total pattern matches
        total_matches = (
            len(self.hindi_regex.findall(text.lower())) +
            len(self.tamil_regex.findall(text.lower())) +
            len(self.telugu_regex.findall(text.lower())) +
            len(self.kannada_regex.findall(text.lower()))
        )
        
        return total_matches > 0


# Singleton instance
_detector = None


def get_language_detector() -> LanguageDetector:
    """Get or create language detector instance."""
    global _detector
    if _detector is None:
        _detector = LanguageDetector()
    return _detector
