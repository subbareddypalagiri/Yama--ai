"""
Transliterator - Convert between Roman English and native scripts
"""

import re
from typing import Dict, Literal


class Transliterator:
    """Handle transliteration between Roman English and native Indian scripts"""

    # Hindi transliteration mappings (simplified IAST to Devanagari)
    HINDI_TO_ROMAN = {
        'ा': 'a', 'ि': 'i', 'ी': 'ee', 'ु': 'u', 'ू': 'oo',
        'े': 'e', 'ै': 'ai', 'ो': 'o', 'ौ': 'au',
        'क': 'ka', 'ख': 'kha', 'ग': 'ga', 'घ': 'gha',
        'च': 'cha', 'छ': 'chha', 'ज': 'ja', 'झ': 'jha',
        'ट': 'ta', 'ठ': 'tha', 'ड': 'da', 'ढ': 'dha',
        'त': 'ta', 'थ': 'tha', 'द': 'da', 'ध': 'dha',
        'न': 'na', 'प': 'pa', 'फ': 'pha', 'ब': 'ba',
        'भ': 'bha', 'म': 'ma', 'य': 'ya', 'र': 'ra',
        'ल': 'la', 'व': 'va', 'श': 'sha', 'ष': 'sha',
        'स': 'sa', 'ह': 'ha', 'ँ': 'n', 'ः': 'h',
    }

    # Tamil transliteration mappings (simplified)
    TAMIL_TO_ROMAN = {
        'ா': 'aa', 'ி': 'i', 'ீ': 'ee', 'ு': 'u', 'ூ': 'oo',
        'ெ': 'e', 'ே': 'ee', 'ை': 'ai', 'ொ': 'o', 'ோ': 'o',
        'க': 'ka', 'ங': 'nga', 'ச': 'cha', 'ஞ': 'nya',
        'ட': 'ta', 'ண': 'na', 'த': 'tha', 'ந': 'na',
        'ப': 'pa', 'ம': 'ma', 'ய': 'ya', 'ர': 'ra',
        'ல': 'la', 'வ': 'va', 'ழ': 'zha', 'ள': 'la',
        'ற': 'ra', 'ன': 'na',
    }

    # Telugu transliteration mappings (simplified)
    TELUGU_TO_ROMAN = {
        'ా': 'aa', 'ి': 'i', 'ీ': 'ee', 'ు': 'u', 'ూ': 'oo',
        'ె': 'e', 'ే': 'e', 'ై': 'ai', 'ొ': 'o', 'ో': 'o',
        'క': 'ka', 'ఖ': 'kha', 'గ': 'ga', 'ఘ': 'gha',
        'ఙ': 'nga', 'చ': 'cha', 'ఛ': 'chha', 'జ': 'ja',
        'ఝ': 'jha', 'ఞ': 'nya', 'ట': 'ta', 'ఠ': 'tha',
        'డ': 'da', 'ఢ': 'dha', 'ణ': 'na', 'త': 'ta',
        'థ': 'tha', 'ద': 'da', 'ధ': 'dha', 'న': 'na',
        'ప': 'pa', 'ఫ': 'pha', 'బ': 'ba', 'భ': 'bha',
        'మ': 'ma', 'య': 'ya', 'ర': 'ra', 'ల': 'la',
        'వ': 'va', 'శ': 'sha', 'ష': 'sha', 'స': 'sa',
        'హ': 'ha',
    }

    # Kannada transliteration mappings (simplified)
    KANNADA_TO_ROMAN = {
        'ಾ': 'aa', 'ಿ': 'i', 'ೀ': 'ee', 'ು': 'u', 'ೂ': 'oo',
        'ೆ': 'e', 'ೇ': 'e', 'ೈ': 'ai', 'ೊ': 'o', 'ೋ': 'o',
        'ಕ': 'ka', 'ಖ': 'kha', 'ಗ': 'ga', 'ಘ': 'gha',
        'ಙ': 'nga', 'ಚ': 'cha', 'ಛ': 'chha', 'ಜ': 'ja',
        'ಝ': 'jha', 'ಞ': 'nya', 'ಟ': 'ta', 'ಠ': 'tha',
        'ಡ': 'da', 'ಢ': 'dha', 'ಣ': 'na', 'ತ': 'ta',
        'ಥ': 'tha', 'ದ': 'da', 'ಧ': 'dha', 'ನ': 'na',
        'ಪ': 'pa', 'ಫ': 'pha', 'ಬ': 'ba', 'ಭ': 'bha',
        'ಮ': 'ma', 'ಯ': 'ya', 'ರ': 'ra', 'ಲ': 'la',
        'ವ': 'va', 'ಶ': 'sha', 'ಷ': 'sha', 'ಸ': 'sa',
        'ಹ': 'ha',
    }

    def __init__(self):
        """Initialize transliterator with reverse mappings."""
        self.hindi_roman = self.HINDI_TO_ROMAN
        self.hindi_native = {v: k for k, v in self.HINDI_TO_ROMAN.items()}
        
        self.tamil_roman = self.TAMIL_TO_ROMAN
        self.tamil_native = {v: k for k, v in self.TAMIL_TO_ROMAN.items()}
        
        self.telugu_roman = self.TELUGU_TO_ROMAN
        self.telugu_native = {v: k for k, v in self.TELUGU_TO_ROMAN.items()}
        
        self.kannada_roman = self.KANNADA_TO_ROMAN
        self.kannada_native = {v: k for k, v in self.KANNADA_TO_ROMAN.items()}

    def transliterate_to_roman(
        self,
        text: str,
        language: Literal["hindi", "tamil", "telugu", "kannada"]
    ) -> str:
        """Convert native script to Roman English."""
        if language == "hindi":
            return self._transliterate_to_roman_helper(text, self.hindi_roman)
        elif language == "tamil":
            return self._transliterate_to_roman_helper(text, self.tamil_roman)
        elif language == "telugu":
            return self._transliterate_to_roman_helper(text, self.telugu_roman)
        elif language == "kannada":
            return self._transliterate_to_roman_helper(text, self.kannada_roman)
        return text

    def transliterate_to_native(
        self,
        text: str,
        language: Literal["hindi", "tamil", "telugu", "kannada"]
    ) -> str:
        """Convert Roman English to native script."""
        if language == "hindi":
            return self._transliterate_to_native_helper(text, self.hindi_native)
        elif language == "tamil":
            return self._transliterate_to_native_helper(text, self.tamil_native)
        elif language == "telugu":
            return self._transliterate_to_native_helper(text, self.telugu_native)
        elif language == "kannada":
            return self._transliterate_to_native_helper(text, self.kannada_native)
        return text

    def _transliterate_to_roman_helper(self, text: str, mapping: Dict[str, str]) -> str:
        """Helper to convert text using character mapping."""
        result = text
        for native, roman in mapping.items():
            result = result.replace(native, roman)
        return result

    def _transliterate_to_native_helper(self, text: str, mapping: Dict[str, str]) -> str:
        """Helper to convert Roman to native using reverse mapping."""
        result = text.lower()
        # Sort by length descending to handle multi-char replacements first
        for roman, native in sorted(mapping.items(), key=lambda x: len(x[0]), reverse=True):
            result = re.sub(r'\b' + roman + r'\b', native, result)
        return result


# Singleton instance
_transliterator = None


def get_transliterator() -> Transliterator:
    """Get or create transliterator instance."""
    global _transliterator
    if _transliterator is None:
        _transliterator = Transliterator()
    return _transliterator
