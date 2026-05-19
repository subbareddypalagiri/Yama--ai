'use client';

import React, { useState, useRef, useEffect } from 'react';
import { useLanguage } from '@/context/LanguageContext';
import { Language } from '@/lib/translations';

export default function LanguageSelector() {
  const { language, setLanguage, languageNames, availableLanguages } = useLanguage();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const languageFlags: Record<Language, string> = {
    en: '🇬🇧',
    hi: '🇮🇳',
    ta: '🇮🇳',
    te: '🇮🇳'
  };

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-2 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 hover:border-purple-500/50 transition-all duration-300 text-white/90 hover:text-white"
      >
        <span className="text-lg">{languageFlags[language]}</span>
        <span className="text-sm font-medium">{languageNames[language]}</span>
        <svg
          className={`w-4 h-4 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isOpen && (
        <div className="absolute top-full right-0 mt-2 w-44 bg-black/90 backdrop-blur-xl border border-white/10 rounded-xl shadow-2xl shadow-purple-500/20 overflow-hidden z-50 animate-fadeIn">
          {availableLanguages.map((lang) => (
            <button
              key={lang}
              onClick={() => {
                setLanguage(lang);
                setIsOpen(false);
              }}
              className={`w-full flex items-center gap-3 px-4 py-3 text-left transition-all duration-200 ${
                language === lang
                  ? 'bg-gradient-to-r from-purple-600/30 to-pink-600/30 text-white'
                  : 'text-white/70 hover:text-white hover:bg-white/5'
              }`}
            >
              <span className="text-xl">{languageFlags[lang]}</span>
              <span className="font-medium">{languageNames[lang]}</span>
              {language === lang && (
                <svg className="w-4 h-4 ml-auto text-green-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
