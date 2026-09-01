'use client';

import React, { useState, useEffect, useRef } from 'react';

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
        recognitionRef.current.stop();
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
        const transcript = event.results[0][0].transcript;
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
        className={`p-3 rounded-2xl transition-all flex items-center justify-center border ${
          isListening
            ? 'bg-rose-600 text-white border-rose-400 shadow-[0_0_20px_rgba(244,63,94,0.6)] animate-pulse scale-105'
            : 'bg-purple-900/40 hover:bg-purple-800/60 text-purple-200 border-purple-500/30'
        }`}
      >
        <span className="text-xl">{isListening ? '🛑' : '🎙️'}</span>
      </button>

      {error && (
        <div className="absolute bottom-14 right-0 w-64 p-2.5 rounded-xl bg-slate-900 border border-rose-500/50 text-xs text-rose-300 shadow-xl z-50">
          {error}
        </div>
      )}
    </div>
  );
}
