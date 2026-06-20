'use client';

import { useState, useRef, useEffect, Suspense } from 'react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { Scale, Loader2, AlertTriangle, BookOpen, ChevronLeft, Sparkles, Paperclip, X, FileText, Image as ImageIcon, File, ArrowUp, Copy, Check, RotateCcw, Settings2 } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { sendChatMessage, type ChatResponseStyle } from '@/lib/api';
import { useLanguage } from '@/context/LanguageContext';
import { SettingsModal } from '@/components/chat/SettingsModal';
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
  const [responseStyle, setResponseStyle] = useState<ChatResponseStyle>('default');
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
      const response: ChatApiResponse = await sendChatMessage(
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
      <header className="relative z-20 flex-shrink-0">
        <div className="absolute inset-0 bg-gradient-to-b from-[#0a0a0b] via-[#0a0a0b]/95 to-transparent" />
        <div className="relative max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/" className="group flex items-center gap-3">
              <div className="relative">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-500 via-violet-600 to-fuchsia-600 flex items-center justify-center shadow-lg shadow-violet-500/25 group-hover:shadow-violet-500/40 transition-shadow">
                  <Scale className="w-5 h-5 text-white" />
                </div>
                <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-violet-500 to-fuchsia-600 blur-lg opacity-40 group-hover:opacity-60 transition-opacity" />
              </div>
              <div className="hidden sm:block">
                <h1 className="font-semibold text-white tracking-tight">YAMA AI</h1>
                <p className="text-[11px] text-white/30 -mt-0.5">Legal Intelligence</p>
              </div>
            </Link>
          </div>
          
          <div className="flex items-center gap-2">
            {messages.length > 0 && (
              <button
                onClick={clearChat}
                className="flex items-center gap-2 px-3 py-2 text-[13px] text-white/40 hover:text-white/70 rounded-lg hover:bg-white/5 transition-all"
              >
                <RotateCcw className="w-4 h-4" />
                <span className="hidden sm:inline">New chat</span>
              </button>
            )}
            <button
              onClick={() => setIsSettingsOpen(true)}
              className="flex items-center justify-center w-9 h-9 text-white/40 hover:text-white/70 rounded-lg hover:bg-white/5 transition-all"
              title="Settings"
            >
              <Settings2 className="w-5 h-5" />
            </button>
            <Link 
              href="/search" 
              className="flex items-center gap-2 px-4 py-2 text-[13px] text-white/40 hover:text-white/70 rounded-lg hover:bg-white/5 transition-all"
            >
              <BookOpen className="w-4 h-4" />
              <span className="hidden sm:inline">Laws</span>
            </Link>
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
                ? 'bg-gradient-to-r from-violet-500/30 via-fuchsia-500/30 to-violet-500/30 blur-xl opacity-100' 
                : 'opacity-0'
            }`} />
            
            {/* Border gradient */}
            <div className={`absolute -inset-[1px] rounded-[26px] transition-all duration-300 ${
              isFocused
                ? 'bg-gradient-to-r from-violet-500/50 via-fuchsia-500/50 to-violet-500/50'
                : 'bg-gradient-to-r from-white/[0.08] via-white/[0.12] to-white/[0.08]'
            }`} />
            
            {/* Main container */}
            <div className="relative rounded-[24px] bg-[#111113] overflow-hidden">
              {/* Subtle inner highlight */}
              <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/10 to-transparent" />
              
              {/* Attachments */}
              {attachments.length > 0 && (
                <div className="px-4 pt-4 pb-2 border-b border-white/[0.06]">
                  <div className="flex flex-wrap gap-2">
                    {attachments.map((att) => (
                      <div key={att.id} className="group/att flex items-center gap-2.5 bg-white/[0.04] hover:bg-white/[0.08] rounded-xl px-3 py-2 transition-colors">
                        {att.preview ? (
                          <img src={att.preview} alt="" className="w-8 h-8 rounded-lg object-cover ring-1 ring-white/10" />
                        ) : (
                          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-500/20 to-fuchsia-500/20 flex items-center justify-center text-violet-400">
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
                  className="flex-shrink-0 w-10 h-10 rounded-xl flex items-center justify-center text-white/25 hover:text-white/50 hover:bg-white/[0.04] transition-all disabled:opacity-30"
                >
                  <Paperclip className="w-5 h-5" />
                </button>

                <div className="flex-1 min-h-[44px] flex items-center">
                  <textarea
                    ref={textareaRef}
                    value={input}
                    onChange={handleTextareaInput}
                    onKeyDown={handleKeyDown}
                    onFocus={() => setIsFocused(true)}
                    onBlur={() => setIsFocused(false)}
                    placeholder="Describe your legal situation..."
                    rows={1}
                    disabled={isLoading}
                    className="w-full resize-none bg-transparent text-[15px] text-white placeholder-white/20 focus:outline-none leading-relaxed py-2.5 max-h-[200px]"
                  />
                </div>

                <button
                  onClick={() => handleSubmit()}
                  disabled={!input.trim() || isLoading}
                  className={`flex-shrink-0 w-10 h-10 rounded-xl flex items-center justify-center transition-all duration-300 ${
                    input.trim() && !isLoading
                      ? 'bg-gradient-to-br from-violet-500 to-fuchsia-600 text-white shadow-lg shadow-violet-500/30 hover:shadow-violet-500/50 hover:scale-105 active:scale-95'
                      : 'bg-white/[0.04] text-white/15'
                  }`}
                >
                  {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : <ArrowUp className="w-5 h-5" />}
                </button>
              </div>

              {/* Response style */}
              <div className="px-3 pb-3 flex justify-end">
                <button
                  type="button"
                  onClick={() => setResponseStyle((prev) => (prev === 'default' ? 'roman_english' : 'default'))}
                  className={`text-[11px] px-3 py-1.5 rounded-lg border transition-colors ${
                    responseStyle === 'roman_english'
                      ? 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30'
                      : 'bg-white/[0.02] text-white/45 border-white/[0.08] hover:text-white/70 hover:border-white/20'
                  }`}
                >
                  {responseStyle === 'roman_english' ? 'Reply mode: Roman English' : 'Reply mode: Default'}
                </button>
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
  const examples = [
    'My landlord refuses to return my security deposit',
    'Someone posted my private photos online without consent',
    'My employer hasn\'t paid salary for 3 months',
    'I received a defective product, seller refusing refund',
  ];

  return (
    <div className="flex flex-col items-center justify-center min-h-[65vh] text-center px-4">
      {/* Logo with glow */}
      <div className="relative mb-8">
        <div className="w-20 h-20 rounded-3xl bg-gradient-to-br from-violet-500 via-violet-600 to-fuchsia-600 flex items-center justify-center shadow-2xl shadow-violet-500/30">
          <Scale className="w-9 h-9 text-white" />
        </div>
        <div className="absolute inset-0 rounded-3xl bg-gradient-to-br from-violet-500 to-fuchsia-600 blur-2xl opacity-40" />
      </div>

      <h2 className="text-3xl font-semibold text-white mb-3 tracking-tight">
        How can I help you?
      </h2>
      <p className="text-white/30 mb-12 max-w-md text-[15px] leading-relaxed">
        Describe any legal situation in plain language. I&apos;ll analyze it using Indian laws and the IRAC framework.
      </p>
      
      {/* Example cards */}
      <div className="w-full max-w-lg space-y-3">
        {examples.map((ex, i) => (
          <button
            key={i}
            onClick={() => onSubmit(ex)}
            className="group w-full relative overflow-hidden"
          >
            <div className="absolute inset-0 bg-gradient-to-r from-violet-500/10 to-fuchsia-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
            <div className="relative px-5 py-4 rounded-2xl text-left text-[14px] text-white/50 bg-white/[0.02] border border-white/[0.06] group-hover:border-violet-500/30 group-hover:text-white/70 transition-all duration-300 flex items-center justify-between">
              <span>{ex}</span>
              <ArrowUp className="w-4 h-4 opacity-0 group-hover:opacity-100 -rotate-45 transition-all" />
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
  
  const copyToClipboard = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className={`group relative ${isUser ? '' : ''}`}>
      <div className={`flex gap-4 ${isUser ? 'flex-row-reverse' : ''}`}>
        {/* Avatar */}
        <div className={`flex-shrink-0 relative ${isUser ? '' : ''}`}>
          <div className={`w-9 h-9 rounded-xl flex items-center justify-center ${
            isUser 
              ? 'bg-gradient-to-br from-emerald-400 to-cyan-500' 
              : 'bg-gradient-to-br from-violet-500 to-fuchsia-600'
          }`}>
            {isUser ? (
              <span className="text-[13px] font-semibold text-white">U</span>
            ) : (
              <Sparkles className="w-4 h-4 text-white" />
            )}
          </div>
          {!isUser && (
            <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-violet-500 to-fuchsia-600 blur-lg opacity-30" />
          )}
        </div>

        {/* Content */}
        <div className={`flex-1 min-w-0 ${isUser ? 'flex justify-end' : ''}`}>
          <div className={`inline-block max-w-full ${isUser ? 'text-right' : ''}`}>
            {/* Label */}
            <div className={`flex items-center gap-2 mb-2 ${isUser ? 'justify-end' : ''}`}>
              <span className="text-[12px] font-medium text-white/40">
                {isUser ? 'You' : 'YAMA AI'}
              </span>
              {!isUser && isLast && (
                <span className="px-2 py-0.5 rounded-full bg-violet-500/10 text-violet-400 text-[10px] font-medium">
                  Latest
                </span>
              )}
            </div>

            {/* Message content */}
            <div className={`relative rounded-2xl px-5 py-4 ${
              isUser 
                ? 'bg-gradient-to-br from-white/[0.08] to-white/[0.04] rounded-tr-md' 
                : 'bg-gradient-to-br from-white/[0.04] to-transparent border border-white/[0.06] rounded-tl-md'
            }`}>
              {isUser ? (
                <p className="text-[15px] text-white/90 leading-relaxed whitespace-pre-wrap">{message.content}</p>
              ) : (
                <div className="prose prose-invert prose-sm max-w-none 
                  prose-p:text-white/80 prose-p:leading-relaxed prose-p:text-[15px]
                  prose-headings:text-white prose-headings:font-semibold
                  prose-strong:text-white prose-strong:font-semibold
                  prose-li:text-white/75
                  prose-code:text-violet-300 prose-code:bg-violet-500/10 prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded
                  prose-pre:bg-black/30 prose-pre:border prose-pre:border-white/10
                  prose-a:text-violet-400 prose-a:no-underline hover:prose-a:underline
                ">
                  <ReactMarkdown>{message.content}</ReactMarkdown>
                </div>
              )}
            </div>

            {/* Actions */}
            {!isUser && (
              <div className="flex items-center gap-2 mt-3 opacity-0 group-hover:opacity-100 transition-opacity">
                <button
                  onClick={copyToClipboard}
                  className="flex items-center gap-1.5 px-2.5 py-1.5 text-[11px] text-white/30 hover:text-white/60 rounded-lg hover:bg-white/5 transition-all"
                >
                  {copied ? <Check className="w-3.5 h-3.5 text-green-400" /> : <Copy className="w-3.5 h-3.5" />}
                  <span>{copied ? 'Copied' : 'Copy'}</span>
                </button>
              </div>
            )}

            {/* Relevant sections */}
            {message.relevantSections && message.relevantSections.length > 0 && (
              <div className="mt-4 flex flex-wrap gap-2">
                {message.relevantSections.slice(0, 5).map((section, i) => (
                  <span 
                    key={i} 
                    className="px-3 py-1.5 rounded-lg bg-gradient-to-r from-violet-500/10 to-fuchsia-500/10 text-violet-300 text-[11px] font-medium border border-violet-500/20"
                  >
                    {section.act_name} § {section.section_number}
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function ThinkingIndicator() {
  return (
    <div className="flex gap-4">
      <div className="relative flex-shrink-0">
        <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-violet-500 to-fuchsia-600 flex items-center justify-center">
          <Sparkles className="w-4 h-4 text-white" />
        </div>
        <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-violet-500 to-fuchsia-600 blur-lg opacity-40 animate-pulse" />
      </div>
      <div className="flex-1">
        <div className="mb-2">
          <span className="text-[12px] font-medium text-white/40">YAMA AI</span>
        </div>
        <div className="inline-flex items-center gap-3 rounded-2xl rounded-tl-md px-5 py-4 bg-gradient-to-br from-white/[0.04] to-transparent border border-white/[0.06]">
          <div className="flex gap-1.5">
            <span className="w-2 h-2 bg-gradient-to-br from-violet-400 to-fuchsia-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
            <span className="w-2 h-2 bg-gradient-to-br from-violet-400 to-fuchsia-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
            <span className="w-2 h-2 bg-gradient-to-br from-violet-400 to-fuchsia-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
          </div>
          <span className="text-[13px] text-white/30">Analyzing your situation...</span>
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
