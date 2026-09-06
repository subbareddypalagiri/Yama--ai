'use client';

import React, { useState, useRef, useEffect, useMemo, Suspense } from 'react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { Scale, Loader2, AlertTriangle, BookOpen, ChevronLeft, Sparkles, Paperclip, X, FileText, Image as ImageIcon, File, ArrowUp, Copy, Check, RotateCcw, Settings2 } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { sendChatMessage, sendChatMessageStream, uploadChatMessage, type ChatResponseStyle, analyzeScorecard, analyzeSimulate, analyzeEstimator, type ScorecardData, type SimulationData, type EstimatorData } from '@/lib/api';
import { useLanguage } from '@/context/LanguageContext';
import { SettingsModal } from '@/components/chat/SettingsModal';
import CaseScorecard from '@/components/intelligence/CaseScorecard';
import CourtroomSimulatorModal from '@/components/intelligence/CourtroomSimulatorModal';
import SosShieldModal from '@/components/intelligence/SosShieldModal';
import LitigationEstimatorCard from '@/components/intelligence/LitigationEstimatorCard';
import VoiceConsultation from '@/components/intelligence/VoiceConsultation';
import AdvocateVoicePlayer from '@/components/intelligence/AdvocateVoicePlayer';
import StatuteDrawer from '@/components/intelligence/StatuteDrawer';
import CourtNoticeExporter from '@/components/intelligence/CourtNoticeExporter';
import type { ChatMessage, ChatApiResponse } from '@/types';


interface AttachedFile {
  file: File;
  id: string;
  preview?: string;
}

export default function ChatPage() {
  return (
    <Suspense fallback={<LoadingScreen />}>
      <ChatPageInner />
    </Suspense>
  );
}

function LoadingScreen() {
  return (
    <div className="min-h-screen bg-[#0a0a0b] flex items-center justify-center">
      <div className="flex flex-col items-center gap-4">
        <div className="relative">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-violet-500 to-fuchsia-500 flex items-center justify-center">
            <Scale className="w-6 h-6 text-white" />
          </div>
          <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-violet-500 to-fuchsia-500 blur-xl opacity-50 animate-pulse" />
        </div>
        <div className="flex gap-1">
          <span className="w-2 h-2 bg-violet-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
          <span className="w-2 h-2 bg-violet-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
          <span className="w-2 h-2 bg-violet-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
        </div>
      </div>
    </div>
  );
}

