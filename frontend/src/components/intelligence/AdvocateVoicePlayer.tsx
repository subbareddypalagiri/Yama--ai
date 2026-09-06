'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Volume2, Square, Loader2 } from 'lucide-react';

interface AdvocateVoicePlayerProps {
  text: string;
  label?: string;
  className?: string;
}

export default function AdvocateVoicePlayer({
  text,
  label,
  className = '',
}: AdvocateVoicePlayerProps) {
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isSupported, setIsSupported] = useState(true);
  const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null);

  useEffect(() => {
    if (typeof window === 'undefined' || !('speechSynthesis' in window)) {
      setIsSupported(false);
    }
    return () => {
      if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
        window.speechSynthesis.cancel();
      }
    };
  }, []);

  const cleanTextForSpeech = (rawText: string): string => {
    return rawText
      .replace(/#+\s+/g, '') // remove markdown headings
      .replace(/\*\*([^*]+)\*\*/g, '$1') // remove bold
      .replace(/\*([^*]+)\*/g, '$1') // remove italic
      .replace(/`([^`]+)`/g, '$1') // remove inline code
      .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1') // remove links
      .replace(/---|\*\*\*/g, '') // remove horizontal rules
      .replace(/>\s+/g, '') // remove blockquotes
      .replace(/§\s*/g, 'Section ') // speak section symbol
      .replace(/\|/g, ', ') // tables
      .trim();
  };

  const handleToggleSpeak = () => {
    if (!isSupported) return;

    if (isSpeaking) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
      return;
    }

    window.speechSynthesis.cancel(); // cancel any ongoing speech

    const cleaned = cleanTextForSpeech(text);
    if (!cleaned) return;

    const utterance = new SpeechSynthesisUtterance(cleaned);

    // Detect Telugu vs English
    const hasTelugu = /[\u0C00-\u0C7F]/.test(cleaned);
    utterance.lang = hasTelugu ? 'te-IN' : 'en-IN';

    // Senior Advocate tone: authoritative, steady, articulate
    utterance.pitch = 0.95;
    utterance.rate = 0.98;

    // Try finding an Indian voice if available
    const voices = window.speechSynthesis.getVoices();
    if (hasTelugu) {
      const teVoice = voices.find((v) => v.lang === 'te-IN' || v.name.toLowerCase().includes('telugu'));
      if (teVoice) utterance.voice = teVoice;
    } else {
      const inVoice = voices.find(
        (v) => v.lang === 'en-IN' || v.name.toLowerCase().includes('india') || v.name.toLowerCase().includes('ravi') || v.name.toLowerCase().includes('heera')
      );
      if (inVoice) utterance.voice = inVoice;
    }

    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = (e) => {
      console.error('TTS error', e);
      setIsSpeaking(false);
    };

    utteranceRef.current = utterance;
    window.speechSynthesis.speak(utterance);
  };

  if (!isSupported) return null;

  return (
    <button
      type="button"
      onClick={handleToggleSpeak}
      title={isSpeaking ? 'Stop Advocate Voice' : 'Read Aloud with Advocate Voice'}
      className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-xl text-xs font-semibold transition-all border shadow-sm ${
        isSpeaking
          ? 'bg-amber-500/20 text-amber-300 border-[#f59e0b] shadow-[0_0_15px_rgba(245,158,11,0.25)] animate-pulse'
          : 'bg-[#12141c] hover:bg-[#181b26] text-gray-300 hover:text-white border-[#252a3a] hover:border-[#f59e0b]/50'
      } ${className}`}
    >
      {isSpeaking ? (
        <>
          <Square className="w-3.5 h-3.5 text-amber-400 fill-amber-400" />
          <span className="font-mono text-[11px] text-amber-300">
            {label || 'Stop Advocate Voice'}
          </span>
          {/* Animated audio wave bars */}
          <span className="flex items-center gap-0.5 ml-1">
            <span className="w-1 h-3 bg-amber-400 rounded-full animate-[bounce_1s_infinite_100ms]" />
            <span className="w-1 h-4 bg-amber-400 rounded-full animate-[bounce_1s_infinite_300ms]" />
            <span className="w-1 h-2 bg-amber-400 rounded-full animate-[bounce_1s_infinite_200ms]" />
          </span>
        </>
      ) : (
        <>
          <Volume2 className="w-3.5 h-3.5 text-[#f59e0b]" />
          <span>{label || 'Read Aloud / విను'}</span>
        </>
      )}
    </button>
  );
}
