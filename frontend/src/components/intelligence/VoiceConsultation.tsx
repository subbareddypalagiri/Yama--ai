'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Mic, MicOff } from 'lucide-react';

interface VoiceConsultationProps {
  onTranscript: (text: string) => void;
  language?: string;
}

export default function VoiceConsultation({ onTranscript, language = 'en-US' }: VoiceConsultationProps) {
  const [isListening, setIsListening] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const recognitionRef = useRef<any>(null);

  const getLangCode = (lang: string) => {
    switch (lang.toLowerCase()) {
      case 'hindi': return 'hi-IN';
      case 'telugu': return 'te-IN';
      case 'tamil': return 'ta-IN';
      case 'kannada': return 'kn-IN';
      default: return 'en-IN';
    }
  };

  const toggleListening = () => {
    if (isListening) {
      if (recognitionRef.current) {
        try { recognitionRef.current.stop(); } catch {}
      }
      setIsListening(false);
      return;
    }

    setError(null);
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setError('Voice recognition is not supported in this browser. Please use Chrome or Edge.');
      return;
    }

    try {
      const recognition = new SpeechRecognition();
      recognition.lang = getLangCode(language);
      recognition.continuous = false;
      recognition.interimResults = false;

      recognition.onstart = () => {
        setIsListening(true);
      };

      recognition.onresult = (event: any) => {
        const transcript = event.results?.[0]?.[0]?.transcript;
        if (transcript) {
          onTranscript(transcript);
        }
        setIsListening(false);
      };

      recognition.onerror = (event: any) => {
        console.error('Speech recognition error', event.error);
        if (event.error !== 'no-speech') {
          setError(`Voice error: ${event.error}`);
        }
        setIsListening(false);
      };

      recognition.onend = () => {
        setIsListening(false);
      };

      recognitionRef.current = recognition;
      recognition.start();
    } catch (err: any) {
      console.error('Failed to start speech recognition', err);
      setError('Could not start microphone access.');
      setIsListening(false);
    }
  };

  useEffect(() => {
    return () => {
      if (recognitionRef.current) {
        try { recognitionRef.current.stop(); } catch {}
      }
    };
  }, []);

  return (
    <div className="relative inline-flex items-center">
      <button
        type="button"
        onClick={toggleListening}
        title={isListening ? 'Listening... Click to stop' : 'Click to speak your legal query'}
        className={`w-9 h-9 sm:w-10 sm:h-10 rounded-xl transition-all flex items-center justify-center border cursor-pointer ${
          isListening
            ? 'bg-red-500/20 text-red-400 border-red-500/60 shadow-[0_0_15px_rgba(239,68,68,0.4)] animate-pulse scale-105'
            : 'bg-white/[0.05] hover:bg-white/[0.1] text-neutral-300 hover:text-[#f59e0b] border-white/[0.1] hover:border-[#f59e0b]/40'
        }`}
      >
        {isListening ? (
          <MicOff className="w-4 h-4 text-red-400 animate-pulse" />
        ) : (
          <Mic className="w-4 h-4 text-neutral-300 hover:text-[#f59e0b] transition-colors" />
        )}
      </button>

      {error && (
        <div className="absolute bottom-14 right-0 w-64 p-2.5 rounded-xl bg-slate-900 border border-rose-500/50 text-xs text-rose-300 shadow-xl z-50">
          {error}
        </div>
      )}
    </div>
  );
}