function ChatPageInner() {
  const { language } = useLanguage();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | undefined>();
  const [error, setError] = useState<string | null>(null);
  const [responseStyle, setResponseStyle] = useState<ChatResponseStyle>('roman_english');
  const [attachments, setAttachments] = useState<AttachedFile[]>([]);
  const [isFocused, setIsFocused] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const searchParams = useSearchParams();
  const autoSubmitted = useRef(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [customApiKey, setCustomApiKey] = useState('');
  const [customModel, setCustomModel] = useState('Gemini 2.5 Flash');

  // Load settings on mount
  useEffect(() => {
    const saved = localStorage.getItem('yama_ai_settings');
    if (saved) {
      try {
        const { apiKey, model } = JSON.parse(saved);
        if (apiKey) setCustomApiKey(apiKey);
        if (model) setCustomModel(model);
      } catch (e) {
        console.error('Failed to parse settings', e);
      }
    }
  }, []);

  const handleSaveSettings = (apiKey: string, model: string) => {
    setCustomApiKey(apiKey);
    setCustomModel(model);
    localStorage.setItem('yama_ai_settings', JSON.stringify({ apiKey, model }));
  };

  // Load saved chat messages on mount
  useEffect(() => {
    try {
      const saved = localStorage.getItem('yama_chat_messages');
      if (saved) {
        const parsed = JSON.parse(saved);
        if (Array.isArray(parsed) && parsed.length > 0) {
          setMessages(parsed);
        }
      }
    } catch (e) {
      console.error('Failed to parse chat messages', e);
    }
  }, []);

  // Persist messages whenever messages state updates
  useEffect(() => {
    if (messages.length > 0) {
      try {
        localStorage.setItem('yama_chat_messages', JSON.stringify(messages));
      } catch (e) {
        console.error('Failed to save chat messages', e);
      }
    }
  }, [messages]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    const q = searchParams.get('q');
    if (q && !autoSubmitted.current) {
      autoSubmitted.current = true;
      handleSubmit(decodeURIComponent(q));
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams]);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    const newAttachments: AttachedFile[] = files.map(file => ({
      file,
      id: Math.random().toString(36).slice(2),
      preview: file.type.startsWith('image/') ? URL.createObjectURL(file) : undefined,
    }));
    setAttachments(prev => [...prev, ...newAttachments].slice(0, 5));
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const removeAttachment = (id: string) => {
    setAttachments(prev => {
      const removed = prev.find(a => a.id === id);
      if (removed?.preview) URL.revokeObjectURL(removed.preview);
      return prev.filter(a => a.id !== id);
    });
  };

  const getFileIcon = (type: string) => {
    if (type.startsWith('image/')) return <ImageIcon className="w-4 h-4" />;
    if (type.includes('pdf') || type.includes('document')) return <FileText className="w-4 h-4" />;
    return <File className="w-4 h-4" />;
  };

  const handleSubmit = async (text?: string) => {
    const messageText = text || input.trim();
    if (!messageText || isLoading) return;
    setError(null);
    const attachmentInfo = attachments.length > 0 ? `\n\n[Attached: ${attachments.map(a => a.file.name).join(', ')}]` : '';
    const userMessage: ChatMessage = { id: Date.now().toString(), role: 'user', content: messageText + attachmentInfo, timestamp: new Date() };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setAttachments([]);
    setIsLoading(true);
    if (textareaRef.current) textareaRef.current.style.height = 'auto';
    
    // Map frontend language selector value to API response language
    const langMapping: Record<string, string> = {
      en: 'english',
      hi: 'hindi',
      ta: 'tamil',
      te: 'telugu',
    };
    const responseLanguage = langMapping[language] || 'english';
    
    try {
      if (attachments.length > 0 && attachments[0].file) {
        let response: ChatApiResponse;
        response = await uploadChatMessage(
          attachments[0].file,
          messageText,
          sessionId,
          responseStyle,
          responseLanguage,
          customApiKey,
          customModel
        );
        setSessionId(response.session_id);
        setMessages((prev) => [...prev, {
          id: (Date.now() + 1).toString(), role: 'assistant', content: response.analysis,
          timestamp: new Date(response.timestamp), relevantSections: response.relevant_sections,
        }]);
      } else {
        const tempId = (Date.now() + 1).toString();
        setMessages((prev) => [...prev, {
          id: tempId, role: 'assistant', content: '',
          timestamp: new Date(), relevantSections: [],
        }]);
        
        const response = await sendChatMessageStream(
          messageText,
          (chunkText) => {
            setMessages((prev) => 
              prev.map(msg => 
                msg.id === tempId 
                  ? { ...msg, content: msg.content + chunkText } 
                  : msg
              )
            );
          },
          sessionId,
          responseStyle,
          responseLanguage,
          customApiKey,
          customModel
        );
        
        setSessionId(response.session_id);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSubmit(); }
  };

  const handleTextareaInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
    e.target.style.height = 'auto';
    e.target.style.height = Math.min(e.target.scrollHeight, 200) + 'px';
  };

  const clearChat = () => {
    localStorage.removeItem('yama_chat_messages');
    setMessages([]);
    setSessionId(undefined);
    setError(null);
  };

  return (
    <div className="flex flex-col h-screen bg-[#0a0a0b] text-white overflow-hidden">
      {/* Ambient background effects */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-violet-600/[0.07] rounded-full blur-[150px]" />
        <div className="absolute bottom-0 right-1/4 w-[400px] h-[400px] bg-fuchsia-600/[0.05] rounded-full blur-[120px]" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-violet-900/[0.03] rounded-full blur-[200px]" />
      </div>

      {/* Header */}
      <header className="relative z-20 flex-shrink-0 border-b border-white/[0.06] bg-[#0a0a0b]/80 backdrop-blur-xl">
        <div className="relative max-w-5xl mx-auto px-4 py-3.5 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/" className="group flex items-center gap-3">
              <div className="relative">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#d4af37] via-[#f59e0b] to-[#78350f] p-[1.2px] shadow-lg shadow-amber-500/20 group-hover:shadow-amber-500/40 transition-shadow">
                  <div className="w-full h-full rounded-[10px] bg-[#0c0e14] flex items-center justify-center">
                    <Scale className="w-5 h-5 text-amber-400 drop-shadow-[0_0_8px_rgba(245,158,11,0.5)]" />
                  </div>
                </div>
                <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-amber-500 to-amber-700 blur-md opacity-30 group-hover:opacity-60 transition-opacity" />
              </div>
              <div className="hidden sm:block">
                <div className="flex items-center gap-2">
                  <h1 className="font-bold text-white tracking-tight text-base">YAMA AI</h1>
                  <span className="text-[9px] font-mono font-extrabold px-1.5 py-0.5 rounded bg-amber-400/10 border border-amber-400/25 text-amber-300">
                    ADVOCATE
                  </span>
                </div>
                <p className="text-[10px] text-neutral-400 font-medium">Senior Legal Intelligence Bench</p>
              </div>
            </Link>
          </div>

          {/* Real-time Statutory Engine Indicator */}
          <div className="hidden md:flex items-center gap-2.5 px-4 py-1.5 rounded-full border border-amber-500/20 bg-amber-950/20 backdrop-blur-md shadow-inner shadow-amber-500/5">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse shadow-[0_0_8px_rgba(52,211,153,0.8)]" />
            <span className="text-[10px] font-mono font-bold tracking-widest text-amber-200/90 uppercase">
              GEMINI 2.5 FLASH • ZERO-LATENCY STATUTORY REASONING
            </span>
          </div>
          
          <div className="flex items-center gap-2">
            {messages.length > 0 && (
              <button
                onClick={clearChat}
                className="flex items-center gap-2 px-3 py-1.5 text-[12px] font-medium text-neutral-300 hover:text-white rounded-lg border border-white/[0.08] hover:border-amber-500/40 bg-white/[0.03] hover:bg-amber-500/10 transition-all shadow-sm"
              >
                <RotateCcw className="w-3.5 h-3.5 text-amber-400" />
                <span className="hidden sm:inline">New Brief</span>
              </button>
            )}
            <Link 
              href="/search" 
              className="flex items-center gap-2 px-3 py-1.5 text-[12px] font-medium text-neutral-300 hover:text-white rounded-lg border border-white/[0.08] hover:border-amber-500/40 bg-white/[0.03] hover:bg-amber-500/10 transition-all shadow-sm"
            >
              <BookOpen className="w-3.5 h-3.5 text-amber-400" />
              <span className="hidden sm:inline">Statutes (12,036+)</span>
            </Link>
            <button
              onClick={() => setIsSettingsOpen(true)}
              className="flex items-center justify-center w-8 h-8 text-neutral-400 hover:text-amber-300 rounded-lg border border-white/[0.08] hover:border-amber-500/40 bg-white/[0.03] hover:bg-amber-500/10 transition-all"
              title="Settings"
            >
              <Settings2 className="w-4 h-4" />
            </button>
          </div>
        </div>
      </header>

      {/* Messages */}
      <div className="relative z-10 flex-1 overflow-y-auto scrollbar-thin scrollbar-thumb-white/10 scrollbar-track-transparent">
        <div className="max-w-3xl mx-auto px-4 py-6">
          {messages.length === 0 ? (
            <EmptyState onSubmit={handleSubmit} />
          ) : (
            <div className="space-y-8">
              {messages.map((msg, idx) => (
                <MessageBubble key={msg.id} message={msg} isLast={idx === messages.length - 1 && msg.role === 'assistant'} />
              ))}
              {isLoading && <ThinkingIndicator />}
              {error && <ErrorMessage error={error} onRetry={() => messages.length > 0 && handleSubmit(messages[messages.length - 1].content)} />}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>
      </div>

      {/* Input Area */}
      <div className="relative z-20 flex-shrink-0">
        <div className="absolute inset-0 bg-gradient-to-t from-[#0a0a0b] via-[#0a0a0b]/98 to-transparent pointer-events-none" style={{ height: '150%', bottom: 0, top: 'auto' }} />
        <div className="relative max-w-3xl mx-auto px-4 pb-6 pt-4">
          <input ref={fileInputRef} type="file" multiple accept=".pdf,.doc,.docx,.txt,.jpg,.jpeg,.png,.gif" onChange={handleFileSelect} className="hidden" />
          
          {/* Premium Input Container */}
          <div className="relative group">
            {/* Glow effect */}
            <div className={`absolute -inset-1 rounded-[28px] transition-all duration-500 ${
              isFocused 
                ? 'bg-gradient-to-r from-amber-500/25 via-amber-400/20 to-amber-600/25 blur-xl opacity-100' 
                : 'opacity-0'
            }`} />
            
            {/* Border gradient */}
            <div className={`absolute -inset-[1px] rounded-[26px] transition-all duration-300 ${
              isFocused
                ? 'bg-gradient-to-r from-[#f59e0b]/70 via-[#fbbf24]/80 to-[#d4af37]/70'
                : 'bg-gradient-to-r from-white/[0.08] via-amber-500/20 to-white/[0.08]'
            }`} />
            
            {/* Main container */}
            <div className="relative rounded-[24px] bg-[#0c0e14]/95 border border-white/[0.04] overflow-hidden backdrop-blur-xl shadow-2xl">
              {/* Subtle inner highlight */}
              <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-amber-400/20 to-transparent" />
              
              {/* Attachments */}
              {attachments.length > 0 && (
                <div className="px-4 pt-4 pb-2 border-b border-white/[0.06]">
                  <div className="flex flex-wrap gap-2">
                    {attachments.map((att) => (
                      <div key={att.id} className="group/att flex items-center gap-2.5 bg-white/[0.04] hover:bg-white/[0.08] rounded-xl px-3 py-2 transition-colors">
                        {att.preview ? (
                          <img src={att.preview} alt="" className="w-8 h-8 rounded-lg object-cover ring-1 ring-white/10" />
                        ) : (
                          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-amber-500/20 to-amber-700/20 flex items-center justify-center text-amber-400">
                            {getFileIcon(att.file.type)}
                          </div>
                        )}
                        <span className="text-[13px] text-white/60 max-w-[120px] truncate">{att.file.name}</span>
                        <button onClick={() => removeAttachment(att.id)} className="opacity-0 group-hover/att:opacity-100 text-white/30 hover:text-red-400 transition-all">
                          <X className="w-4 h-4" />
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Input row */}
              <div className="flex items-end gap-3 p-3">
                <button
                  onClick={() => fileInputRef.current?.click()}
                  disabled={isLoading || attachments.length >= 5}
                  className="flex-shrink-0 w-10 h-10 rounded-xl flex items-center justify-center text-white/30 hover:text-amber-400 hover:bg-white/[0.04] transition-all disabled:opacity-30"
                  title="Attach Documents or Photos"
                >
                  <Paperclip className="w-5 h-5" />
                </button>

                <VoiceConsultation
                  language={language}
                  onTranscript={(text) => setInput((prev) => (prev ? `${prev} ${text}` : text))}
                />

                <div className="flex-1 min-h-[44px] flex items-center">
                  <textarea
                    ref={textareaRef}
                    value={input}
                    onChange={handleTextareaInput}
                    onKeyDown={handleKeyDown}
                    onFocus={() => setIsFocused(true)}
                    onBlur={() => setIsFocused(false)}
                    placeholder="Describe your legal situation, dispute, or question in plain words..."
                    rows={1}
                    disabled={isLoading}
                    className="w-full resize-none bg-transparent text-[15px] text-white placeholder-neutral-500 focus:outline-none leading-relaxed py-2.5 max-h-[200px]"
                  />
                </div>

                <button
                  onClick={() => handleSubmit()}
                  disabled={!input.trim() || isLoading}
                  className={`flex-shrink-0 w-10 h-10 rounded-xl flex items-center justify-center transition-all duration-300 ${
                    input.trim() && !isLoading
                      ? 'bg-gradient-to-br from-[#f59e0b] via-[#fbbf24] to-[#d4af37] text-black font-extrabold shadow-lg shadow-amber-500/30 hover:shadow-amber-500/50 hover:scale-105 active:scale-95'
                      : 'bg-white/[0.04] text-white/20'
                  }`}
                >
                  {isLoading ? <Loader2 className="w-5 h-5 animate-spin text-black" /> : <ArrowUp className="w-5 h-5 font-bold" />}
                </button>
              </div>

              {/* Bottom bar inside dock */}
              <div className="px-4 pb-3 pt-1 flex items-center justify-between border-t border-white/[0.04]">
                <div className="hidden sm:flex items-center gap-2 text-[11px] text-neutral-500 font-mono">
                  <kbd className="px-1.5 py-0.5 rounded bg-white/[0.06] border border-white/10 text-neutral-300 text-[10px]">⏎</kbd> send
                  <span className="opacity-30">•</span>
                  <kbd className="px-1.5 py-0.5 rounded bg-white/[0.06] border border-white/10 text-neutral-300 text-[10px]">Shift + ⏎</kbd> newline
                </div>

                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={() => setResponseStyle((prev) => (prev === 'default' ? 'roman_english' : 'default'))}
                    className={`inline-flex items-center gap-1.5 text-[11px] px-3 py-1 rounded-full border transition-all font-mono font-medium ${
                      responseStyle === 'roman_english'
                        ? 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30 shadow-sm shadow-emerald-500/10'
                        : 'bg-white/[0.02] text-white/45 border-white/[0.08] hover:text-white/70 hover:border-white/20'
                    }`}
                  >
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                    {responseStyle === 'roman_english' ? 'ROMAN ENGLISH (ACTIVE)' : 'DEFAULT MODE'}
                  </button>
                </div>
              </div>
            </div>
          </div>

          <p className="text-[11px] text-white/15 mt-4 text-center">
            YAMA AI provides legal information only — always consult a qualified advocate for legal advice
          </p>
        </div>
      </div>

      <SettingsModal 
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        onSave={handleSaveSettings}
        initialApiKey={customApiKey}
        initialModel={customModel}
      />
    </div>
  );
}

function EmptyState({ onSubmit }: { onSubmit: (text: string) => void }) {
  const scenarios = [
    {
      title: 'Tenant Security Deposit Recovery',
      statute: 'AP/TS Tenancy Act § 21 & Contract Act § 73',
      badge: '18% PENAL INTEREST',
      prompt: 'My landlord refuses to return my security deposit after 30 days of vacating the flat.',
    },
    {
      title: 'Challan Lok Adalat Waiver Petition',
      statute: 'MV Act § 136A & Legal Services Act § 19',
      badge: '50-75% DISCOUNT',
      prompt: 'I received an automated speed camera challan without calibration certificate, need Lok Adalat waiver petition.',
    },
    {
      title: 'Police Arrest / Unlawful Summons Shield',
      statute: 'BNSS § 35, § 43 & Arnesh Kumar',
      badge: 'ARREST SHIELD',
      prompt: 'Police called me to the police station without Section 35 BNSS notice of appearance.',
    },
    {
      title: 'BSA Cryptographic Evidence Verification',
      statute: 'BSA 2023 § 63 & Arjun Panditrao',
      badge: 'CRYPTO CERTIFIED',
      prompt: 'Need Section 63 BSA certificate hash for WhatsApp chat screenshots and UPI payment proofs.',
    },
  ];

  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] text-center px-4 py-8">
      {/* Executive Seal with Gold Rim */}
      <div className="relative mb-6">
        <div className="w-20 h-20 rounded-3xl bg-gradient-to-br from-[#d4af37] via-[#f59e0b] to-[#78350f] p-[1.5px] shadow-2xl shadow-amber-500/25">
          <div className="w-full h-full rounded-[22px] bg-[#0a0b10] flex items-center justify-center">
            <Scale className="w-9 h-9 text-amber-400 drop-shadow-[0_0_12px_rgba(245,158,11,0.6)]" />
          </div>
        </div>
        <div className="absolute inset-0 rounded-3xl bg-gradient-to-br from-amber-500 to-amber-700 blur-2xl opacity-30" />
      </div>

      {/* Pill Badge */}
      <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full border border-amber-500/30 bg-amber-950/30 text-amber-300 text-[11px] font-mono font-bold tracking-widest uppercase mb-4 shadow-sm">
        <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse shadow-[0_0_8px_rgba(52,211,153,0.8)]" />
        SENIOR ADVOCATE BENCH • 12,036+ LAWS ENFORCED
      </div>

      <h2 className="text-3xl sm:text-4xl font-extrabold text-white mb-3 tracking-tight">
        Executive Legal Consultation
      </h2>
      <p className="text-neutral-400 mb-10 max-w-lg text-[14px] leading-relaxed">
        Autonomous statutory defense under the 2023 Sanhitas &amp; 28 State Acts. Ask in Roman English, Telugu, or English for immediate legal leverage.
      </p>
      
      {/* High-Contrast Scenario Cards */}
      <div className="w-full max-w-2xl grid grid-cols-1 sm:grid-cols-2 gap-3 text-left">
        {scenarios.map((sc, i) => (
          <button
            key={i}
            onClick={() => onSubmit(sc.prompt)}
            className="group relative p-4 rounded-2xl bg-[#0e1017] border border-[#1d2230] hover:border-amber-500/60 hover:bg-[#131622] transition-all duration-200 flex flex-col justify-between shadow-lg text-left"
          >
            <div>
              <div className="flex items-center justify-between gap-2 mb-2">
                <span className="text-[9px] font-mono font-extrabold px-2 py-0.5 rounded bg-amber-400/10 border border-amber-400/30 text-amber-300 uppercase tracking-wide">
                  {sc.badge}
                </span>
                <ArrowUp className="w-3.5 h-3.5 text-neutral-500 group-hover:text-amber-400 rotate-45 transition-colors" />
              </div>
              <h4 className="text-[13px] font-bold text-white group-hover:text-amber-200 transition-colors leading-snug mb-1">
                {sc.title}
              </h4>
              <p className="text-[10px] font-mono font-semibold text-amber-400/80 mb-2">
                {sc.statute}
              </p>
              <p className="text-[12px] text-neutral-400 line-clamp-2 leading-relaxed">
                &ldquo;{sc.prompt}&rdquo;
              </p>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}

function MessageBubble({ message, isLast }: { message: ChatMessage; isLast: boolean }) {
  const isUser = message.role === 'user';
  const [copied, setCopied] = useState(false);
  
  // Intelligence Suite states
  const [scorecard, setScorecard] = useState<ScorecardData | null>(null);
  const [loadingScorecard, setLoadingScorecard] = useState(false);
  const [showScorecard, setShowScorecard] = useState(false);

  const [simulation, setSimulation] = useState<SimulationData | null>(null);
  const [loadingSimulation, setLoadingSimulation] = useState(false);
  const [isSimulatorOpen, setIsSimulatorOpen] = useState(false);

  const [estimator, setEstimator] = useState<EstimatorData | null>(null);
  const [loadingEstimator, setLoadingEstimator] = useState(false);
  const [isEstimatorOpen, setIsEstimatorOpen] = useState(false);

  const [isSosOpen, setIsSosOpen] = useState(false);
  const [activeCitation, setActiveCitation] = useState<string | null>(null);

  const detectedCitations = React.useMemo(() => {
    if (isUser) return [];
    const text = message.content;
    const list: { key: string; label: string }[] = [];
    if (/318|cheating/i.test(text)) list.push({ key: '318_bns', label: '§ 318 BNS (Cheating)' });
    if (/35(\s*bnss|\s*of\s*bnss)|notice\s*of\s*appearance/i.test(text)) list.push({ key: '35_bnss', label: '§ 35 BNSS (Notice Mandate)' });
    if (/43(\s*bnss|\s*of\s*bnss)|meet\s*advocate/i.test(text)) list.push({ key: '43_bnss', label: '§ 43 BNSS (Right to Advocate)' });
    if (/63(\s*bsa|\s*of\s*bsa)|electronic\s*record|65b/i.test(text)) list.push({ key: '63_bsa', label: '§ 63 BSA (Electronic Hash)' });
    if (/136a|speed\s*camera|challan|lok\s*adalat/i.test(text)) list.push({ key: '136a_mv', label: '§ 136A MV Act (Challan Waiver)' });
    if (/22|fundamental\s*right|custody|24\s*hours/i.test(text)) list.push({ key: '22_art', label: 'Art. 22 (Arrest Rights)' });
    if (/deposit|tenan|landlord|rent/i.test(text)) list.push({ key: '21_tenancy', label: '§ 21 Tenancy Act (Deposit Refund)' });
    return list;
  }, [message.content, isUser]);

  const copyToClipboard = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleOpenScorecard = async () => {
    setShowScorecard(!showScorecard);
    if (!scorecard && !loadingScorecard && !showScorecard) {
      setLoadingScorecard(true);
      try {
        const data = await analyzeScorecard(message.content);
        setScorecard(data);
      } catch (e) {
        console.error('Scorecard analysis failed', e);
      } finally {
        setLoadingScorecard(false);
      }
    }
  };

  const handleOpenSimulation = async () => {
    setIsSimulatorOpen(true);
    if (!simulation && !loadingSimulation) {
      setLoadingSimulation(true);
      try {
        const data = await analyzeSimulate(message.content);
        setSimulation(data);
      } catch (e) {
        console.error('Simulation failed', e);
      } finally {
        setLoadingSimulation(false);
      }
    }
  };

  const handleOpenEstimator = async () => {
    setIsEstimatorOpen(true);
    if (!estimator && !loadingEstimator) {
      setLoadingEstimator(true);
      try {
        const data = await analyzeEstimator(message.content);
        setEstimator(data);
      } catch (e) {
        console.error('Estimator failed', e);
      } finally {
        setLoadingEstimator(false);
      }
    }
  };

  return (
    <div className={`group relative mb-6 ${isUser ? 'flex justify-end' : 'w-full'}`}>
      {isUser ? (
        <div className="flex items-start gap-3 max-w-[85%] sm:max-w-[75%]">
          <div className="p-4 rounded-2xl rounded-tr-sm bg-gradient-to-br from-[#121c24] to-[#142624] border border-[#1d3d3a] shadow-lg text-white">
            <div className="flex items-center justify-between gap-4 mb-1 text-[11px] font-mono text-emerald-400">
              <span className="font-bold">CLIENT INQUIRY</span>
              <span className="text-gray-500">{new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
            </div>
            <p className="text-[14px] leading-relaxed whitespace-pre-wrap font-sans text-gray-100">{message.content}</p>
          </div>
          <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-700 flex items-center justify-center text-xs font-bold text-black shrink-0 shadow-md">
            U
          </div>
        </div>
      ) : (
        <div className="w-full rounded-2xl bg-[#0c0e15] border border-white/[0.08] hover:border-[#f59e0b]/35 transition-all duration-300 shadow-[0_15px_40px_rgba(0,0,0,0.6)] overflow-hidden">
          {/* Card Top Header - Senior Counsel Identity */}
          <div className="px-5 py-3.5 bg-[#0f121b] border-b border-[#1b1f2e] flex flex-wrap items-center justify-between gap-2 text-xs">
            <div className="flex items-center gap-2.5">
              <div className="w-7 h-7 rounded-lg bg-[#1a1711] border border-[#3e311a] flex items-center justify-center">
                <Scale className="w-3.5 h-3.5 text-[#f59e0b]" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-bold text-white tracking-tight">YAMA AI</span>
                  <span className="px-1.5 py-0.5 rounded text-[8px] font-mono font-bold bg-amber-500/10 text-amber-300 border border-amber-500/20 uppercase">
                    SENIOR ADVOCATE
                  </span>
                  <span className="px-1.5 py-0.5 rounded text-[8px] font-mono font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 uppercase hidden sm:inline">
                    ROMAN ENGLISH
                  </span>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-2 text-gray-400 text-[11px] font-mono">
              {isLast && (
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" title="Active Analysis" />
              )}
              <span>{new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
            </div>
          </div>

          {/* Analysis Body */}
          <div className="p-5 sm:p-6 text-gray-200 leading-relaxed text-[14px] font-sans">
            <div className="prose prose-invert prose-sm max-w-none 
              prose-p:text-gray-300 prose-p:leading-relaxed prose-p:text-[14px] prose-p:my-2.5
              prose-headings:text-white prose-headings:font-bold prose-headings:tracking-tight
              prose-h3:text-base prose-h3:mt-4 prose-h3:mb-2 prose-h3:border-l-2 prose-h3:border-[#f59e0b] prose-h3:pl-2.5
              prose-h4:text-sm prose-h4:mt-3 prose-h4:mb-1.5 prose-h4:text-amber-200
              prose-strong:text-white prose-strong:font-bold
              prose-li:text-gray-300 prose-li:my-1
              prose-code:text-amber-300 prose-code:bg-[#1a1c26] prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded prose-code:border prose-code:border-[#2b3042]
              prose-pre:bg-[#07080b] prose-pre:border prose-pre:border-white/10
              prose-a:text-[#f59e0b] prose-a:underline hover:prose-a:text-amber-300
            ">
              <ReactMarkdown>{message.content}</ReactMarkdown>
            </div>
          </div>

          {/* Statutory Grounding Citations Strip */}
          {detectedCitations.length > 0 && (
            <div className="px-5 sm:px-6 py-2.5 bg-[#090b10] border-t border-[#161a26] flex flex-wrap items-center gap-2 text-xs">
              <span className="text-[10px] font-mono text-amber-400 font-bold uppercase tracking-wider">
                Statutory Citations:
              </span>
              {detectedCitations.map((c) => (
                <button
                  key={c.key}
                  onClick={() => setActiveCitation(c.key)}
                  className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-[11px] font-mono font-bold bg-[#12141c] hover:bg-[#1a1f2e] text-amber-300 border border-[#242a3c] hover:border-[#f59e0b]/70 transition-all shadow-sm cursor-pointer"
                  title="Click to view full statutory text & punishment details"
                >
                  <Scale className="w-3 h-3 text-[#f59e0b]" />
                  <span>{c.label}</span>
                </button>
              ))}
            </div>
          )}

          {/* Segmented Action Deck */}
          <div className="px-5 sm:px-6 py-3.5 bg-[#0a0c12] border-t border-[#161a26] flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            {/* Primary Action Controls: Voice, PDF, Copy */}
            <div className="flex flex-wrap items-center gap-2">
              <AdvocateVoicePlayer text={message.content} />
              <CourtNoticeExporter content={message.content} />
              <button
                onClick={copyToClipboard}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold bg-[#12141c] hover:bg-[#181b26] text-gray-300 hover:text-white border border-[#252a3a] hover:border-[#f59e0b]/50 transition-all shadow-sm"
              >
                {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5 text-gray-400" />}
                <span>{copied ? 'Copied' : 'Copy Brief'}</span>
              </button>
            </div>

            {/* Secondary Intelligence Tools */}
            <div className="flex flex-wrap items-center gap-1.5">
              <button
                onClick={handleOpenScorecard}
                className="px-2.5 py-1.5 text-xs font-bold text-purple-300 hover:text-white rounded-lg bg-purple-950/40 hover:bg-purple-900/60 border border-purple-500/30 transition-all shadow-sm cursor-pointer"
                title="Calculate Case Win Probability"
              >
                <span>📊 {showScorecard ? 'Hide Odds' : 'Win Odds'}</span>
              </button>

              <button
                onClick={handleOpenSimulation}
                className="px-2.5 py-1.5 text-xs font-bold text-indigo-300 hover:text-white rounded-lg bg-indigo-950/40 hover:bg-indigo-900/60 border border-indigo-500/30 transition-all shadow-sm cursor-pointer"
                title="360° Courtroom Simulator"
              >
                <span>⚔️ Simulator</span>
              </button>

              <button
                onClick={() => setIsSosOpen(true)}
                className="px-2.5 py-1.5 text-xs font-bold text-rose-300 hover:text-white rounded-lg bg-rose-950/40 hover:bg-rose-900/60 border border-rose-500/30 transition-all shadow-sm cursor-pointer animate-pulse"
                title="Emergency SOS Police Arrest Rights"
              >
                <span>🚨 SOS</span>
              </button>

              <button
                onClick={handleOpenEstimator}
                className="px-2.5 py-1.5 text-xs font-bold text-emerald-300 hover:text-white rounded-lg bg-emerald-950/40 hover:bg-emerald-900/60 border border-emerald-500/30 transition-all shadow-sm cursor-pointer"
                title="Litigation Timeline & Court Cost Estimator"
              >
                <span>⏳ Timeline</span>
              </button>
            </div>
          </div>

          {/* Attached Modals */}
          <StatuteDrawer
            isOpen={!!activeCitation}
            citationKey={activeCitation}
            onClose={() => setActiveCitation(null)}
          />

          {showScorecard && (
            <div className="p-4 border-t border-[#161a26] bg-[#07080b]">
              <CaseScorecard
                scorecard={scorecard}
                loading={loadingScorecard}
                onRefresh={() => {
                  setScorecard(null);
                  handleOpenScorecard();
                }}
              />
            </div>
          )}

          <CourtroomSimulatorModal
            isOpen={isSimulatorOpen}
            onClose={() => setIsSimulatorOpen(false)}
            simulation={simulation}
            loading={loadingSimulation}
            situation={message.content}
          />

          <SosShieldModal
            isOpen={isSosOpen}
            onClose={() => setIsSosOpen(false)}
          />

          <LitigationEstimatorCard
            isOpen={isEstimatorOpen}
            onClose={() => setIsEstimatorOpen(false)}
            estimator={estimator}
            loading={loadingEstimator}
          />
        </div>
      )}
    </div>
  );
}


function ThinkingIndicator() {
  return (
    <div className="flex gap-4">
      <div className="relative flex-shrink-0">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#d4af37] via-[#f59e0b] to-[#78350f] p-[1.2px] shadow-lg shadow-amber-500/20">
          <div className="w-full h-full rounded-[10px] bg-[#0c0e14] flex items-center justify-center">
            <Scale className="w-5 h-5 text-amber-400 animate-pulse drop-shadow-[0_0_8px_rgba(245,158,11,0.5)]" />
          </div>
        </div>
      </div>
      <div className="flex-1">
        <div className="mb-2 flex items-center gap-2">
          <span className="text-[12px] font-bold text-amber-300">YAMA AI</span>
          <span className="text-[10px] font-mono text-neutral-400 uppercase tracking-widest">• Senior Advocate Bench</span>
        </div>
        <div className="inline-flex items-center gap-3 rounded-2xl rounded-tl-md px-5 py-3.5 bg-[#0e1017] border border-amber-500/20 shadow-xl">
          <div className="flex gap-1.5">
            <span className="w-2 h-2 bg-amber-400 rounded-full animate-bounce shadow-[0_0_6px_rgba(245,158,11,0.6)]" style={{ animationDelay: '0ms' }} />
            <span className="w-2 h-2 bg-amber-400 rounded-full animate-bounce shadow-[0_0_6px_rgba(245,158,11,0.6)]" style={{ animationDelay: '150ms' }} />
            <span className="w-2 h-2 bg-amber-400 rounded-full animate-bounce shadow-[0_0_6px_rgba(245,158,11,0.6)]" style={{ animationDelay: '300ms' }} />
          </div>
          <span className="text-[13px] text-neutral-300 font-medium font-mono">Evaluating 12,036+ Bare Acts &amp; Sanhita Precedents...</span>
        </div>
      </div>
    </div>
  );
}

function ErrorMessage({ error, onRetry }: { error: string; onRetry: () => void }) {
  return (
    <div className="flex gap-4">
      <div className="flex-shrink-0 w-9 h-9 rounded-xl bg-gradient-to-br from-red-500/20 to-orange-500/20 border border-red-500/30 flex items-center justify-center">
        <AlertTriangle className="w-4 h-4 text-red-400" />
      </div>
      <div className="flex-1">
        <div className="mb-2">
          <span className="text-[12px] font-medium text-red-400">Error</span>
        </div>
        <div className="rounded-2xl rounded-tl-md px-5 py-4 bg-red-500/5 border border-red-500/20">
          <p className="text-[14px] text-red-300/80 mb-3">{error}</p>
          <button
            onClick={onRetry}
            className="flex items-center gap-2 px-4 py-2 text-[13px] text-white bg-red-500/20 hover:bg-red-500/30 rounded-lg transition-colors"
          >
            <RotateCcw className="w-4 h-4" />
            Try again
          </button>
        </div>
      </div>
    </div>
  );
}
