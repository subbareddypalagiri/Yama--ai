"""
Translation Cache - Speeds up language processing by caching translations
"""

from functools import lru_cache
from typing import Dict, Tuple

class TranslationCache:
    """In-memory cache for translations to avoid redundant API calls"""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.cache: Dict[str, str] = {}
    
    def get(self, text: str, source_lang: str, target_lang: str) -> str | None:
        """Get cached translation if exists"""
        key = self._make_key(text, source_lang, target_lang)
        return self.cache.get(key)
    
    def set(self, text: str, source_lang: str, target_lang: str, translation: str):
        """Cache translation result"""
        if len(self.cache) >= self.max_size:
            # Remove oldest entry if cache is full (simple FIFO)
            self.cache.pop(next(iter(self.cache)))
        
        key = self._make_key(text, source_lang, target_lang)
        self.cache[key] = translation
    
    @staticmethod
    def _make_key(text: str, source_lang: str, target_lang: str) -> str:
        """Create cache key from text and language pair"""
        return f"{source_lang}_{target_lang}_{hash(text)}"
    
    def clear(self):
        """Clear cache"""
        self.cache.clear()


# Global cache instance
_cache = None

def get_translation_cache() -> TranslationCache:
    """Get or create translation cache instance"""
    global _cache
    if _cache is None:
        _cache = TranslationCache(max_size=1000)
    return _cache
